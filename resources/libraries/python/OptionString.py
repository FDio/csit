# Copyright (c) 2019 Cisco and/or its affiliates.
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

"""Utility function for handling options without doubled or trailing spaces."""


class OptionString(object):
    """Class serving as a builder for option strings.

    Motivation: Both manual contatenation and .join() methods
    are prone to leaving superfluous spaces if some parts of options
    are optional (missing, empty).

    The scope of this class is more general than just command line options,
    it can concatenate any string consisting of words that may be missing.
    But options were the first usage, so method arguments are frequently
    named "parameter" and "value".
    To keep this generality, automated adding of dashes is optional,
    and disabled by default.

    Parts of the whole option string are kept as list items (string, stipped),
    with prefix already added.
    Empty strings are never added to the list (except by constructor).

    The class offers many methods for adding, so that callers can pick
    the best fitting one, without much logic near the call site.
    """

    def __init__(self, parts=tuple(), prefix=""):
        """Create instance with listed strings as parts to use.

        Prefix will be converted to string and stripped.
        The typical (nonempty) prefix values are "-" and "--".

        TODO: Support users calling with parts being a string?

        :param parts: List of of stringifiable objects to become parts.
        :param prefix: Subtring to prepend to every parameter (not value).
        :type parts: Iterable of object
        :type prefix: object
        """
        self.parts = [str(part) for part in parts]
        self.prefix = str(prefix).strip()  # Not worth to call change_prefix.

    def __repr__(self):
        """Return string executable as Python constructor call.

        :returns: Executable constructor call as string.
        :rtype: str
        """
        return "OptionString(parts={parts!r},prefix={prefix!r})".format(
            parts=self.parts, prefix=self.prefix)

    # TODO: Would we ever need a copy() method?
    # Currently, superstring "master" is mutable but unique,
    # substring "slave" can be used to extend, but does not need to be mutated.

    def change_prefix(self, prefix):
        """Change the prefix field from the initialized value.

        Sometimes it is more convenient to change the prefix in the middle
        of string construction.
        Typical use is for constructing a command, where the first part
        (executeble filename) does not have a dash, but the other parameters do.
        You could put the first part into constructor argument,
        but using .add and only then enabling prefix is horizontally shorter.

        :param prefix: New prefix value, to be converted and tripped.
        :type prefix: object
        :returns: Self, to enable method chaining.
        :rtype: OptionString
        """
        self.prefix = str(prefix).strip()

    def extend(self, other):
        """Extend self by contents of other option string.

        :param other: Another instance to add to the end of self.
        :type other: OptionString
        :returns: Self, to enable method chaining.
        :rtype: OptionString
        """
        self.parts.extend(other.parts)
        return self

    def _check_and_add(self, part, prefixed):
        """Convert to string, strip, conditionally add prefixed if non-empty.

        Value of None is converted to empty string.
        Emptiness is tested before adding prefix.

        :param part: Unchecked part to add to list of parts.
        :param prefixed: Whether to add prefix when adding.
        :type part: object
        :type prefixed: object
        :returns: The converted part without prefix, empty means not added.
        :rtype: str
        """
        part = "" if part is None else str(part).strip()
        if part:
            prefixed_part = self.prefix + part if prefixed else part
            self.parts.append(prefixed_part)
        return part

    def add(self, parameter):
        """Add parameter if nonempty to the list of parts.

        Parameter object is converted to string and stripped.
        If parameter converts to empty string, nothing is added.
        Parameter is prefixed before adding.

        :param parameter: Parameter object, usually a word starting with dash.
        :type variable: object
        :returns: Self, to enable method chaining.
        :rtype: OptionString
        """
        self._check_and_add(parameter, prefixed=True)
        return self

    def add_if(self, parameter, condition):
        """Add parameter if nonempty and condition is true to the list of parts.

        If condition truth value is false, nothing is added.
        Parameter object is converted to string and stripped.
        If parameter converts to empty string, nothing is added.
        Parameter is prefixed before adding.

        :param parameter: Parameter object, usually a word starting with dash.
        :param condition: Do not add if truth value of this is false.
        :type variable: object
        :type condition: object
        :returns: Self, to enable method chaining.
        :rtype: OptionString
        """
        if condition:
            self.add(parameter)
        return self

    def add_with_value(self, parameter, value):
        """Add parameter, if followed by a value to the list of parts.

        Parameter and value are converted to string and stripped.
        If parameter or value converts to empty string, nothing is added.
        If added, parameter (but not value) is prefixed.

        :param parameter: Parameter object, usually a word starting with dash.
        :param value: Value object. Prefix is never added.
        :type variable: object
        :type value: object
        :returns: Self, to enable method chaining.
        :rtype: OptionString
        """
        temp = OptionString(prefix=self.prefix)
        # TODO: Is pylint really that ignorant?
        # How could it not understand temp is of type of this class?
        # pylint: disable=protected-access
        if temp._check_and_add(parameter, prefixed=True):
            if temp._check_and_add(value, prefixed=False):
                self.extend(temp)
        return self

    def add_equals(self, parameter, value):
        """Add parameter=value to the list of parts.

        Parameter and value are converted to string and stripped.
        If parameter or value converts to empty string, nothing is added.
        If added, parameter (but not value) is prefixed.

        :param parameter: Parameter object, usually a word starting with dash.
        :param value: Value object. Prefix is never added.
        :type variable: object
        :type value: object
        :returns: Self, to enable method chaining.
        :rtype: OptionString
        """
        temp = OptionString(prefix=self.prefix)
        # pylint: disable=protected-access
        if temp._check_and_add(parameter, prefixed=True):
            if temp._check_and_add(value, prefixed=False):
                self.parts.append("=".join(temp.parts))
        return self

    def add_with_value_if(self, parameter, value, condition):
        """Add parameter and value if condition is true and nothing is empty.

        If condition truth value is false, nothing is added.
        Parameter and value are converted to string and stripped.
        If parameter or value converts to empty string, nothing is added.
        If added, parameter (but not value) is prefixed.

        :param parameter: Parameter object, usually a word starting with dash.
        :param value: Value object. Prefix is never added.
        :param condition: Do not add if truth value of this is false.
        :type variable: object
        :type value: object
        :type condition: object
        :returns: Self, to enable method chaining.
        :rtype: OptionString
        """
        if condition:
            self.add_with_value(parameter, value)
        return self

    def add_equals_if(self, parameter, value, condition):
        """Add parameter=value to the list of parts if condition is true.

        If condition truth value is false, nothing is added.
        Parameter and value are converted to string and stripped.
        If parameter or value converts to empty string, nothing is added.
        If added, parameter (but not value) is prefixed.

        :param parameter: Parameter object, usually a word starting with dash.
        :param value: Value object. Prefix is never added.
        :param condition: Do not add if truth value of this is false.
        :type variable: object
        :type value: object
        :type condition: object
        :returns: Self, to enable method chaining.
        :rtype: OptionString
        """
        if condition:
            self.add_equals(parameter, value)
        return self

    def add_with_value_from_dict(self, parameter, key, mapping, default=""):
        """Add parameter with value from dict under key, or default.

        If key is missing, default is used as value.
        Parameter and value are converted to string and stripped.
        If parameter or value converts to empty string, nothing is added.
        If added, parameter (but not value) is prefixed.

        :param parameter: The parameter part to add with prefix.
        :param key: The key to look the value for.
        :param mapping: Mapping with keys and values to use.
        :param default: The value to use if key is missing.
        :type parameter: object
        :type key: str
        :type mapping: dict
        :type default: object
        :returns: Self, to enable method chaining.
        :rtype: OptionString
        """
        value = mapping.get(key, default)
        return self.add_with_value(parameter, value)

    def add_equals_from_dict(self, parameter, key, mapping, default=""):
        """Add parameter=value to options where value is from dict.

        If key is missing, default is used as value.
        Parameter and value are converted to string and stripped.
        If parameter or value converts to empty string, nothing is added.
        If added, parameter (but not value) is prefixed.

        :param parameter: The parameter part to add with prefix.
        :param key: The key to look the value for.
        :param mapping: Mapping with keys and values to use.
        :param default: The value to use if key is missing.
        :type parameter: object
        :type key: str
        :type mapping: dict
        :type default: object
        :returns: Self, to enable method chaining.
        :rtype: OptionString
        """
        value = mapping.get(key, default)
        return self.add_equals(parameter, value)

    def add_if_from_dict(self, parameter, key, mapping, default="False"):
        """Add parameter based on if the condition in dict is true.

        If key is missing, default is used as condition.
        If condition truth value is false, nothing is added.
        Parameter is converted to string and stripped.
        If parameter converts to empty string, nothing is added.
        Parameter is prefixed before adding.

        :param parameter: The parameter part to add with prefix.
        :param key: The key to look the value for.
        :param mapping: Mapping with keys and values to use.
        :param default: The value to use if key is missing.
        :type parameter: object
        :type key: str
        :type mapping: dict
        :type default: object
        :returns: Self, to enable method chaining.
        :rtype: OptionString
        """
        condition = mapping.get(key, default)
        return self.add_if(parameter, condition)

    def add_with_value_if_from_dict(
            self, parameter, value, key, mapping, default="False"):
        """Add parameter and value based on condition in dict.

        If key is missing, default is used as condition.
        If condition truth value is false, nothing is added.
        Parameter and value are converted to string and stripped.
        If parameter or value converts to empty string, nothing is added.
        If added, parameter (but not value) is prefixed.

        :param parameter: The parameter part to add with prefix.
        :param value: Value object. Prefix is never added.
        :param key: The key to look the value for.
        :param mapping: Mapping with keys and values to use.
        :param default: The value to use if key is missing.
        :type parameter: object
        :type value: object
        :type key: str
        :type mapping: dict
        :type default: object
        :returns: Self, to enable method chaining.
        :rtype: OptionString
        """
        condition = mapping.get(key, default)
        return self.add_with_value_if(parameter, value, condition)

    def add_equals_if_from_dict(
            self, parameter, value, key, mapping, default="False"):
        """Add parameter=value based on condition in dict.

        If key is missing, default is used as condition.
        If condition truth value is false, nothing is added.
        Parameter and value are converted to string and stripped.
        If parameter or value converts to empty string, nothing is added.
        If added, parameter (but not value) is prefixed.

        :param parameter: The parameter part to add with prefix.
        :param value: Value object. Prefix is never added.
        :param key: The key to look the value for.
        :param mapping: Mapping with keys and values to use.
        :param default: The value to use if key is missing.
        :type parameter: object
        :type value: object
        :type key: str
        :type mapping: dict
        :type default: object
        :returns: Self, to enable method chaining.
        :rtype: OptionString
        """
        condition = mapping.get(key, default)
        return self.add_equals_if(parameter, value, condition)

    def __str__(self):
        """Return space separated string of nonempty parts.

        The format is suitable to be pasted as (part of) command line.
        Do not call str() prematurely just to get a substring, consider
        converting the surrounding text manipulation to OptionString as well.

        :returns: Space separated string of options.
        :rtype: str
        """
        return " ".join(self.parts)
