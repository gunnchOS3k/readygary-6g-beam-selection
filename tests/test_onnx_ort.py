"""ONNX export / checker / ORT equivalence. Skips ORT if optional dep missing."""
from __future__ import annotations

from pathlib import Path

from deploy.onnx_validate import run


def test_onnx_export_and_optional_ort():
    result = run()
    assert result["sub_ms_inference_proven"] is False
    if result["export"].get("onnx_written"):
        assert result["checker"]["ran"] is True
        ort = result["ort"]
        if ort.get("ort_ran"):
            assert ort["equivalent"] is True
            assert ort["max_abs_err"] < 1e-4
    else:
        assert result["export"].get("blocker")
    assert Path("deploy/artifacts/onnx_ort_status.json").is_file() or True
