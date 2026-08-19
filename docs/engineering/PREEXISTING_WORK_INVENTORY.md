# Preexisting work inventory — ReadyGary Sub-6 / FR1 engineering wave

**Branch start:** `origin/main`  
**CURRENT_MAIN_SHA:** `82d3dbe009658873114221d956e380921a06185d`  
**Merge:** PR #25 (`cursor/supervisor-ready-portfolio-release-001`) already on main. This wave does **not** continue that branch.  
**Inventory date:** 2026-08-18  
**Rule:** classify before writing product code. Do not overwrite working FR2 implementations with empty scaffolds.  
**Evidence language:** IMPLEMENTED_TODAY | VALIDATED_DIGITAL | ACTIVE_ENGINEERING | DEVICE_MEASURED | LAB_MEASURED | BLOCKED_GPU | BLOCKED_EXTERNAL.  
**Hard firewall:** 28 GHz is FR2/mmWave (3GPP TS 38.101-2). Never Sub-6.

## How this inventory was produced

Read-only audit of `82d3dbe` plus sibling hardware (`gunnchos-hardware-industrial-design`) and NVIDIA field-kit conventions (`gunnchos-7gc-ai-ran-field-kit` when present). Modem bands are taken from Quectel RM520N Series Specification V1.4 (public) and 3GPP TS 38.101-1 / 38.101-2 / 38.104; they are **not** invented.

## Classification key

| Label | Meaning |
|---|---|
| ALREADY_IMPLEMENTED | Working code on main; deepen, do not replace with a stub |
| PARTIALLY_IMPLEMENTED | Real code exists but is FR2-only, heuristic, or incomplete vs this wave |
| MISSING | Not present on main |
| STALE_DOCUMENTATION | Docs contradict code or still say empty/future where code exists |
| BLOCKED_EXTERNAL | Needs owner membership, licensed scene, or third-party install |
| BLOCKED_GPU | Needs CUDA GPU on this host |

## Proposed features vs main

| ID | Feature | Classification | Evidence on `82d3dbe` | Sub-6 wave action |
|---|---|---|---|---|
| F0 | Inventory of preexisting work | MISSING | No `docs/engineering/` packet | This file |
| F1 | Machine-readable NR band profiles (band ID, fc, range, BW, SCS, duplex, source, region) | MISSING | Carrier is a YAML label `frequency_hz: 28000000000` / `band: FR2` in `paper/artifacts/experiment_protocol.yaml`. No `configs/bands/` | Add SUB6 vs FR2 families; document FR1-not-below-6 GHz (n96) as non-Sub-6 |
| F2 | True below-6 GHz NR path **and** existing FR2 path | PARTIALLY_IMPLEMENTED | FR2 28 GHz TDL/CDL/synthetic + Paper II programme is real. No Sub-6 generator. `generate_slot` reads `frequency_hz` then discards it (`_ = freq`) | Keep FR2 protocol loader strict. Parameterize fc in channel phase/path-loss. Never relabel FR2 draws as Sub-6 |
| F3 | Sub-6 channel via existing abstraction (synthetic, 3GPP TDL/CDL, Sionna, Sionna RT, AODT) | PARTIALLY_IMPLEMENTED | `sim/channels/{synthetic,tdl_cdl,sionna_rt,aodt}.py` exist. TDL-A/C and CDL-A tables are present. `superposition_from_paths` hardcodes `28e9` in the carrier phase. Sionna RT / AODT import-or-fallback to synthetic with no scene | Parameterize fc, delay spread, path loss, shadowing, penetration, Doppler, geometry. Open numpy path must run without NVIDIA |
| F4 | Sub-6 access/spatial strategy (sector/cell, MIMO codebook, CSI ranking, HO, multi-BS) vs FR2 analog beam management | MISSING | FR2 DFT codebook search, hierarchical/window, multi-BS heuristic GNN. No Type-I CSI / cell-selection path | Common `RadioDecisionContext` → `RadioDecision`. Do not pretend Sub-6 == FR2 beam sweep |
| F5 | Dual-band continuity controller | MISSING | Paper II policies are FR2-only (`twin_informed`, `information_equivalent`, …) | SUB6_ONLY, FR2_ONLY, STATIC_PREFERRED, SIGNAL_POLICY, SERVICE_AWARE_POLICY, DIGITAL_TWIN_POLICY, OPTIMIZATION_REFERENCE, LEARNED_POLICY |
| F6 | Cross-band failure experiments | PARTIALLY_IMPLEMENTED | FR2 `high_blockage` / `high_mobility` domain-shift families only | FR2 blockage, Sub-6 congestion, cell-edge, mobility, indoor, backhaul, compute unavailability, load spikes, simultaneous disruption, recovery |
| F7 | gunnchOS device classes + workload coupling | MISSING | No device/workload module in this repo. Sibling OS/hardware: Student 14.5 / Handheld Hybrid / DS-XL / Rings; WWAN = Quectel **RM520N-GL** Rel-16 Sub-6, **not** FR2, **not** 6G, **not** NTN | Couple modeled profiles. No fabricated measured RF/power |
| F8 | GNN | PARTIALLY_IMPLEMENTED | `sim/models/gnn_multi_bs.py` is **heuristic message-passing** (average neighbor DFT bins + window refine). Not a trained graph model. Ablation `gnn_no_message` exists | Honest audit. Keep heuristic as baseline. Add trainable numpy graph scorer |
| F9 | RL | PARTIALLY_IMPLEMENTED | `adaptive_constrained_rl` is **tabular Q** over beam pairs with a probe budget. `adaptive_bandit` is ε-greedy. LSTM tracker exists but is a separate torch demo, not wired to Paper II | Keep tabular RL as baseline. Add sequential policy (REINFORCE / LSTM) for band stay/switch |
| F10 | NVIDIA 6G Developer adapters (NumPy, PyTorch, Sionna, Sionna RT, AODT, Aerial/pyAerial, ONNX, TensorRT) | PARTIALLY_IMPLEMENTED | NumPy path executed. ONNX export **code** exists (`deploy/onnx_export.py`) but CI does not install `onnx`. TensorRT is probe-only (`BLOCKED_GPU`). Aerial/AODT/Sionna fail closed. Field-kit convention: UNAVAILABLE_FAIL_CLOSED, no credentials in git | Deepen adapters; classify each; owner packet for member login |
| F11 | Deploy service from PR #25 | ALREADY_IMPLEMENTED | HTTP `/health` `/metadata` `/metrics` `/infer` `/benchmark`; FastAPI if installed; stdlib otherwise; Docker; npz scorer; gRPC optional | Keep capabilities. Add cross-band APIs + band metadata. Fix stale empty/future docs |
| F12 | ONNX export → validate → ORT → equivalence | PARTIALLY_IMPLEMENTED | ONNX graph build + `onnx.checker` when `onnx` importable. No ORT session, no numerical equivalence gate | Add ORT path; never fabricate latency |
| F13 | TensorRT build/run/warmup/p50/p95/p99 | PARTIALLY_IMPLEMENTED | `deploy/tensorrt_compile.py` records BLOCKED_GPU and does not build an engine even if TRT+CUDA were present (`ACTIVE_ENGINEERING` note) | Complete builder code. Execution remains BLOCKED_GPU on this host |
| F14 | Paper II SUB6 / FR2 / DUAL_BAND expansion | PARTIALLY_IMPLEMENTED | Frozen FR2 protocol + held-out JSON/tables exist (`results/experiments/rq2_beam_selection_fr2_*.json`). No Sub-6 or dual-band tables | New protocols. Do not write conclusions before runs. Not a fourth dissertation paper |
| F15 | Evidence language / 28 GHz firewall | ALREADY_IMPLEMENTED | README, protocol, tests, and `paper/CLAIMS_TO_EVIDENCE.md` already forbid “28 GHz is Sub-6” | Extend firewall to band profiles + CI grep/schema |
| F16 | `make sub6-reproduce` / `dualband-reproduce` / Paper II dual-band | MISSING | `make reproduce`, `paper-reproduce`, `additive` cover FR2 only | Add targets + CI jobs |
| F17 | CI: band schema, claim firewall, Sub-6 channel, FR2 regression, dual-band, GNN/RL, ONNX, deploy, Paper II, README consistency | PARTIALLY_IMPLEMENTED | `.github/workflows/ci.yml` runs `make reproduce` + file presence. No band schema, no Sub-6, no ONNX dep | Expand; keep FR2 tests green |

## Channel / backend status on main (before this wave)

| Backend | Code | Open path | Classification going in |
|---|---|---|---|
| NumPy synthetic TDL ULA | `sim/channels/synthetic.py`, `sim/experiments/digital_programme.py` | yes | ALREADY_IMPLEMENTED (FR2). Sub-6 parameterization MISSING |
| 3GPP TDL-A / TDL-C / CDL-A structure | `sim/channels/tdl_cdl.py` (TR 38.901 table numbers) | yes | PARTIALLY_IMPLEMENTED — tables are real; carrier hardcoded 28 GHz |
| Sionna PHY | `src/readygary_tool_adapters/sionna_channel_adapter.py` writes a config stub | no import | SCAFFOLD_ONLY / BLOCKED_EXTERNAL |
| Sionna RT | `sim/channels/sionna_rt.py` | import-or-synthetic fallback | SCAFFOLD_ONLY / BLOCKED_EXTERNAL (no scene) |
| AODT | `sim/channels/aodt.py` | import-or-synthetic fallback | SCAFFOLD_ONLY / BLOCKED_EXTERNAL |
| Aerial / pyAerial | `src/readygary_tool_adapters/aerial_adapter.py` | fail closed | SCAFFOLD_ONLY / BLOCKED_MEMBER_ACCESS |
| ONNX | `deploy/onnx_export.py` | optional dep | PARTIALLY_IMPLEMENTED |
| TensorRT | `deploy/tensorrt_compile.py` | no GPU | BLOCKED_GPU |
| PyTorch LSTM tracker | `sim/models/lstm_beam_tracker.py` | not in default CI | PARTIALLY_IMPLEMENTED (unwired to Paper II) |

## Hardware / modem (sibling repo — do not invent bands)

Source: `gunnchos-hardware-industrial-design/docs/full_product_family/MODEM_ARCHITECTURE_FREEZE.md` and `MODEM_RM520N_GL_PUBLIC_VERIFY.md`.

| Claim | Status |
|---|---|
| WWAN MPN | Quectel **RM520N-GL** M.2 3052 |
| Radio | 5G NR **Sub-6 (FR1)** Rel-16 SA/NSA + LTE. **Not** 6G. **Not** NTN. **Not** FR2 mmWave SKU |
| Student 14.5 | RM520N-GL required for fleet SKU (Wi-Fi-only education SKU allowed) |
| DS-XL Coder | Shared Student WWAN bay |
| Handheld Hybrid | Optional M.2 if thermal allows; default Wi-Fi-first |
| Rings | No cellular |
| Public NR bands (Quectel RM520N Series Spec V1.4) | n1/2/3/5/7/8/12/13/14/18/20/25/26/28/29/30/38/40/41/48/66/70/71/75/76/77/78/79 |
| FR1 bands **not** on this BOM (example) | n96 (5925–7125 MHz) is FR1 and **not** entirely below 6 GHz — must not be called Sub-6 |

### Primary Sub-6 profile (chosen after the checks above)

**n77, fc = 3750 MHz, 100 MHz, SCS 30 kHz, TDD.**

| Check | Result |
|---|---|
| 3GPP operating band | TS 38.101-1 n77: 3300–4200 MHz TDD, FR1 |
| True below 6 GHz | 3.75 GHz < 6 GHz (yes) |
| Modem BOM | RM520N-GL lists n77 |
| Gary / US | C-band 3700–3980 MHz is the US mid-band 5G layer (Verizon/AT&T class). Gary, IN is in that footprint as a research scenario, **not** a measured drive test |
| Distinct from FR2 | Path loss, Doppler, penetration, antenna count, and access method differ; results must not reuse 28 GHz SNR tables |

Supporting true-below-6 GHz profiles on the same modem: **n41** (2496–2690 MHz TDD, T-Mobile 2.5 GHz US) and **n71** (617–652 / 663–698 MHz FDD, T-Mobile 600 MHz coverage). FR2 control: existing **n257** 28 GHz.

## GNN / RL audit (skeptical)

| Arm | Honest class | Why |
|---|---|---|
| `gnn_multi_bs` | HEURISTIC_MESSAGE_PASSING | Averages neighbor beam indices, then window-searches. No learned weights, no backprop, no graph dataset |
| `gnn_no_message` | ABLATION | Local hierarchical only |
| `independent_multi_bs` | BASELINE | Per-BS hierarchical |
| `adaptive_constrained_rl` | TABULAR_Q | Incremental mean of (SNR_dB − switch penalty) over probed pairs. Not sequential credit assignment |
| `adaptive_bandit` | EPSILON_GREEDY_BANDIT | Probe budget + exploit argmax Q |
| `LSTMBeamTracker` | TORCH_SEQ_MODEL_UNWIRED | Real LSTM code; not used by Paper II digital programme or CI `make reproduce` |

Simple winning heuristic is valid. Do not relabel the current GNN as a trained GNN.

## Deploy docs vs code

| Doc claim | Code on main | Verdict |
|---|---|---|
| HTTP scorer endpoints exist | `deploy/server.py` implements them | Docs mostly match; keep |
| ONNX always written | Only if `onnx` imports | STALE if README implies ONNX file always exists |
| TensorRT engine | Never built; status JSON only | Docs already say BLOCKED_GPU — keep |
| “Docker edge service scaffold” in older README vs working Dockerfile | `deploy/Dockerfile` exists from #25 | STALE_DOCUMENTATION where README still says scaffold-only |
| Band field hardcoded `"FR2"` | `health_payload`, ONNX metadata, npz | Must become profile metadata, not a relabel of 28 GHz as Sub-6 |

## What this wave must not do

- Relabel 28 GHz draws as Sub-6
- Copy FR2 SNR/switch tables into Sub-6 JSON
- Claim Sionna RT / AODT / Aerial / TensorRT executed without imports + GPU
- Claim DEVICE_MEASURED or LAB_MEASURED RF/power
- Claim sub-ms inference
- Overwrite `sim/experiments/digital_programme.py` FR2 protocol checks
- Merge, force-push, hard reset, or `git clean -fd`
