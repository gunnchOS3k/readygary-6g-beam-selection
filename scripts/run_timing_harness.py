#!/usr/bin/env python3
"""Host-process timing harness. Not RF latency. Sub-ms inference remains unproven."""
from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path

os.environ.setdefault("MPLBACKEND", "Agg")

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from sim.metrics import inference_latency_ms, toy_beam_gains, oracle_beam_index


def _noop_predict() -> int:
    gains = toy_beam_gains(seed=42)
    return oracle_beam_index(gains)


def _time_codebook_search() -> dict:
    payload = {
        "exhaustive_search_ms": None,
        "hierarchical_search_ms": None,
        "note": "numpy/matplotlib optional; skipped if import fails",
    }
    try:
        import numpy as np

        sys.path.insert(0, str(ROOT / "sim" / "baselines"))
        from exhaustive_search import ExhaustiveBeamSearch
        from hierarchical_search import HierarchicalBeamSearch
    except Exception as exc:  # pragma: no cover - optional stack
        payload["skip_reason"] = str(exc)
        return payload

    rng = np.random.default_rng(0)
    # Small H keeps CI fast; still SYNTHETIC_SIM.
    h = rng.normal(size=(8, 8)) + 1j * rng.normal(size=(8, 8))
    exh = ExhaustiveBeamSearch(num_tx_beams=16, num_rx_beams=16)
    hier = HierarchicalBeamSearch(num_tx_beams=16, num_rx_beams=16)
    t0 = time.perf_counter()
    exh.search_optimal_beams(h)
    payload["exhaustive_search_ms"] = round((time.perf_counter() - t0) * 1000.0, 4)
    t1 = time.perf_counter()
    hier.coarse_search(h)
    payload["hierarchical_search_ms"] = round((time.perf_counter() - t1) * 1000.0, 4)
    return payload


def main() -> int:
    host_ms = inference_latency_ms(_noop_predict)
    search = _time_codebook_search()
    result = {
        "evidence_class": "SYNTHETIC_SIM",
        "latency_class": "HOST_PROCESS_TIMING",
        "sub_ms_inference_proven": False,
        "toy_oracle_callable_ms": round(host_ms, 4),
        "search": search,
        "note": (
            "Wall-clock around Python callables on the host. "
            "Not gNB slot time, not ONNX/TensorRT, not OTA. "
            "Do not cite as proof of sub-ms edge inference."
        ),
    }
    out_dir = ROOT / "results"
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / "timing_harness.json"
    path.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    md = out_dir / "timing_harness.md"
    lines = ["# Timing harness (`HOST_PROCESS_TIMING`)\n", ""]
    for k, v in result.items():
        if k == "search":
            continue
        lines.append(f"- **{k}**: {v}")
    lines.append("")
    md.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    print(f"Wrote {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
