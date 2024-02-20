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

"""This module provides functions to run external binary files.
"""


import subprocess
import shlex

from robot.api import logger


def run_binary(command: str|list, timeout: int=None):
    """
    """

    logger.info(f"Executing {command}")
    result = None
    if isinstance(command, list):
        args = command
    elif isinstance(command, str):
        args = shlex.split(command)
    else:
        raise RuntimeError(
            f"The command {command} must be string or list of strings."
        )
    try:
        result = subprocess.run(
            args=args,
            capture_output=True,
            text=True,
            timeout=timeout
        )
    except subprocess.TimeoutExpired as err:
        logger.error(f"The command {command} was not finished in {timeout}s.")
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
                raise RuntimeError(f"The command {command} failed.")
        else:
            raise RuntimeError(f"The command {command} failed.")


if __name__ == "__main__":
    """For testing purposes.

    Specify commands in the "commands" list to test the functionality.

    Will be removed before merge.
    """

    logger.logging.basicConfig(
        format="%(asctime)s %(levelname)s: %(message)s",
        datefmt="%H:%M:%S",
        level=logger.logging.DEBUG
    )

    commands = [
        "ls -la /",
        'echo "bla bla"',
        "echo 'bla bla'",
        ["python3", "-c", "print('bla bla')"],
        "This will not work",
        2,
        "python3 -c 'raise ValueError(1)'",
        "python3 -c 'import time; time.sleep(2)'"
    ]

    for cmd in commands:
        try:
            run_binary(command=cmd, timeout=1)
        except RuntimeError as err:
            logger.logging.error(repr(err))
        finally:
            print("\n")
