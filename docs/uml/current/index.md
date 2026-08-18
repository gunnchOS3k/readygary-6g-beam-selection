# Current-state UML index

**Lane:** shipped Python in this checkout. **Not** hardware beam management, **not** measured FR2/FR3 RF.

**Evidence wording (authoritative):** `SYNTHETIC_SIM` for toy/TDL tables; `HOST_PROCESS_TIMING` for `time.perf_counter` / `time.time` around Python; sub-ms **unproven**.

**28 GHz:** FR2 mmWave (`ChannelConfig.carrier_freq = 28e9`) — **not** Sub-6.

| Perspective | Page | Backed by |
|-------------|------|-----------|
| **Component** | [component.md](component.md) | `sim/`, `scripts/run_benchmark_table.py`, `src/readygary_tool_adapters/` |
| **Class (beam / model)** | [class_beam_model.md](class_beam_model.md) | `ExhaustiveBeamSearch`, `HierarchicalBeamSearch`, `LSTMBeamTracker`, `TDLChannelGenerator`, `sim/metrics.py` |
| **Sequence (inference)** | [sequence_inference.md](sequence_inference.md) | `scripts/run_benchmark_table.py --toy` |
| **State (beam tracking)** | [state_beam_tracking.md](state_beam_tracking.md) | `sim/models/lstm_beam_tracker.py` `BeamTracker` buffer + LSTM forward |
| **Timing** | [timing.md](timing.md) | `sim/metrics.inference_latency_ms`, `scripts/run_timing_harness.py` |
| **Deployment (edge)** | [deployment.md](deployment.md) | Laptop Python, GitHub Actions `latex.yml` + `ci.yml`; `deploy/` is **empty** |

[Traceability](../traceability_matrix.md) · [UML README](../README.md) · [Future](../future/index.md) · [Legacy](../legacy/index.md)
