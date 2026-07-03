# GitHub Issues to Create

## Issue 1: Build reproducible beam selection benchmark suite

**Labels**: enhancement, research

Create a standardized benchmark suite with defined mobility scenarios, channel models, and beam codebook configurations. Include scripts for running all baseline comparisons (exhaustive sweep, random, static) and generating result tables.

---

## Issue 2: Document beam selection integration with service-continuity middleware

**Labels**: documentation, architecture

Define the interface between beam selection outputs (beam quality reports, predicted availability, failure events) and the service-continuity middleware. Specify message formats, timing requirements, and fallback behavior.

---

## Issue 3: Implement Device Quartet mobility scenario profiles

**Labels**: enhancement, simulation

Create simulation scenario profiles for each Device Quartet member: Handheld Hybrid (high mobility), Student 14.5" (indoor relocation), DS-XL Coder (stationary), Edge IO (indirect via relay). Include mobility traces, orientation models, and environment configurations.

---

## Issue 4: Add metrics collection and reporting framework

**Labels**: enhancement, tooling

Implement automated metrics collection for handover interruption time, beam alignment latency, throughput during mobility, reliability, outage time, and recovery time. Include statistical analysis (mean, percentile, CDF) and standardized output format for cross-scenario comparison.

---

## Issue 5: Validate simulation parameters against IMT-2030 targets

**Labels**: research, validation

Review and document all simulation parameters (frequency, bandwidth, beam codebook, channel model) against published 3GPP TR 38.901 and ITU IMT-2030 vision documents. Flag any parameters that deviate from published values and justify the deviation.
