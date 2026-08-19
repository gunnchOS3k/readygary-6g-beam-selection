# What Is Real Today

- sim/ baselines, GNN multi-BS **heuristic** + trainable numpy graph scorer, adaptive trackers, sequential dual-band REINFORCE
- pluggable channels: synthetic, 3GPP TDL/CDL structure (fc parameterized), **Sub-6 UMa/O2I/Doppler** backends, Sionna/AODT adapters (optional, fail closed)
- Dual-band continuity controller (SUB6_ONLY … LEARNED_POLICY)
- Band profiles in `configs/bands/` (n77 primary Sub-6, n257 FR2, n96 FR1-not-below-6 GHz)
- `deploy/` HTTP scorer + `/bands` `/decide` + Docker + ONNX-when-available + ORT equivalence when `onnxruntime` is installed
- LaTeX paper + CI
- `make smoke` / `make reproduce` / `make sub6-reproduce` / `make dualband-reproduce` / `make paper-reproduce`
- Docker edge service (`deploy/Dockerfile`) — working HTTP path, not an empty scaffold

28 GHz is FR2 mmWave, **never Sub-6**. Twin/sim ≠ OTA. Sub-ms inference is TARGET. TensorRT GPU execution is BLOCKED_GPU on this host unless an engine is actually built.

Smoke: `make smoke`

Smoke: `make smoke`
