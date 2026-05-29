#!/usr/bin/env python3
"""Generate toy benchmark table — not publication results."""
import argparse
from pathlib import Path

from sim.metrics import top_k_accuracy, db_loss_vs_oracle, spectral_efficiency_loss, inference_latency_ms


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--toy", action="store_true")
    args = parser.parse_args()
    rows = [
        ("exhaustive", top_k_accuracy([1, 1, 2], 1, 1), db_loss_vs_oracle(0.5, 0.0), spectral_efficiency_loss(4.0, 4.5), inference_latency_ms(500)),
        ("learned_lstm", top_k_accuracy([1, 2, 3], 1, 3), db_loss_vs_oracle(1.2, 0.0), spectral_efficiency_loss(3.8, 4.5), inference_latency_ms(1200)),
    ]
    md = "| Method | Top-1 acc (toy) | dB loss | SE loss | infer ms |\n|---|---:|---:|---:|---:|\n"
    for name, t1, db, se, lat in rows:
        md += f"| {name} | {t1:.2f} | {db:.2f} | {se:.2f} | {lat:.1f} |\n"
    md += "\n> **Preliminary toy benchmark** — not validated publication results.\n"
    Path("results").mkdir(exist_ok=True)
    Path("results/benchmark_summary.md").write_text(md)
    print(md)


if __name__ == "__main__":
    main()
