"""Publication-grade beam selection metrics (toy/real)."""
from __future__ import annotations


def top_k_accuracy(predicted_ranks: list[int], oracle_rank: int, k: int = 1) -> float:
    hits = sum(1 for p in predicted_ranks if p <= k and oracle_rank <= k)
    return hits / len(predicted_ranks) if predicted_ranks else 0.0


def db_loss_vs_oracle(predicted_db: float, oracle_db: float) -> float:
    return max(0.0, predicted_db - oracle_db)


def spectral_efficiency_loss(se_pred: float, se_oracle: float) -> float:
    if se_oracle <= 0:
        return 0.0
    return max(0.0, (se_oracle - se_pred) / se_oracle)


def inference_latency_ms(n_params: int = 1000) -> float:
    return 0.01 * n_params  # toy stub
