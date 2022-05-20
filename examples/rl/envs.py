#
# Copyright 2022 Marco Favorito
#
# ------------------------------
#
# This file is part of scibench.
#
# scibench is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# scibench is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with scibench.  If not, see <https://www.gnu.org/licenses/>.
#
import gym
from gym.core import Env

from scibench.registry import get_registry, register_class

register_class("env", Env, gym.envs.registration.registry)

get_registry("env").register(
    "Taxi-v3",
    entry_point="gym.envs.toy_text:TaxiEnv",
    reward_threshold=8,
    max_episode_steps=200,
)

get_registry("env").register(
    "FrozenLake-v1",
    entry_point="gym.envs.toy_text:FrozenLakeEnv",
    kwargs={"map_name": "4x4"},
    max_episode_steps=100,
    reward_threshold=0.70,
)
