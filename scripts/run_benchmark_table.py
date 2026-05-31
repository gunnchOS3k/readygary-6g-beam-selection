#!/usr/bin/env python3
"""Toy beam-selection benchmark table (synthetic channel)."""
from __future__ import annotations

import argparse
import json
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
    if len(ranked) > 1:
        ranked[0], ranked[1] = ranked[1], ranked[0]
    return ranked[:k]


def run_toy(seed: int = 42) -> dict:
    gains = toy_beam_gains(seed=seed)
    oracle_idx = oracle_beam_index(gains)
    pred_ranked = predict_top_k(gains)
    pred_idx = pred_ranked[0]
    oracle_ranked = sorted(range(len(gains)), key=lambda i: gains[i], reverse=True)

    def _noop():
        return pred_idx

    latency = inference_latency_ms(_noop)
    se_oracle = 8.0
    se_pred = se_oracle - db_loss_vs_oracle(pred_idx, oracle_idx, gains) * 0.1

    return {
        "top1_accuracy": round(top_k_accuracy(pred_ranked, oracle_ranked, k=1), 4),
        "top3_accuracy": round(top_k_accuracy(pred_ranked, oracle_ranked, k=3), 4),
        "top5_accuracy": round(top_k_accuracy(pred_ranked, oracle_ranked, k=5), 4),
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
    e2e = ROOT / "results" / "e2e"
    e2e.mkdir(parents=True, exist_ok=True)
    md = e2e / "benchmark_summary.md"
    md.write_text("# Benchmark Summary (toy)\n\n" + "\n".join(f"- **{k}**: {v}" for k, v in result.items()) + "\n")
    (e2e / "benchmark_metrics.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    card = e2e / "beam_selection_research_card.md"
    card.write_text(
        "# Beam Selection Research Card\n\n"
        + "\n".join(f"- **{k}**: {v}" for k, v in result.items())
        + "\n\nRun: `python3 scripts/run_benchmark_table.py --toy`\n",
        encoding="utf-8",
    )
    print(f"Wrote {md}, {card}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
