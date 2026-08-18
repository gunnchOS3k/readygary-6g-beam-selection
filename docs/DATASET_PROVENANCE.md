# Dataset provenance

| Source | Path / generator | Evidence class | Notes |
|--------|------------------|----------------|-------|
| Toy beam gains | `sim/metrics.toy_beam_gains` | `SYNTHETIC_SIM` | Uniform random dB in [-15, 0], seeded |
| TDL channels | `scripts/generate_dataset.py` `TDLChannelGenerator` | `SYNTHETIC_SIM` | Random paths, FSPL + log-normal shadowing |
| Carrier | `ChannelConfig.carrier_freq = 28e9` | label only | **FR2 mmWave**, not Sub-6 |
| DeepMIMO | `src/readygary_tool_adapters/deepmimo_adapter.py` | config stub | `is_data_available()` is False unless local data |
| Sionna | `src/readygary_tool_adapters/sionna_channel_adapter.py` | config stub | Not executed in `make benchmark-toy` |
| Campus radio YAML | `configs/campus_radio_profiles/*.yaml` | scenario labels | Not RF captures |

No competition IQ. No PII. Do not relabel pickle dumps from the TDL generator as measured mmWave.
