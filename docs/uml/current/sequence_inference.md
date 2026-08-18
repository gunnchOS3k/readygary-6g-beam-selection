# Sequence — toy inference / benchmark (current)

| | |
|---|---|
| **Status** | **Current** — `python3 scripts/run_benchmark_table.py --toy` |
| **Evidence** | `SYNTHETIC_SIM`. Latency field is `HOST_PROCESS_TIMING` of a tiny Python callable, **not** radio or accelerator inference. |

```mermaid
sequenceDiagram
  autonumber
  actor U as Researcher
  participant CLI as run_benchmark_table.py
  participant M as sim.metrics
  participant FS as results/

  U->>CLI: make benchmark-toy / --toy --seed 42
  CLI->>M: toy_beam_gains(seed)
  M-->>CLI: list of synthetic dB gains
  CLI->>M: oracle_beam_index(gains)
  CLI->>CLI: predict_top_k (deliberately swaps rank-1/rank-2)
  CLI->>M: top_k_accuracy / db_loss_vs_oracle / spectral_efficiency_loss
  CLI->>M: inference_latency_ms(_noop)
  Note over M: HOST_PROCESS_TIMING of a no-op wrapper<br/>does not prove sub-ms edge inference
  M-->>CLI: metric dict + evidence_class SYNTHETIC_SIM
  CLI->>FS: benchmark_table.md / e2e/benchmark_metrics.json
  FS-->>U: cite those files, not README folklore tables
```

LSTM `forward` is **not** on this path. Optional tracker training is `python sim/models/lstm_beam_tracker.py` when torch is installed.

[← Current index](index.md)
