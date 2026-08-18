# Ablation notes

What the **current** scripts compare. Not a conference ablation on measured RF.

## Toy benchmark (`run_benchmark_table.py --toy`)

`predict_top_k` ranks by synthetic gain then **swaps the top two indices**. That is a deliberate non-oracle predictor so top-1 is not trivially 1.0 on every seed. Metrics (`top_k_accuracy`, `db_loss_vs_oracle`, `spectral_efficiency_loss`) are computed against `oracle_beam_index`.

This is **not** an LSTM vs exhaustive vs hierarchical bake-off. Those three algorithms live in `sim/` but are **not** wired into the toy table generator.

## Search algorithms (optional, host timing)

When numpy is present, `scripts/run_timing_harness.py` times:

- `ExhaustiveBeamSearch.search_optimal_beams` on a small random `H`
- `HierarchicalBeamSearch` coarse+fine on the same `H`

Compare **host wall time and SNR on that synthetic H only**. Do not report as mmWave latency.

## Not ablated here

- Trained LSTM vs oracle on a frozen dataset
- Probe-budget RL
- FR1 vs FR2 vs FR3
- Hardware quantization
