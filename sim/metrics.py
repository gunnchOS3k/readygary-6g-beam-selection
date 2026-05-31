"""Publication-grade beam-selection metrics (toy oracle for reproducible demos)."""
from __future__ import annotations

import random
import time
from typing import Sequence


def top_k_accuracy(predicted: Sequence[int], oracle: Sequence[int], k: int = 3) -> float:
    if not oracle:
        return 0.0
    pred_set = set(predicted[:k])
    oracle_set = set(oracle[:k])
    return len(pred_set & oracle_set) / min(k, len(oracle_set))


def db_loss_vs_oracle(predicted_idx: int, oracle_idx: int, beam_gains_db: list[float]) -> float:
    if not beam_gains_db:
        return 0.0
    pred = beam_gains_db[min(predicted_idx, len(beam_gains_db) - 1)]
    best = beam_gains_db[min(oracle_idx, len(beam_gains_db) - 1)]
    return max(0.0, best - pred)


def spectral_efficiency_loss(pred_se: float, oracle_se: float) -> float:
    return max(0.0, oracle_se - pred_se)


def inference_latency_ms(fn, *args, **kwargs) -> float:
    t0 = time.perf_counter()
    fn(*args, **kwargs)
    return (time.perf_counter() - t0) * 1000.0


def toy_beam_gains(n_beams: int = 64, seed: int = 42) -> list[float]:
    rng = random.Random(seed)
    return [rng.uniform(-15.0, 0.0) for _ in range(n_beams)]


def oracle_beam_index(gains: list[float]) -> int:
    return max(range(len(gains)), key=lambda i: gains[i])
