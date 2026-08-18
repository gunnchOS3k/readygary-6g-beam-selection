"""Tiny FR2 beam scorer: |H| (8x8) → 8 TX-beam logits. Numpy only.

Weights are seeded and exported to npz / ONNX-when-available. Not a trained
production model. HOST_PROCESS_TIMING. Sub-ms is TARGET, not fact.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np

N_IN = 64
N_HID = 16
N_OUT = 8


@dataclass
class TinyBeamScorer:
    w1: np.ndarray
    b1: np.ndarray
    w2: np.ndarray
    b2: np.ndarray

    def pre(self, H: np.ndarray) -> np.ndarray:
        mag = np.abs(H).reshape(-1).astype(np.float32)
        mag = mag / (np.linalg.norm(mag) + 1e-8)
        return mag

    def model(self, x: np.ndarray) -> np.ndarray:
        h = np.tanh(x @ self.w1 + self.b1)
        return h @ self.w2 + self.b2

    def post(self, logits: np.ndarray) -> int:
        return int(np.argmax(logits))

    def infer(self, H: np.ndarray) -> int:
        return self.post(self.model(self.pre(H)))


def seeded_scorer(seed: int = 7) -> TinyBeamScorer:
    rng = np.random.default_rng(seed)
    w1 = rng.normal(0.0, 0.3, size=(N_IN, N_HID)).astype(np.float32)
    b1 = np.zeros(N_HID, dtype=np.float32)
    w2 = rng.normal(0.0, 0.3, size=(N_HID, N_OUT)).astype(np.float32)
    b2 = np.zeros(N_OUT, dtype=np.float32)
    return TinyBeamScorer(w1, b1, w2, b2)


def save_npz(scorer: TinyBeamScorer, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    np.savez(
        path,
        w1=scorer.w1,
        b1=scorer.b1,
        w2=scorer.w2,
        b2=scorer.b2,
        n_in=N_IN,
        n_hid=N_HID,
        n_out=N_OUT,
        carrier_hz=28_000_000_000,
        band="FR2",
    )
    return path


def load_npz(path: Path) -> TinyBeamScorer:
    z = np.load(path)
    return TinyBeamScorer(z["w1"], z["b1"], z["w2"], z["b2"])
