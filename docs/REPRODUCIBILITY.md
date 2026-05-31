# Reproducibility

## Quickstart

```bash
git clone https://github.com/gunnchOS3k/readygary-6g-beam-selection.git
cd readygary-6g-beam-selection
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
pytest -q
python scripts/run_benchmark_table.py --toy
```

## Tests

```bash
pytest -q
```

## Sample data policy

Synthetic/toy only. **No private competition data.** No student PII.

## Regenerate artifacts

Demo commands write to `results/` or `docs/generated/` where applicable.

## Citation

See `CITATION.cff` in repo root.
