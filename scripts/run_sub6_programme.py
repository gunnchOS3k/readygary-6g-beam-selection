#!/usr/bin/env python3
"""Run Sub-6 programme. Protocol must already exist."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from sim.experiments.sub6_programme import run_programme, write_bundle  # noqa: E402


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--heldout", action="store_true")
    args = p.parse_args()
    proto = ROOT / "paper" / "artifacts" / "experiment_protocol_sub6.yaml"
    if not proto.is_file():
        raise SystemExit("Missing frozen Sub-6 protocol")
    bundle = run_programme(heldout=args.heldout)
    path = write_bundle(bundle, args.heldout)
    print(json.dumps({"wrote": str(path), "carrier_hz": bundle["carrier"]["frequency_hz"], "family": "SUB6"}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
