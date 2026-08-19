"""Trainable graph beam scorer.

The existing gnn_multi_bs.py arm is HEURISTIC_MESSAGE_PASSING (average neighbor
DFT bins). This module is a real numpy GraphSAGE-style model with SGD on
oracle beam labels. SYNTHETIC_SIM. Not PyG.
"""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from sim.experiments.digital_programme import BeamAction, exhaustive


def _node_features(H: np.ndarray) -> np.ndarray:
    mag = np.abs(H)
    return np.array(
        [
            float(mag.mean()),
            float(mag.max()),
            float(mag.std()),
            float(np.angle(H).mean()),
            float(np.linalg.norm(mag) / (mag.size ** 0.5)),
        ],
        dtype=np.float64,
    )


def _softmax(z: np.ndarray) -> np.ndarray:
    z = z - np.max(z)
    e = np.exp(z)
    return e / (np.sum(e) + 1e-18)


@dataclass
class TrainableGNN:
    in_dim: int = 5
    hid: int = 8
    n_classes: int = 8
    rng: np.random.Generator = field(default_factory=lambda: np.random.default_rng(0))
    w_self: np.ndarray = field(init=False)
    w_msg: np.ndarray = field(init=False)
    w_out: np.ndarray = field(init=False)

    def __post_init__(self) -> None:
        s = 0.3
        self.w_self = self.rng.normal(0.0, s, size=(self.in_dim, self.hid))
        self.w_msg = self.rng.normal(0.0, s, size=(self.in_dim, self.hid))
        self.w_out = self.rng.normal(0.0, s, size=(self.hid, self.n_classes))

    def encode(self, Hs: list[np.ndarray], message_passing: bool = True) -> list[np.ndarray]:
        xs = [_node_features(H) for H in Hs]
        hs = []
        mean_x = sum(xs) / max(len(xs), 1)
        for x in xs:
            h = np.tanh(x @ self.w_self + (mean_x @ self.w_msg if message_passing else 0.0))
            logits = h @ self.w_out
            hs.append(logits)
        return hs

    def predict(self, Hs: list[np.ndarray]) -> list[int]:
        return [int(np.argmax(z)) for z in self.encode(Hs)]

    def train_step(self, Hs: list[np.ndarray], labels: list[int], lr: float = 0.05) -> float:
        logits_list = self.encode(Hs)
        loss = 0.0
        # Mean-field backprop through tanh GNN (one-step).
        g_self = np.zeros_like(self.w_self)
        g_msg = np.zeros_like(self.w_msg)
        g_out = np.zeros_like(self.w_out)
        xs = [_node_features(H) for H in Hs]
        mean_x = sum(xs) / max(len(xs), 1)
        for x, logits, y in zip(xs, logits_list, labels):
            p = _softmax(logits)
            loss += -np.log(p[y] + 1e-18)
            dlogits = p
            dlogits[y] -= 1.0
            h = np.tanh(x @ self.w_self + mean_x @ self.w_msg)
            g_out += np.outer(h, dlogits)
            dh = (dlogits @ self.w_out.T) * (1.0 - h ** 2)
            g_self += np.outer(x, dh)
            g_msg += np.outer(mean_x, dh)
        n = max(len(Hs), 1)
        self.w_self -= lr * g_self / n
        self.w_msg -= lr * g_msg / n
        self.w_out -= lr * g_out / n
        return float(loss / n)


def train_on_oracle(
    episodes: list[list[np.ndarray]],
    tx_cb: np.ndarray,
    rx_cb: np.ndarray,
    *,
    seed: int = 0,
    steps: int = 8,
) -> TrainableGNN:
    gnn = TrainableGNN(n_classes=tx_cb.shape[0], rng=np.random.default_rng(seed))
    for _ in range(steps):
        for Hs in episodes:
            labels = []
            for H in Hs:
                ti, _, _ = exhaustive(H, tx_cb, rx_cb)
                labels.append(ti)
            gnn.train_step(Hs, labels)
    return gnn


def run_trainable(
    Hs_seq: list[list[np.ndarray]],
    tx_cb: np.ndarray,
    rx_cb: np.ndarray,
    model: TrainableGNN,
) -> dict[str, float]:
    snrs = []
    for Hs in Hs_seq:
        preds = model.predict(Hs)
        for H, t in zip(Hs, preds):
            t = int(np.clip(t, 0, tx_cb.shape[0] - 1))
            # Use predicted TX beam with RX 0 as a cheap sequential head.
            val = tx_cb[t] @ H @ rx_cb[min(t, rx_cb.shape[0] - 1)]
            snrs.append(float(np.abs(val) ** 2))
    mean_lin = float(sum(snrs) / max(len(snrs), 1))
    return {
        "mean_snr_linear": mean_lin,
        "mean_snr_db": float(10.0 * np.log10(max(mean_lin, 1e-18))),
        "model": "trainable_graphsage_numpy",
        "class": "TRAINED_GRAPH_MODEL",
        "heuristic_gnn_class": "HEURISTIC_MESSAGE_PASSING",
    }


def classify_existing_gnn() -> dict[str, str]:
    return {
        "sim.models.gnn_multi_bs": "HEURISTIC_MESSAGE_PASSING",
        "sim.models.gnn_trainable": "TRAINED_GRAPH_MODEL",
        "note": "Heuristic averages neighbor DFT bins. TrainableGNN has SGD weights.",
    }
