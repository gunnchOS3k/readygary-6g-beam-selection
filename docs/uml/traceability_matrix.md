# Traceability — diagrams to source

RQ2 beam-selection artifact. Lanes: current shipped code · adapter stubs · future hardware.

| Diagram element | Source path |
|-----------------|-------------|
| Toy benchmark / top-k / dB / SE | `scripts/run_benchmark_table.py`, `sim/metrics.py` |
| Exhaustive DFT codebook search | `sim/baselines/exhaustive_search.py` `ExhaustiveBeamSearch` |
| Hierarchical coarse→fine | `sim/baselines/hierarchical_search.py` `HierarchicalBeamSearch` |
| LSTM + attention tracker | `sim/models/lstm_beam_tracker.py` `LSTMBeamTracker`, `BeamTracker` |
| Synthetic TDL / 28 GHz FR2 | `scripts/generate_dataset.py` `ChannelConfig.carrier_freq = 28e9` |
| Host timing | `sim/metrics.inference_latency_ms`, `scripts/run_timing_harness.py` |
| Tool adapters (config only) | `src/readygary_tool_adapters/` |
| Campus radio YAML | `configs/campus_radio_profiles/` |
| Tests | `tests/test_metrics.py`, `tests/test_tool_adapters.py` |
| CI | `.github/workflows/ci.yml`, `.github/workflows/latex.yml` |
| Cited tables | `results/e2e/benchmark_summary.md`, `results/benchmark_table.md` |
| Docker / FastAPI | **absent** (`deploy/` empty) — future lane |

[← UML README](README.md)
