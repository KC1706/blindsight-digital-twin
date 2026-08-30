"""Make the repo root importable under a bare ``pytest`` invocation.

CI runs ``pytest -q`` (not ``python -m pytest``), which does not put the working directory
on ``sys.path`` — so ``import engine`` failed to collect. Prepending the repo root here fixes
collection for every test module regardless of how pytest is launched.
"""

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
