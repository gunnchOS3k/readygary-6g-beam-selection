# Add PhD application readiness documentation

## Summary

- Document beam selection as one technical method supporting service continuity under mobility
- Map beam selection workloads to the Device Quartet (Handheld Hybrid as primary stress case)
- Define metrics (handover interruption time, beam alignment latency, throughput, reliability, outage time) with baselines (exhaustive sweep, random, static)
- State limitations explicitly: simulation-only, modeled channels, 6G parameters based on IMT-2030 projections

## What This Does NOT Claim

- No access to live 6G infrastructure or mmWave hardware
- No measured beam performance from physical antennas
- No deployed beam management systems
- No validated performance in real-world propagation environments

## Files Added

- `docs/PHD_APPLICATION_READINESS.md` — Overall readiness status and definition of done
- `docs/phd-research-role.md` — Research context and connection to service continuity
- `docs/service-continuity-beam-selection.md` — How beam selection supports continuity, Device Quartet and 7GC connections
- `docs/device-workload-mapping.md` — Per-device beam management workload profiles
- `docs/metrics-baselines-and-limitations.md` — Evaluation metrics, baseline strategies, and stated limitations
- `docs/GITHUB_ISSUES_TO_CREATE.md` — Follow-up issues for implementation work
