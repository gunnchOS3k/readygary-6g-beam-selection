# PhD Application Readiness — 6G mmWave Beam Selection

## Role

6G mmWave beam selection benchmarks supporting **service continuity under mobility** and changing network conditions. Beam selection is one technical method that contributes to the larger service-continuity research agenda by optimizing PHY-layer decisions that directly affect session quality during movement.

## Status: Concept-Complete

### Complete

- Beam selection algorithm framework
- 6G URLLC research context and positioning

### Prototype-Pending

- Integration with service-continuity middleware
- Reproducible benchmark suite with standardized scenarios

### Simulation-Only

- All evaluations are simulation-based
- No live 6G or mmWave hardware is used

### Ethics-Gated

- None — this is pure technical simulation with no human subjects or sensitive data

## Metrics

| Metric | Description | Measurement Method |
|---|---|---|
| Handover interruption time | Duration of service gap during beam or cell handover | Simulation timestamp analysis |
| Beam alignment latency | Time to establish optimal beam pair after trigger | Algorithm execution time in simulation |
| Throughput during mobility | Sustained data rate while user moves through coverage | Simulated channel capacity tracking |
| Reliability | Probability of maintaining target QoS during mobility | Statistical analysis across simulation runs |
| Outage time | Total duration where service is below minimum threshold | Threshold-based event counting in simulation |

## Evidence

- Algorithm source code in this repository
- Simulation framework and configuration
- Benchmark result data (simulated)

## Must Not Claim

- Access to live 6G infrastructure or mmWave hardware
- Measured beam performance from physical antennas
- Deployed beam management systems
- Validated performance in real-world propagation environments

## Fallback

All work is simulation-based. Channel models use published 3GPP/ITU parameters. Beam patterns are modeled analytically or from published antenna specifications.

## Definition of Done

1. Beam selection documented as one method supporting service continuity
2. Metrics defined with clear measurement methodology
3. Baselines compared (exhaustive sweep, random, static)
4. Limitations explicitly stated (simulation-only, modeled channels)
5. Connection to Device Quartet and 7GC scenarios documented
