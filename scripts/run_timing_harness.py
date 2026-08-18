#!/usr/bin/env python3
"""Host-process timing: pre / model / post / full path.

Warmup, batch=1, p50/p95/p99. Sub-ms is TARGET, not fact.
TensorRT without GPU → BLOCKED_GPU. Not RF / gNB slot / OTA.
"""
from __future__ import annotations

import json
import math
import os
import sys
import time
from pathlib import Path

os.environ.setdefault("MPLBACKEND", "Agg")

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from deploy.tensorrt_compile import probe as tensorrt_probe  # noqa: E402
from deploy.tiny_beam_scorer import seeded_scorer  # noqa: E402

try:
    import numpy as np
except Exception as exc:  # pragma: no cover
    print("numpy required:", exc)
    raise SystemExit(1)

from sim.metrics import inference_latency_ms, oracle_beam_index, toy_beam_gains  # noqa: E402


def percentile(xs: list[float], p: float) -> float:
    if not xs:
        return float("nan")
    ys = sorted(xs)
    k = (len(ys) - 1) * (p / 100.0)
    f = math.floor(k)
    c = math.ceil(k)
    if f == c:
        return ys[int(k)]
    return ys[f] * (c - k) + ys[c] * (k - f)


def stage_times(n_warmup: int, n_trials: int, seed: int = 0) -> dict:
    rng = np.random.default_rng(seed)
    scorer = seeded_scorer(7)
    Hs = [rng.normal(size=(8, 8)) + 1j * rng.normal(size=(8, 8)) for _ in range(n_warmup + n_trials)]
    for H in Hs[:n_warmup]:
        scorer.infer(H)
    buckets = {"pre": [], "model": [], "post": [], "full": []}
    for H in Hs[n_warmup:]:
        t0 = time.perf_counter()
        x = scorer.pre(H)
        t1 = time.perf_counter()
        logits = scorer.model(x)
        t2 = time.perf_counter()
        scorer.post(logits)
        t3 = time.perf_counter()
        buckets["pre"].append((t1 - t0) * 1000.0)
        buckets["model"].append((t2 - t1) * 1000.0)
        buckets["post"].append((t3 - t2) * 1000.0)
        buckets["full"].append((t3 - t0) * 1000.0)
    summary = {}
    for name, vals in buckets.items():
        summary[name] = {
            "p50_ms": percentile(vals, 50),
            "p95_ms": percentile(vals, 95),
            "p99_ms": percentile(vals, 99),
            "mean_ms": float(sum(vals) / len(vals)),
            "n": len(vals),
        }
    return summary


def _time_codebook_search() -> dict:
    payload = {
        "exhaustive_search_ms": None,
        "hierarchical_search_ms": None,
        "note": "numpy/matplotlib optional; skipped if import fails",
    }
    try:
        sys.path.insert(0, str(ROOT / "sim" / "baselines"))
        from exhaustive_search import ExhaustiveBeamSearch
        from hierarchical_search import HierarchicalBeamSearch
    except Exception as exc:
        payload["skip_reason"] = str(exc)
        return payload
    rng = np.random.default_rng(0)
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
    host_ms = inference_latency_ms(lambda: oracle_beam_index(toy_beam_gains(seed=42)))
    stages = stage_times(n_warmup=8, n_trials=64, seed=0)
    trt = tensorrt_probe()
    result = {
        "evidence_class": "SYNTHETIC_SIM",
        "latency_class": "HOST_PROCESS_TIMING",
        "sub_ms_inference_proven": False,
        "sub_ms_inference_target": True,
        "batch_size": 1,
        "warmup": 8,
        "trials": 64,
        "stages_ms": stages,
        "tensorrt": trt,
        "toy_oracle_callable_ms": round(host_ms, 4),
        "search": _time_codebook_search(),
        "note": (
            "Wall-clock around Python callables on the host. "
            "Not gNB slot time, not TensorRT unless tensorrt.status says compiled, not OTA. "
            "Do not cite as proof of sub-ms edge inference. <1ms is TARGET."
        ),
    }
    out_dir = ROOT / "results"
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / "timing_harness.json"
    path.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    (ROOT / "deploy" / "artifacts").mkdir(parents=True, exist_ok=True)
    (ROOT / "deploy" / "artifacts" / "timing_harness.json").write_text(
        json.dumps(result, indent=2) + "\n", encoding="utf-8"
    )
    md = out_dir / "timing_harness.md"
    lines = [
        "# Timing harness (`HOST_PROCESS_TIMING`)\n",
        "",
        "Sub-ms inference is **TARGET**, not proven.",
        "",
        f"- tensorrt: `{trt['status']}`",
        f"- full-path p50_ms: `{stages['full']['p50_ms']:.4f}`",
        f"- full-path p95_ms: `{stages['full']['p95_ms']:.4f}`",
        f"- full-path p99_ms: `{stages['full']['p99_ms']:.4f}`",
        "",
    ]
    md.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    print(f"Wrote {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
