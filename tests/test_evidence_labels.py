import runpy
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_toy_benchmark_is_synthetic_sim():
    mod = runpy.run_path(str(ROOT / "scripts" / "run_benchmark_table.py"))
    result = mod["run_toy"](seed=42)
    assert result["evidence_class"] == "SYNTHETIC_SIM"
    assert result["latency_class"] == "HOST_PROCESS_TIMING"
    assert result["sub_ms_inference_proven"] is False
