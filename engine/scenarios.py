"""Scenario loading (issue #3).

Scenarios are JSON files in ``scenarios/`` validated against the ``Scenario`` schema.
Each names a duration, a seed, and a list of timed events (cycle_shift / drift / surge)
applied to the default line at run time.
"""

from __future__ import annotations

import json
from pathlib import Path

from .schemas import Scenario

SCENARIO_DIR = Path(__file__).resolve().parent.parent / "scenarios"


def load_scenario(name: str) -> Scenario:
    path = SCENARIO_DIR / f"{name}.json"
    if not path.exists():
        raise FileNotFoundError(f"no scenario '{name}' in {SCENARIO_DIR} "
                                f"(have: {', '.join(available())})")
    return Scenario.model_validate_json(path.read_text())


def available() -> list[str]:
    return sorted(p.stem for p in SCENARIO_DIR.glob("*.json"))
