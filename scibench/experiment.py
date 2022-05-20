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

"""This module contains the implementation of a generic experiment."""
import dataclasses
import itertools
import logging
import shutil
from abc import ABC, abstractmethod
from copy import deepcopy
from logging import Logger
from pathlib import Path
from typing import Any, Dict, List, Mapping, Optional

from joblib import Parallel, delayed

from scibench.helpers import (
    EntryPointId,
    ItemId,
    RegistryId,
    RegistryIdOrStr,
    configure_logging,
)


@dataclasses.dataclass
class ItemConfiguration:
    class_id: RegistryId
    name: str
    item_id: ItemId
    kwargs: Dict[str, Any]
    entry_point: Optional[str] = None


@dataclasses.dataclass
class ExperimentConfiguration:
    item_configurations: Dict[RegistryId, List[ItemConfiguration]]
    run_configuration: Dict[str, Any]
    experiment_cls: EntryPointId
    root_output_dir: Path
    nb_jobs: int = 1
    nb_runs: int = 10


class AbstractExperiment(ABC):
    """Class for running experiments."""

    def __init__(self, config: ExperimentConfiguration) -> None:
        """Initialize."""
        self.config = config

    @abstractmethod
    def run(
        self,
        item_configurations: Dict[RegistryIdOrStr, ItemConfiguration],
        run_configuration: Dict[str, Any],
        run_id: int,
        output_path: Path,
    ) -> None:
        """Do a run."""

    def _produce_tasks(self, logger: Logger):
        classes, item_classes = zip(*self.config.item_configurations.items())
        item_combinations = itertools.product(*item_classes)
        for item_combination in item_combinations:
            current_experiment_dir = self.config.root_output_dir
            for item_config in item_combination:
                current_experiment_dir = current_experiment_dir / item_config.item_id
            current_experiment_dir.mkdir(parents=True, exist_ok=True)
            dict_item_configurations = dict(zip(classes, item_combination))
            nb_runs_digits = str(len(str(self.config.nb_runs - 1)))
            for run_id in range(self.config.nb_runs):
                run_dir_name = ("{run_id:0" + nb_runs_digits + "d}").format(
                    run_id=run_id
                )
                current_experiment_run_dir = current_experiment_dir / run_dir_name
                current_experiment_run_dir.mkdir(parents=True)
                experiment_id = current_experiment_run_dir.relative_to(
                    self.config.root_output_dir
                )
                logger.info(f"Launching experiment {experiment_id}")
                try:
                    yield deepcopy(
                        dict_item_configurations
                    ), run_id, current_experiment_run_dir
                except KeyboardInterrupt:
                    logger.warning("keyboard interrupt received. Exiting...")
                    return
                except Exception:
                    logger.exception("exception occurred:")
                    raise

    def run_experiment(self) -> None:
        """Run a full experiment."""
        shutil.rmtree(self.config.root_output_dir)
        self.config.root_output_dir.mkdir(parents=True)

        # set up logging
        logging_path = self.config.root_output_dir / "output.log"
        logger = configure_logging("main", filename=str(logging_path))

        logger.info(f"Running experiment in folder {self.config.root_output_dir}")

        # # remember Git info
        # dump_git_info(self.config.root_output_dir, logger)

        with Parallel(n_jobs=self.config.nb_jobs) as parallel:
            parallel(
                delayed(self.run)(
                    dict_item_configurations,
                    self.config.run_configuration,
                    run_id,
                    current_experiment_run_dir,
                )
                for dict_item_configurations, run_id, current_experiment_run_dir in self._produce_tasks(
                    logger
                )
            )


def configuration_from_dict(obj: Mapping[str, Any]) -> ExperimentConfiguration:
    """
    Load a configuration from a dictionary.

    No consistency check is made over the input.
    """
    item_configurations = {}
    for class_id, items in obj["classes"].items():
        item_configurations[class_id] = []
        for item_name, item_spec in items.items():
            item_id = item_spec["item_id"]
            item_config = item_spec.get("config", {})
            item_configuration_obj = ItemConfiguration(
                class_id, item_name, item_id, item_config
            )
            item_configurations[class_id].append(item_configuration_obj)

    run_config = obj["run"]
    nb_runs = obj["nb_runs"]
    nb_jobs = obj["nb_jobs"]
    root_output_dir = Path(obj["output_dir"])
    experiment_cls = EntryPointId(obj["experiment_cls"])
    return ExperimentConfiguration(
        item_configurations,
        run_config,
        experiment_cls,
        root_output_dir,
        nb_jobs,
        nb_runs,
    )
