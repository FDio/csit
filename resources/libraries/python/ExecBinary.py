# Copyright (c) 2024 Cisco and/or its affiliates.
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

"""This module provides functions to execute binary files.
"""


import subprocess
import shlex

from robot.api import logger


def exec_binary(command: str|list, timeout: int=None):
    """Executes a binary file, optionaly with its command line arguments, and
    checks the return value. If it is not 0, it raises RuntimeError. It is also
    raised if the execution takes more time then defined by "timeout" [s].

    The command can be defined as a string, e.g.:
    "ls -la /" or
    "python3 -c 'import time; time.sleep(2)'"

    or as a list of strings, e.g.:
    ["python3", "-c", "print('bla bla')"]

    :param command: Command to be executed.
    :param timeout: The time in seconds to execute the command. If the timeout
        expires, the child process will be killed. timeout = None means no
        timeout.
    :type command: str | list
    :type timeout: int
    :raises RuntimeError: if the return value is not 0 or if the timeout occurs.
    """

    logger.info(f"Executing '{command}'")

    # Check the input parameters:
    if timeout is not None and not isinstance(timeout, int):
        raise RuntimeError(
            f"The timeout ({timeout}) must be an integer or None."
        )

    if isinstance(command, list):
        args = command
    elif isinstance(command, str):
        args = shlex.split(command)
    else:
        raise RuntimeError(
            f"The command '{command}' must be a string or a list of strings."
        )

    # Execute the command:
    result = None
    try:
        result = subprocess.run(
            args=args,
            capture_output=True,
            text=True,
            timeout=timeout
        )
    except subprocess.TimeoutExpired as err:
        logger.error(f"The command '{command}' was not finished in {timeout}s.")
        logger.trace(repr(err))
    except subprocess.SubprocessError as err:
        logger.trace(repr(err))
    except OSError as err:
        logger.trace(repr(err))
    finally:
        if result:
            logger.debug(f"Return Code: {result.returncode}")
            logger.debug(f"stdout:\n{result.stdout}")
            logger.debug(f"stderr:\n{result.stderr}")
            if result.returncode:
                raise RuntimeError(f"The command '{command}' failed.")
        else:
            raise RuntimeError(f"The command '{command}' failed.")


def exec_binaries(commands: list, timeouts: int|list=None,
                  continue_on_error: bool=False):
    """Executes a list of commands using "exec_binary" function.

    :param commands: A list of commands to be executed.
    :param timeouts: A list of timeouts, one value for each command or an
        integer defining timeout for each command (not for all together).
    :param continue_on_error: If True, the execution continues if the previous
        command failes. Otherwise the failed command terminates the execution of
        the list of commands.
    :type commands: list[list | str]
    :type timeouts: list | int
    :type continue_on_error: bool
    :raises RuntimeError: if the lengths of list of timeouts and list of
        commands is not the same.
    """

    if timeouts is None or isinstance(timeouts, int):
        timeouts = [timeouts, ] * len(commands)
    elif isinstance(timeouts, list) and (len(timeouts) != len(commands)):
        raise RuntimeError(
            f"The number of timeouts ({len(timeouts)}) must be the same as "
            f"the number of commands ({len(commands)})."
        )

    for command, timeout in zip(commands, timeouts):
        try:
            exec_binary(command=command, timeout=timeout)
        except RuntimeError as err:
            logger.logging.error(repr(err))
            if not continue_on_error:
                raise
