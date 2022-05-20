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

"""SciBench main entrypoint."""
import argparse
from pathlib import Path

import yaml

from scibench.experiment import AbstractExperiment, configuration_from_dict
from scibench.helpers import load

if __name__ == "__main__":

    parser = argparse.ArgumentParser("scibench")
    parser.add_argument(
        "--config", type=str, required=True, help="Path to configuration file."
    )

    arguments = parser.parse_args()
    config = configuration_from_dict(
        yaml.load(Path(arguments.config).open(), yaml.SafeLoader)
    )
    experiment_cls = load(config.experiment_cls)
    experiment: AbstractExperiment = experiment_cls(config)
    experiment.run_experiment()
