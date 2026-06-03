from pathlib import Path
import yaml

def config_path(out: Path | None = None) -> Path:
    out = out or Path("results/tool_exports/deepmimo_config.yaml")
    out.parent.mkdir(parents=True, exist_ok=True)
    cfg = {"dataset": "placeholder", "scenario": "urban_micro", "evidence_status": "config_only", "data_present": False}
    out.write_text(yaml.dump(cfg), encoding="utf-8")
    return out

def is_data_available() -> bool:
    return False
