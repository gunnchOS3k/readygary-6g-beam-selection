# PhD Research Role — Beam Selection for Service Continuity

## Context

Beam selection is **one technical method** supporting service continuity under mobility. It is not the entire research contribution — it is a PHY-layer optimization input that feeds into the larger service-continuity architecture.

## The Problem

When users move through a wireless environment, the directional beams used in mmWave (and anticipated 6G sub-THz) communication must adapt to maintain connectivity. If beam alignment is slow or fails, the user experiences:

- **Throughput degradation** — reduced data rate during beam search
- **Latency spikes** — queued packets during beam realignment
- **Session interruption** — complete service loss during handover
- **Application failure** — real-time applications (video, collaboration) break under sustained outage

## How Beam Selection Supports Service Continuity

Faster and smarter beam selection reduces the impact of mobility on session quality:

1. **Faster beam alignment** = shorter interruption during handover
2. **Predictive beam management** = proactive adaptation before link degradation
3. **Beam failure recovery** = reduced outage when current beam is lost
4. **Multi-beam coordination** = smoother transitions across coverage boundaries

## Connection to the Research Agenda

This repository evaluates how beam management decisions affect:

- **Latency**: Does predictive beam selection reduce handover interruption time?
- **Throughput**: Can beam quality tracking maintain higher sustained rates during movement?
- **Session continuity**: Do smarter beam decisions translate to fewer application-level disruptions?

These questions are evaluated in the context of **affordable edge devices** — the Device Quartet — where computational resources for beam management may be limited and where user mobility patterns differ by device class.

## Connection to the Larger Architecture

Beam selection provides PHY-layer optimization inputs to the service-continuity middleware:

- Beam quality reports inform handover timing decisions
- Predicted beam availability supports proactive session migration
- Beam failure events trigger fallback mechanisms in the continuity layer

This is one component in a multi-layer approach to maintaining quality of experience during mobility.
