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
from .schemas import Band


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
