import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from readygary_tool_adapters.deepmimo_adapter import config_path, is_data_available
def test_deepmimo_graceful():
    assert is_data_available() is False
    p = config_path()
    assert p.exists()
