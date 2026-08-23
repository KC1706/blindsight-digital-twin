"""SPC change-point detection + causal attribution (issues #32, #33).

- ``cusum_change_point`` runs a two-sided CUSUM over a signal (e.g. windowed segment
  travel time or an estimated cycle-time series) and returns the onset index of a
  sustained shift — catching slow drift a Shewhart chart would miss.
- ``attribute`` classifies a detected degradation across candidate drivers (abrupt
  tooling/method change vs gradual wear vs variant-correlated upstream quality), returning
  ranked contributions with confidence. Interpretable, not an LLM guess.
"""

from __future__ import annotations

import numpy as np


def ewma(values, alpha: float = 0.3):
    values = np.asarray(values, float)
    out = np.empty_like(values)
    acc = values[0] if len(values) else 0.0
    for i, v in enumerate(values):
        acc = alpha * v + (1 - alpha) * acc
        out[i] = acc
    return out


def cusum_change_point(values, k_sigma: float = 0.5, h_sigma: float = 4.0):
    """Return (onset_index or None, upper_cusum). Detects an upward sustained shift."""
    x = np.asarray(values, float)
    if len(x) < 4:
        return None, np.zeros(len(x))
    baseline = np.median(x[: max(2, len(x) // 4)])
    sigma = np.std(x[: max(2, len(x) // 4)]) or (0.05 * abs(baseline) + 1e-6)
    k = k_sigma * sigma
    h = h_sigma * sigma
    s = 0.0
    cusum = np.zeros(len(x))
    onset = None
    for i, v in enumerate(x):
        s = max(0.0, s + (v - baseline) - k)
        cusum[i] = s
        if onset is None and s > h:
            # walk back to where the accumulation started
            j = i
            while j > 0 and cusum[j - 1] > 0:
                j -= 1
            onset = j
    return onset, cusum


def attribute(series, times, variant_series=None) -> list[dict]:
    """Rank likely drivers of a degradation. Each: {driver, contribution, confidence}."""
    x = np.asarray(series, float)
    onset, _ = cusum_change_point(x)
    drivers: list[dict] = []
    if onset is None or onset >= len(x) - 1:
        return [{"driver": "no significant degradation", "contribution": 0.0,
                 "confidence": 0.5}]

    before, after = x[:onset], x[onset:]
    step = float(after.mean() - before.mean())
    # abruptness: is it a step (tooling/method) or a ramp (wear)?
    ramp = float(np.polyfit(np.arange(len(after)), after, 1)[0]) if len(after) > 2 else 0.0
    step_score = abs(step)
    ramp_score = abs(ramp) * len(after)

    if step_score >= ramp_score:
        drivers.append({"driver": "tooling / method change (abrupt step)",
                        "contribution": round(step, 2),
                        "confidence": round(step_score / (step_score + ramp_score + 1e-6), 2)})
    else:
        drivers.append({"driver": "equipment wear (gradual ramp)",
                        "contribution": round(ramp * len(after), 2),
                        "confidence": round(ramp_score / (step_score + ramp_score + 1e-6), 2)})

    # variant correlation => upstream part-quality signal
    if variant_series is not None and len(variant_series) == len(x):
        v = np.asarray([hash(s) % 3 for s in variant_series], float)
        if np.std(v) > 0:
            corr = float(np.corrcoef(v[onset:], after)[0, 1]) if len(after) > 2 else 0.0
            if abs(corr) > 0.4:
                drivers.append({"driver": "upstream part quality (variant-correlated)",
                                "contribution": round(corr, 2),
                                "confidence": round(min(1.0, abs(corr)), 2)})
    return sorted(drivers, key=lambda d: -abs(d["contribution"]))
