#!/usr/bin/env python3
"""TensorRT compile of the ONNX scorer.

Code path is complete. GPU execution is BLOCKED_GPU on hosts without CUDA+TRT.
Never invent p50/p95/p99. Sub-ms remains TARGET unless measured.
"""
from __future__ import annotations

import json
import shutil
import sys
import time
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / "deploy" / "artifacts"


def _reasons() -> list[str]:
    reasons: list[str] = []
    if shutil.which("nvidia-smi") is None:
        reasons.append("nvidia-smi not on PATH")
    try:
        import torch

        if not torch.cuda.is_available():
            reasons.append("torch.cuda.is_available() is False")
    except Exception:
        reasons.append("torch not importable")
    try:
        import tensorrt  # noqa: F401
    except Exception as exc:
        reasons.append(f"tensorrt not importable ({type(exc).__name__})")
    if not (ART / "tiny_beam_scorer.onnx").is_file():
        reasons.append("ONNX artifact missing; run deploy/onnx_export.py")
    return reasons


def build_engine(onnx_path: Path, engine_path: Path) -> dict[str, Any]:
    """Real TensorRT builder. Raises if TRT is missing — caller records BLOCKED_GPU."""
    import tensorrt as trt  # type: ignore

    logger = trt.Logger(trt.Logger.WARNING)
    builder = trt.Builder(logger)
    network = builder.create_network(1 << int(trt.NetworkDefinitionCreationFlag.EXPLICIT_BATCH))
    parser = trt.OnnxParser(network, logger)
    with onnx_path.open("rb") as fh:
        if not parser.parse(fh.read()):
            errs = [parser.get_error(i).desc() for i in range(parser.num_errors)]
            raise RuntimeError(f"ONNX parse failed: {errs}")
    config = builder.create_builder_config()
    if hasattr(config, "set_memory_pool_limit"):
        config.set_memory_pool_limit(trt.MemoryPoolType.WORKSPACE, 256 << 20)
    engine = builder.build_serialized_network(network, config)
    if engine is None:
        raise RuntimeError("TensorRT build_serialized_network returned None")
    engine_path.parent.mkdir(parents=True, exist_ok=True)
    engine_path.write_bytes(bytes(engine))
    return {"engine_path": str(engine_path), "bytes": engine_path.stat().st_size}


def run_engine(engine_path: Path, n_warmup: int = 10, n_trials: int = 50) -> dict[str, Any]:
    """Execute TRT engine and report HOST_PROCESS_TIMING percentiles. No fabrication."""
    import numpy as np
    import tensorrt as trt  # type: ignore

    logger = trt.Logger(trt.Logger.WARNING)
    runtime = trt.Runtime(logger)
    engine = runtime.deserialize_cuda_engine(engine_path.read_bytes())
    context = engine.create_execution_context()
    # Timing here is still HOST_PROCESS_TIMING of the TRT run loop, not gNB slot time.
    times = []
    x = np.random.default_rng(0).random((1, 64), dtype=np.float32)
    y = np.zeros((1, 8), dtype=np.float32)
    try:
        import pycuda.autoinit  # noqa: F401
        import pycuda.driver as cuda
    except Exception as exc:
        raise RuntimeError(f"pycuda required for TRT GPU execution ({type(exc).__name__})") from exc

    d_in = cuda.mem_alloc(x.nbytes)
    d_out = cuda.mem_alloc(y.nbytes)
    bindings = [int(d_in), int(d_out)]
    for _ in range(n_warmup):
        cuda.memcpy_htod(d_in, x)
        context.execute_v2(bindings)
        cuda.memcpy_dtoh(y, d_out)
    for _ in range(n_trials):
        t0 = time.perf_counter()
        cuda.memcpy_htod(d_in, x)
        context.execute_v2(bindings)
        cuda.memcpy_dtoh(y, d_out)
        times.append((time.perf_counter() - t0) * 1000.0)
    arr = np.sort(np.array(times))
    p = lambda q: float(arr[min(len(arr) - 1, int(round(q * (len(arr) - 1))))])
    return {
        "n_warmup": n_warmup,
        "n_trials": n_trials,
        "p50_ms": p(0.50),
        "p95_ms": p(0.95),
        "p99_ms": p(0.99),
        "latency_class": "HOST_PROCESS_TIMING",
        "sub_ms_inference_proven": bool(p(0.99) < 1.0),
        "sub_ms_inference_target": True,
    }


def probe() -> dict[str, Any]:
    out: dict[str, Any] = {
        "tensorrt_compiled": False,
        "status": "BLOCKED_GPU",
        "tensorrt_code_complete": True,
        "tensorrt_gpu_execution": "BLOCKED_GPU",
        "sub_ms_inference_proven": False,
        "sub_ms_inference_target": True,
        "latency_class": "HOST_PROCESS_TIMING",
        "engine_path": None,
        "reasons": _reasons(),
    }
    if out["reasons"]:
        out["status"] = "BLOCKED_GPU"
        return out
    try:
        built = build_engine(ART / "tiny_beam_scorer.onnx", ART / "tiny_beam_scorer.engine")
        timed = run_engine(Path(built["engine_path"]))
        out.update(
            {
                "tensorrt_compiled": True,
                "status": "IMPLEMENTED_AND_EXECUTED",
                "tensorrt_gpu_execution": "IMPLEMENTED_AND_EXECUTED",
                "engine_path": built["engine_path"],
                "timing": timed,
                "sub_ms_inference_proven": timed["sub_ms_inference_proven"],
            }
        )
        return out
    except Exception as exc:
        out["status"] = "ACTIVE_ENGINEERING"
        out["tensorrt_gpu_execution"] = "BLOCKED_GPU"
        out["reasons"].append(f"builder/run failed: {type(exc).__name__}")
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
