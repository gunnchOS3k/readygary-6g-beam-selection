# State machine — LSTM beam tracker (current)

| | |
|---|---|
| **Status** | **Current** code path in `sim/models/lstm_beam_tracker.py` |
| **Purpose** | Temporal CSI buffer → LSTM+attention → codebook index. Trained weights are **not** a CI artifact. |

```mermaid
stateDiagram-v2
  [*] --> Idle
  Idle --> BufferingCSI : BeamTracker.sequence_buffer append
  BufferingCSI --> BufferingCSI : len(buffer) < sequence_length
  BufferingCSI --> ExtractFeatures : len(buffer) >= sequence_length
  ExtractFeatures --> LSTMForward : extract_csi_features
  LSTMForward --> RankBeams : fc2 logits over num_beams
  RankBeams --> CompareOracle : if oracle pair available
  RankBeams --> Idle : inference-only, no oracle
  CompareOracle --> Report : top-k vs exhaustive pair
  Report --> Idle

  note right of LSTMForward
    Requires torch. Not executed by
    make benchmark-toy.
    Evidence remains SYNTHETIC_SIM
    until a frozen checkpoint + dataset
    provenance is cited.
  end note
```

Blockage and mobility in `TDLChannelGenerator` are **parameterized synthetic paths** (Doppler phase increment), not field traces.

[← Current index](index.md)
