"""Observability mask (issue #5).

Turns ground-truth ``SimResult`` into the *observable* subset a real plant would have:

- **instrumented** stations expose their state mix (working/blocked/starved) and their own
  measured cycle time (they have sensors);
- **dark** stations expose nothing;
- **scan checkpoints** expose a timestamp per vehicle (VIN).

Everything else in ``SimResult`` (true cycle times of dark stations, injected defects) is
ground-truth-only and must never be read by the twin. This function is the enforced boundary.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from .ground_truth_sim import SimResult
from .schemas import LineConfig


@dataclass
class Observation:
    line: LineConfig                                   # topology is known (not "sensed")
    measured_cycle_s: dict[int, float]                 # instrumented stations only
    state_frac: dict[int, dict[str, float]]            # instrumented only: working/blocked/starved
    scans: list[tuple[int, int, float]]                # (vin, checkpoint_id, t)
    vehicle_scans: dict[int, dict[int, float]] = field(default_factory=dict)  # vin -> {cp: t}

    def segments(self) -> list[tuple[int, int]]:
        cps = self.line.checkpoints()
        return list(zip(cps, cps[1:]))

    def stations_in_segment(self, a: int, b: int) -> list[int]:
        # a vehicle scanned entering checkpoint a, then entering checkpoint b, passed
        # through stations [a, b) in between.
        return list(range(a, b))


def extract_observation(res: SimResult, sensor_noise: float = 0.03,
                        seed: int = 0) -> Observation:
    rng = np.random.default_rng(seed)
    line = res.line
    measured: dict[int, float] = {}
    state_frac: dict[int, dict[str, float]] = {}
    for s in line.stations:
        if not s.instrumented:
            continue
        # instrumented stations measure their own cycle time (with small sensor noise)
        true = res.true_mean_cycle.get(s.id, s.mean_cycle_s)
        measured[s.id] = float(true * (1 + rng.normal(0, sensor_noise)))
        log = res.state_log[s.id]
        total = max(1, sum(log.values()))
        state_frac[s.id] = {k: v / total for k, v in log.items()}

    vehicle_scans: dict[int, dict[int, float]] = {}
    for vin, cp, t in res.scans:
        vehicle_scans.setdefault(vin, {})[cp] = t

    return Observation(line=line, measured_cycle_s=measured, state_frac=state_frac,
                       scans=list(res.scans), vehicle_scans=vehicle_scans)
