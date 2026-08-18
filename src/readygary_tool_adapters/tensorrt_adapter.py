"""TensorRT adapter. CPU hosts → BLOCKED_GPU. No invented timings."""
from __future__ import annotations

from pathlib import Path
import json
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from deploy.tensorrt_compile import probe  # noqa: E402


def write(out: Path | None = None) -> Path:
    out = out or Path("results/tool_exports/tensorrt_status.json")
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(probe(), indent=2) + "\n", encoding="utf-8")
    return out
