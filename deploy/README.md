# ReadyGary deploy path

Open path (no NVIDIA membership required):

```bash
python deploy/onnx_export.py
python deploy/onnx_validate.py      # checker + ORT equivalence when onnxruntime is installed
python deploy/tensorrt_compile.py   # TENSORRT_CODE_COMPLETE; BLOCKED_GPU on CPU hosts
python deploy/server.py 8088
python deploy/client.py http://127.0.0.1:8088
```

| Surface | Status |
|---|---|
| Numpy FR2 scorer + `/health` `/metadata` `/metrics` `/infer` `/benchmark` | IMPLEMENTED TODAY |
| `/bands` `/decide` cross-band APIs | IMPLEMENTED TODAY |
| Band profile metadata (n77 Sub-6 primary, n257 FR2) | IMPLEMENTED TODAY |
| ONNX file | IMPLEMENTED TODAY if `onnx` is installed; else `ONNX_EXPORT_BLOCKED_OPTIONAL_DEP` + npz |
| ONNX Runtime equivalence | IMPLEMENTED TODAY if `onnxruntime` is installed |
| FastAPI/uvicorn | used when installed; stdlib HTTP otherwise |
| gRPC | BLOCKED_OPTIONAL_BACKEND without grpcio |
| TensorRT engine | TENSORRT_CODE_COMPLETE; TENSORRT_GPU_EXECUTION=BLOCKED_GPU without CUDA |
| Sub-ms inference | TARGET, not proven |

The HTTP scorer remains an 8×8 FR2 toy model. Sub-6 decisions go through `/decide` (Type-I CSI / dual-band controller), not a relabel of 28 GHz logits.

Container:

```bash
docker build -f deploy/Dockerfile -t readygary-beam:local .
docker run --rm -p 8088:8088 readygary-beam:local
```

Never commit NVIDIA credentials. Aerial/Sionna/AODT/TensorRT adapters live under `src/readygary_tool_adapters/`. Owner GPU login: `docs/packets/OWNER_ACTION_NVIDIA_SUB6.md`.

