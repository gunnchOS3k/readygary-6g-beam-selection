#!/usr/bin/env python3
"""Run dual-band continuity programme. Protocol must already exist."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from sim.experiments.dualband_programme import run_programme, write_bundle  # noqa: E402


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--heldout", action="store_true")
    args = p.parse_args()
    proto = ROOT / "paper" / "artifacts" / "experiment_protocol_dualband.yaml"
    if not proto.is_file():
        raise SystemExit("Missing frozen dual-band protocol")
    bundle = run_programme(heldout=args.heldout)
    path = write_bundle(bundle, args.heldout)
    print(json.dumps({"wrote": str(path), "n_rows": len(bundle["rows"]), "heldout": args.heldout}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
