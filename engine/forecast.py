"""Probabilistic forecast (issues #11, #12, #30, #31).

Spike #31 decision: a full tick-level DES per replication (40 stations x 7200 ticks x 500
runs) is too slow for an interactive forecast. A serial line's throughput is set by its
bottleneck, so we use a **bottleneck-rate metamodel** as the forward model and Monte-Carlo
over the *parameter posterior* from virtual sensing (#30). This runs 500 replications in
milliseconds and is validated against the DES in M5.

Each replication samples every station's cycle time from its estimate Band (so dark stations,
with wide bands, inject the most forecast uncertainty), finds the binding constraint, and
projects throughput over the horizon. Aggregation yields P(binding constraint), an ETA band,
and expected units lost — all with percentile bands, never bare numbers.
"""

from __future__ import annotations

import numpy as np

from .schemas import Band, ForecastResult, LineConfig


def _sample_means(estimates, rng) -> dict[int, float]:
    out = {}
    for sid, b in estimates.items():
        sd = max(0.5, (b.hi - b.lo) / (2 * 1.64))
        out[sid] = max(1.0, float(rng.normal(b.mean, sd)))
    return out


def _candidates(estimates, line, k: int = 5) -> list[int]:
    """Only the slowest few stations can realistically be the constraint. Restricting the
    argmax to these avoids the max-of-40-noisy-samples inflation that would fabricate loss."""
    ids = [s.id for s in line.stations]
    return sorted(ids, key=lambda i: -estimates[i].mean)[:k]


def forecast(estimates: dict[int, Band], line: LineConfig,
             horizon_s: float = 7200.0, M: int = 500, seed: int = 0) -> ForecastResult:
    rng = np.random.default_rng(seed)
    takt = line.takt_s
    cand = _candidates(estimates, line)

    binding = {i: 0 for i in cand}
    throughput = np.empty(M)
    bn_means = np.empty(M)
    for m in range(M):
        means = _sample_means(estimates, rng)
        j = max(cand, key=lambda i: means[i])     # the bottleneck sets the line rate
        binding[j] += 1
        bn_mean = float(means[j])
        bn_means[m] = bn_mean
        throughput[m] = horizon_s / bn_mean       # steady-state bottleneck-rate model

    p_binding = {i: c / M for i, c in binding.items()}
    constraint = max(p_binding, key=p_binding.get)
    ideal = horizon_s / takt
    units_lost = np.clip(ideal - throughput, 0, None)

    # ETA: time to lose the first unit once the constraint is slower than takt.
    bn_med = float(np.median(bn_means))
    def eta_of(bn):
        deficit = (1.0 / takt) - (1.0 / bn)       # units lost per second
        return horizon_s if deficit <= 0 else min(horizon_s, 1.0 / deficit)
    etas = np.array([eta_of(b) for b in bn_means])

    def band(a):
        return Band(mean=round(float(a.mean()), 1),
                    lo=round(float(np.percentile(a, 10)), 1),
                    hi=round(float(np.percentile(a, 90)), 1))

    return ForecastResult(
        horizon_s=horizon_s,
        constraint_station_id=int(constraint),
        p_binding=round(float(p_binding[constraint]), 3),
        eta_s=band(etas),
        units_lost=band(units_lost),
    )


def p_binding_by_station(estimates: dict[int, Band], line: LineConfig,
                         M: int = 500, seed: int = 0) -> dict[int, float]:
    """Full distribution over which station is the constraint (for the dashboard)."""
    rng = np.random.default_rng(seed)
    cand = _candidates(estimates, line)
    counts = {i: 0 for i in cand}
    for _ in range(M):
        means = _sample_means(estimates, rng)
        j = max(cand, key=lambda i: means[i])
        counts[j] += 1
    return {i: round(c / M, 3) for i, c in counts.items()}
