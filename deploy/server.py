#!/usr/bin/env python3
"""Stdlib HTTP serving surface: health, metadata, metrics, infer, benchmark.

FastAPI is used when installed (`requirements-serve.txt`); otherwise http.server.
No NVIDIA credentials. TensorRT absence → BLOCKED_GPU on /metadata.
"""
from __future__ import annotations

import json
import sys
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from deploy.tiny_beam_scorer import seeded_scorer  # noqa: E402
from deploy.tensorrt_compile import probe as tensorrt_probe  # noqa: E402

SCORER = seeded_scorer(7)
STARTED = time.time()
INFER_COUNT = 0


def health_payload() -> dict:
    trt = tensorrt_probe()
    return {
        "status": "ok",
        "service": "readygary-beam-scorer",
        "uptime_s": round(time.time() - STARTED, 3),
        "gpu": False if trt["status"] == "BLOCKED_GPU" else True,
        "tensorrt": trt["status"],
        "band": "FR2",
        "carrier_hz": 28_000_000_000,
        "sub_ms_inference_proven": False,
        "sub_ms_inference_target": True,
    }


def metadata_payload() -> dict:
    meta_path = ROOT / "deploy" / "artifacts" / "metadata.json"
    trt = tensorrt_probe()
    meta = {}
    if meta_path.is_file():
        meta = json.loads(meta_path.read_text(encoding="utf-8"))
    meta["tensorrt"] = trt
    meta["observability"] = {"infer_count": INFER_COUNT}
    return meta


def metrics_text() -> str:
    return (
        "# HELP readygary_infer_count Number of /infer calls\n"
        "# TYPE readygary_infer_count counter\n"
        f"readygary_infer_count {INFER_COUNT}\n"
        "# HELP readygary_up 1 if serving\n"
        "# TYPE readygary_up gauge\n"
        "readygary_up 1\n"
    )


def infer_payload(body: dict) -> dict:
    global INFER_COUNT
    import numpy as np

    H = np.array(body.get("H_real"), dtype=np.float32) + 1j * np.array(body.get("H_imag"), dtype=np.float32)
    if H.shape != (8, 8):
        H = np.ones((8, 8), dtype=np.complex64)
    t0 = time.perf_counter()
    x = SCORER.pre(H)
    t1 = time.perf_counter()
    logits = SCORER.model(x)
    t2 = time.perf_counter()
    beam = SCORER.post(logits)
    t3 = time.perf_counter()
    INFER_COUNT += 1
    return {
        "tx_beam": beam,
        "timing_ms": {
            "pre": (t1 - t0) * 1000.0,
            "model": (t2 - t1) * 1000.0,
            "post": (t3 - t2) * 1000.0,
            "full": (t3 - t0) * 1000.0,
        },
        "latency_class": "HOST_PROCESS_TIMING",
        "sub_ms_inference_proven": False,
        "batch": 1,
    }


def build_fastapi():
    try:
        from fastapi import FastAPI
        from pydantic import BaseModel
    except Exception:
        return None

    app = FastAPI(title="ReadyGary beam scorer")

    class InferIn(BaseModel):
        H_real: list
        H_imag: list

    @app.get("/health")
    def health():
        return health_payload()

    @app.get("/metadata")
    def metadata():
        return metadata_payload()

    @app.get("/metrics")
    def metrics():
        from fastapi.responses import PlainTextResponse

        return PlainTextResponse(metrics_text())

    @app.post("/infer")
    def infer(body: InferIn):
        return infer_payload(body.model_dump())

    @app.post("/benchmark")
    def benchmark():
        import numpy as np

        H = np.eye(8, dtype=np.complex64)
        rows = [infer_payload({"H_real": H.real.tolist(), "H_imag": H.imag.tolist()}) for _ in range(16)]
        full = [r["timing_ms"]["full"] for r in rows]
        return {"n": len(full), "p50_ms": sorted(full)[len(full) // 2], "sub_ms_inference_proven": False}

    return app


class Handler(BaseHTTPRequestHandler):
    def _json(self, code: int, payload: dict) -> None:
        raw = json.dumps(payload).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def log_message(self, fmt: str, *args) -> None:  # noqa: A003
        sys.stderr.write("readygary-serve: " + (fmt % args) + "\n")

    def do_GET(self) -> None:  # noqa: N802
        path = urlparse(self.path).path
        if path == "/health":
            self._json(200, health_payload())
            return
        if path == "/metadata":
            self._json(200, metadata_payload())
            return
        if path == "/metrics":
            raw = metrics_text().encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "text/plain; version=0.0.4")
            self.send_header("Content-Length", str(len(raw)))
            self.end_headers()
            self.wfile.write(raw)
            return
        self._json(404, {"error": "not found"})

    def do_POST(self) -> None:  # noqa: N802
        path = urlparse(self.path).path
        length = int(self.headers.get("Content-Length") or 0)
        body = json.loads(self.rfile.read(length) or b"{}")
        if path == "/infer":
            self._json(200, infer_payload(body))
            return
        if path == "/benchmark":
            import numpy as np

            H = np.eye(8, dtype=np.complex64)
            rows = [infer_payload({"H_real": H.real.tolist(), "H_imag": H.imag.tolist()}) for _ in range(16)]
            full = [r["timing_ms"]["full"] for r in rows]
            self._json(200, {"n": len(full), "p50_ms": sorted(full)[len(full) // 2], "sub_ms_inference_proven": False})
            return
        self._json(404, {"error": "not found"})


def main() -> int:
    app = build_fastapi()
    host = "0.0.0.0"
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8088
    if app is not None:
        try:
            import uvicorn

            uvicorn.run(app, host=host, port=port)
            return 0
        except Exception:
            pass
    httpd = ThreadingHTTPServer((host, port), Handler)
    print(json.dumps({"serving": f"http://{host}:{port}", "stack": "stdlib-http"}))
    httpd.serve_forever()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
