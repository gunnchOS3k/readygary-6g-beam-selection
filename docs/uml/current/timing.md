# Timing — what is actually measured (current)

| | |
|---|---|
| **Status** | **Current** |
| **Purpose** | Separate host Python timers from RF / accelerator latency. |

```mermaid
flowchart TB
  subgraph host["HOST_PROCESS_TIMING — shipped"]
    T1["sim.metrics.inference_latency_ms\ntime.perf_counter around a callable"]
    T2["ExhaustiveBeamSearch.search_optimal_beams\ntime.time around DFT codebook search"]
    T3["HierarchicalBeamSearch coarse+fine\ntime.time around reduced search"]
    T4["scripts/run_timing_harness.py\nwrites results/timing_harness.json"]
  end

  subgraph not["Not measured in this repo"]
    N1[gNB scheduling slot time]
    N2[ONNX / TensorRT engine]
    N3[Device under test / Pixel / SDR]
    N4[Sub-ms URLLC bound]
  end

  T1 --> OUT[results/timing_harness.json]
  T2 --> OUT
  T3 --> OUT
  OUT -.->|does not imply| N4
```

Classification table: [`docs/LATENCY_EVIDENCE.md`](../../LATENCY_EVIDENCE.md).

[← Current index](index.md)
