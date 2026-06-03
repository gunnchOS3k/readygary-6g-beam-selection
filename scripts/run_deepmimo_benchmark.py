#!/usr/bin/env python3
import sys
sys.path.insert(0,'src')
from readygary_tool_adapters.deepmimo_adapter import is_data_available
if not is_data_available():
    print('SKIP: DeepMIMO data not present — see DEEPMIMO_BENCHMARK_PATH.md')
    raise SystemExit(0)
