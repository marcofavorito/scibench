from abc import abstractmethod
from collections import defaultdict
from typing import Any, Dict, List, Optional, cast

import gym
import numpy as np
from gym.spaces import Discrete
from utils import np_random

from examples.rl.policies import AbstractPolicy, GreedyPolicy
from scibench.helpers import enforce
from scibench.registry import Item


class AbstractAgent(Item):
    """An abstract RL agent."""

    class_id = "agent"

    _seed: Optional[int]
    _rng: np.random.Generator

    def __init__(self, policy: AbstractPolicy, env: gym.Env) -> None:
        """
        Initialize the agent.

        :param env: the gym Environment.
        """
        self._policy = policy
        self._env = env

    @abstractmethod
    def learn(self, time_steps: int, seed: Optional[int] = None) -> None:
        """
        Learn from the environment.

        :param time_steps: the number of time steps.
        :param seed: the random seed.
        """

    @abstractmethod
    def best_action(self, obs) -> Any:
        """Return best action."""

    @property
    def action_space(self):
        return self._env.action_space

    def _set_seed(self, seed: Optional[int] = None):
        """Set seed."""
        self._seed = seed
        self._rng = np_random(seed)
        self._policy.seed(seed=seed)
        self._env.reset(seed=seed)
        self._env.action_space.seed(seed=seed)
        self._env.observation_space.seed(seed=seed)

    def test(self, time_steps: int, render: bool = False) -> List:
        env = self._env
        current_episode = 0
        current_time_step = 0
        histories = []

        while current_time_step < time_steps:
            history = []
            obs = env.reset()
            current_episode += 1
            done = False
            while not done and current_time_step < time_steps:
                action = self._policy.get_action(self, obs)
                next_obs, reward, done, info = env.step(action)
                current_time_step += 1
                history.append((obs, action, reward, next_obs))
                obs = next_obs
                if render:
                    env.render()
                if done:
                    histories.append(history)
                    break
        return histories


class QLearning(AbstractAgent):

    item_id = "q-learning"

    def __init__(
        self,
        policy: AbstractPolicy,
        env: gym.Env,
        alpha: float = 0.1,
        gamma: float = 0.9,
    ) -> None:
        """Initialize the Q-learning agent."""
        super().__init__(policy, env)

        self._alpha = alpha
        self._gamma = gamma

        enforce(isinstance(env.action_space, Discrete))
        n_actions = cast(Discrete, env.action_space).n
        self._Q: Dict[Any, np.ndarray] = defaultdict(
            lambda: self._rng.random(n_actions) * 0.01
        )

    def best_action(self, obs) -> Any:
        """Get action."""
        return self._Q[obs].argmax()

    def learn(self, time_steps: int, seed: Optional[int] = None) -> List:
        """Learn from the environment."""
        env = self._env
        self._set_seed(seed)
        current_episode = 0
        current_time_step = 0
        histories = []

        while current_time_step < time_steps:
            history = []
            obs = env.reset()
            current_episode += 1
            done = False
            while not done and current_time_step < time_steps:
                action = self._policy.get_action(self, obs)
                next_obs, reward, done, info = env.step(action)
                current_time_step += 1
                self.update(obs, action, reward, next_obs)
                history.append((obs, action, reward, next_obs))
                obs = next_obs
                if done:
                    histories.append(history)
                    break
        return histories

    def update(self, obs, action, reward, next_obs) -> None:
        """Do the Q-learning update."""
        old_q = self._Q[obs][action]
        self._Q[obs][action] += +self._alpha * (
            reward + self._gamma * np.max(self._Q[next_obs]) - old_q
        )


class Sarsa(AbstractAgent):

    item_id = "sarsa"

    def __init__(
        self,
        policy: AbstractPolicy,
        env: gym.Env,
        alpha: float = 0.1,
        gamma: float = 0.9,
    ) -> None:
        """Initialize the Q-learning agent."""
        super().__init__(policy, env)

        self._alpha = alpha
        self._gamma = gamma

        enforce(isinstance(env.action_space, Discrete))
        n_actions = cast(Discrete, env.action_space).n
        self._Q: Dict[Any, np.ndarray] = defaultdict(
            lambda: np.random.random(n_actions) * 0.01
        )

    def best_action(self, obs) -> Any:
        """Get action."""
        return self._Q[obs].argmax()

    def learn(self, time_steps: int, seed: Optional[int] = None) -> List:
        """Learn from the environment."""
        env = self._env
        self._set_seed(seed)
        current_episode = 0
        current_time_step = 0
        histories = []

        while current_time_step < time_steps:
            history = []
            obs = env.reset()
            action = self._policy.get_action(self, obs)
            current_episode += 1
            done = False
            while not done and current_time_step < time_steps:
                next_obs, reward, done, info = env.step(action)
                current_time_step += 1
                next_action = self._policy.get_action(self, obs)
                self.update(obs, action, reward, next_obs, next_action)
                history.append((obs, action, reward, next_obs))
                obs = next_obs
                action = next_action
                if done:
                    histories.append(history)
                    break
        return histories

    def update(self, obs, action, reward, next_obs, next_action) -> None:
        """Do the Q-learning update."""
        old_q = self._Q[obs][action]
        self._Q[obs][action] += +self._alpha * (
            reward + self._gamma * self._Q[next_obs][next_action] - old_q
        )
