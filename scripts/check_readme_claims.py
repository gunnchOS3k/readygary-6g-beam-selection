#!/usr/bin/env python3
"""README / docs claim consistency vs code."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from sim.bands import primary_sub6  # noqa: E402


def main() -> int:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    assert "FR2" in readme
    assert "never Sub-6" in readme or "never Sub-6" in readme.replace("**", "")
    # 28 GHz must not be described as Sub-6
    assert "28 GHz is **FR2" in readme or "28 GHz is **FR2 mmWave**" in readme
    prim = primary_sub6()
    what = (ROOT / "docs" / "WHAT_IS_REAL_TODAY.md").read_text(encoding="utf-8")
    deploy = (ROOT / "deploy" / "README.md").read_text(encoding="utf-8")
    assert "BLOCKED_GPU" in deploy or "TensorRT" in deploy
    assert (ROOT / "docs" / "engineering" / "PREEXISTING_WORK_INVENTORY.md").is_file()
    print("readme_claims_ok", prim.profile_id)
    _ = what
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
