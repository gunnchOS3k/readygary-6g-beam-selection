# Claims (Paper II ReadyGary companion)

| Claim | Allowed | Evidence |
|---|---|---|
| 28 GHz is FR2 mmWave | yes | protocol `carrier.frequency_hz: 28000000000`, `band: FR2`; TS 38.101-2 |
| 28 GHz is Sub-6 | **false** | never |
| n77 3.75 GHz is true below-6 GHz FR1 | yes | `configs/bands/sub6/n77_us_cband.yaml`; TS 38.101-1; RM520N-GL public band list |
| n96 is Sub-6 | **false** | FR1 but not entirely below 6 GHz; excluded from SUB6 family |
| Sub-6 JSON is a relabel of FR2 tables | **false** | `rq2_sub6_fr1_heldout.json` carrier 3750000000 ≠ 28000000000; UMa path-loss/Doppler differ |
| Held-out oracle SNR $2.5263$ dB $[1.7954,3.2572]$ | yes | `rq2_beam_selection_fr2_heldout.json`; matches `cloud_only` |
| Hierarchical $1.2082$ dB loss vs oracle | yes | same JSON; `HOST_PROCESS_TIMING` $0.3714$ ms vs $1.0244$ ms |
| Twin vs information-equivalent (same AoA) | yes | $-3.6178$ dB vs $-21.3758$ dB |
| AoA hint always helps | **no** | `no_aoa_hint` hierarchical fallback $1.3182$ dB > hinted window |
| Sub-ms RF inference | **no** | `sub_ms_inference_proven: false` |
| Measured RF / OTA | **no** | SYNTHETIC_SIM TDL |
