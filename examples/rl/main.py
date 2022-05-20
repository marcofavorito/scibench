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
import logging
from pathlib import Path
from typing import Any, Dict

import algo
import envs
import numpy as np
from policies import EpsGreedyPolicy

from scibench.experiment import AbstractExperiment, ItemConfiguration
from scibench.helpers import RegistryIdOrStr, configure_logging
from scibench.registry import get_registry


class RLExperiment(AbstractExperiment):
    def run(
        self,
        item_configurations: Dict[RegistryIdOrStr, ItemConfiguration],
        run_configuration: Dict[str, Any],
        run_id: int,
        output_path: Path,
    ) -> None:
        logging_path = output_path / "output.log"
        logger = configure_logging(f"{output_path}", filename=str(logging_path))
        logger.info(f"Starting experiment run {output_path}")
        env_config = item_configurations["env"]
        agent_config = item_configurations["agent"]

        eps = agent_config.kwargs.pop("eps")
        time_steps = run_configuration["time_steps"]

        env = get_registry("env").make(env_config.item_id, **env_config.kwargs)
        policy = EpsGreedyPolicy(eps=eps)
        agent = get_registry("agent").make(
            agent_config.item_id, policy=policy, env=env, **agent_config.kwargs
        )
        train_histories = agent.learn(time_steps=time_steps, seed=run_id)
        train_histories = np.array(train_histories, dtype=object)
        np.save(str(output_path / "histories"), train_histories)
        logger.info(f"Experiment run {output_path} done!")
