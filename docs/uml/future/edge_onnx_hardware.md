# Future — edge inference and realistic RF

Targets for evidence upgrade. None of these are `SYNTHETIC_SIM` replacements until artifacts exist.

```mermaid
flowchart TB
  DM[DeepMIMO / Sionna RT execution\nnot config-only stubs]
  HW[Hardware timing on named DUT\nmean/p99 with clock source]
  ONX[Frozen ONNX or TensorRT engine\nbatch-1 latency]
  FR3[Optional FR3 upper-mid-band campaign\nseparate from FR2 28 GHz]
  OTA[OTA beam tracking under mobility]

  DM --> HW
  ONX --> HW
  HW --> OTA
  FR3 -.-> OTA
```

Until then, cite `results/` with class `SYNTHETIC_SIM` and latency class `HOST_PROCESS_TIMING`. Sub-ms remains **unproven**.
