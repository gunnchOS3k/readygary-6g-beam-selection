"""AODT adapter. Optional. No NVIDIA credentials."""
from __future__ import annotations

from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sim.channels.aodt import AodtBackend  # noqa: E402


def write(out: Path | None = None) -> Path:
    ok, reason = AodtBackend().available()
    payload = {
        "backend": "aodt",
        "available": ok,
        "reason": reason,
        "evidence_class": "SYNTHETIC_SIM",
        "ota": False,
        "credentials_committed": False,
    }
    out = out or Path("results/tool_exports/aodt_status.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return out
