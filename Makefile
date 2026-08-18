.PHONY: test benchmark-toy timing e2e smoke reproduce e2e-tooling paper paper-reproduce

PY := $(if $(wildcard .venv/bin/python),.venv/bin/python,python3)

test:
	PYTHONPATH=. $(PY) -m pytest -q

benchmark-toy:
	$(PY) scripts/run_benchmark_table.py --toy

timing:
	$(PY) scripts/run_timing_harness.py

reproduce: test benchmark-toy timing

paper-reproduce:
	@test -f paper/artifacts/experiment_protocol.yaml
	$(PY) scripts/run_benchmark_table.py --toy
	$(PY) scripts/run_timing_harness.py
	PYTHONPATH=. $(PY) scripts/run_paper_ii_heldout.py
	$(PY) paper/scripts/generate_tables.py

paper: paper-reproduce
	@test -f paper/manuscript.tex
	@test -f paper/MANUSCRIPT_STATUS.md
	@test -f paper/CITATION_AUDIT.md
	@test -f results/experiments/rq2_beam_selection_fr2_heldout.json
	@echo "Paper II ReadyGary: SYNTHETIC_SIM; HOST_PROCESS_TIMING; 28 GHz FR2 not Sub-6"

e2e:
	@mkdir -p results/e2e
	PYTHONPATH=. pytest -q 2>&1 | tee results/e2e/e2e_terminal_output.txt
	python3 scripts/run_benchmark_table.py --toy >> results/e2e/e2e_terminal_output.txt
	python3 scripts/run_timing_harness.py >> results/e2e/e2e_terminal_output.txt
	@cp results/benchmark_summary.md results/e2e/benchmark_summary.md
	python3 scripts/run_all_tool_exports.py 2>> results/e2e/e2e_terminal_output.txt || true
	$(MAKE) e2e-tooling 2>> results/e2e/e2e_terminal_output.txt || true
	python3 scripts/e2e_check_required_artifacts.py

# Smoke test only — not evidence of readiness
smoke: e2e

e2e-tooling:
	@mkdir -p results/tool_exports
	python3 scripts/run_all_tool_exports.py 2>/dev/null || python3 scripts/check_optional_backends.py || true

e2e-sionna e2e-deepmimo e2e-aerial e2e-oran:
	@echo "Optional target $@ — requires external install; not run in default CI"
