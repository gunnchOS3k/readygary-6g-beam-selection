"""Sequential dual-band policy (REINFORCE). Tabular Q remains the FR2 beam baseline."""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from sim.access.radio_decision import RadioDecisionContext
from sim.dualband.controller import decide


ACTIONS = ("stay_sub6", "stay_fr2", "switch_to_sub6", "switch_to_fr2")


def _state(m: dict) -> np.ndarray:
    return np.array(
        [
            float(m.get("sinr_sub6_db", 0.0)) / 20.0,
            float(m.get("sinr_fr2_db", 0.0)) / 20.0,
            1.0 if m.get("fr2_blockage") else 0.0,
            float(m.get("congestion", 0.0)),
            1.0 if m.get("indoor") else 0.0,
            float(m.get("velocity_mps", 0.0)) / 30.0,
        ],
        dtype=np.float64,
    )


def _softmax(z: np.ndarray) -> np.ndarray:
    z = z - np.max(z)
    e = np.exp(np.clip(z, -20, 20))
    return e / (np.sum(e) + 1e-18)


@dataclass
class SequentialBandPolicy:
    """Categorical policy π(a|s) = softmax(Ws). REINFORCE with baseline."""

    rng: np.random.Generator = field(default_factory=lambda: np.random.default_rng(0))
    w: np.ndarray = field(default_factory=lambda: np.zeros((6, 4)))
    baseline: float = 0.0

    def probs(self, s: np.ndarray) -> np.ndarray:
        return _softmax(s @ self.w)

    def act(self, s: np.ndarray) -> int:
        p = self.probs(s)
        return int(self.rng.choice(len(ACTIONS), p=p))

    def update(self, traj: list[tuple[np.ndarray, int, float]], lr: float = 0.05) -> float:
        returns = []
        g = 0.0
        for _, _, r in reversed(traj):
            g = r + 0.9 * g
            returns.append(g)
        returns.reverse()
        mean_g = float(sum(returns) / max(len(returns), 1))
        self.baseline = 0.9 * self.baseline + 0.1 * mean_g
        for (s, a, _), Gt in zip(traj, returns):
            p = self.probs(s)
            grad = -p
            grad[a] += 1.0
            adv = Gt - self.baseline
            self.w += lr * adv * np.outer(s, grad)
        return mean_g


def reward(ctx: RadioDecisionContext, action_name: str) -> tuple[float, RadioDecisionContext]:
    m = dict(ctx.measurements)
    family = "FR2" if "fr2" in action_name else "SUB6"
    if action_name.startswith("switch"):
        family = "SUB6" if "sub6" in action_name else "FR2"
    m["preferred_family"] = family
    ctx2 = RadioDecisionContext(
        device_class=ctx.device_class,
        workload=ctx.workload,
        available_families=ctx.available_families,
        measurements=m,
        twin_hint=ctx.twin_hint,
        previous=ctx.previous,
        seed=ctx.seed,
    )
    pol = "FR2_ONLY" if family == "FR2" else "SUB6_ONLY"
    dec = decide(pol, ctx2)
    useful = 1.0 if dec.min_useful_service else -1.0
    switch = float(dec.costs.get("switched", 0.0))
    outage = float(dec.costs.get("outage", 0.0))
    r = useful - 0.4 * switch - 0.8 * outage - 0.002 * float(dec.costs.get("interruption_ms", 0.0))
    ctx2.previous = dec
    return r, ctx2


def train_sequential(scenarios: list[RadioDecisionContext], *, seed: int = 0, epochs: int = 6) -> SequentialBandPolicy:
    pol = SequentialBandPolicy(rng=np.random.default_rng(seed))
    for _ in range(epochs):
        for ctx0 in scenarios:
            ctx = ctx0
            traj = []
            for t in range(6):
                s = _state(ctx.measurements)
                a = pol.act(s)
                r, ctx = reward(ctx, ACTIONS[a])
                traj.append((s, a, r))
                # Simple environment: blockage may persist; congestion mean-reverts.
                m = dict(ctx.measurements)
                m["congestion"] = min(1.0, max(0.0, float(m.get("congestion", 0.0)) * 0.8 + 0.05))
                ctx.measurements = m
            pol.update(traj)
    return pol


def classify_rl() -> dict[str, str]:
    return {
        "adaptive_constrained_rl": "TABULAR_Q",
        "adaptive_bandit": "EPSILON_GREEDY_BANDIT",
        "sequential_band_policy": "REINFORCE_SEQUENTIAL",
        "note": "Tabular Q is a valid FR2 beam baseline. Sequential policy acts on stay/switch over time.",
    }
