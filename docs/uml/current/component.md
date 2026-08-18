# Component — current

| | |
|---|---|
| **Status** | **Current** |
| **Purpose** | Modules that exist and are invoked by `make test` / `make benchmark-toy` / `make timing`. |
| **Does not include** | FastAPI/gRPC server, Docker image, ONNX session — those paths are **future** (`deploy/` is empty). |

```mermaid
flowchart TB
  subgraph cli["Scripts"]
    GEN[scripts/generate_dataset.py]
    BENCH[scripts/run_benchmark_table.py]
    TIME[scripts/run_timing_harness.py]
    ADAPT[src/readygary_tool_adapters/*]
  end

  subgraph sim["sim/"]
    EXH[baselines/exhaustive_search.py]
    HIER[baselines/hierarchical_search.py]
    LSTM[models/lstm_beam_tracker.py]
    MET[metrics.py]
  end

  subgraph out["Cited artifacts"]
    RES[results/e2e/benchmark_summary.md]
    TAB[results/benchmark_table.md]
    TIMR[results/timing_harness.json]
  end

  subgraph test["Checks"]
    PYT[tests/test_metrics.py]
    CI[.github/workflows/ci.yml]
  end

  GEN -->|"synthetic TDL H at 28e9 FR2"| EXH
  GEN --> HIER
  GEN --> LSTM
  BENCH --> MET
  TIME --> MET
  TIME --> EXH
  TIME --> HIER
  MET --> RES
  BENCH --> TAB
  TIME --> TIMR
  ADAPT -->|config / stub exports| CFG[configs/ + results/tool_exports]
  PYT --> MET
  CI --> PYT
```

[← Current index](index.md)
