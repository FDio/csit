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


from robot.api import logger
from robot.libraries.BuiltIn import BuiltIn, RobotNotRunningError

# Module level cache for BuiltIn class instance.
# Repeated instantiation is fast, but caching is even faster,
# even if wrapped in a function call.
# We want to mutate the cache, but doing that for scalar a variable
# from a function needs "global" keyword, which pylint stamps with W0603.
# So we cheat by using an "immutable" value of a list,
# with maybe the instance inserted inside.
_builtin_instance_list = list()


def _builtin():
    """Make sure Builtin library instance is cached on module level.

    Can be run repeatedly, does nothing if the instance is already initialized.

    The initialization may fail in a context without running Robot.
    Example: Static analysis tools, such as pylint.

    Current pylint version does not actually need this workaround,
    but there may be other tools in the future.
    And in general, we want to avoid heavy logic on import.

    :returns: The instance, useful for method chaining.
    :rtype: BuiltIn
    :raises RobotNotRunningError: If initialization fails.
    """
    if not _builtin_instance_list:
        _builtin_instance_list.append(BuiltIn())
    return _builtin_instance_list[0]


def get_library_instance(name):
    """Return library instance for current Robot scope.

    If robot is not running, return None.

    It is also possible that the requested library instance
    has not been imported yet. Return None (instead of raising RuntimeError)
    in that case as well.

    :param name: Library name, insensitive to case and spaces/underscores.
    :type name: str
    :returns: Current library instance as found by Builtin.
    :rtype: Optional[object]
    """
    try:
        instance = _builtin().get_library_instance(name)
    except (RobotNotRunningError, RuntimeError):
        return None
    return instance

def get_variable(name, default=None):
    """Return value stored in Robot variable of current scope.

    It is recommended to include the "\\${" and "}" in the variable name.
    Inside, you can use more curly bracket substitutions
    supported by Robot, e.g. u"\\${${foo}}" gets you the value of the variable
    whose name is stored in variable named "foo".
    Beware of f-formatting, which also treats curly braces in a special way,
    use double braces to escape, e.g. f"\\${{text{python_var}text}}".

    Default value is returned if Robot is not running
    or if the variable is not defined.

    :param name: Variable name, insensitive to case and spaces/underscores.
    :param default: What value to return if the variable does not exist.
    :type name: str
    :type default: object
    :returns: Found value or default.
    :rtype: object
    """
    try:
        return _builtin().get_variable_value(name, default)
    except RobotNotRunningError:
        return default

def set_global_variable(name, value):
    """Store value into Robot variable of global scope.

    It is recommended to include the "\\${" and "}" in the variable name.
    Inside, you can use more curly bracket substitutions
    supported by Robot, e.g. u"\\${${foo}}" gets you the value of the variable
    whose name is stored in variable named "foo".
    Beware of f-formatting, which also treats curly braces in a special way,
    use double braces to escape, e.g. f"\\${{text{python_var}text}}".

    TODO: Maybe silent noop instead of RobotNotRunningError?

    :param name: Variable name, insensitive to case and spaces/underscores.
    :param value: What value to set as a global variable.
    :type name: str
    :type value: object
    :raise RobotNotRunningError: If Robot is not running.
    """
    _builtin().set_global_variable(name, value)
