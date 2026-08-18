#!/usr/bin/env python3
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from readygary_tool_adapters import (  # noqa: E402
    aerial_adapter,
    aodt_adapter,
    benchmark_dataset_registry,
    deepmimo_adapter,
    sionna_channel_adapter,
    tensorrt_adapter,
)
from sim.channels import availability_report  # noqa: E402

deepmimo_adapter.config_path()
sionna_channel_adapter.config_path()
benchmark_dataset_registry.write_registry()
aerial_adapter.write()
aodt_adapter.write()
tensorrt_adapter.write()
Path("results/tool_exports").mkdir(parents=True, exist_ok=True)
Path("results/tool_exports/channel_backends.json").write_text(
    json.dumps(availability_report(), indent=2) + "\n", encoding="utf-8"
)
print("readygary tool exports done")
