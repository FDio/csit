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

"""Library for utilities simplifying data transfer from Robot to python.

This is a centralized space for interaction using Builtin library.
"""

from robot.libraries.BuiltIn import BuiltIn


# Module level cache.
# Repeated instantiation is fast, but caching is even faster,
# even if wrapped in a function call.
_builtin_instance = None


def _builtin():
    """Make sure Builtin library instance is cached on module level.

    Can be run repeatedly, does nothing if the instance is already initialized.

    The initialization may fail in a context without running Robot.
    Example: Static analysis tools, such as pylint.

    Current pylint version does not actually need this workaround,
    but there may be other tools in the future.
    And in general, we want to avoid heavy logic on import.

    :returns: The instance, useful for method chaining.
    :raises RobotNotRunningError: If initialization fails.
    """
    if _builtin_instance is None:
        _builtin_instance = BuiltIn()
    return _builtin_instance


def get_library_instance(name):
    """Return library instance for current Robot scope.

    :param name: Library name, insensitive to case and spaces/underscores.
    :type name: str
    :returns: Current library instance as found by Builtin.
    :rtype: object
    :raises RobotNotRunningError: If no Robot to get library from.
    """
    return _builtin().get_library_instance(name)


def get_variable(name, default=None):
    """Return value stored in Robot variable of current scope.

    It is recommended to include the "${" and "}" in the variable name.
    Inside, you can use more curly bracket substitutions
    supported by Robot, e.g. u"${${foo}}" gets you the value of the variable
    whose name is stored in variable named "foo".
    Beware of f-formatting, which also treats curly braces in a special way,
    use double braces to escape, e.g. f"${{text{python_var}text}}".

    :param name: Variable name, insensitive to case and spaces/underscores.
    :param default: What value to return if the variable does not exist.
    :type name: str
    :type default: object
    :returns: Found value or default.
    :rtype: object
    :raises RobotNotRunningError: If no Robot to get variable value from.
    """
    return _builtin().get_variable_value(name, default)
