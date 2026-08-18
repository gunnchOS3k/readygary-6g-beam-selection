#!/usr/bin/env python3
"""Held-out confirmatory FR2 beam split. Protocol must exist (committed first)."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from run_paper_ii_beam_experiment import main as beam_main


def main() -> int:
    sys.argv = [sys.argv[0], "--held-out", "--domain-shift", "--ablations"]
    return beam_main()


if __name__ == "__main__":
    raise SystemExit(main())
