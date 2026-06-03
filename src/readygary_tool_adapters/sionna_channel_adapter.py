from pathlib import Path
import yaml

def config_path(out: Path | None = None) -> Path:
    out = out or Path("results/tool_exports/sionna_channel_config.yaml")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(yaml.dump({"backend": "sionna_optional", "evidence_status": "config_only"}), encoding="utf-8")
    return out
