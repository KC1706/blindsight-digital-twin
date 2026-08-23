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
    prior = 0.9 * line.takt_s                        # spec-sheet nominal cycle
    bottleneck, _ = blocked_starved_bottleneck(obs)

    est: dict[int, Band] = {}
    # instrumented stations: measured directly, tight band
    for sid, m in obs.measured_cycle_s.items():
        est[sid] = Band(mean=round(m, 2), lo=round(m * 0.95, 2), hi=round(m * 1.05, 2))

    # dark stations: tomography per segment
    for a, b in obs.segments():
        seg = obs.stations_in_segment(a, b)
        dark = [j for j in seg if not instrumented[j]]
        if not dark:
            continue
        measured_in_seg = sum(obs.measured_cycle_s.get(j, prior)
                              for j in seg if instrumented[j])
        # segment travel times for vehicles scanned at both ends
        Ts = np.array([sc[b] - sc[a] for sc in obs.vehicle_scans.values()
                       if a in sc and b in sc and sc[b] > sc[a]], float)

        def attribute(ts: np.ndarray) -> dict[int, float]:
            if len(ts) < 3:
                return {j: prior for j in dark}
            # #27: the free-flow (near-minimum) traversal carries essentially no queue wait,
            # so it isolates service time. Use the mean of the 3 fastest vehicles (robust min).
            k = min(3, len(ts))
            free_flow = float(np.sort(ts)[:k].mean())
            residual = max(0.0, free_flow - measured_in_seg)   # sum of dark service
            excess = residual - prior * len(dark)              # beyond nominal
            out = {}
            bn_here = bottleneck in dark
            for j in dark:
                if bn_here and j == bottleneck:
                    out[j] = prior + max(0.0, excess)          # real service excess -> constraint
                else:
                    # not the flow-identified constraint: apparent excess is queue wait
                    # (this segment is up/downstream of the real bottleneck), not service.
                    out[j] = prior
            return out

        point = attribute(Ts)
        # bootstrap over vehicles for bands
        boots = {j: [] for j in dark}
        for _ in range(n_boot):
            if len(Ts) >= 3:
                sample = Ts[rng.integers(0, len(Ts), len(Ts))]
            else:
                sample = Ts
            a_ = attribute(sample)
            for j in dark:
                boots[j].append(a_[j])
        widen = np.sqrt(len(dark))                    # joint-identifiability widening
        for j in dark:
            arr = np.array(boots[j])
            mean = float(point[j])
            sd = float(arr.std()) * widen + 1.0
            est[j] = Band(mean=round(mean, 2),
                          lo=round(max(1.0, mean - 1.64 * sd), 2),
                          hi=round(mean + 1.64 * sd, 2))
    return est
