# Additive FR2 arms (SYNTHETIC_SIM, HOST_PROCESS_TIMING, 28 GHz FR2, never Sub-6)

Source `rq2_beam_selection_fr2_additive_heldout.json`. Twin/sim ≠ OTA. Sub-ms TARGET, not proven.

## Channel backends

| backend | available | evidence | oracle SNR linear mean |
|---|---|---|---|
| `synthetic` | True | SYNTHETIC_SIM | 2.0487 |
| `tdl_a` | True | SYNTHETIC_SIM | 2.0819 |
| `tdl_c` | True | SYNTHETIC_SIM | 3.2609 |
| `cdl_a` | True | SYNTHETIC_SIM | 1.9675 |
| `sionna_rt` | False | SYNTHETIC_SIM | 2.0487 |
| `aodt` | False | SYNTHETIC_SIM | 2.0487 |

## GNN multi-BS

| mode | SNR dB mean [95% CI] | switches |
|---|---|---|
| `independent_multi_bs` | 1.8208 [1.6495, 1.9921] | 14.3250 |
| `gnn_multi_bs` | 1.8689 [1.7168, 2.0209] | 14.4000 |
| `gnn_no_message` | 1.8208 [1.6495, 1.9921] | 14.3250 |

## Adaptive tracking

| policy | SNR dB mean [95% CI] | probes | switches |
|---|---|---|---|
| `adaptive_static` | -3.2156 [-5.7710, -0.6602] | 0.0000 | 0.0000 |
| `adaptive_heuristic` | -6.1180 [-8.9800, -3.2560] | 0.0000 | 3.2750 |
| `adaptive_opt` | 3.7221 [3.4647, 3.9794] | 0.0000 | 4.8000 |
| `adaptive_bandit` | -22.1665 [-26.6370, -17.6959] | 0.8000 | 0.7500 |
| `adaptive_constrained_rl` | -10.0018 [-11.6633, -8.3403] | 13.0000 | 2.2750 |
