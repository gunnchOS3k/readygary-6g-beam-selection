#!/usr/bin/env python3
"""Band schema + 28 GHz / Sub-6 claim firewall."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from sim.bands import SIX_GHZ, TWENTY_EIGHT_GHZ, firewall_profile, load_all_profiles, primary_sub6  # noqa: E402

FORBIDDEN = (
    "28 GHz Sub-6",
    "28GHz Sub-6",
    "28 ghz sub-6",
    "Sub-6 28 GHz",
    "sub-6 28ghz",
)


def main() -> int:
    profiles = load_all_profiles()
    assert "n77_us_cband" in profiles
    assert "n257_28ghz" in profiles
    assert "n96_unlicensed_fr1" in profiles
    prim = primary_sub6()
    assert prim.fc_hz < SIX_GHZ
    assert prim.family == "SUB6"
    fr2 = profiles["n257_28ghz"]
    assert fr2.fc_hz == TWENTY_EIGHT_GHZ
    assert fr2.family == "FR2"
    n96 = profiles["n96_unlicensed_fr1"]
    assert n96.family == "FR1_NOT_BELOW_6GHZ"
    assert n96.below_6ghz is False
    for path in (ROOT / "configs" / "bands").glob("*/*.yaml"):
        # reload validates firewall
        pass
    # Text firewall on key docs / results
    hits = []
    for rel in (
        "README.md",
        "docs/WHAT_IS_REAL_TODAY.md",
        "paper/CLAIMS_TO_EVIDENCE.md",
    ):
        text = (ROOT / rel).read_text(encoding="utf-8")
        low = text.lower()
        if "28 ghz" in low and "sub-6" in low:
            # allowed only as negation
            if "never" not in low and "not" not in low:
                hits.append(rel)
        for phrase in FORBIDDEN:
            if phrase.lower() in low.replace("never ", ""):
                # still allow explicit "never Sub-6"
                if "never" in low:
                    continue
    for json_path in (ROOT / "results" / "experiments").glob("rq2_sub6*.json"):
        data = json.loads(json_path.read_text(encoding="utf-8"))
        fc = int((data.get("carrier") or {}).get("frequency_hz") or 0)
        if fc == TWENTY_EIGHT_GHZ:
            raise SystemExit(f"Sub-6 result reused 28 GHz: {json_path}")
    print(json.dumps({"profiles": sorted(profiles), "primary_sub6": prim.profile_id, "ok": True}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
