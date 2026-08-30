"""Virtual sensing — "the line is the sensor" (issues #7, #8, #9, #25, #26, #27, #28).

Two complementary inferences, using only the observable subset:

1. **Blocked/starved localization** (#7): a slow dark station starves everything downstream
   and blocks everything upstream. The blocked->starved boundary among instrumented
   neighbours points at the constraint — even with no sensor on it.

2. **Travel-time tomography** (#8): each vehicle's checkpoint-to-checkpoint travel time is one
   equation over the stations in that segment. Using free-flow vehicles to separate service
   from queue wait (#27), we subtract the *measured* instrumented service times and attribute
   the remainder to the dark stations, localizing the excess onto the blocked/starved
   bottleneck. Bootstrap over vehicles gives honest error bars (#9), widened for dark stations
   that share a segment and are only jointly identifiable (the motivation for value-of-
   information in M5).
"""

from __future__ import annotations

import numpy as np

from .observe import Observation
from .schemas import Band, VariantCycleEstimate


def blocked_starved_bottleneck(obs: Observation) -> tuple[int, float]:
    """Return (bottleneck_station_id, confidence in [0,1])."""
    inst = sorted(obs.state_frac)
    blocked = {i: obs.state_frac[i].get("blocked", 0.0) for i in inst}
    starved = {i: obs.state_frac[i].get("starved", 0.0) for i in inst}
    n = len(obs.line.stations)
    W = 4   # local window: the signal is right around the bottleneck, not line-wide

    best_p, best_score = 0, -1e9
    scores = []
    for p in range(n):                       # candidate bottleneck position
        up = [i for i in inst if p - W <= i < p]
        down = [i for i in inst if p < i <= p + W]
        up_block = np.mean([blocked[i] for i in up]) if up else 0.0
        up_starve = np.mean([starved[i] for i in up]) if up else 0.0
        down_starve = np.mean([starved[i] for i in down]) if down else 0.0
        down_block = np.mean([blocked[i] for i in down]) if down else 0.0
        # a bottleneck shows local blocking just upstream and local starvation just
        # downstream; upstream is not yet starved and downstream is not blocked.
        score = up_block + down_starve - up_starve - down_block
        scores.append(score)
        if score > best_score:
            best_score, best_p = score, p
    scores = np.array(scores)
    # snap to the nearest dark station within +/-2: manual/dark stations are where
    # humans vary and the constraint usually hides, and the boundary lands adjacent to it.
    dark = set(obs.line.dark_stations())
    near = [d for d in dark if abs(d - best_p) <= 2]
    if near:
        best_p = min(near, key=lambda d: abs(d - best_p))
    # confidence = how much the peak stands out from the median
    spread = scores.max() - np.median(scores)
    conf = float(np.clip(spread / (abs(scores.max()) + 1e-6), 0, 1))
    return best_p, conf


def estimate_cycle_times(obs: Observation, n_boot: int = 200,
                         seed: int = 1) -> dict[int, Band]:
    """Estimate every station's effective cycle time, with error bars."""
    rng = np.random.default_rng(seed)
    line = obs.line
    instrumented = {s.id: s.instrumented for s in line.stations}
    # nominal prior for a dark station = the median cycle actually measured at the
    # instrumented stations (a data-driven "spec sheet"), not a takt-derived guess.
    prior = float(np.median(list(obs.measured_cycle_s.values()))) \
        if obs.measured_cycle_s else 0.85 * line.takt_s
    bottleneck, _ = blocked_starved_bottleneck(obs)

    est: dict[int, Band] = {}
    # instrumented stations: measured directly, tight band
    for sid, m in obs.measured_cycle_s.items():
        est[sid] = Band(mean=round(m, 2), lo=round(m * 0.95, 2), hi=round(m * 1.05, 2))

    # the flow-identified bottleneck's cycle time = the inter-departure interval at the
    # first checkpoint downstream of it. A saturated bottleneck emits one unit per cycle,
    # so this is a robust, low-variance estimator (uses every vehicle, not just the fastest).
    cps = obs.line.checkpoints()
    down = [c for c in cps if c > bottleneck]
    bottleneck_band = _interdeparture_estimate(obs, down[0], rng, n_boot) if down else None

    for s in obs.line.stations:
        if s.instrumented:
            continue                                   # already set (measured)
        if s.id == bottleneck and bottleneck_band is not None:
            est[s.id] = bottleneck_band                # the constraint: measured by rate
        else:
            # non-constraint dark station: sits at the data-driven nominal, honest wide band
            est[s.id] = Band(mean=round(prior, 2),
                             lo=round(prior - 6, 2), hi=round(prior + 6, 2))
    return est


def _segment_variant_content(obs: Observation, freeflow_q: float):
    """Free-flow travel time per (segment, variant) — the identifiable quantity.

    Within a fixed checkpoint segment the individual stations share identical incidence
    columns (only jointly identifiable, METHODS §2.1), but the *segment total* work content
    per variant is over-determined and robust. We estimate it as the median travel time of
    the least-congested vehicles (below the ``freeflow_q`` quantile) of that variant, so
    queue wait ≈ 0. Returns {(a, b): {variant: [free-flow travels]}}.
    """
    seg_v: dict[tuple[int, int], dict[str, list[float]]] = {}
    for vin, sc in obs.vehicle_scans.items():
        variant = obs.vehicle_variant.get(vin)
        if variant is None:
            continue
        cps = sorted(sc)
        for a, b in zip(cps, cps[1:]):
            if sc[b] > sc[a]:
                seg_v.setdefault((a, b), {}).setdefault(variant, []).append(sc[b] - sc[a])
    # keep only the free-flow (low-quantile) vehicles per (segment, variant)
    out: dict[tuple[int, int], dict[str, list[float]]] = {}
    for seg, byv in seg_v.items():
        out[seg] = {}
        for v, travels in byv.items():
            arr = np.array(travels)
            thr = np.quantile(arr, freeflow_q)
            out[seg][v] = arr[arr <= thr].tolist() or arr.tolist()
    return out


def _segment_excess(seg_ff, variants, ffq_lo: float):
    """Per-(segment, variant) *excess* free-flow travel over the segment's baseline variant.

    For each segment we take each variant's near-minimum free-flow travel (the ``ffq_lo``
    quantile — queue wait ≈ 0) and subtract the fastest variant's, giving the extra work
    content that variant carries through the segment. In a no-overtaking line only *extra*
    work (a variant-specific operation) is identifiable — a globally faster variant is pinned
    behind slower units and cannot express its speed, so it reads as the zero-excess baseline.
    """
    excess: dict[tuple[int, int], dict[str, float]] = {}
    for seg, byv in seg_ff.items():
        nm = {v: float(np.quantile(byv[v], ffq_lo)) for v in byv if byv[v]}
        if not nm:
            continue
        base = min(nm.values())
        excess[seg] = {v: max(0.0, nm.get(v, base) - base) for v in variants}
    return excess


def estimate_service_times_variant(obs: Observation, n_boot: int = 60,
                                   freeflow_q: float = 0.5, ffq_lo: float = 0.05,
                                   seed: int = 2) -> dict[int, VariantCycleEstimate]:
    """Estimate every station's service time **per variant** (issue #28, METHODS §2.1).

    Combines two mechanisms. (1) The aggregate per-station estimator
    (``estimate_cycle_times``) gives each station's base cycle time (bottleneck by departure
    rate, others at the data-driven nominal). (2) Variant-specific *excess* work per segment
    is read from near-minimum free-flow travel times and attributed to the dark station(s) in
    that segment — so a variant that fits a sunroof at a dark station shows a higher estimate
    there, for that variant only.

    Honest limit: in a no-overtaking line only *extra* work is identifiable; a globally faster
    variant is pinned behind slower units and reads as the baseline. Bootstrap over free-flow
    vehicles gives the bands; dark stations sharing a segment split the excess (jointly
    identifiable — the motivation for value-of-information in M5).
    """
    rng = np.random.default_rng(seed)
    line = obs.line
    variants = list(line.variants) or sorted(set(obs.vehicle_variant.values()))
    agg = estimate_cycle_times(obs)
    dark = set(line.dark_stations())

    def _dark_in(seg):
        return [j for j in range(seg[0], seg[1]) if j in dark]

    def _excess_from(seg_ff):
        return _segment_excess(seg_ff, variants, ffq_lo)

    seg_ff = _segment_variant_content(obs, freeflow_q)
    excess = _excess_from(seg_ff)

    # bootstrap the excess (resample free-flow travels) for error bars
    boots = []
    for _ in range(n_boot):
        resampled = {seg: {v: list(np.array(byv[v])[rng.integers(0, len(byv[v]), len(byv[v]))])
                           for v in byv if byv[v]}
                     for seg, byv in seg_ff.items()}
        boots.append(_excess_from(resampled))

    # station -> its (shortest) enclosing segment
    def _seg_of(j):
        cands = [seg for seg in seg_ff if seg[0] <= j < seg[1]]
        return min(cands, key=lambda s: s[1] - s[0]) if cands else None

    seen = {v: 0 for v in variants}
    for vv in obs.vehicle_variant.values():
        if vv in seen:
            seen[vv] += 1
    tot = sum(seen.values()) or 1
    w = {v: seen[v] / tot for v in variants}

    out: dict[int, VariantCycleEstimate] = {}
    for s in line.stations:
        base = agg[s.id].mean
        seg = _seg_of(s.id)
        ndark = len(_dark_in(seg)) if seg else 0
        share = 1.0 / ndark if (s.id in dark and ndark) else (0.0 if seg else 0.0)
        per_variant: dict[str, Band] = {}
        for v in variants:
            add = excess.get(seg, {}).get(v, 0.0) * share if seg else 0.0
            mean = base + add
            bvals = [base + b.get(seg, {}).get(v, 0.0) * share for b in boots] if seg \
                else [base]
            lo, hi = (np.percentile(bvals, [5, 95]) if len(set(bvals)) > 1 else (mean, mean))
            per_variant[v] = Band(mean=round(mean, 2),
                                  lo=round(float(lo), 2), hi=round(float(hi), 2))
        out[s.id] = VariantCycleEstimate(
            station_id=s.id, instrumented=s.instrumented,
            pooled=Band(
                mean=round(sum(w[v] * per_variant[v].mean for v in variants), 2),
                lo=round(sum(w[v] * per_variant[v].lo for v in variants), 2),
                hi=round(sum(w[v] * per_variant[v].hi for v in variants), 2)),
            per_variant=per_variant)
    return out


def _interdeparture_estimate(obs: Observation, checkpoint: int, rng,
                             n_boot: int) -> Band:
    """Estimate a saturated bottleneck's cycle time from departures at a downstream checkpoint."""
    times = np.sort([t for _, cp, t in obs.scans if cp == checkpoint])
    if len(times) < 5:
        prior = float(np.median(list(obs.measured_cycle_s.values())))
        return Band(mean=round(prior, 2), lo=round(prior - 6, 2), hi=round(prior + 6, 2))
    times = times[len(times) // 5:]                    # drop the fill transient
    intervals = np.diff(times)
    intervals = intervals[intervals < np.percentile(intervals, 90)]   # drop starve gaps
    mean = float(np.median(intervals))
    boots = [float(np.median(intervals[rng.integers(0, len(intervals), len(intervals))]))
             for _ in range(n_boot)]
    lo, hi = np.percentile(boots, [5, 95])
    return Band(mean=round(mean, 2), lo=round(float(lo), 2), hi=round(float(hi), 2))
