# Evaluation Protocol — ReadyGary 6G Beam Selection

## Scope

Document how to evaluate this **research prototype** without overclaiming.

## Environments

1. **Synthetic smoke** — default CI path; deterministic seeds where applicable.
2. **Fresh machine** — follow [REPRODUCIBILITY.md](../REPRODUCIBILITY.md).
3. **Field / opt-in** — planned; requires ethics review (see PRIVACY_AND_ETHICS.md).

## Metrics

- Correctness: tests pass
- Reproducibility: same command → same synthetic outputs
- Latency / resource: document host spec in logs

## Baselines

Document baseline commands in README. Label synthetic-only results in `results/`.

## Reporting

Aggregated metrics only for any field work. No private payload content.
