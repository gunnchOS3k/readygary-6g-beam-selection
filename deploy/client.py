#!/usr/bin/env python3
"""HTTP client for the ReadyGary beam scorer. Stdlib only."""
from __future__ import annotations

import json
import sys
import urllib.request


def call(base: str, method: str, path: str, body: dict | None = None) -> dict:
    data = None if body is None else json.dumps(body).encode("utf-8")
    req = urllib.request.Request(
        base.rstrip("/") + path,
        data=data,
        method=method,
        headers={"Content-Type": "application/json"} if body is not None else {},
    )
    with urllib.request.urlopen(req, timeout=5) as resp:
        raw = resp.read().decode("utf-8")
        if path == "/metrics":
            return {"text": raw}
        return json.loads(raw)


def main() -> int:
    base = sys.argv[1] if len(sys.argv) > 1 else "http://127.0.0.1:8088"
    health = call(base, "GET", "/health")
    print(json.dumps({"health": health}, indent=2))
    return 0 if health.get("status") == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
