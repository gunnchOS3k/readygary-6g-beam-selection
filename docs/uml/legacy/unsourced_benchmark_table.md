# Legacy — unsourced algorithm table (do not cite)

A previous README listed Exhaustive 100% / 50 ms, Hierarchical 95% / 12 ms, LSTM 85% / **0.8 ms** as if they were experimental results.

Those numbers are **not** emitted by `scripts/run_benchmark_table.py` or `scripts/run_timing_harness.py`. The 0.8 ms LSTM figure is **not** a hardware measurement.

**Cite instead:** `results/e2e/benchmark_metrics.json` (`SYNTHETIC_SIM`) and `results/timing_harness.json` (`HOST_PROCESS_TIMING`). Sub-ms inference remains **unproven**.
