"""End-to-end analysis pipeline (feeds the API/dashboard).

Runs ground-truth sim -> observe -> virtual sensing -> forecast -> prescription ->
defect trace, and packages everything the three dashboard views need into one JSON-able
dict. Results are cached per scenario so the API is snappy.
"""

from __future__ import annotations

from functools import lru_cache

import numpy as np

from .defect_trace import trace_defects
from .forecast import forecast, p_binding_by_station
from .ground_truth_sim import GroundTruthSim
from .line import build_variant_line
from .observe import extract_observation
from .online_filter import run_live
from .prescribe import recommend
from .root_cause import cusum_change_point
from .scenarios import load_scenario
from .virtual_sensor import (
    blocked_starved_bottleneck,
    estimate_cycle_times,
    estimate_service_times_variant,
)


def _display_state(sid, instrumented, obs, bottleneck):
    if instrumented and sid in obs.state_frac:
        f = obs.state_frac[sid]
        return max(("working", "blocked", "starved"), key=lambda k: f.get(k, 0))
    # dark station: infer from position relative to the constraint
    if sid == bottleneck:
        return "working"
    return "blocked" if sid < bottleneck else "starved"


def _drift_window(obs, station_id):
    """Detect an SPC onset at a station via segment travel-time CUSUM."""
    cps = obs.line.checkpoints()
    a = max([c for c in cps if c <= station_id], default=cps[0])
    b = min([c for c in cps if c > station_id], default=cps[-1])
    pairs = sorted((sc[a], sc[b] - sc[a]) for sc in obs.vehicle_scans.values()
                   if a in sc and b in sc and sc[b] > sc[a])
    if len(pairs) < 8:
        return None
    times = [t for t, _ in pairs]
    series = [d for _, d in pairs]
    bins = np.linspace(0, obs.line.takt_s and max(times) or 1, 41)
    idx = np.digitize(times, bins)
    wt, wtimes = [], []
    for k in range(1, len(bins)):
        vals = [series[i] for i in range(len(series)) if idx[i] == k]
        if vals:
            wt.append(float(np.mean(vals)))
            wtimes.append(float(np.mean([times[i] for i in range(len(times)) if idx[i] == k])))
    onset, _ = cusum_change_point(wt)
    if onset is None:
        return None
    return wtimes[min(onset, len(wtimes) - 1)]


@lru_cache(maxsize=8)
def analyze(scenario_name: str) -> dict:
    res = GroundTruthSim(scenario=load_scenario(scenario_name)).run()
    obs = extract_observation(res)
    est = estimate_cycle_times(obs)
    bottleneck, conf = blocked_starved_bottleneck(obs)
    pb = p_binding_by_station(est, res.line, M=500)
    fc = forecast(est, res.line, horizon_s=7200, M=500)
    rec = recommend(est, res.line, 7200)

    stations = []
    for s in res.line.stations:
        b = est[s.id]
        stations.append({
            "id": s.id, "name": s.name, "zone": s.zone,
            "instrumented": s.instrumented,
            "state": _display_state(s.id, s.instrumented, obs, bottleneck),
            "cycle": {"mean": b.mean, "lo": b.lo, "hi": b.hi},
            "p_binding": pb.get(s.id, 0.0),
            "is_bottleneck": s.id == bottleneck,
        })

    # defect trace (only meaningful when a drift was injected)
    defect = None
    drift_ev = next((e for e in res.scenario.events if e.type == "drift"), None)
    if drift_ev and drift_ev.station_id is not None:
        onset = _drift_window(obs, drift_ev.station_id) or drift_ev.at_s
        tr = trace_defects(obs, drift_ev.station_id, onset, res.duration_s)
        n = len(res.line.stations)
        still_on_line = sum(1 for p in tr.current_positions.values() if p < n)
        defect = {
            "station_id": tr.station_id, "onset_s": round(onset),
            "affected_count": len(tr.affected_vins),
            "still_on_line": still_on_line,
            "sample_vins": tr.affected_vins[:12],
        }

    return {
        "scenario": {"name": res.scenario.name, "description": res.scenario.description},
        "line": {"name": res.line.name, "takt_s": res.line.takt_s,
                 "n_stations": len(res.line.stations),
                 "instrumented": sum(s.instrumented for s in res.line.stations)},
        "stations": stations,
        "bottleneck": {"station_id": bottleneck, "confidence": round(conf, 2),
                       "name": res.line.stations[bottleneck].name,
                       "instrumented": res.line.stations[bottleneck].instrumented},
        "forecast": {"constraint_station_id": fc.constraint_station_id,
                     "p_binding": fc.p_binding,
                     "eta_min": {"mean": round(fc.eta_s.mean / 60), "lo": round(fc.eta_s.lo / 60),
                                 "hi": round(fc.eta_s.hi / 60)},
                     "units_lost": {"mean": fc.units_lost.mean, "lo": fc.units_lost.lo,
                                    "hi": fc.units_lost.hi}},
        "recommendation": (None if rec is None else {
            "driver": rec.driver, "action": rec.action, "confidence": rec.confidence,
            "recovered": {"mean": rec.expected_units_recovered.mean,
                          "lo": rec.expected_units_recovered.lo,
                          "hi": rec.expected_units_recovered.hi}}),
        "defect": defect,
        "throughput": res.throughput,
    }


@lru_cache(maxsize=8)
def live_state(scenario_name: str, n_frames: int = 80) -> dict:
    """Recursive live-state posterior over the shift (issue #29).

    Precomputed and cached so the API/dashboard never runs a stateful filter inside a
    request/socket loop. Returns per-segment posterior frames (aligned to ``live_frames``)
    plus the segment→station map the floor view needs to name the live constraint.
    """
    res = GroundTruthSim(scenario=load_scenario(scenario_name)).run()
    obs = extract_observation(res)
    frames = run_live(obs, res.duration_s, n_frames=n_frames)
    segs = list(zip(res.line.checkpoints(), res.line.checkpoints()[1:]))
    seg_labels = {f"{a}-{b}": [res.line.stations[j].name for j in range(a, b)]
                  for a, b in segs}
    dark = set(res.line.dark_stations())
    seg_dark = {f"{a}-{b}": [res.line.stations[j].name for j in range(a, b) if j in dark]
                for a, b in segs}
    return {
        "scenario": {"name": res.scenario.name, "description": res.scenario.description},
        "segments": [{"a": a, "b": b, "label": f"S{a}–S{b}"} for a, b in segs],
        "segment_stations": seg_labels,
        "segment_dark": seg_dark,
        "frames": frames,
    }


@lru_cache(maxsize=4)
def analyze_variants(scenario_name: str = "baseline") -> dict:
    """Mixed-model variant analysis (issue #28): recover per-variant service times on a line
    where different variants carry different work content, and localize each variant-specific
    operation to its (dark) station — all from travel-time tomography, no sensor required."""
    line = build_variant_line()
    res = GroundTruthSim(line=line, scenario=load_scenario(scenario_name)).run()
    est = estimate_service_times_variant(extract_observation(res))
    variants = list(line.variants)
    dark = set(line.dark_stations())

    stations = []
    for s in line.stations:
        e = est[s.id]
        stations.append({
            "id": s.id, "name": s.name, "instrumented": s.instrumented,
            "dark": s.id in dark,
            "per_variant": {v: {"mean": e.per_variant[v].mean,
                                "lo": e.per_variant[v].lo, "hi": e.per_variant[v].hi}
                            for v in variants},
            "pooled": {"mean": e.pooled.mean, "lo": e.pooled.lo, "hi": e.pooled.hi},
        })

    # the "what did we find" story: each variant-specific operation, localized
    findings = []
    for v, ops in line.variant_ops.items():
        for sid in ops:
            here = est[sid].per_variant
            base = min(here[o].mean for o in variants if o != v)
            findings.append({
                "variant": v, "station_id": sid, "station": line.stations[sid].name,
                "extra_s": round(here[v].mean - base, 1),
                "estimate_s": here[v].mean, "dark": sid in dark,
            })

    # honest accuracy scoring vs ground truth (dark stations only)
    errs = [abs(est[j].per_variant[v].mean - res.true_mean_cycle_variant[j][v])
            / res.true_mean_cycle_variant[j][v]
            for j in dark for v in variants if v in res.true_mean_cycle_variant.get(j, {})]

    return {
        "scenario": {"name": res.scenario.name, "description": res.scenario.description},
        "variants": variants,
        "variant_ops": {v: {str(k): val for k, val in ops.items()}
                        for v, ops in line.variant_ops.items()},
        "stations": stations,
        "findings": findings,
        "dark_per_variant_mape": round(100 * float(np.mean(errs)), 1) if errs else None,
    }


def live_frames(scenario_name: str, n_frames: int = 80) -> list[dict]:
    """Reconstruct animated vehicle positions over the shift from scan timestamps.

    Between two checkpoints a vehicle's station index is linearly interpolated by time;
    this drives the dashboard's live line-map animation. Precomputed and cached.
    """
    res = GroundTruthSim(scenario=load_scenario(scenario_name)).run()
    n = len(res.line.stations)
    cps = res.line.checkpoints()
    dur = res.scenario.duration_s
    takt = res.line.takt_s

    scans = {v.vin: dict(sorted(v.scans.items())) for v in res.vehicles if v.scans}
    exits = {v.vin: v.exit_s for v in res.vehicles}
    frames = []
    for f in range(n_frames):
        t = dur * f / (n_frames - 1)
        positions = []
        for vin, sc in scans.items():
            ex = exits.get(vin)
            if ex is not None and t > ex:
                continue                       # already left the line
            items = list(sc.items())
            first_cp, first_t = items[0]
            if t < first_t:
                continue                       # not yet entered
            pos = None
            for (c0, t0), (c1, t1) in zip(items, items[1:]):
                if t0 <= t <= t1 and t1 > t0:
                    pos = c0 + (c1 - c0) * (t - t0) / (t1 - t0)
                    break
            if pos is None:                     # past last scan: extrapolate by takt
                last_cp, last_t = items[-1]
                pos = min(n - 1, last_cp + (t - last_t) / takt)
            positions.append(round(pos, 2))
        thru = sum(1 for ex in exits.values() if ex is not None and ex <= t)
        frames.append({"t_s": round(t), "t_min": round(t / 60),
                       "positions": positions, "throughput": thru})
    return frames
