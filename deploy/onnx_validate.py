"""ONNX export + checker + ORT equivalence. Never fabricate latency."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np

from deploy.onnx_export import try_onnx
from deploy.tiny_beam_scorer import seeded_scorer

ROOT = Path(__file__).resolve().parents[1]
ART = ROOT / "deploy" / "artifacts"


def numpy_logits(scorer, x: np.ndarray) -> np.ndarray:
    return scorer.model(x.reshape(1, -1) if x.ndim == 1 else x)


def validate_ort(onnx_path: Path, scorer, x: np.ndarray) -> dict[str, Any]:
    out: dict[str, Any] = {
        "ort_ran": False,
        "equivalent": False,
        "max_abs_err": None,
        "blocker": None,
    }
    try:
        import onnxruntime as ort
    except Exception as exc:
        out["blocker"] = f"ORT_BLOCKED_OPTIONAL_DEP: {type(exc).__name__}"
        return out
    sess = ort.InferenceSession(str(onnx_path), providers=["CPUExecutionProvider"])
    y_ort = sess.run(None, {"X": x.astype(np.float32)})[0]
    y_np = numpy_logits(scorer, x).astype(np.float32)
    err = float(np.max(np.abs(y_ort - y_np)))
    out["ort_ran"] = True
    out["max_abs_err"] = err
    out["equivalent"] = err < 1e-4
    out["latency_class"] = "HOST_PROCESS_TIMING"
    out["sub_ms_inference_proven"] = False
    return out


def run() -> dict[str, Any]:
    ART.mkdir(parents=True, exist_ok=True)
    scorer = seeded_scorer(7)
    onnx_path = ART / "tiny_beam_scorer.onnx"
    exp = try_onnx(scorer, onnx_path)
    x = scorer.pre(np.eye(8, dtype=np.complex64)).reshape(1, -1)
    result: dict[str, Any] = {
        "export": exp,
        "checker": {"ran": bool(exp.get("onnx_written"))},
        "ort": {"ort_ran": False},
        "evidence_class": "SYNTHETIC_SIM",
        "sub_ms_inference_proven": False,
    }
    if exp.get("onnx_written"):
        try:
            import onnx

            model = onnx.load(str(onnx_path))
            onnx.checker.check_model(model)
            result["checker"] = {"ran": True, "ok": True}
        except Exception as exc:
            result["checker"] = {"ran": True, "ok": False, "error": type(exc).__name__}
        result["ort"] = validate_ort(onnx_path, scorer, x)
    (ART / "onnx_ort_status.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    return result


if __name__ == "__main__":
    print(json.dumps(run(), indent=2))
