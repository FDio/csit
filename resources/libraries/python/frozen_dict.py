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

"""Library defining a type for persistent mapping and some utility functions."""


from collections.abc import (Iterable, Mapping)


def freeze_obj(obj):
    """Return a recursively immutable deep copy of the argument value.

    In case of simple types, the same value (or reference) is returned.
    Composite types are repackaged using tuple or FrozenDict (below).
    Namedtuples are not explicitly supported.

    :param obj: The structure to freeze.
    :type obj: object
    :returns: Frozen equivalent, of the structure.
    :rtype: object
    :raises ValueError: If a type is found that we do not know how to freeze.
    """
    # NoneType was in 2.7 and will be in 3.10, but is not in 3.7.
    if isinstance(obj, (str, bytes, int, float, type(None))):
        return obj
    if isinstance(obj, Mapping):
        return FrozenDict(obj)
    if isinstance(obj, Iterable):
        return tuple(freeze_obj(item) for item in obj)
    raise ValueError(f"Unsupported type, value: {obj!r}")


class FrozenDict(Mapping):
    """A class looking like a dict, but without mutability.

    Persistent-style API allowing creation of copies with different content
    is similar to https://www.python.org/dev/peps/pep-0603/

    It would be nice to inherit from MappingProxyType,
    but "TypeError: type 'mappingproxy' is not an acceptable base type".
    Implementation is inspired by https://stackoverflow.com/a/2704866

    Write performance is currently bad.
    All keys and values are recursively frozen,
    meaning any dict- or list- like attempts at mutating any sub-structure
    would fail. Devoted callers can still mutate data, e.g. by calling __init__.

    For for read access, this class looks like a dict.
    """

    def __init__(self, mapping):
        """Construct, with frozen content.

        :param mapping: Content to freeze, usually a dict.
        :type mapping: Mapping
        :raises ValueError: If mapping contains unfreezable sub-data.
        """
        self._dict = {
            freeze_obj(key): freeze_obj(value) for key, value in mapping.items()
        }

    def __repr__(self):
        """Return a string as if this was a non-frozen dict.

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

        :returns: Shallow copy, values are still frozen.
        :rtype: dict
        """
        return self._dict.copy()

    def including(self, key, value):
        """Construct a new instance with added or replaced item.

        :param key: New key to add.
        :param value: Value to add or replace under the key.
        :type key: Hashable
        :type value: object
        :returns: Independent instance with added/replaced item.
        :rtype: self.__class__
        :raise ValueError: If key or value is not freezable.
        """
        # One shalow copy to create mutable dict, one deep freeze to seal.
        data = self.copy()
        data[key] = value
        return self.__class__(data)

    def excluding(self, key, do_raise=True):
        """Construct a new instance with removed item.

        :param key: Old key to delete.
        :param do_raise: If false, do nothing if the key is missing
        :type key: Hashable
        :param do_raise: bool
        :returns: Independent instance with deleted item.
        :rtype: self.__class__
        :raise KeyError: If the key is not present and do_raise is true.
        """
        # One shalow copy to create mutable dict, one deep freeze to seal.
        data = self.copy()
        try:
            del data[key]
        except KeyError:
            if do_raise:
                raise
        return self.__class__(data)
