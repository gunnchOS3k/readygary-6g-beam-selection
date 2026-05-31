#!/usr/bin/env python3
"""Toy beam-selection benchmark table (synthetic channel)."""
from __future__ import annotations

import argparse
import json
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from sim.metrics import (
    db_loss_vs_oracle,
    inference_latency_ms,
    oracle_beam_index,
    spectral_efficiency_loss,
    top_k_accuracy,
    toy_beam_gains,
)


def predict_top_k(gains: list[float], k: int = 3) -> list[int]:
    ranked = sorted(range(len(gains)), key=lambda i: gains[i], reverse=True)
    # Toy model: oracle with one rank slip
    if len(ranked) > 1:
        ranked[0], ranked[1] = ranked[1], ranked[0]
    return ranked[:k]


def run_toy(seed: int = 42) -> dict:
    gains = toy_beam_gains(seed=seed)
    oracle_idx = oracle_beam_index(gains)
    pred_ranked = predict_top_k(gains)
    pred_idx = pred_ranked[0]
    oracle_ranked = sorted(range(len(gains)), key=lambda i: gains[i], reverse=True)[:3]

    def _noop():
        return pred_idx

    latency = inference_latency_ms(_noop)
    se_oracle = 8.0
    se_pred = se_oracle - db_loss_vs_oracle(pred_idx, oracle_idx, gains) * 0.1

    return {
        "top_k_accuracy": round(top_k_accuracy(pred_ranked, oracle_ranked, k=3), 4),
        "db_loss_vs_oracle": round(db_loss_vs_oracle(pred_idx, oracle_idx, gains), 4),
        "spectral_efficiency_loss": round(spectral_efficiency_loss(se_pred, se_oracle), 4),
        "inference_latency_ms": round(latency, 4),
        "note": "toy synthetic channel — not calibrated mmWave measurements",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--toy", action="store_true")
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()
    if not args.toy:
        print("Use --toy", file=sys.stderr)
        return 2

    result = run_toy(seed=args.seed)
    print(json.dumps(result, indent=2))
    md = ROOT / "results" / "benchmark_summary.md"
    md.parent.mkdir(parents=True, exist_ok=True)
    md.write_text(
        "# Benchmark Summary (toy)\n\n"
        + "\n".join(f"- **{k}**: {v}" for k, v in result.items())
        + "\n",
        encoding="utf-8",
    )
    (ROOT / "results" / "benchmark_summary.json").write_text(
        json.dumps(result, indent=2) + "\n", encoding="utf-8"
    )
    print(f"Wrote {md}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
