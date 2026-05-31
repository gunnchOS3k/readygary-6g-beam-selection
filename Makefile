.PHONY: test demo demo-research benchmark-toy map

test:
	PYTHONPATH=. pytest -q

benchmark-toy:
	python3 scripts/run_benchmark_table.py --toy
