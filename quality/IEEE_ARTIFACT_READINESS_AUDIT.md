# IEEE Artifact Readiness Audit — ReadyGary 6G Beam Selection

**Framing:** IMT-2030-aligned / 6G-aligned **research prototype**. Not commercial deployment.

| Criterion | Current evidence | Missing evidence | Priority | Action item |
|-----------|------------------|------------------|----------|-------------|
| Problem statement | README.md, MISSION_ALIGNMENT.md | Independent reviewer quotes | P1 | Expand paper §1–2 |
| Related work | paper/ieee_conference_draft.md | Full BibTeX DOIs | P1 | Complete references |
| Architecture | docs/SYSTEM_OVERVIEW.md or docs/ | Field deployment diagram | P2 | Link device spine |
| Methods | docs/EVAL_PROTOCOL.md, src/ | Live RIC integration | P2 | Keep synthetic primary |
| Dataset / schema | data/, examples/ | Public field release | P2 | Opt-in export pipeline |
| Baselines | Makefile / scripts | Additional baselines | P2 | Document in EVAL_PROTOCOL |
| Metrics | results/ | Multi-seed stats | P2 | Extend CLI |
| Ablations | results/ablation/ (if present) | Statistical tests | P2 | `--seeds` flag |
| Limitations | README not-claimed section | Reviewer sign-off | P1 | Mirror in paper |
| Ethics / privacy | docs/PRIVACY_AND_ETHICS.md | IRB for field | P1 | Community partner protocol |
| Reproducibility | REPRODUCIBILITY.md, CI | Zenodo DOI | P1 | Umbrella release |
| CI / tests | .github/workflows/ci.yml | Benchmark artifacts in CI | P2 | Upload results/ |
| Release / DOI | CITATION.cff | Zenodo | P1 | Tag release |

**Overall:** Conference-draft ready where synthetic evidence exists — not field-validated deployment.
