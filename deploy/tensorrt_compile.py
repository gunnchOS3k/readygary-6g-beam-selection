#!/usr/bin/env python3
"""TensorRT compile of the ONNX scorer. No GPU → BLOCKED_GPU. Never invent timings."""
from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / "deploy" / "artifacts"


def probe() -> dict:
    out = {
        "tensorrt_compiled": False,
        "status": "BLOCKED_GPU",
        "sub_ms_inference_proven": False,
        "sub_ms_inference_target": True,
        "latency_class": "HOST_PROCESS_TIMING",
        "engine_path": None,
        "reasons": [],
    }
    if shutil.which("nvidia-smi") is None:
        out["reasons"].append("nvidia-smi not on PATH")
    try:
        import torch

        if not torch.cuda.is_available():
            out["reasons"].append("torch.cuda.is_available() is False")
    except Exception:
        out["reasons"].append("torch not importable")
    try:
        import tensorrt  # noqa: F401
    except Exception as exc:
        out["reasons"].append(f"tensorrt not importable ({type(exc).__name__})")
    onnx_path = ART / "tiny_beam_scorer.onnx"
    if not onnx_path.is_file():
        out["reasons"].append("ONNX artifact missing; run deploy/onnx_export.py")
    if out["reasons"]:
        out["status"] = "BLOCKED_GPU"
        return out
    # GPU + TensorRT present: still do not fabricate engines in CI. Record ACTIVE ENGINEERING.
    out["status"] = "ACTIVE_ENGINEERING"
    out["reasons"].append("TensorRT+CUDA present but engine build is owner/lab gated (Nsight/TRT version pin).")
    return out


def main() -> int:
    ART.mkdir(parents=True, exist_ok=True)
    result = probe()
    path = ART / "tensorrt_status.json"
    path.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
