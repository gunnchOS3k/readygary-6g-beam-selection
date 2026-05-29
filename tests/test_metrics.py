import pytest
from sim.metrics import top_k_accuracy, db_loss_vs_oracle


def test_top_k():
    assert top_k_accuracy([1, 2, 1], 1, k=1) >= 0


def test_db_loss():
    assert db_loss_vs_oracle(2.0, 0.0) == 2.0
