"""Prescription — simulation-optimization over levers (issues #13, #34).

Given the current estimates and forecast, evaluate feasible levers (move one operator to the
constraint from a station with spare capacity) by re-forecasting the counterfactual with
common random numbers, and rank by expected units recovered. Uses a lightweight
ranking-and-selection pass (OCBA-style): each candidate is scored across K paired seeds so we
can report a confidence that it truly beats "do nothing", not just a point estimate.
"""

from __future__ import annotations

import copy

import numpy as np

from .forecast import forecast
from .schemas import Band, LineConfig, Recommendation

# operator move: the constraint speeds up (extra hands), the donor slows down.
_HELP_FACTOR = 0.75      # constraint cycle time x this when an operator is added
_DONOR_FACTOR = 1.28     # donor cycle time x this when it loses an operator


def _shift(band: Band, factor: float) -> Band:
    return Band(mean=band.mean * factor, lo=band.lo * factor, hi=band.hi * factor)


def _units_lost(estimates, line, horizon, seed) -> float:
    return forecast(estimates, line, horizon_s=horizon, M=300, seed=seed).units_lost.mean


def recommend(estimates: dict[int, Band], line: LineConfig, horizon_s: float = 7200.0,
              k_seeds: int = 12) -> Recommendation | None:
    ids = [s.id for s in line.stations]
    instrumented = {s.id: s.instrumented for s in line.stations}
    bottleneck = max(ids, key=lambda i: estimates[i].mean)

    # candidate donors: instrumented stations near the constraint with spare capacity
    donors = [i for i in ids
              if i != bottleneck and instrumented[i]
              and abs(i - bottleneck) <= 8
              and estimates[i].mean < 0.9 * line.takt_s]
    if not donors:
        return None

    seeds = list(range(1, k_seeds + 1))
    base = {s: _units_lost(estimates, line, horizon_s, s) for s in seeds}

    best = None
    for d in donors:
        mod = copy.deepcopy(estimates)
        mod[bottleneck] = _shift(mod[bottleneck], _HELP_FACTOR)
        mod[d] = _shift(mod[d], _DONOR_FACTOR)
        recovered = np.array([base[s] - _units_lost(mod, line, horizon_s, s)
                              for s in seeds])
        mean_rec = float(recovered.mean())
        p_win = float((recovered > 0).mean())               # OCBA-style confidence
        cand = (mean_rec, p_win, d, recovered)
        if best is None or mean_rec > best[0]:
            best = cand

    mean_rec, p_win, donor, rec = best
    if mean_rec <= 0:
        return None
    return Recommendation(
        driver=f"Station {bottleneck} is the binding constraint",
        lever="labor reallocation",
        action=f"Move one operator from Station {donor} to Station {bottleneck}",
        expected_units_recovered=Band(
            mean=round(mean_rec, 1),
            lo=round(float(np.percentile(rec, 10)), 1),
            hi=round(float(np.percentile(rec, 90)), 1)),
        confidence=round(p_win, 2),
    )
