# Device Workload Mapping — Beam Selection

## Overview

This document maps beam selection research to the workload characteristics of each device in the Device Quartet. The primary stress case is the **mobile learner with Handheld Hybrid traversing coverage boundaries**.

## Device Mapping

### Handheld Hybrid — High Mobility, Frequent Beam Changes

| Characteristic | Value |
|---|---|
| Mobility level | High |
| Beam change frequency | Frequent (seconds to minutes) |
| Orientation variability | High (handheld rotation, pocket, bag) |
| Beam management complexity | Highest in quartet |

**Workload profile**: Continuous beam tracking and adaptation. The device moves through multiple coverage areas during typical use — walking on campus, riding transit, moving between indoor and outdoor environments. Beam selection must handle rapid changes in angle of arrival, blockage events, and handover between cells.

**Stress case**: Mobile learner traversing coverage boundaries while maintaining a real-time collaborative session. Beam selection must keep handover interruption below perceptible thresholds.

### Student 14.5" — Low Mobility, Indoor Coverage

| Characteristic | Value |
|---|---|
| Mobility level | Low (relocating between fixed positions) |
| Beam change frequency | Infrequent (minutes to hours) |
| Orientation variability | Low (placed on desk/table) |
| Beam management complexity | Moderate |

**Workload profile**: Beam establishment when opening the device at a new location. Indoor propagation with reflections, NLoS conditions, and potential interference from other devices. Session continuity matters during the transition between locations (closing laptop, moving, reopening).

**Stress case**: Student moves from classroom to library. The device must re-establish beam alignment quickly at the new location while maintaining session state.

### DS-XL Coder — Stationary, Minimal Beam Management

| Characteristic | Value |
|---|---|
| Mobility level | Stationary |
| Beam change frequency | Rare (only on initial setup or environment change) |
| Orientation variability | None (fixed position on desk) |
| Beam management complexity | Low |

**Workload profile**: One-time beam establishment at session start. Beam tracking only needed if the propagation environment changes (door opens, person walks through beam path). Primary concern is maintaining a stable, high-throughput link for sustained development workloads.

**Stress case**: Temporary beam blockage during otherwise stationary operation. Recovery must be fast enough to avoid disrupting interactive coding sessions.

### Edge IO — Body-Area, Short-Range, Minimal Beam Concern

| Characteristic | Value |
|---|---|
| Mobility level | Tied to body movement |
| Beam change frequency | N/A (short-range omnidirectional) |
| Orientation variability | High (body movement) |
| Beam management complexity | Minimal |

**Workload profile**: The Edge IO primarily uses BLE/UWB for communication, not mmWave beamforming. Beam selection research has minimal direct relevance to this device. However, the Edge IO may relay data through a Handheld Hybrid's mmWave link, creating an indirect dependency on beam quality.

**Stress case**: Data relay through Handheld Hybrid during mobility. Beam quality on the Handheld Hybrid's mmWave link affects the Edge IO's upstream connectivity.

## Primary Research Focus

The beam selection research in this repository focuses on the **Handheld Hybrid** workload as the primary evaluation scenario, with the **Student 14.5"** as a secondary scenario. The DS-XL Coder and Edge IO are included for completeness but do not drive beam selection algorithm design.
