# Owner action — NVIDIA 6G Developer extras (Sub-6 wave)

**Do not put NGC keys, API tokens, or cookies in git or chat.**

This packet is required only for member-only NVIDIA execution. The open NumPy Sub-6 / FR2 / dual-band path reproduces without it.

Field-kit convention (fail closed, silent fake forbidden) is reused from `gunnchos-7gc-ai-ran-field-kit` NVIDIA probe JSON.

## Why a human is needed

NVIDIA 6G Developer / NGC membership exists for the owner. Cursor must not store those credentials. Aerial, pyAerial, Sionna RT scenes, AODT geometry, TensorRT engines, and Nsight traces need that login plus a CUDA GPU.

## Exact owner commands (you run them)

```bash
nvidia-smi
# NGC login: https://ngc.nvidia.com/ → Generate API Key → docker login nvcr.io
# Do not paste the key into chat or commit it.

pip install -r deploy/requirements-serve.txt
# then, if licensed: sionna, tensorrt, aerial / pyAerial per NVIDIA docs

PYTHONPATH=src:. python -c "from readygary_tool_adapters.nvidia_probe import write; print(write())"
python deploy/onnx_export.py
python deploy/onnx_validate.py
python deploy/tensorrt_compile.py
PYTHONPATH=. python scripts/run_all_tool_exports.py
```

## Expected classification after owner login

| Backend | Open path without membership | After owner GPU+login |
|---|---|---|
| NumPy | IMPLEMENTED_AND_EXECUTED | same |
| PyTorch | IMPLEMENTED_NOT_EXECUTED unless torch installed | IMPLEMENTED_AND_EXECUTED if CUDA |
| Sionna PHY TDL | BLOCKED_EXTERNAL | IMPLEMENTED_AND_EXECUTED if TDL call works; still SYNTHETIC_SIM |
| Sionna RT scene | BLOCKED_EXTERNAL (no scene) | IMPLEMENTED_AND_EXECUTED only with a committed/measured scene |
| AODT | BLOCKED_EXTERNAL / BLOCKED_MEMBER_ACCESS | same until scene |
| Aerial / pyAerial | BLOCKED_MEMBER_ACCESS | ACTIVE_ENGINEERING until a RAN graph runs |
| ONNX + ORT | IMPLEMENTED_AND_EXECUTED when `onnx`/`onnxruntime` installed | same |
| TensorRT | TENSORRT_CODE_COMPLETE; TENSORRT_GPU_EXECUTION=BLOCKED_GPU | IMPLEMENTED_AND_EXECUTED only if engine builds and p50/p95/p99 are measured |

Do not relabel HOST_PROCESS_TIMING as radio latency. Do not claim sub-ms until p99 of the TensorRT full path is measured on target hardware. Do not call Sionna/AODT OTA.

## Status

`OWNER_ACTION_PENDING` for Aerial/AODT/Sionna RT scene/TensorRT GPU. Open Sub-6 path remains `IMPLEMENTED_TODAY`.
