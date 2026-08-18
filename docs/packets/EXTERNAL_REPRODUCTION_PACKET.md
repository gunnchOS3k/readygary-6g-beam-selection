# External / independent reproduction packet

**Repo:** `readygary-6g-beam-selection`  
**RQ:** RQ2 (beam selection / PHY-facing evidence)  
**Status:** `INDEPENDENT_REPRODUCTION_PENDING`

Cursor cannot sign this on another person’s behalf. This packet is for an **outside researcher** on a clean machine.

## Why still pending

No returned evidence record from an independent researcher exists in this tree (`artifacts/independent_reproduction/` is empty until someone files one).

## What this repo can reproduce today

Toy metrics, host-process timers, and the frozen Paper II FR2 digital programme. **Not** measured RF. **Not** sub-ms edge inference. 28 GHz in the TDL generator is **FR2 mmWave**, not Sub-6.

`make paper-reproduce` requires `paper/artifacts/experiment_protocol.yaml` and writes `paper/tables/` plus `results/experiments/rq2_beam_selection_fr2_heldout.json`.

## Frozen checkout

```bash
git clone https://github.com/gunnchOS3k/readygary-6g-beam-selection.git
cd readygary-6g-beam-selection
git checkout <frozen-sha-from-the-draft-PR>
python3 -m venv .venv && source .venv/bin/activate
python3 -m pip install pytest numpy pyyaml matplotlib
make test
make paper-reproduce
```

Expect:

- pytest PASS
- `results/e2e/benchmark_metrics.json` with `"evidence_class": "SYNTHETIC_SIM"`
- `results/timing_harness.json` with `"latency_class": "HOST_PROCESS_TIMING"`
- `sub_ms_inference_proven` is false

Optional heavier smoke (torch, matplotlib): `pip install -r requirements.txt` then `make smoke`. Still not field validation.

## Expected evidence form

Store as `artifacts/independent_reproduction/<lab-or-person-id>.md` (no extra PII).

```text
system:
commit:
command: make reproduce
start:
end:
result:
output_hashes:
  results/e2e/benchmark_metrics.json:
  results/timing_harness.json:
deviations:
PASS_FAIL:
notes: SYNTHETIC_SIM only; sub-ms unproven
```

## Physical / external blockers (remain after this packet)

- No independent PASS on file
- No OTA / channel-sounder dataset
- No instrumented DUT latency
- DeepMIMO / Sionna execution optional and not in default CI
- `deploy/` edge service not in tree
