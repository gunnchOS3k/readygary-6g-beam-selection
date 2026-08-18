# Owner action — NVIDIA 6G Developer extras

**Do not put NGC keys, API tokens, or cookies in git.**

Local probe on 2026-08-18 (this host): no `nvidia-smi`, no `nvcc`, no `torch`/`sionna`/`tensorrt`/`aerial` import. TensorRT path is **`BLOCKED_GPU`**. Sionna RT and AODT are **`BLOCKED_OPTIONAL_BACKEND`**.

The open ReadyGary path (numpy TDL/CDL-structure, GNN ablation, adaptive trackers, HTTP scorer) reproduces without this packet.

## Why a human is needed

NVIDIA 6G Developer / NGC membership exists for the owner. Cursor must not store those credentials. Aerial, pyAerial, Sionna RT scenes, AODT, TensorRT engines, and Nsight traces require that login plus a CUDA GPU.

## Exact owner commands (you run them)

```bash
# 1) Confirm GPU
nvidia-smi

# 2) Login to NGC (do not paste the key into chat or commit it)
#    https://ngc.nvidia.com/ → Generate API Key → docker login nvcr.io

# 3) Optional extras (venv)
pip install -r deploy/requirements-serve.txt
# then, if licensed: sionna, tensorrt, aerial / pyAerial per NVIDIA docs

# 4) Re-run
python deploy/onnx_export.py
python deploy/tensorrt_compile.py
PYTHONPATH=. python scripts/run_all_tool_exports.py
```

## Expected artifacts (still SYNTHETIC_SIM until OTA)

- `deploy/artifacts/tiny_beam_scorer.onnx`
- `deploy/artifacts/tensorrt_status.json` with `tensorrt_compiled: true` only if an engine was actually built
- `results/tool_exports/aerial_status.json`, `aodt_status.json`, `sionna_channel_config.yaml`

Do not relabel HOST_PROCESS_TIMING as gNB slot time. Do not claim sub-ms until p99 of the TensorRT full path is measured on target hardware.

## Status

`OWNER_ACTION_PENDING` for Aerial/AODT/TensorRT/Nsight. Open path remains `IMPLEMENTED TODAY`.
