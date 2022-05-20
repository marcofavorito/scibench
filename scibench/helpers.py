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

"""Helper functions."""
import importlib
import logging
import re
from collections import UserString
from pathlib import Path
from typing import Optional, Type, Union

from git import Repo


def enforce(
    condition: bool, message: str = "", exception_cls: Type[Exception] = AssertionError
):
    """User-defined assert."""
    if not condition:
        raise exception_cls(message)


def is_direct_subclass(subcls: Type, supercls: Type) -> bool:
    """
    Check if a class is a direct subclass of another class.

    :param subcls: the supposed subclass
    :param supercls: the supposed superclass
    :return: True if subcls is a direct subclass of supercls, false otherwise.
    """
    return subcls in supercls.__subclasses__()


def configure_logging(
    logger_name: str, has_console: bool = True, filename: Optional[str] = None
) -> logging.Logger:
    """
    Configure logging.

    :param logger_name: the logger name.
    :param has_console: has console handler
    :param filename: the output file
    :return: the logger
    """
    logger = logging.getLogger(logger_name)
    logger.handlers = []
    handlers = []
    if has_console:
        console = logging.StreamHandler()
        handlers += [console]
    if filename:
        file = logging.FileHandler(filename)
        handlers += [file]
    formatter = NewLineFormatter("[{asctime}][{name}][{levelname:^5s}] {message}")
    for handler in handlers:
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    logger.setLevel(logging.DEBUG)
    return logger


class NewLineFormatter(logging.Formatter):
    def __init__(self, fmt, datefmt=None, style="{"):
        """
        Init given the log line format and date format
        """
        logging.Formatter.__init__(self, fmt, datefmt, style=style)

    def format(self, record):
        """
        Override format function
        """
        msg = logging.Formatter.format(self, record)

        if record.message != "":
            parts = msg.split(record.message)
            msg = msg.replace("\n", "\n" + parts[0])

        return msg


def dump_git_info(output_directory: Path, logger: logging.Logger):
    repo = Repo()
    commit_hex = repo.commit().hexsha
    git_diff = repo.git.diff()

    # save commit hex
    logger.info(f"Writing git commit info: {commit_hex}")
    (output_directory / "git-commit-hex.txt").write_text(commit_hex)
    logger.info(f"Writing git diff patch:\n{git_diff}")
    (output_directory / "git-diff.patch").write_text(git_diff)


class RegexConstrainedString(UserString):
    """
    A string that is constrained by a regex.
    The default behaviour is to match anything.
    Subclass this class and change the 'REGEX' class
    attribute to implement a different behaviour.
    """

    REGEX = re.compile(".*", flags=re.DOTALL)

    def __init__(self, seq: Union[UserString, str]) -> None:
        """Initialize a regex constrained string."""
        super().__init__(seq)

        if not self.REGEX.fullmatch(self.data):
            self._handle_no_match()

    def _handle_no_match(self) -> None:
        raise ValueError(
            "Value {data} does not match the regular expression {regex}".format(
                data=self.data, regex=self.REGEX
            )
        )


class ItemId(RegexConstrainedString):
    """Class to represent item ids."""

    REGEX = re.compile("[A-Za-z_][a-zA-Z\\d_-]{0,31}")


class RegistryId(RegexConstrainedString):
    """Class to represent registry ids."""

    REGEX = re.compile("[a-z_][a-z\\d_-]{0,31}")


def _get_entrypoint_id_pattern() -> str:
    """Compute the pattern for the entrypoint id."""
    item_id_pattern = ItemId.REGEX.pattern

    module_name_pattern = "[a-zA-Z_]\w*"
    python_import_path = f"{module_name_pattern}(\.{module_name_pattern})*"

    final_pattern = f"{python_import_path}:{item_id_pattern}"
    return final_pattern


class EntryPointId(RegexConstrainedString):
    """Class to represent registry ids."""

    REGEX = re.compile(_get_entrypoint_id_pattern())


ItemIdOrStr = Union[ItemId, str]
RegistryIdOrStr = Union[RegistryId, str]
EntryPointIdOrStr = Union[EntryPointId, str]


def load(entry_point: EntryPointIdOrStr) -> Type:
    """Load a class."""
    entry_point = EntryPointId(entry_point)
    mod_name, attr_name = entry_point.split(":")
    mod = importlib.import_module(mod_name)
    fn = getattr(mod, attr_name)
    return fn
