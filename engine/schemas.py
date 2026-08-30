"""Shared data contract for Blindsight (issue #37).

These pydantic models are the seam between the engine, the API, and the dashboard.
Config models (StationConfig/LineConfig/Scenario) are loaded from JSON; the analytics
models (snapshots, estimates, forecasts, recommendations) are what the API serves and the
three dashboard views render. Every estimate/forecast carries an explicit uncertainty band.
"""

from __future__ import annotations

from enum import Enum

from pydantic import BaseModel, Field


# ----------------------------- configuration -------------------------------- #

class StationKind(str, Enum):
    robot = "robot"      # richly instrumented
    manual = "manual"    # often dark (no sensor) — where humans vary


class StationState(str, Enum):
    working = "working"
    blocked = "blocked"   # finished a unit, nowhere to put it (downstream full)
    starved = "starved"   # free, nothing to work on (upstream empty)
    idle = "idle"


class StationConfig(BaseModel):
    id: int
    name: str
    zone: str                        # Body | Paint | GA
    kind: StationKind
    instrumented: bool               # False => "dark" station, no sensor
    mean_cycle_s: float              # true mean service time (ground truth only)
    cv: float = 0.15                 # coefficient of variation of service time
    in_buffer_cap: int = 2           # capacity of the queue feeding this station
    checkpoint: bool = False         # a scan point timestamps every vehicle here


class LineConfig(BaseModel):
    name: str = "mixed-model-line-40"
    takt_s: float = 55.0
    arrival_interval_s: float = 52.0  # source offers a new vehicle this often
    variants: list[str] = Field(default_factory=lambda: ["A", "B", "C"])
    # mixed-model work content (issue #28). ``variant_content`` is a per-variant multiplier
    # on every station; ``variant_ops`` adds variant-specific extra work at specific stations
    # (e.g. a sunroof fitted only on variant B at S19). Both empty => single-model line,
    # byte-identical to before.
    variant_content: dict[str, float] = Field(default_factory=dict)
    variant_ops: dict[str, dict[int, float]] = Field(default_factory=dict)
    stations: list[StationConfig]

    def variant_mult(self, variant: str) -> float:
        return float(self.variant_content.get(variant, 1.0))

    def variant_extra_s(self, variant: str, station_id: int) -> float:
        return float(self.variant_ops.get(variant, {}).get(station_id, 0.0))

    def checkpoints(self) -> list[int]:
        return [s.id for s in self.stations if s.checkpoint]

    def dark_stations(self) -> list[int]:
        return [s.id for s in self.stations if not s.instrumented]


class ScenarioEvent(BaseModel):
    at_s: float                       # when the event fires (sim seconds)
    type: str                         # cycle_shift | drift | surge
    station_id: int | None = None
    params: dict[str, float] = Field(default_factory=dict)
    note: str = ""


class Scenario(BaseModel):
    name: str
    description: str = ""
    duration_s: float = 7200.0
    seed: int = 7
    events: list[ScenarioEvent] = Field(default_factory=list)


# ------------------------------- runtime data ------------------------------- #

class ScanRecord(BaseModel):
    vin: int
    variant: str
    checkpoint_id: int
    t_s: float


class StationSnapshot(BaseModel):
    id: int
    state: StationState
    instrumented: bool
    queue_len: int
    processed: int


class LineSnapshot(BaseModel):
    t_s: float
    stations: list[StationSnapshot]
    wip: int
    throughput: int


# --------------------------- analytics (later Ms) --------------------------- #

class Band(BaseModel):
    """A point estimate with an uncertainty interval — never a bare number."""
    mean: float
    lo: float          # e.g. P10 / lower credible bound
    hi: float          # e.g. P90 / upper credible bound


class CycleTimeEstimate(BaseModel):
    station_id: int
    instrumented: bool
    estimate: Band     # estimated effective cycle time (s), with error bars


class VariantCycleEstimate(BaseModel):
    """Per-variant service-time estimate for one station (issue #28, mixed-model).

    ``pooled`` is the variant-mix-weighted station cycle time (what the rest of the
    pipeline consumes); ``per_variant`` is the identifiable-per-variant detail.
    """
    station_id: int
    instrumented: bool
    pooled: Band
    per_variant: dict[str, Band]


class ForecastResult(BaseModel):
    horizon_s: float
    constraint_station_id: int
    p_binding: float                 # P(this station is the binding constraint)
    eta_s: Band                      # time until it becomes the constraint
    units_lost: Band


class Recommendation(BaseModel):
    driver: str
    lever: str
    action: str
    expected_units_recovered: Band
    confidence: float
    owner: str = "floor supervisor"


class DefectTrace(BaseModel):
    station_id: int
    onset_s: float
    end_s: float
    affected_vins: list[int]
    current_positions: dict[int, int]   # vin -> station id right now


class ValidationReport(BaseModel):
    cycle_time_mape_instrumented: float
    cycle_time_mape_dark: float
    forecast_crps: float
    false_alarm_rate: float
    median_lead_time_s: float
