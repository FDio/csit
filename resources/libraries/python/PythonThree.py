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

"""Library holding utility functions to be replaced by later Python builtins."""

from robot.api import logger


def raise_from(raising, excepted, level="WARN"):
    """Function to be replaced by "raise from" in Python 3.

    Neither "six" nor "future" offer good enough implementation right now.
    chezsoi.org/lucas/blog/displaying-chained-exceptions-stacktraces-in-python-2

    Current implementation just logs the excepted error, and raises the new one.
    For allower log level values, see:
    robot-framework.readthedocs.io/en/latest/autodoc/robot.api.html#log-levels

    :param raising: The exception to raise.
    :param excepted: The exception we excepted and want to log.
    :param level: Robot logger logging level to log with.
    :type raising: BaseException
    :type excepted: BaseException
    :type level: str
    :raises: raising
    """
    logger.write("Excepted: {exc!r}\nRaising: {rai!r}".format(
        exc=excepted, rai=raising), level)
    raise raising
