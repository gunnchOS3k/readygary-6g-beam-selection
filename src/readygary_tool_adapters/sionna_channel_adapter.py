from pathlib import Path
import json

def config_path(out: Path | None = None) -> Path:
    """Write a Sionna config. Does not import sionna (open path)."""
    out = out or Path("results/tool_exports/sionna_channel_config.yaml")
    out.parent.mkdir(parents=True, exist_ok=True)
    try:
        import sionna  # noqa: F401
        status = "IMPLEMENTED_NOT_EXECUTED"
        note = "sionna importable; RT scene not committed; still SYNTHETIC_SIM"
    except Exception as exc:
        status = "BLOCKED_EXTERNAL"
        note = f"sionna not importable ({type(exc).__name__})"
    payload = {
        "backend": "sionna_optional",
        "status": status,
        "evidence_status": "config_only" if status != "IMPLEMENTED_AND_EXECUTED" else "executed",
        "evidence_class": "SYNTHETIC_SIM",
        "ota": False,
        "note": note,
        "sub6_carrier_hz": 3750000000,
        "fr2_carrier_hz": 28000000000,
        "never": "28 GHz as Sub-6; Sionna as OTA",
    }
    try:
        import yaml
        out.write_text(yaml.dump(payload), encoding="utf-8")
    except Exception:
        out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    return out
