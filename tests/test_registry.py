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

"""Main tests."""

from scibench.registry import Item, _MetaItem


class BaseMetaItemTest:
    """Base class for test class that use the _MetaItem class (directly or indirectly)."""

    def setup(self) -> None:
        """Set up the test."""
        _MetaItem._meta_registry = {}

    def teardown(self) -> None:
        """Tear down the test."""
        _MetaItem._meta_registry = {}


class TestItem(BaseMetaItemTest):
    """Test the definition of item classes."""

    def test_run(self) -> None:
        """Run the test."""

        class ItemA(Item):
            """Item of type A."""

            class_id = "a"

        class ItemB(Item):
            """Item of type B."""

            class_id = "b"

        class ItemA1(ItemA):
            """Item A1, of type ItemA."""

            item_id = "a1"

        class ItemA2(ItemA):
            """Item A2, of type ItemA."""

            item_id = "a2"

        class ItemB1(ItemB):
            """Item B1, of type ItemB."""

            item_id = "b1"
