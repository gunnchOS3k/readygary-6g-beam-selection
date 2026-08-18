# Reproducibility — readygary-6g-beam-selection

RQ2 beam-selection artifact. **Synthetic / host-process only.** Not Oulu affiliation. Not measured FR2 OTA.

## Quickstart (laptop)

```bash
git clone https://github.com/gunnchOS3k/readygary-6g-beam-selection.git
cd readygary-6g-beam-selection
git checkout <frozen-sha>
python3 -m venv .venv && source .venv/bin/activate
python3 -m pip install pytest numpy pyyaml matplotlib
make reproduce
```

`make reproduce` runs `make test`, `make benchmark-toy`, and `make timing`.

Full `requirements.txt` pulls torch and plotting stacks; they are **not** required for the toy table or unit tests.

## Canonical commands

| Target | What it proves |
|--------|----------------|
| `make test` | `tests/test_metrics.py` + adapter stub |
| `make benchmark-toy` | Regenerates `results/` toy tables (`SYNTHETIC_SIM`) |
| `make timing` | Host-process timers (`HOST_PROCESS_TIMING`) |
| `make smoke` / `make e2e` | Broader local smoke; still not field validation |

Equivalent table generator: `python3 scripts/run_benchmark_table.py --toy`

## Cite these files (do not paste folklore tables)

- [`results/benchmark_table.md`](results/benchmark_table.md)
- [`results/e2e/benchmark_summary.md`](results/e2e/benchmark_summary.md)
- [`results/e2e/benchmark_metrics.json`](results/e2e/benchmark_metrics.json)
- [`results/timing_harness.json`](results/timing_harness.json)

## Evidence classes

| Class | Meaning |
|-------|---------|
| `SYNTHETIC_SIM` | Toy gains or generated TDL — not a channel sounder |
| `HOST_PROCESS_TIMING` | `time.perf_counter` / `time.time` around Python |
| `MEASURED_RF` | **Not claimed** |
| Sub-ms inference | **Unproven** |

## Dataset

See [`docs/DATASET_PROVENANCE.md`](docs/DATASET_PROVENANCE.md). No private IQ. No student PII.

## Independent reproduction

[`docs/packets/EXTERNAL_REPRODUCTION_PACKET.md`](docs/packets/EXTERNAL_REPRODUCTION_PACKET.md)

## Citation

[`CITATION.cff`](CITATION.cff) · MIT [`LICENSE`](LICENSE)
