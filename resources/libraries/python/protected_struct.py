# Copyright (c) 2021 Cisco and/or its affiliates.
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at:
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Library defining a types and utilities for "read only" data steructures.

For read access, the structures look like a deserialized JSON
with dicts and lists. But attempts to mutate the state lead to failures,
which allows only some call sites to facilitate write access,
usually keywords in topology.Topology to ensure proper logging.

Also sub-structures are protected, while still acting as references
so successful edit on one structure is visible in other structures.

The implementation uses new classes to replace lists and dicts, recursively.
"""


from abc import ABC
#from collections.abc import Iterable, Mapping, MutableSequence, MutableMapping
from collections.abc import MutableSequence, MutableMapping


def protect_object(obj):
    """Return maybe wrapped object containing protected sub-structures.

    In case of simple (leaf) types, the same value (or reference) is returned.
    Composite substructures are wrapped using ProtectedDict or ProtectedList,
    while the original containers are still used to make edits visible.
    This wrapping is done recursively.
    Values already wrapped are not wrapped again (substructures not examined).
    The top level container is also wrapped.

    Namedtuples are not explicitly supported.

    TODO: Is support for non-mutable substructures needed?
    TODO: Should we re-examine nominally protected substructures?

    :param obj: The structure to protect.
    :type obj: object
    :returns: The same structure but wrapped and mutated to protected values.
    :rtype: ProtectedStructure
    :raises TypeError: If a type is found that we do not know how protect,
        or if a mapping has non-string keys.
    """
    if isinstance(obj, ProtectedStructure):
        return obj
    if isinstance(obj, MutableMapping):
        return ProtectedDict(obj)
    #if isinstance(obj, Mapping):
    #    return ProtectedDict(dict(obj))
    if isinstance(obj, MutableSequence):
        return ProtectedList(obj)
    #if isinstance(obj, Iterable):
    #    return ProtectedList(list(obj))
    raise TypeError(f"Unsupported type, value: {obj!r}")


class ProtectedDict(MutableMapping):
    """A class looking like a dict, but with mutability not directly available.

    Mutating methods have different names, so only informed call sites
    are able to mutate the state.
    Any dict- or list- like attempts at mutating any sub-structure will fail.
    Devoted uninformed callers can still mutate data, e.g. by calling __init__.

    For for read access, this class looks like a dict.
    """

    def __init__(self, mapping):
        """Construct, with protected content.

        The mapping is modified in place to contain protected values.
        Only string keys are supported.

        :param mapping: Content to protect, usually a dict.
        :type mapping: collections.abc.MutableMapping[str, object]
        :raises TypeError: If mapping contains unprotectable sub-data,
            or if a key is not string.
        """
        for key, value in mapping.items():
            mapping[key] = self.protect_item(key, value)
        self._dict = mapping

    @staticmethod
    def protect_item(key, value):
        """Check key, convert value to be protected.

        :param key: Key has to be string.
        :param value: Value to return or convert yo protected structure.
        :type key: str
        :type value: object
        :raises TypeError: If value is not protectable, or if key is not string.
        """
        if not isinstance(key, str):
            raise TypeError(f"Not a string key: {key!r}")
        if not isinstance(value, ProtectedStructure):
            value = protect_object(value)
        return value

    def __repr__(self):
        """Return a string as if this was a non-protected dict.

        :returns: Executable Python text of this as a dict.
        :rtype: str
        """
        return repr(self._dict)

    def __iter__(self):
        """Return iterator acting on the wrapped dict.

        :returns: Iterator for read access.
        :rtype: Iterator[Hashable]
        """
        return iter(self._dict)

    def __len__(self):
        """Return number of keys present.

        :return: Size of the mapping.
        :rtype: int
        """
        return len(self._dict)

    def __getitem__(self, key):
        """Get value for the key.

        :param key: Key to get value for.
        :type key: Hashable
        :returns: The value for the key.
        :rtype: object
        :raises KeyError: If the key is not present.
        """
        return self._dict[key]

    def copy(self):
        """Return shallowly mutable copy.

        :returns: Shallow copy, values are still protected.
        :rtype: dict
        """
        return self._dict.copy()

    def protected_set_item(self, key, value):
        """Add or replace the item.

        Key has to be string, value will get protected.

        :param key: Key to add/replace value under.
        :param value: Value to add/replace.
        :type key: str
        :type value: object
        :raises TypeError: If value is not protectable, or if key is not string.
        """
        value = self.protect_item(key, value)
        self._dict[key] = value

    def __setitem__(self, key, value):
        """Raise when dict-like add/replace is attempted.

        :param key: Key to add/replace value under.
        :param value: Value to add/replace.
        :type key: Hashable
        :type value: object
        :raises RuntimeError: On any mutation attempt.
        """
        raise RuntimeError(u"Setitem not allowed: {self!r}")

    def protected_del_item(self, key):
        """Delete the item by the key.

        :param key: Key to delete value under.
        :type key: str
        :raises KeyError: If key is not present.
        """
        del self._dict[key]

    def __delitem__(self, key):
        """Raise when dict-like delete is attempted.

        :param key: Key to delete value under.
        :type key: str
        :raises RuntimeError: On any mutation attempt.
        """
        raise RuntimeError(u"Delitem not allowed: {self!r}")


class ProtectedList(MutableSequence):
    """A class looking like a list, but with mutability not directly available.

    Mutating methods have different names, so only informed call sites
    are able to mutate the state.
    Any dict- or list- like attempts at mutating any sub-structure will fail.
    Devoted uninformed callers can still mutate data, e.g. by calling __init__.

    For for read access, this class looks like a list.
    """

    def __init__(self, sequence):
        """Construct, with protected content.

        The sequence is modified in place to contain protected values.

        :param sequence: Content to protect, usually a list.
        :type sequence: collections.abc.MutableSequence[object]
        :raises TypeError: If sequence contains unprotectable sub-data.
        """
        for index, element in enumerate(sequence):
            sequence[index] = protect_object(element)
        self._list = sequence

    def __repr__(self):
        """Return a string as if this was a non-protected list.

        :returns: Executable Python text of this as a list.
        :rtype: str
        """
        return repr(self._list)

    def __iter__(self):
        """Return iterator acting on the wrapped list.

        :returns: Iterator for read access.
        :rtype: Iterator[object]
        """
        return iter(self._list)

    def __len__(self):
        """Return number of elements present.

        :return: Size of the list.
        :rtype: int
        """
        return len(self._list)

    def __getitem__(self, index):
        """Get element at the index.

        :param index: Index to get element for.
        :type index: int
        :returns: Reference for the element.
        :rtype: object
        :raises IndexError: If the index is out of bounds.
        """
        return self._list[index]

    def copy(self):
        """Return shallowly mutable copy.

        :returns: Shallow copy, elements are still protected.
        :rtype: list
        """
        return self._list.copy()

    def protected_set_item(self, index, element):
        """Replace the element at the index.

        New element will get protected.

        :param index: Index to replace element under.
        :param element: Element to replace with.
        :type index: int
        :type element: object
        :raises TypeError: If element is not protectable
        :raises IndexError: If the index is out of bounds.
        """
        element = protect_object(element)
        self._list[index] = element

    def __setitem__(self, index, element):
        """Raise when list-like replace is attempted.

        :param index: Index to replace element under.
        :param element: Element to replace with.
        :type index: int
        :type element: object
        :raises RuntimeError: On any mutation attempt.
        """
        raise RuntimeError(u"Setitem not allowed: {self!r}")

    def protected_del_item(self, index):
        """Delete the element at the index.

        :param index: Index to delete element under.
        :type index: int
        :raises IndexError: If the index is out of bounds.
        """
        del self._list[index]

    def __delitem__(self, key):
        """Raise when list-like delete is attempted.

        :param index: Index to delete element under.
        :type index: int
        :raises RuntimeError: On any mutation attempt.
        """
        raise RuntimeError(u"Delitem not allowed: {self!r}")

    def protected_insert(self, index, element):
        """Insert the element just before the index.

        New element will get protected.

        :param index: Index to insert element before.
        :param element: Element to insert.
        :type index: int
        :type element: object
        :raises TypeError: If element is not protectable
        :raises IndexError: If the index is out of bounds.
        """
        element = protect_object(element)
        self._list.insert(index, element)

    # Pylint requires the same signature as MutableSequence.insert.
    def insert(self, i, x):
        """Raise when list-like insert is attempted.

        :param i: Index to insert element before.
        :param x: Element to insert.
        :type i: int
        :type x: object
        :raises RuntimeError: On any mutation attempt.
        """
        raise RuntimeError(u"Insert not allowed: {self!r}")


class ProtectedLeaf(ABC):
    """Marker interface for leaf values supported by protected structures."""

ProtectedLeaf.register(str)
ProtectedLeaf.register(bytes)
ProtectedLeaf.register(int)
ProtectedLeaf.register(float)
# NoneType was in 2.7 and will be in 3.10, but is not in 3.7.
ProtectedLeaf.register(type(None))


class ProtectedInner(ABC):
    """Marker interface for inner (container) protected structures."""

ProtectedInner.register(ProtectedDict)
ProtectedInner.register(ProtectedList)


class ProtectedStructure(ProtectedLeaf, ProtectedInner):
    """Marker interface for any protected sub-structure."""
