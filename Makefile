.PHONY: test benchmark-toy e2e

test:
	PYTHONPATH=. pytest -q

benchmark-toy:
	python3 scripts/run_benchmark_table.py --toy

e2e:
	@mkdir -p results/e2e
	PYTHONPATH=. pytest -q 2>&1 | tee results/e2e/e2e_terminal_output.txt
	python3 scripts/run_benchmark_table.py --toy >> results/e2e/e2e_terminal_output.txt
	@cp results/benchmark_summary.md results/e2e/benchmark_summary.md
	python3 scripts/e2e_check_required_artifacts.py


# Smoke test only — not evidence of readiness
smoke: e2e
