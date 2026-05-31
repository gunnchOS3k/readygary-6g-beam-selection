from sim.metrics import db_loss_vs_oracle, top_k_accuracy, toy_beam_gains, oracle_beam_index


def test_top_k_perfect_when_same():
    assert top_k_accuracy([0, 1, 2], [0, 1, 2], k=3) == 1.0


def test_toy_gains_oracle():
    g = toy_beam_gains(16, seed=1)
    idx = oracle_beam_index(g)
    assert 0 <= idx < len(g)
