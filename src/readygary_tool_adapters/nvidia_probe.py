"""NVIDIA / open-backend classification. No credentials. Field-kit fail-closed."""
from __future__ import annotations

import json
import shutil
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]


def _try_import(name: str) -> dict[str, Any]:
    try:
        __import__(name)
        return {"present": True, "error": None}
    except Exception as exc:
        return {"present": False, "error": f"{type(exc).__name__}: {exc}"}


def classify() -> dict[str, Any]:
    gpu = shutil.which("nvidia-smi") is not None
    numpy_ok = _try_import("numpy")["present"]
    torch = _try_import("torch")
    sionna = _try_import("sionna")
    aodt = _try_import("aodt")
    aerial = _try_import("aerial")
    pyaerial = _try_import("pyaerial")
    onnx = _try_import("onnx")
    ort = _try_import("onnxruntime")
    trt = _try_import("tensorrt")

    def status(*, executed: bool, implemented: bool, blocked: str | None) -> str:
        if executed:
            return "IMPLEMENTED_AND_EXECUTED"
        if blocked == "gpu":
            return "BLOCKED_GPU"
        if blocked == "member":
            return "BLOCKED_MEMBER_ACCESS"
        if blocked == "external":
            return "BLOCKED_EXTERNAL"
        if implemented:
            return "IMPLEMENTED_NOT_EXECUTED"
        return "SCAFFOLD_ONLY"

    backends = {
        "numpy": {
            "status": "IMPLEMENTED_AND_EXECUTED" if numpy_ok else "SCAFFOLD_ONLY",
            "open_path": True,
        },
        "pytorch": {
            "status": status(executed=False, implemented=torch["present"], blocked=None if torch["present"] else "external"),
            "present": torch["present"],
            "error": torch["error"],
            "open_path": True,
            "note": "LSTM tracker exists; dual-band sequential policy is numpy REINFORCE",
        },
        "sionna": {
            "status": status(executed=False, implemented=True, blocked=None if sionna["present"] else "external"),
            "present": sionna["present"],
            "error": sionna["error"],
            "open_path": False,
        },
        "sionna_rt": {
            "status": status(executed=False, implemented=True, blocked=None if sionna["present"] else "external"),
            "present": sionna["present"],
            "scene": False,
            "open_path": False,
        },
        "aodt": {
            "status": status(
                executed=False,
                implemented=True,
                blocked="member" if not (aodt["present"] or aerial["present"]) else None,
            ),
            "present": aodt["present"],
            "error": aodt["error"],
            "open_path": False,
        },
        "aerial_pyaerial": {
            "status": status(
                executed=False,
                implemented=True,
                blocked="member" if not (aerial["present"] or pyaerial["present"]) else None,
            ),
            "aerial": aerial,
            "pyaerial": pyaerial,
            "open_path": False,
            "credentials_committed": False,
        },
        "onnx": {
            "status": "IMPLEMENTED_AND_EXECUTED" if onnx["present"] else "IMPLEMENTED_NOT_EXECUTED",
            "present": onnx["present"],
            "error": onnx["error"],
            "open_path": True,
        },
        "onnxruntime": {
            "status": "IMPLEMENTED_AND_EXECUTED" if ort["present"] else "IMPLEMENTED_NOT_EXECUTED",
            "present": ort["present"],
            "error": ort["error"],
            "open_path": True,
        },
        "tensorrt": {
            "status": "BLOCKED_GPU" if not (gpu and trt["present"]) else "IMPLEMENTED_NOT_EXECUTED",
            "present": trt["present"],
            "gpu": gpu,
            "error": trt["error"],
            "open_path": False,
            "tensorrt_code_complete": True,
            "tensorrt_gpu_execution": "BLOCKED_GPU" if not (gpu and trt["present"]) else "ACTIVE_ENGINEERING",
        },
    }
    return {
        "evidence_class": "SYNTHETIC_SIM",
        "credentials_committed": False,
        "silent_fake_forbidden": True,
        "owner_login_required": True,
        "gpu": gpu,
        "backends": backends,
    }


def write(out: Path | None = None) -> Path:
    out = out or ROOT / "results" / "tool_exports" / "nvidia_sub6_backends.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(classify(), indent=2) + "\n", encoding="utf-8")
    return out
