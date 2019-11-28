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

"""Python library from executing command on local hosts.

Subprocess offers various functions,
but there are differences between Python 2 and 3.

Overall, it is more convenient to introduce this internal API
so call sites are shorter and unified.

This library should support commands given as Iterable, OptionString.

Commands given as a string are explicitly not supported,
call sites should call .split(" ") on their own risk.
Similarly, parts within OptionString should not be aggregates.
Alternatively, long string can be wrapped as 'bash -c "{str}"'.
Both approaches can be hacked by malicious values.
"""

import subprocess

from robot.api import logger

from resources.libraries.python.OptionString import OptionString

__all__ = [u"run"]


MESSAGE_TEMPLATE = u"Command {com} ended with RC {ret} and output:\n{out}"


def run(command, msg=u"", check=True, log=False, console=False):
    """Wrapper around subprocess.check_output that can tolerates nonzero RCs.

    Stderr is redirected to stdout, so it is part of output
    (but can be mingled as the two streams are buffered independently).
    If check and rc is nonzero, RuntimeError is raised.
    If log (and not checked failure), both rc and output are logged.
    Logging is performed on robot logger. By default .debug(),
    optionally .console() instead.
    The default log message is optionally prepended by user-given string,
    separated by ": ".

    Commands given as single string are not supported, for safety reasons.
    Invoke bash explicitly if you need its glob support for arguments.

    :param command: List of commands and arguments. Split your long string.
    :param msg: Message prefix. Argument name is short just to save space.
    :param check: Whether to raise if return code is nonzero.
    :param log: Whether to log results.
    :param console: Whether use .console() instead of .debug().
        Mainly useful when running from non-main thread.
    :type command: Iterable or OptionString
    :type msg: str
    :type check: bool
    :type log: bool
    :type console: bool
    :returns: rc and output
    :rtype: 2-tuple of int and str
    :raises RuntimeError: If check is true and return code non-zero.
    :raises TypeError: If command is not an iterable.
    """
    if isinstance(command, OptionString):
        command = command.parts
    if not hasattr(command, u"__iter__"):
        # Strings are indexable, but turning into iterator is not supported.
        raise TypeError(f"Command {command!r} is not an iterable.")
    ret_code = 0
    output = u""
    try:
        output = subprocess.check_output(command, stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as err:
        output = err.output
        ret_code = err.returncode
        if check:
            raise RuntimeError(
                MESSAGE_TEMPLATE.format(com=err.cmd, ret=ret_code, out=output)
            )
    if log:
        message = MESSAGE_TEMPLATE.format(com=command, ret=ret_code, out=output)
        if msg:
            message = f"{msg}: {message}"
        if console:
            logger.console(message)
        else:
            logger.debug(message)
    return ret_code, output
