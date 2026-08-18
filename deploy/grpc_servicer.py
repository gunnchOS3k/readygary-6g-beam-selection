"""Optional gRPC servicer. grpcio is not a hard dependency."""
from __future__ import annotations

import json
from pathlib import Path


def status() -> dict:
    try:
        import grpc  # noqa: F401
    except Exception as exc:
        return {
            "grpc_serving": False,
            "status": "BLOCKED_OPTIONAL_BACKEND",
            "reason": f"grpcio not importable ({type(exc).__name__})",
            "http_fallback": "deploy/server.py",
        }
    return {
        "grpc_serving": False,
        "status": "ACTIVE_ENGINEERING",
        "reason": "grpcio present; protobuf contract not pinned — HTTP /infer is the open path.",
        "http_fallback": "deploy/server.py",
    }


def write_artifact(root: Path) -> Path:
    path = root / "deploy" / "artifacts" / "grpc_status.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(status(), indent=2) + "\n", encoding="utf-8")
    return path
