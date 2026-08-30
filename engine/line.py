"""Line topology & station configuration (issue #2).

Builds the default ~40-station mixed-model assembly line: Body -> Paint -> General
Assembly, with buffers, uneven sensor coverage (~65% instrumented), and scan checkpoints
at zone boundaries. Stations 8 and 14 are deliberately *manual/dark* so the demo scenarios
(torque drift at S8, takt slip at S14) exercise the "estimate a station with no sensor" case.
"""

from __future__ import annotations

from .schemas import LineConfig, StationConfig, StationKind

# zone -> (count, base mean cycle seconds)
_ZONES = [
    ("Body", 16, 50.0),
    ("Paint", 10, 48.0),
    ("GA", 14, 52.0),
]

# station ids that are manual & dark (no sensor). Includes the two demo targets 8 & 14.
_DARK = {3, 8, 11, 14, 19, 24, 27, 31, 33, 37}

# a few naturally slower stations so a bottleneck exists even at baseline
_SLOW = {8: 53.0, 14: 54.0, 27: 53.0}

# scan checkpoints at zone boundaries + a couple mid-zone anchors
_CHECKPOINTS = {0, 8, 16, 21, 26, 33, 39}


def build_default_line() -> LineConfig:
    stations: list[StationConfig] = []
    sid = 0
    for zone, count, base in _ZONES:
        for _ in range(count):
            manual = sid in _DARK
            mean = _SLOW.get(sid, base)
            stations.append(
                StationConfig(
                    id=sid,
                    name=f"{zone[:1]}{sid:02d}",
                    zone=zone,
                    kind=StationKind.manual if manual else StationKind.robot,
                    instrumented=not manual,
                    mean_cycle_s=mean,
                    cv=0.20 if manual else 0.10,        # humans vary more than robots
                    in_buffer_cap=3 if sid in _CHECKPOINTS else 2,
                    checkpoint=sid in _CHECKPOINTS,
                )
            )
            sid += 1
    # feed faster than the slowest station so the line saturates and a real
    # bottleneck forms (blocking upstream, starvation downstream) — the signal
    # virtual sensing depends on.
    return LineConfig(stations=stations, takt_s=60.0, arrival_interval_s=40.0)


# variant-specific extra operations (issue #28): each optioned variant adds work at ONE dark
# station sitting alone in an interior checkpoint segment, so the extra work content is cleanly
# localizable from travel-time tomography.
#   A: base trim  (no extra work — the reference variant)
#   B: sunroof fit at dark S19  (interior segment 16->21)
#   C: trim option at dark S24  (interior segment 21->26)
_VARIANT_OPS = {"A": {}, "B": {19: 18.0}, "C": {24: 12.0}}


def build_variant_line(variant_ops: dict[str, dict[int, float]] | None = None,
                       variant_content: dict[str, float] | None = None) -> LineConfig:
    """The default line as a genuine mixed-model line (issue #28).

    Variants carry different work content: ``variant_ops`` adds variant-specific operations
    at specific stations (the realistic mixed-model case — a sunroof only on one trim), and
    optional ``variant_content`` scales every station per variant. This is the structure the
    variant-aware tomography must recover. Defaults to 3 variants; pass a dict to demo 2 or 4.
    """
    if variant_ops is None:
        variant_ops = _VARIANT_OPS
    line = build_default_line()
    line.variants = list(variant_ops)
    line.variant_ops = {v: dict(ops) for v, ops in variant_ops.items()}
    line.variant_content = dict(variant_content or {})
    # ease loading a little so free-flow vehicles exist and work content is observable
    line.arrival_interval_s = 52.0
    return line


if __name__ == "__main__":  # quick manual check
    line = build_default_line()
    print(f"{line.name}: {len(line.stations)} stations, takt {line.takt_s}s")
    print(f"instrumented: {sum(s.instrumented for s in line.stations)}/{len(line.stations)}")
    print(f"dark stations: {line.dark_stations()}")
    print(f"checkpoints:   {line.checkpoints()}")
