"""Ground-truth discrete-event simulator (issue #4).

Produces "reality": a mixed-model line running forward in discrete 1-second ticks, with
per-station service times, buffers, blocking/starvation, scan timestamps, and injected
faults. It emits the FULL event log and per-vehicle records.

IMPORTANT: this is the ground truth. The digital twin (later issues) must consume only the
*observable* subset produced by ``observe.py`` (instrumented station states + scan
timestamps) — never the fields marked ground-truth-only here.
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from .line import build_default_line
from .schemas import LineConfig, Scenario, StationState


@dataclass
class Vehicle:
    vin: int
    variant: str
    entry_s: float
    scans: dict[int, float] = field(default_factory=dict)   # checkpoint_id -> t
    defects: set[int] = field(default_factory=set)          # station ids that damaged it
    exit_s: float | None = None


@dataclass
class SimResult:
    line: LineConfig
    scenario: Scenario
    vehicles: list[Vehicle]
    scans: list[tuple[int, int, float]]          # (vin, checkpoint_id, t)
    state_log: dict[int, dict[str, int]]         # station_id -> ticks in each state
    true_mean_cycle: dict[int, float]            # ground-truth realized mean service time
    throughput: int
    duration_s: float

    def summary_rows(self):
        rows = []
        for s in self.line.stations:
            log = self.state_log[s.id]
            total = max(1, sum(log.values()))
            rows.append({
                "id": s.id, "name": s.name, "zone": s.zone,
                "instrumented": s.instrumented,
                "true_cycle_s": round(self.true_mean_cycle.get(s.id, 0.0), 1),
                "pct_working": round(100 * log["working"] / total),
                "pct_blocked": round(100 * log["blocked"] / total),
                "pct_starved": round(100 * log["starved"] / total),
            })
        return rows

    def ground_truth_bottleneck(self) -> int:
        # the capacity constraint = the slowest realized station (longest service time).
        # (Max-utilization would wrongly pick the arrival-fed first station.)
        return max(self.true_mean_cycle, key=self.true_mean_cycle.get)


class GroundTruthSim:
    def __init__(self, line: LineConfig | None = None, scenario: Scenario | None = None):
        self.line = line or build_default_line()
        self.scenario = scenario or Scenario(name="baseline")
        self.rng = np.random.default_rng(self.scenario.seed)
        n = len(self.line.stations)
        self.n = n
        # per-station live state
        self.mean = np.array([s.mean_cycle_s for s in self.line.stations], float)
        self.cv = np.array([s.cv for s in self.line.stations], float)
        self.cap = [s.in_buffer_cap for s in self.line.stations]
        self.queue: list[list[Vehicle]] = [[] for _ in range(n)]   # units waiting to enter i
        self.working: list[Vehicle | None] = [None] * n
        self.remaining = np.zeros(n, int)
        self.finished: list[Vehicle | None] = [None] * n           # done, awaiting handoff
        self.state_log = {i: {"working": 0, "blocked": 0, "starved": 0, "idle": 0}
                          for i in range(n)}
        self._cycles: list[list[float]] = [[] for _ in range(n)]
        self.checkpoints = set(self.line.checkpoints())
        # scenario deltas / flags applied over time
        self._drift_station: set[int] = set()
        self._defect_rate: dict[int, float] = {}
        self.arrival_interval = self.line.arrival_interval_s
        # bookkeeping
        self.vehicles: list[Vehicle] = []
        self.scans: list[tuple[int, int, float]] = []
        self.throughput = 0
        self._vin = 0
        self._next_arrival = 0.0
        self._applied: set[int] = set()

    # ---- service-time sampling (lognormal with given mean & cv) ---- #
    def _sample_cycle(self, i: int) -> int:
        m, cv = self.mean[i], self.cv[i]
        sigma = np.sqrt(np.log(1 + cv * cv))
        mu = np.log(max(m, 1e-6)) - 0.5 * sigma * sigma
        return max(1, int(round(float(np.exp(self.rng.normal(mu, sigma))))))

    def _apply_events(self, t: float):
        for idx, ev in enumerate(self.scenario.events):
            if idx in self._applied or t < ev.at_s:
                continue
            self._applied.add(idx)
            if ev.type == "cycle_shift" and ev.station_id is not None:
                self.mean[ev.station_id] += ev.params.get("delta_s", 0.0)
            elif ev.type == "drift" and ev.station_id is not None:
                self.mean[ev.station_id] += ev.params.get("delta_s", 0.0)
                self._drift_station.add(ev.station_id)
                self._defect_rate[ev.station_id] = ev.params.get("defect_rate", 1.0)
            elif ev.type == "surge":
                self.arrival_interval /= ev.params.get("factor", 1.0)

    def _classify(self, i: int) -> StationState:
        if self.working[i] is not None:
            return StationState.working
        if self.finished[i] is not None:
            return StationState.blocked
        if not self.queue[i]:
            return StationState.starved
        return StationState.idle

    def step(self, t: float):
        self._apply_events(t)
        # process stations downstream-first so space frees before upstream pushes
        for i in range(self.n - 1, -1, -1):
            # advance current work
            if self.working[i] is not None:
                self.remaining[i] -= 1
                if self.remaining[i] <= 0:
                    veh = self.working[i]
                    self.working[i] = None
                    if i in self._drift_station and \
                            self.rng.random() < self._defect_rate.get(i, 0.0):
                        veh.defects.add(i)
                    self.finished[i] = veh
            # hand off finished unit
            if self.finished[i] is not None:
                veh = self.finished[i]
                if i == self.n - 1:                      # exit the line
                    veh.exit_s = t
                    self.finished[i] = None
                    self.throughput += 1
                elif len(self.queue[i + 1]) < self.cap[i + 1]:
                    self.queue[i + 1].append(veh)
                    self.finished[i] = None
            # pull new work if free
            if self.working[i] is None and self.finished[i] is None and self.queue[i]:
                veh = self.queue[i].pop(0)
                if i in self.checkpoints:
                    veh.scans[i] = t
                    self.scans.append((veh.vin, i, t))
                self.remaining[i] = self._sample_cycle(i)
                self._cycles[i].append(self.remaining[i])
                self.working[i] = veh
            self.state_log[i][self._classify(i).value] += 1
        # arrivals into station 0's queue
        if t >= self._next_arrival and len(self.queue[0]) < self.cap[0]:
            variant = self.line.variants[self._vin % len(self.line.variants)]
            veh = Vehicle(vin=self._vin, variant=variant, entry_s=t)
            self.vehicles.append(veh)
            self.queue[0].append(veh)
            self._vin += 1
            self._next_arrival = t + self.arrival_interval

    def run(self) -> SimResult:
        for t in range(int(self.scenario.duration_s)):
            self.step(float(t))
        true_mean = {i: (float(np.mean(c)) if c else 0.0)
                     for i, c in enumerate(self._cycles)}
        return SimResult(
            line=self.line, scenario=self.scenario, vehicles=self.vehicles,
            scans=self.scans, state_log=self.state_log, true_mean_cycle=true_mean,
            throughput=self.throughput, duration_s=self.scenario.duration_s,
        )
