# rq2_sub6 (SYNTHETIC_SIM, HOST_PROCESS_TIMING, n77 3.75 GHz FR1, NEVER 28 GHz)

carrier_hz=3750000000 profile=n77_us_cband. Not OTA.

FSPL gap vs 28 GHz (digital): 17.46253527229001 dB. UMa-NLOS 35 m n77=85.36280452776315 dB vs n257=102.82533980005316 dB.

| family | SNR dB mean [95% CI] | path loss dB | Doppler Hz | carrier_hz |
|---|---|---|---|---|
| `held_out` | 1.3683 [-0.6225, 3.3592] | 85.3628 | 18.7630 | 3750000000 |
| `high_blockage` | -11.8007 [-13.7384, -9.8630] | 116.7982 | 18.7630 | 3750000000 |
| `high_mobility` | 2.2022 [1.2993, 3.1050] | 85.3628 | 275.1904 | 3750000000 |
| `indoor` | -3.8007 [-5.7384, -1.8630] | 116.7982 | 18.7630 | 3750000000 |
| `cell_edge` | -2.8008 [-4.7916, -0.8099] | 113.1567 | 18.7630 | 3750000000 |
| `congestion` | 0.4758 [-1.5150, 2.4667] | 85.3628 | 18.7630 | 3750000000 |

## Supporting true-below-6 GHz profiles

| profile | carrier_hz | SNR dB |
|---|---|---|
| `n41_us_2500` | 2593000000 | 1.5896 |
| `n71_us_600` | 680500000 | 4.5707 |
