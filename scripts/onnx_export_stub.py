#!/usr/bin/env python3
"""Optional ONNX export stub — does not require onnx package."""
from __future__ import annotations

import sys


def main() -> int:
    try:
        import onnx  # noqa: F401
    except ImportError:
        print("ONNX not installed. Toy export skipped.")
        print("Install: pip install onnx onnxruntime")
        print("Then implement export from sim/models/lstm_beam_tracker.py")
        return 0
    print("ONNX installed — implement model export in a future PR.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
