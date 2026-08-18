# Class — beam search and tracker models (current)

| | |
|---|---|
| **Status** | **Current** — types and functions in `sim/` and `scripts/generate_dataset.py` |
| **Purpose** | Bind diagram names to source. LSTM training is **optional** (needs torch); the toy benchmark does **not** load a trained checkpoint. |

```mermaid
classDiagram
  direction TB

  class ChannelConfig {
    +num_channels
    +num_tx_ant
    +num_rx_ant
    +carrier_freq  28e9 FR2 mmWave
    +num_paths
  }

  class TDLChannelGenerator {
    +config
    +generate_tdl_channel()
    +_calculate_path_loss()
    +_create_steering_vector()
  }

  class ExhaustiveBeamSearch {
    +num_tx_beams
    +num_rx_beams
    +generate_codebook()
    +compute_snr()
    +search_optimal_beams()
  }

  class HierarchicalBeamSearch {
    +coarse_search()
    +fine_search()
  }

  class BeamTrackingDataset {
    +sequences
    +targets
    +__getitem__()
  }

  class LSTMBeamTracker {
    +lstm
    +attention
    +fc1
    +fc2
    +forward(x)
  }

  class BeamTracker {
    +model
    +sequence_buffer
    +extract_csi_features()
    +prepare_training_data()
  }

  class metrics {
    <<module sim/metrics.py>>
    +top_k_accuracy()
    +db_loss_vs_oracle()
    +spectral_efficiency_loss()
    +inference_latency_ms()
    +toy_beam_gains()
    +oracle_beam_index()
  }

  ChannelConfig --> TDLChannelGenerator
  TDLChannelGenerator ..> ExhaustiveBeamSearch : supplies H
  TDLChannelGenerator ..> HierarchicalBeamSearch : supplies H
  ExhaustiveBeamSearch ..> BeamTracker : oracle pairs for training
  BeamTrackingDataset --> LSTMBeamTracker
  BeamTracker --> LSTMBeamTracker
  metrics ..> ExhaustiveBeamSearch : oracle index on toy gains
```

**Not in this class model:** GNN, RL policy, FastAPI handlers — they are not present as implementations.

[← Current index](index.md)
