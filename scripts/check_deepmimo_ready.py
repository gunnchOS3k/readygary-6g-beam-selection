#!/usr/bin/env python3
import sys
sys.path.insert(0,'src')
from readygary_tool_adapters.deepmimo_adapter import is_data_available
print('ready:', is_data_available())
