"""Defect propagation trace (issue #14).

When an SPC signal fires at a station over an onset window [t0, t1], enumerate the exact
vehicles (VINs) that were at that station during the window using scan timestamps, and
estimate where each one is on the line right now — a containment list produced before the
fault reaches end-of-line audit.

Works directly when the station is a scan checkpoint (e.g. S8). For a non-checkpoint station
we fall back to the nearest downstream checkpoint and shift by the nominal transit time.
"""

from __future__ import annotations

from .observe import Observation
from .schemas import DefectTrace


def _current_station(cps: dict[int, float], now: float, n: int, takt: float) -> int:
    """Estimate a vehicle's current station from its scan history and elapsed time."""
    last_cp = max(cps)
    advanced = int((now - cps[last_cp]) / max(takt, 1.0))
    pos = last_cp + advanced
    return min(pos, n)          # n == "exited the line"


def trace_defects(obs: Observation, station_id: int, onset_s: float, end_s: float,
                  now_s: float | None = None) -> DefectTrace:
    line = obs.line
    n = len(line.stations)
    takt = line.takt_s
    checkpoints = line.checkpoints()
    now = now_s if now_s is not None else max((t for _, _, t in obs.scans), default=end_s)

    # pick the scan point to read the window from
    if station_id in checkpoints:
        scan_cp = station_id
        shift = 0.0
    else:
        downstream = [c for c in checkpoints if c >= station_id]
        scan_cp = downstream[0] if downstream else max(checkpoints)
        shift = (scan_cp - station_id) * takt      # nominal transit to that checkpoint

    affected: list[int] = []
    positions: dict[int, int] = {}
    for vin, cps in obs.vehicle_scans.items():
        if scan_cp not in cps:
            continue
        t_at_station = cps[scan_cp] - shift
        if onset_s <= t_at_station <= end_s:
            affected.append(vin)
            positions[vin] = _current_station(cps, now, n, takt)

    affected.sort()
    return DefectTrace(station_id=station_id, onset_s=onset_s, end_s=end_s,
                       affected_vins=affected, current_positions=positions)
