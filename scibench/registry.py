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

"""This module contains the implementation of a generic registry."""
import importlib
from abc import ABC, ABCMeta
from collections import deque
from typing import Any, Dict, Generic, Optional, Type, TypeVar, Union, cast

from scibench.helpers import (
    EntryPointId,
    EntryPointIdOrStr,
    ItemId,
    ItemIdOrStr,
    RegistryId,
    RegistryIdOrStr,
    enforce,
    is_direct_subclass,
    load,
)


class _MetaItem(ABCMeta):
    """A metaclass for items."""

    _meta_registry: Dict[RegistryId, "Registry"] = {}

    def __new__(mcs, name, bases, namespace, **kwargs):
        cls = super().__new__(mcs, name, bases, namespace, **kwargs)
        if name == "Item" and namespace["__module__"] == "scibench.registry":
            # this is the Item abstract class
            return cls

        enforce(issubclass(cls, Item), "only Item subclasses are allowed")
        cls_ = cast(Type[Item], cls)
        mcs.register_item_class(cls_)
        return cls_

    @classmethod
    def get_registry(mcs, class_id: RegistryIdOrStr) -> "Registry":
        """Get registry of a class id."""
        class_id = RegistryId(class_id)
        enforce(class_id in mcs._meta_registry, f"class id {class_id} not registered")
        return mcs._meta_registry[class_id]

    @classmethod
    def register_item_class(mcs, item_cls: Type["Item"]) -> None:
        """Register an item class."""
        if is_direct_subclass(item_cls, Item):
            mcs._handle_direct_item_subclass(item_cls)
        else:
            # not a direct subclass; need to check if item_id is already registered
            mcs._handle_non_direct_subclass(item_cls)

    @classmethod
    def _handle_direct_item_subclass(mcs, item_cls: Type["Item"]) -> None:
        """Handle a class which is a direct Item subclass."""
        assert is_direct_subclass(item_cls, Item)
        mcs._check_no_other_item_superclasses(item_cls)
        mcs._check_attribute_set(item_cls, "class_id")
        mcs._check_attribute_not_set(item_cls, "item_id")
        mcs._check_class_id_not_registered_with_different_class(
            item_cls.class_id, item_cls
        )
        mcs._meta_registry[item_cls.class_id] = Registry[item_cls](item_cls)

    @classmethod
    def _handle_non_direct_subclass(mcs, item_cls: Type["Item"]) -> None:
        """Handle a non-direct subclass of Item."""
        mcs._check_attribute_set(item_cls, "class_id")
        mcs._check_attribute_set(item_cls, "item_id")
        mcs._check_attribute_set(item_cls, "default_kwargs")
        ItemId(item_cls.item_id)
        mcs._check_only_one_item_ancestor(item_cls)
        if item_cls.register:
            mcs._meta_registry[item_cls.class_id].register(
                item_cls.item_id, item_cls, **item_cls.default_kwargs
            )

    @classmethod
    def _check_attribute_not_set(mcs, cls: Any, attr_name: str) -> None:
        """Check that a class has not set an attribute."""
        enforce(
            not hasattr(cls, attr_name),
            f"expected class {cls} not defined attribute {attr_name}",
            ValueError,
        )

    @classmethod
    def _check_attribute_set(mcs, cls: Type, attr_name: str) -> None:
        """Check that a class has set an attribute."""
        enforce(
            hasattr(cls, attr_name),
            f"expected class {cls} defined attribute {attr_name}",
            ValueError,
        )

    @classmethod
    def _check_class_id_same_of_parent(mcs, item_cls: Type["Item"]) -> None:
        """Check that Item direct subclass has class attribute 'class_id'."""
        assert is_direct_subclass(item_cls, Item)
        enforce(
            hasattr(item_cls, "class_id"),
            "direct subclasses of Item must define class attribute 'class_id'",
            ValueError,
        )

    @classmethod
    def _check_class_id_not_registered_with_different_class(
        mcs, class_id: RegistryId, item_cls: Type
    ) -> None:
        """Check that a class id has not been registered already."""
        enforce(
            class_id not in mcs._meta_registry
            or mcs._meta_registry[class_id] != item_cls,
            f"class id {class_id} already registered by Item class {mcs._meta_registry.get(class_id)}",
            ValueError,
        )

    @classmethod
    def _check_no_other_item_superclasses(mcs, item_cls: Type["Item"]) -> None:
        """Check there are no other item superclasses."""
        assert is_direct_subclass(item_cls, Item)
        bases = item_cls.__bases__
        enforce(
            len([base for base in bases if base == Item]) == 1,
            "more than one Item superclass found",
            ValueError,
        )
        for base in bases:
            if base == Item:
                continue
            enforce(
                not issubclass(base, Item),
                "item subclass has a superclass which is a subclass of the Item base class",
                ValueError,
            )

    @classmethod
    def _check_only_one_item_ancestor(mcs, item_cls: Type["Item"]) -> None:
        """Check there is only one item subclass ancestor."""
        bases = item_cls.__bases__
        item_subclasses = tuple(filter(lambda b: issubclass(b, Item), bases))
        queue = deque(item_subclasses)
        item_direct_subclasses = set()
        while len(queue) > 0:
            current_base = queue.popleft()
            if not issubclass(current_base, Item):
                continue
            if is_direct_subclass(current_base, Item):
                item_direct_subclasses.add(current_base)
            new_bases = current_base.__bases__
            queue.extend(new_bases)
        enforce(
            len(item_direct_subclasses) == 1,
            f"found more than one Item direct subclasses: {{{', '.join(map(str, item_direct_subclasses))}}}",
        )
        item_direct_subclass = list(item_direct_subclasses)[0]

        enforce(
            item_cls.class_id == item_direct_subclass.class_id,
            f"class ids do not match: {item_cls} has {item_cls.class_id}, {item_direct_subclass} has {item_direct_subclass.class_id}",
        )

    @classmethod
    def register_non_item_class(
        mcs, class_id: RegistryIdOrStr, item_cls: Type, registry: Any = None
    ) -> None:
        """Register a non-item subclass."""
        class_id = RegistryId(class_id)
        enforce(
            not issubclass(item_cls, Item),
            f"class {item_cls} already a subclass of Item, it is automatically registered",
        )
        mcs._check_class_id_not_registered_with_different_class(class_id, item_cls)
        if registry is not None:
            _MetaItem._meta_registry[class_id] = registry
        else:
            _MetaItem._meta_registry[class_id] = Registry[item_cls](item_cls)


class Item(ABC, metaclass=_MetaItem):
    """Abstract item that can be added to the registry."""

    class_id: RegistryId
    item_id: ItemId
    register: bool = True
    default_kwargs: Dict[str, Any] = {}


ItemType = TypeVar("ItemType")


class _ItemSpec(Generic[ItemType]):
    """A specification for a particular instance of an object."""

    def __init__(
        self,
        item_id: str,
        item_cls: Type[ItemType],
        **kwargs: Dict,
    ) -> None:
        """
        Initialize an item specification.

        :param id_: the id associated to this specification
        :param item_cls: the Model class
        :param kwargs: other custom keyword arguments.
        """
        self.item_id = item_id
        self.item_cls = item_cls
        self.kwargs = {} if kwargs is None else kwargs

    def make(self, *args, **kwargs) -> ItemType:
        """
        Instantiate an instance of the item object with appropriate arguments.

        :return: an item
        """
        _kwargs = self.kwargs.copy()
        # # no overrides
        # enforce(_kwargs.keys().isdisjoint(kwargs))
        _kwargs.update(**kwargs)
        item = self.item_cls(*args, **_kwargs)
        return item


class Registry(Generic[ItemType]):
    """Item registry."""

    def __init__(self, item_type: Type[ItemType]):
        """Initialize the registry."""
        self._specs: Dict[ItemId, _ItemSpec[ItemType]] = {}
        self._item_supercls = item_type
        if issubclass(item_type, Item):
            enforce(
                is_direct_subclass(self._item_supercls, Item),
                "subclass of Item is not a direct subclass of Item",
                ValueError,
            )

    def register(
        self,
        item_id: ItemIdOrStr,
        item_cls: Optional[ItemType] = None,
        entry_point: Optional[EntryPointIdOrStr] = None,
        **kwargs: Any,
    ):
        """Register an item."""
        item_cls_not_none = item_cls is not None
        entry_point_not_none = entry_point is not None
        enforce(
            item_cls_not_none != entry_point_not_none,
            "only one of 'item_cls' and 'entry_point' must be provided",
            ValueError,
        )

        if entry_point_not_none:
            entrypoint = EntryPointId(entry_point)
            item_cls = load(entrypoint)
        enforce(
            issubclass(item_cls, self._item_supercls),
            f"{item_cls} not a subclass of {self._item_supercls}",
            ValueError,
        )
        item_id = ItemId(item_id)
        self._specs[item_id] = _ItemSpec[ItemType](item_id, item_cls, **kwargs)

    def make(self, item_id: ItemIdOrStr, *args, **kwargs) -> ItemType:
        """
        Make the Model.

        :param item_id: the item ID
        :return: the item instance
        """
        item_id = ItemId(item_id)
        if item_id not in self._specs:
            raise ValueError(f"Item id '{item_id}' not configured")
        item_spec = self._specs[item_id]
        return item_spec.make(*args, **kwargs)


def register_class(
    class_id: RegistryIdOrStr, item_cls: Type, registry: Any = None
) -> None:
    """Register an Item class which is not a subclass of Item."""
    class_id = RegistryId(class_id)
    _MetaItem.register_non_item_class(class_id, item_cls, registry)


def get_registry(class_id: RegistryIdOrStr) -> Registry:
    """Get a registry, given the class id."""
    return _MetaItem.get_registry(class_id)
