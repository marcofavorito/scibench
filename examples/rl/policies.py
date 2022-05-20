from abc import abstractmethod
from typing import Any, Optional

import numpy as np
from utils import np_random

from scibench.registry import Item


class AbstractPolicy(Item):
    """Abstract Policy."""

    class_id = "policy"
    _rng: np.random.Generator

    @abstractmethod
    def get_action(self, agent: "AbstractAgent", obs: Any) -> None:
        """Get action."""

    def seed(self, seed: Optional[int] = None) -> None:
        """Seed the PRNG of this policy."""
        self._rng = np_random(seed=seed)


class GreedyPolicy(AbstractPolicy):
    """Greedy policy."""

    item_id = "greedy"

    def get_action(self, agent: "AbstractAgent", obs: Any) -> None:
        return agent.best_action(obs)


class EpsGreedyPolicy(AbstractPolicy):
    """Eps-Greedy policy."""

    item_id = "eps-greedy"
    default_kwargs = dict(eps=0.1)

    def __init__(self, eps: float = 0.1):
        self._eps = eps

    def get_action(self, agent: "AbstractAgent", obs: Any) -> None:
        if self._rng.random() < self._eps:
            return agent.action_space.sample()
        return agent.best_action(obs)
