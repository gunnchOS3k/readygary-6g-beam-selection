# ReadyGary deploy path

Open path (no NVIDIA membership required):

```bash
python deploy/onnx_export.py
python deploy/tensorrt_compile.py   # records BLOCKED_GPU on CPU hosts
python deploy/server.py 8088
python deploy/client.py http://127.0.0.1:8088
```

| Surface | Status |
|---|---|
| Numpy scorer + `/health` `/metadata` `/metrics` `/infer` `/benchmark` | IMPLEMENTED TODAY |
| ONNX file | IMPLEMENTED TODAY if `onnx` is installed; else `ONNX_EXPORT_BLOCKED_OPTIONAL_DEP` + npz |
| FastAPI/uvicorn | used when installed; stdlib HTTP otherwise |
| gRPC | BLOCKED_OPTIONAL_BACKEND without grpcio |
| TensorRT engine | BLOCKED_GPU without CUDA |
| Sub-ms inference | TARGET, not proven |

Container:

```bash
docker build -f deploy/Dockerfile -t readygary-beam:local .
docker run --rm -p 8088:8088 readygary-beam:local
```

Never commit NVIDIA credentials. Aerial/Sionna/AODT/TensorRT adapters live under `src/readygary_tool_adapters/`.
