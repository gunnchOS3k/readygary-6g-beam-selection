#!/usr/bin/env python3
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from readygary_tool_adapters import deepmimo_adapter, sionna_channel_adapter, benchmark_dataset_registry
deepmimo_adapter.config_path()
sionna_channel_adapter.config_path()
benchmark_dataset_registry.write_registry()
print('readygary tool exports done')
