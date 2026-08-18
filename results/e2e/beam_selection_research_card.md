# Beam Selection Research Card

- **evidence_class**: SYNTHETIC_SIM
- **latency_class**: HOST_PROCESS_TIMING
- **sub_ms_inference_proven**: False
- **carrier_note**: Toy gains are unitless dB draws; the TDL generator default 28e9 is FR2 mmWave, not Sub-6.
- **top1_accuracy**: 0.0
- **top3_accuracy**: 1.0
- **top5_accuracy**: 0.6
- **db_loss_vs_oracle**: 0.2461
- **spectral_efficiency_loss**: 0.0246
- **inference_latency_ms**: 0.001
- **note**: toy synthetic channel — not calibrated mmWave measurements; do not cite as measured RF

Run: `python3 scripts/run_benchmark_table.py --toy`
Evidence class: `SYNTHETIC_SIM`.
