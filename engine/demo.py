"""Terminal demo of the ground-truth line simulator (M0 checkpoint).

Run a scenario and print what "reality" looks like: per-station cycle time and
working/blocked/starved mix, throughput, and the ground-truth bottleneck. This is the
foundation the digital twin will later have to reconstruct from only the *observable*
subset.

    python -m engine.demo                 # baseline
    python -m engine.demo takt_slip_s14   # dark Station 14 slips over takt
    python -m engine.demo torque_drift_s8
    python -m engine.demo surge_3x
"""

from __future__ import annotations

import sys

from .ground_truth_sim import GroundTruthSim
from .scenarios import available, load_scenario


def main(argv: list[str]) -> int:
    name = argv[1] if len(argv) > 1 else "baseline"
    try:
        scenario = load_scenario(name)
    except FileNotFoundError as e:
        print(e)
        print("available scenarios:", ", ".join(available()))
        return 1

    print(f"\n=== Blindsight ground-truth sim · scenario '{scenario.name}' ===")
    print(scenario.description)
    sim = GroundTruthSim(scenario=scenario)
    result = sim.run()

    rows = result.summary_rows()
    print(f"\n{'st':>3} {'name':<5} {'zone':<5} {'sensor':<6} "
          f"{'cyc_s':>6} {'work%':>6} {'block%':>7} {'starv%':>7}")
    print("-" * 54)
    for r in rows:
        sensor = "yes" if r["instrumented"] else "DARK"
        print(f"{r['id']:>3} {r['name']:<5} {r['zone']:<5} {sensor:<6} "
              f"{r['true_cycle_s']:>6} {r['pct_working']:>5}% "
              f"{r['pct_blocked']:>6}% {r['pct_starved']:>6}%")

    bn = result.ground_truth_bottleneck()
    bs = result.line.stations[bn]
    dark = " (DARK — no sensor!)" if not bs.instrumented else ""
    defects = sum(1 for v in result.vehicles if v.defects)
    print("-" * 54)
    print(f"duration        : {int(result.duration_s)} s "
          f"({result.duration_s/3600:.1f} h)")
    print(f"throughput      : {result.throughput} units")
    print(f"vehicles seen   : {len(result.vehicles)}  |  scan records: {len(result.scans)}")
    print(f"GROUND-TRUTH bottleneck : Station {bn} ({bs.name}){dark}")
    if defects:
        print(f"defective units : {defects} (carry a fault from a drifted station)")
    print("\nNote: the twin does NOT get this table for dark stations — "
          "it must reconstruct it. That's the next checkpoint.\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
