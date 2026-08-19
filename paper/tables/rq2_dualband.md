# rq2_dualband (SYNTHETIC_SIM, min-useful service, n77 + n257)

28 GHz remains FR2. Sub-6 is n77 3.75 GHz. Not OTA. Negative results valid.

| policy | failure | device | workload | min-useful mean [95% CI] | switch | interrupt_ms | outage |
|---|---|---|---|---|---|---|---|
| `SUB6_ONLY` | `nominal` | `student_14_5` | `lecture_video` | 1.0000 [1.0000, 1.0000] | 0.0000 | 0.0000 | 0.0000 |
| `SUB6_ONLY` | `fr2_blockage` | `student_14_5` | `lecture_video` | 1.0000 [1.0000, 1.0000] | 0.0000 | 0.0000 | 0.0000 |
| `SUB6_ONLY` | `sub6_congestion` | `student_14_5` | `lecture_video` | 0.0000 [0.0000, 0.0000] | 0.0000 | 0.0000 | 1.0000 |
| `SUB6_ONLY` | `cell_edge` | `student_14_5` | `lecture_video` | 0.0000 [0.0000, 0.0000] | 0.0000 | 0.0000 | 1.0000 |
| `SUB6_ONLY` | `mobility` | `student_14_5` | `lecture_video` | 1.0000 [1.0000, 1.0000] | 0.0000 | 0.0000 | 0.0000 |
| `SUB6_ONLY` | `indoor` | `student_14_5` | `lecture_video` | 1.0000 [1.0000, 1.0000] | 0.0000 | 0.0000 | 0.0000 |
| `SUB6_ONLY` | `backhaul` | `student_14_5` | `lecture_video` | 1.0000 [1.0000, 1.0000] | 0.0000 | 0.0000 | 0.0000 |
| `SUB6_ONLY` | `compute_unavailability` | `student_14_5` | `lecture_video` | 1.0000 [1.0000, 1.0000] | 0.0000 | 0.0000 | 0.0000 |
| `SUB6_ONLY` | `load_spike` | `student_14_5` | `lecture_video` | 1.0000 [1.0000, 1.0000] | 0.0000 | 0.0000 | 0.0000 |
| `SUB6_ONLY` | `simultaneous` | `student_14_5` | `lecture_video` | 0.0000 [0.0000, 0.0000] | 0.0000 | 0.0000 | 1.0000 |
| `SUB6_ONLY` | `recovery` | `student_14_5` | `lecture_video` | 1.0000 [1.0000, 1.0000] | 0.0000 | 0.0000 | 0.0000 |
| `FR2_ONLY` | `nominal` | `student_14_5` | `lecture_video` | 1.0000 [1.0000, 1.0000] | 0.0000 | 1.0000 | 0.0000 |
| `FR2_ONLY` | `fr2_blockage` | `student_14_5` | `lecture_video` | 0.0000 [0.0000, 0.0000] | 0.0000 | 8.0000 | 1.0000 |
| `FR2_ONLY` | `sub6_congestion` | `student_14_5` | `lecture_video` | 1.0000 [1.0000, 1.0000] | 0.0000 | 1.0000 | 0.0000 |
| `FR2_ONLY` | `cell_edge` | `student_14_5` | `lecture_video` | 0.0000 [0.0000, 0.0000] | 0.0000 | 1.0000 | 0.0000 |
| `FR2_ONLY` | `mobility` | `student_14_5` | `lecture_video` | 1.0000 [1.0000, 1.0000] | 0.0000 | 1.0000 | 0.0000 |
| `FR2_ONLY` | `indoor` | `student_14_5` | `lecture_video` | 0.0000 [0.0000, 0.0000] | 0.0000 | 8.0000 | 1.0000 |
| `FR2_ONLY` | `backhaul` | `student_14_5` | `lecture_video` | 1.0000 [1.0000, 1.0000] | 0.0000 | 1.0000 | 0.0000 |
| `FR2_ONLY` | `compute_unavailability` | `student_14_5` | `lecture_video` | 1.0000 [1.0000, 1.0000] | 0.0000 | 1.0000 | 0.0000 |
| `FR2_ONLY` | `load_spike` | `student_14_5` | `lecture_video` | 1.0000 [1.0000, 1.0000] | 0.0000 | 1.0000 | 0.0000 |
| `FR2_ONLY` | `simultaneous` | `student_14_5` | `lecture_video` | 0.0000 [0.0000, 0.0000] | 0.0000 | 8.0000 | 1.0000 |
| `FR2_ONLY` | `recovery` | `student_14_5` | `lecture_video` | 1.0000 [1.0000, 1.0000] | 0.0000 | 1.0000 | 0.0000 |
| `STATIC_PREFERRED` | `nominal` | `student_14_5` | `lecture_video` | 1.0000 [1.0000, 1.0000] | 0.0000 | 0.0000 | 0.0000 |
| `STATIC_PREFERRED` | `fr2_blockage` | `student_14_5` | `lecture_video` | 1.0000 [1.0000, 1.0000] | 0.0000 | 0.0000 | 0.0000 |
| `STATIC_PREFERRED` | `sub6_congestion` | `student_14_5` | `lecture_video` | 0.0000 [0.0000, 0.0000] | 0.0000 | 0.0000 | 1.0000 |
| `STATIC_PREFERRED` | `cell_edge` | `student_14_5` | `lecture_video` | 0.0000 [0.0000, 0.0000] | 0.0000 | 0.0000 | 1.0000 |
| `STATIC_PREFERRED` | `mobility` | `student_14_5` | `lecture_video` | 1.0000 [1.0000, 1.0000] | 0.0000 | 0.0000 | 0.0000 |
| `STATIC_PREFERRED` | `indoor` | `student_14_5` | `lecture_video` | 1.0000 [1.0000, 1.0000] | 0.0000 | 0.0000 | 0.0000 |
| `STATIC_PREFERRED` | `backhaul` | `student_14_5` | `lecture_video` | 1.0000 [1.0000, 1.0000] | 0.0000 | 0.0000 | 0.0000 |
| `STATIC_PREFERRED` | `compute_unavailability` | `student_14_5` | `lecture_video` | 1.0000 [1.0000, 1.0000] | 0.0000 | 0.0000 | 0.0000 |
| `STATIC_PREFERRED` | `load_spike` | `student_14_5` | `lecture_video` | 1.0000 [1.0000, 1.0000] | 0.0000 | 0.0000 | 0.0000 |
| `STATIC_PREFERRED` | `simultaneous` | `student_14_5` | `lecture_video` | 0.0000 [0.0000, 0.0000] | 0.0000 | 0.0000 | 1.0000 |
| `STATIC_PREFERRED` | `recovery` | `student_14_5` | `lecture_video` | 1.0000 [1.0000, 1.0000] | 0.0000 | 0.0000 | 0.0000 |
| `SIGNAL_POLICY` | `nominal` | `student_14_5` | `lecture_video` | 1.0000 [1.0000, 1.0000] | 0.3750 | 30.3333 | 0.0000 |
| `SIGNAL_POLICY` | `fr2_blockage` | `student_14_5` | `lecture_video` | 1.0000 [1.0000, 1.0000] | 0.0000 | 0.0000 | 0.0000 |
| `SIGNAL_POLICY` | `sub6_congestion` | `student_14_5` | `lecture_video` | 1.0000 [1.0000, 1.0000] | 0.0000 | 1.0000 | 0.0000 |
| `SIGNAL_POLICY` | `cell_edge` | `student_14_5` | `lecture_video` | 0.0000 [0.0000, 0.0000] | 0.0000 | 0.0000 | 1.0000 |
| `SIGNAL_POLICY` | `mobility` | `student_14_5` | `lecture_video` | 1.0000 [1.0000, 1.0000] | 0.0000 | 0.0000 | 0.0000 |
| `SIGNAL_POLICY` | `indoor` | `student_14_5` | `lecture_video` | 1.0000 [1.0000, 1.0000] | 0.0000 | 0.0000 | 0.0000 |
| `SIGNAL_POLICY` | `backhaul` | `student_14_5` | `lecture_video` | 1.0000 [1.0000, 1.0000] | 0.3750 | 30.3333 | 0.0000 |
| `SIGNAL_POLICY` | `compute_unavailability` | `student_14_5` | `lecture_video` | 1.0000 [1.0000, 1.0000] | 0.3750 | 30.3333 | 0.0000 |
| `SIGNAL_POLICY` | `load_spike` | `student_14_5` | `lecture_video` | 1.0000 [1.0000, 1.0000] | 0.0000 | 1.0000 | 0.0000 |
| `SIGNAL_POLICY` | `simultaneous` | `student_14_5` | `lecture_video` | 0.0000 [0.0000, 0.0000] | 0.0000 | 0.0000 | 1.0000 |
| `SIGNAL_POLICY` | `recovery` | `student_14_5` | `lecture_video` | 1.0000 [1.0000, 1.0000] | 0.0000 | 0.0000 | 0.0000 |
| `SERVICE_AWARE_POLICY` | `nominal` | `student_14_5` | `lecture_video` | 1.0000 [1.0000, 1.0000] | 0.0000 | 0.0000 | 0.0000 |
| `SERVICE_AWARE_POLICY` | `fr2_blockage` | `student_14_5` | `lecture_video` | 1.0000 [1.0000, 1.0000] | 0.0000 | 0.0000 | 0.0000 |
| `SERVICE_AWARE_POLICY` | `sub6_congestion` | `student_14_5` | `lecture_video` | 1.0000 [1.0000, 1.0000] | 0.0000 | 1.0000 | 0.0000 |
| `SERVICE_AWARE_POLICY` | `cell_edge` | `student_14_5` | `lecture_video` | 0.0000 [0.0000, 0.0000] | 0.0000 | 0.0000 | 1.0000 |
| `SERVICE_AWARE_POLICY` | `mobility` | `student_14_5` | `lecture_video` | 1.0000 [1.0000, 1.0000] | 0.0000 | 0.0000 | 0.0000 |
| `SERVICE_AWARE_POLICY` | `indoor` | `student_14_5` | `lecture_video` | 1.0000 [1.0000, 1.0000] | 0.0000 | 0.0000 | 0.0000 |
| `SERVICE_AWARE_POLICY` | `backhaul` | `student_14_5` | `lecture_video` | 1.0000 [1.0000, 1.0000] | 0.0000 | 0.0000 | 0.0000 |
| `SERVICE_AWARE_POLICY` | `compute_unavailability` | `student_14_5` | `lecture_video` | 1.0000 [1.0000, 1.0000] | 0.0000 | 0.0000 | 0.0000 |
| `SERVICE_AWARE_POLICY` | `load_spike` | `student_14_5` | `lecture_video` | 1.0000 [1.0000, 1.0000] | 0.0000 | 0.0000 | 0.0000 |
| `SERVICE_AWARE_POLICY` | `simultaneous` | `student_14_5` | `lecture_video` | 0.0000 [0.0000, 0.0000] | 0.0000 | 0.0000 | 1.0000 |
| `SERVICE_AWARE_POLICY` | `recovery` | `student_14_5` | `lecture_video` | 1.0000 [1.0000, 1.0000] | 0.0000 | 0.0000 | 0.0000 |
| `DIGITAL_TWIN_POLICY` | `nominal` | `student_14_5` | `lecture_video` | 1.0000 [1.0000, 1.0000] | 0.0000 | 1.0000 | 0.0000 |
| `DIGITAL_TWIN_POLICY` | `fr2_blockage` | `student_14_5` | `lecture_video` | 1.0000 [1.0000, 1.0000] | 0.0000 | 0.0000 | 0.0000 |
| `DIGITAL_TWIN_POLICY` | `sub6_congestion` | `student_14_5` | `lecture_video` | 1.0000 [1.0000, 1.0000] | 0.0000 | 1.0000 | 0.0000 |
| `DIGITAL_TWIN_POLICY` | `cell_edge` | `student_14_5` | `lecture_video` | 0.0000 [0.0000, 0.0000] | 0.0000 | 1.0000 | 0.0000 |
| `DIGITAL_TWIN_POLICY` | `mobility` | `student_14_5` | `lecture_video` | 1.0000 [1.0000, 1.0000] | 0.0000 | 1.0000 | 0.0000 |
| `DIGITAL_TWIN_POLICY` | `indoor` | `student_14_5` | `lecture_video` | 1.0000 [1.0000, 1.0000] | 0.0000 | 0.0000 | 0.0000 |
| `DIGITAL_TWIN_POLICY` | `backhaul` | `student_14_5` | `lecture_video` | 1.0000 [1.0000, 1.0000] | 0.0000 | 1.0000 | 0.0000 |
| `DIGITAL_TWIN_POLICY` | `compute_unavailability` | `student_14_5` | `lecture_video` | 1.0000 [1.0000, 1.0000] | 0.0000 | 1.0000 | 0.0000 |
| `DIGITAL_TWIN_POLICY` | `load_spike` | `student_14_5` | `lecture_video` | 1.0000 [1.0000, 1.0000] | 0.0000 | 1.0000 | 0.0000 |
| `DIGITAL_TWIN_POLICY` | `simultaneous` | `student_14_5` | `lecture_video` | 0.0000 [0.0000, 0.0000] | 0.0000 | 0.0000 | 1.0000 |
| `DIGITAL_TWIN_POLICY` | `recovery` | `student_14_5` | `lecture_video` | 1.0000 [1.0000, 1.0000] | 0.0000 | 1.0000 | 0.0000 |
| `OPTIMIZATION_REFERENCE` | `nominal` | `student_14_5` | `lecture_video` | 1.0000 [1.0000, 1.0000] | 0.0000 | 0.0000 | 0.0000 |
| `OPTIMIZATION_REFERENCE` | `fr2_blockage` | `student_14_5` | `lecture_video` | 1.0000 [1.0000, 1.0000] | 0.0000 | 0.0000 | 0.0000 |
| `OPTIMIZATION_REFERENCE` | `sub6_congestion` | `student_14_5` | `lecture_video` | 1.0000 [1.0000, 1.0000] | 0.0000 | 1.0000 | 0.0000 |
| `OPTIMIZATION_REFERENCE` | `cell_edge` | `student_14_5` | `lecture_video` | 0.0000 [0.0000, 0.0000] | 0.0000 | 0.0000 | 1.0000 |
| `OPTIMIZATION_REFERENCE` | `mobility` | `student_14_5` | `lecture_video` | 1.0000 [1.0000, 1.0000] | 0.0000 | 0.0000 | 0.0000 |
| `OPTIMIZATION_REFERENCE` | `indoor` | `student_14_5` | `lecture_video` | 1.0000 [1.0000, 1.0000] | 0.0000 | 0.0000 | 0.0000 |
| `OPTIMIZATION_REFERENCE` | `backhaul` | `student_14_5` | `lecture_video` | 1.0000 [1.0000, 1.0000] | 0.0000 | 0.0000 | 0.0000 |
| `OPTIMIZATION_REFERENCE` | `compute_unavailability` | `student_14_5` | `lecture_video` | 1.0000 [1.0000, 1.0000] | 0.0000 | 0.0000 | 0.0000 |
| `OPTIMIZATION_REFERENCE` | `load_spike` | `student_14_5` | `lecture_video` | 1.0000 [1.0000, 1.0000] | 0.0000 | 0.0000 | 0.0000 |
| `OPTIMIZATION_REFERENCE` | `simultaneous` | `student_14_5` | `lecture_video` | 0.0000 [0.0000, 0.0000] | 0.0000 | 0.0000 | 1.0000 |
| `OPTIMIZATION_REFERENCE` | `recovery` | `student_14_5` | `lecture_video` | 1.0000 [1.0000, 1.0000] | 0.0000 | 0.0000 | 0.0000 |
| `LEARNED_POLICY` | `nominal` | `student_14_5` | `lecture_video` | 1.0000 [1.0000, 1.0000] | 0.0000 | 0.0000 | 0.0000 |
| `LEARNED_POLICY` | `fr2_blockage` | `student_14_5` | `lecture_video` | 1.0000 [1.0000, 1.0000] | 0.0000 | 0.0000 | 0.0000 |
| `LEARNED_POLICY` | `sub6_congestion` | `student_14_5` | `lecture_video` | 0.8333 [0.6540, 1.0126] | 0.2917 | 24.1667 | 0.1667 |
| `LEARNED_POLICY` | `cell_edge` | `student_14_5` | `lecture_video` | 0.0000 [0.0000, 0.0000] | 0.0000 | 0.0000 | 1.0000 |
| `LEARNED_POLICY` | `mobility` | `student_14_5` | `lecture_video` | 1.0000 [1.0000, 1.0000] | 0.0000 | 0.0000 | 0.0000 |
| `LEARNED_POLICY` | `indoor` | `student_14_5` | `lecture_video` | 1.0000 [1.0000, 1.0000] | 0.0000 | 0.0000 | 0.0000 |
| `LEARNED_POLICY` | `backhaul` | `student_14_5` | `lecture_video` | 1.0000 [1.0000, 1.0000] | 0.0000 | 0.0000 | 0.0000 |
| `LEARNED_POLICY` | `compute_unavailability` | `student_14_5` | `lecture_video` | 1.0000 [1.0000, 1.0000] | 0.0000 | 0.0000 | 0.0000 |
| `LEARNED_POLICY` | `load_spike` | `student_14_5` | `lecture_video` | 1.0000 [1.0000, 1.0000] | 0.0000 | 0.0000 | 0.0000 |
| `LEARNED_POLICY` | `simultaneous` | `student_14_5` | `lecture_video` | 0.0000 [0.0000, 0.0000] | 0.0000 | 0.0000 | 1.0000 |
| `LEARNED_POLICY` | `recovery` | `student_14_5` | `lecture_video` | 1.0000 [1.0000, 1.0000] | 0.0000 | 0.0000 | 0.0000 |
| `SERVICE_AWARE_POLICY` | `nominal` | `student_14_5` | `lecture_video` | 1.0000 [1.0000, 1.0000] | 0.0000 | 0.0000 | 0.0000 |
| `SERVICE_AWARE_POLICY` | `simultaneous` | `student_14_5` | `lecture_video` | 0.0000 [0.0000, 0.0000] | 0.0000 | 0.0000 | 1.0000 |
| `SERVICE_AWARE_POLICY` | `nominal` | `student_14_5` | `interactive_tutor` | 1.0000 [1.0000, 1.0000] | 0.0000 | 0.0000 | 0.0000 |
| `SERVICE_AWARE_POLICY` | `simultaneous` | `student_14_5` | `interactive_tutor` | 0.0000 [0.0000, 0.0000] | 0.0000 | 0.0000 | 0.0000 |
| `SERVICE_AWARE_POLICY` | `nominal` | `handheld_hybrid` | `lecture_video` | 1.0000 [1.0000, 1.0000] | 0.0000 | 0.0000 | 0.0000 |
| `SERVICE_AWARE_POLICY` | `simultaneous` | `handheld_hybrid` | `lecture_video` | 0.0000 [0.0000, 0.0000] | 0.0000 | 0.0000 | 1.0000 |
| `SERVICE_AWARE_POLICY` | `nominal` | `handheld_hybrid` | `interactive_tutor` | 1.0000 [1.0000, 1.0000] | 0.0000 | 0.0000 | 0.0000 |
| `SERVICE_AWARE_POLICY` | `simultaneous` | `handheld_hybrid` | `interactive_tutor` | 0.0000 [0.0000, 0.0000] | 0.0000 | 0.0000 | 0.0000 |
| `SERVICE_AWARE_POLICY` | `nominal` | `ds_xl_coder` | `lecture_video` | 1.0000 [1.0000, 1.0000] | 0.0000 | 0.0000 | 0.0000 |
| `SERVICE_AWARE_POLICY` | `simultaneous` | `ds_xl_coder` | `lecture_video` | 0.0000 [0.0000, 0.0000] | 0.0000 | 0.0000 | 1.0000 |
| `SERVICE_AWARE_POLICY` | `nominal` | `ds_xl_coder` | `interactive_tutor` | 1.0000 [1.0000, 1.0000] | 0.0000 | 0.0000 | 0.0000 |
| `SERVICE_AWARE_POLICY` | `simultaneous` | `ds_xl_coder` | `interactive_tutor` | 0.0000 [0.0000, 0.0000] | 0.0000 | 0.0000 | 0.0000 |
| `SERVICE_AWARE_POLICY` | `nominal` | `edge_io_rings` | `lecture_video` | 0.0000 [0.0000, 0.0000] | 0.0000 | 0.0000 | 0.0000 |
| `SERVICE_AWARE_POLICY` | `simultaneous` | `edge_io_rings` | `lecture_video` | 0.0000 [0.0000, 0.0000] | 0.0000 | 0.0000 | 0.0000 |
| `SERVICE_AWARE_POLICY` | `nominal` | `edge_io_rings` | `interactive_tutor` | 0.0000 [0.0000, 0.0000] | 0.0000 | 0.0000 | 0.0000 |
| `SERVICE_AWARE_POLICY` | `simultaneous` | `edge_io_rings` | `interactive_tutor` | 0.0000 [0.0000, 0.0000] | 0.0000 | 0.0000 | 0.0000 |

## GNN / RL audit

- heuristic GNN: `HEURISTIC_MESSAGE_PASSING`
- trainable GNN: `TRAINED_GRAPH_MODEL`
- tabular RL: `TABULAR_Q`
- sequential: `REINFORCE_SEQUENTIAL`

Trained GNN SNR dB: 4.9967 (SYNTHETIC_SIM).
