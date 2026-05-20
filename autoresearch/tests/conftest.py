"""Make the evals/ directory importable for the autoresearch test suite."""

from __future__ import annotations

import sys
from pathlib import Path

EVALS_DIR = Path(__file__).resolve().parents[1] / "evals"
if str(EVALS_DIR) not in sys.path:
    sys.path.insert(0, str(EVALS_DIR))
