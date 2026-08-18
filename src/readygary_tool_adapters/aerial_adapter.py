"""Optional NVIDIA Aerial / pyAerial probe. Never a hard dependency. No credentials."""
from __future__ import annotations

from pathlib import Path
import json


def probe() -> dict:
    status = {
        "backend": "nvidia_aerial",
        "available": False,
        "status": "BLOCKED_OPTIONAL_BACKEND",
        "evidence_class": "SYNTHETIC_SIM",
        "credentials_committed": False,
    }
    try:
        import aerial  # noqa: F401

        status["available"] = True
        status["status"] = "ACTIVE_ENGINEERING"
        status["note"] = "aerial imported; no in-tree credentials; scene still owner-gated"
        return status
    except Exception:
        pass
    try:
        import pyaerial  # noqa: F401

        status["available"] = True
        status["status"] = "ACTIVE_ENGINEERING"
        status["import"] = "pyaerial"
        return status
    except Exception as exc:
        status["reason"] = f"{type(exc).__name__}"
        return status


def write(out: Path | None = None) -> Path:
    out = out or Path("results/tool_exports/aerial_status.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(probe(), indent=2) + "\n", encoding="utf-8")
    return out
