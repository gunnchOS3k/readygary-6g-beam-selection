# Metrics, Baselines, and Limitations

## Metrics

| Metric | Definition | Unit | Target Direction |
|---|---|---|---|
| Handover interruption time | Duration of service gap during beam or cell handover | ms | Minimize |
| Beam alignment latency | Time from beam search trigger to stable beam pair | ms | Minimize |
| Throughput during mobility | Sustained data rate while user traverses coverage areas | Mbps | Maximize |
| Reliability | Probability of maintaining target QoS (latency, throughput) during mobility | % | Maximize |
| Outage time | Total duration where service falls below minimum acceptable threshold | ms (cumulative) | Minimize |
| Recovery time | Time from beam failure detection to restored service | ms | Minimize |

### Metric Measurement

All metrics are measured within the simulation environment:

- **Handover interruption**: Timestamp difference between last packet on source beam and first packet on target beam
- **Beam alignment latency**: Timestamp difference between beam search initiation and beam pair confirmation
- **Throughput**: Simulated channel capacity based on beam gain, interference, and channel model
- **Reliability**: Fraction of simulation time where QoS targets are met, across multiple runs
- **Outage time**: Sum of intervals where throughput or latency exceeds minimum thresholds
- **Recovery time**: Timestamp difference between beam failure event and service restoration

## Baselines

Three baseline beam selection strategies are used for comparison:

### 1. Exhaustive Beam Sweep (No Prediction)

- Tests all candidate beam pairs sequentially
- Guarantees optimal beam selection
- Maximizes beam alignment latency
- Represents the worst-case latency bound

### 2. Random Beam Selection

- Selects a beam uniformly at random from the candidate set
- Provides a lower bound on expected performance
- Useful for validating that proposed methods provide meaningful improvement

### 3. Static Beam (No Adaptation)

- Maintains the initial beam assignment without adaptation
- Performance degrades as user moves away from optimal alignment
- Represents the cost of not performing beam management

## Limitations

### Simulation Environment

- All evaluations are conducted in simulation — no live mmWave hardware or 6G testbeds are used
- Channel models are based on published 3GPP TR 38.901 and ITU IMT-2030 parameters
- Simulated propagation does not capture all real-world effects (weather, foliage, dynamic obstacles)

### 6G Parameter Assumptions

- 6G system parameters are based on IMT-2030 vision documents and published research projections
- Actual 6G specifications are not finalized — results are valid within stated parameter assumptions
- Frequency bands, bandwidth allocations, and beam codebook sizes are representative, not definitive

### Beam and Antenna Modeling

- Beam patterns are modeled analytically (uniform linear/planar arrays) or from published specifications
- Mutual coupling, manufacturing tolerances, and non-ideal antenna effects are not modeled
- Beamforming weights assume ideal phase shifters

### Mobility Modeling

- User mobility follows standard models (random waypoint, Manhattan grid, linear trajectory)
- Real human mobility patterns are more complex and context-dependent
- Rotation and orientation changes are modeled probabilistically, not from measured data

### Scope

- This repository evaluates beam selection as one component of service continuity
- Results do not validate the full service-continuity architecture
- Integration with higher-layer handover and session migration is not implemented here
- No claims are made about deployed system performance
