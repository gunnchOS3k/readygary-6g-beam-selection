#!/usr/bin/env python3
"""Export tiny beam scorer to npz always; ONNX when onnx/torch is available.

Never requires NVIDIA software. TensorRT is a separate compile step.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from deploy.tiny_beam_scorer import N_HID, N_IN, N_OUT, save_npz, seeded_scorer  # noqa: E402

ART = ROOT / "deploy" / "artifacts"


def try_onnx(scorer, onnx_path: Path) -> dict:
    status = {
        "onnx_written": False,
        "onnx_path": str(onnx_path),
        "blocker": None,
    }
    try:
        import numpy as np
        import onnx
        from onnx import TensorProto, helper, numpy_helper
    except Exception as exc:
        status["blocker"] = f"ONNX_EXPORT_BLOCKED_OPTIONAL_DEP: {type(exc).__name__}"
        return status

    w1 = numpy_helper.from_array(scorer.w1, name="W1")
    b1 = numpy_helper.from_array(scorer.b1, name="B1")
    w2 = numpy_helper.from_array(scorer.w2, name="W2")
    b2 = numpy_helper.from_array(scorer.b2, name="B2")
    x = helper.make_tensor_value_info("X", TensorProto.FLOAT, [1, N_IN])
    y = helper.make_tensor_value_info("Y", TensorProto.FLOAT, [1, N_OUT])
    nodes = [
        helper.make_node("Gemm", ["X", "W1", "B1"], ["H"], name="gemm1"),
        helper.make_node("Tanh", ["H"], ["Hact"], name="tanh"),
        helper.make_node("Gemm", ["Hact", "W2", "B2"], ["Y"], name="gemm2"),
    ]
    graph = helper.make_graph(nodes, "tiny_beam_scorer", [x], [y], [w1, b1, w2, b2])
    model = helper.make_model(graph, opset_imports=[helper.make_opsetid("", 13)])
    model.ir_version = 8
    onnx.checker.check_model(model)
    onnx_path.parent.mkdir(parents=True, exist_ok=True)
    onnx.save(model, onnx_path)
    status["onnx_written"] = True
    return status


def main() -> int:
    ART.mkdir(parents=True, exist_ok=True)
    scorer = seeded_scorer(7)
    npz = save_npz(scorer, ART / "tiny_beam_scorer.npz")
    onnx_status = try_onnx(scorer, ART / "tiny_beam_scorer.onnx")
    meta = {
        "model": "tiny_beam_scorer",
        "n_in": N_IN,
        "n_hid": N_HID,
        "n_out": N_OUT,
        "carrier_hz": 28_000_000_000,
        "band": "FR2",
        "never": "Sub-6 for this FR2 8x8 scorer",
        "families": ["FR2", "SUB6"],
        "sub6_primary": "n77_us_cband",
        "npz": str(npz.relative_to(ROOT)),
        "onnx": onnx_status,
        "sub_ms_inference_proven": False,
        "sub_ms_inference_target": True,
        "evidence_class": "SYNTHETIC_SIM",
        "latency_class": "HOST_PROCESS_TIMING",
        "note": "Seeded untrained logits for deploy plumbing, not a claimed accuracy model.",
    }
    (ART / "metadata.json").write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(meta, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
