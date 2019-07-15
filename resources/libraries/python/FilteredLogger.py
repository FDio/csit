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

"""Python library for customizing robot.api.logger

As robot.api.logger is a module, it is not easy to copy, edit or inherit from.
This module offers a class to wrap it.
The main point of the class is to lower verbosity of Robot logging,
especially when injected to third party code (such as vpp_papi.VPPApiClient).

Logger.console() is not supported.
"""

import logging

_LEVELS = {
    "TRACE": logging.DEBUG // 2,
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "HTML": logging.INFO,
    "WARN": logging.WARN,
    "ERROR": logging.ERROR,
    "CRITICAL": logging.CRITICAL,
    "NONE": logging.CRITICAL,
}

class FilteredLogger(object):
    """Instances of this class have the similar API to robot.api.logger.

    TODO: Support html argument?
    TODO: Support console with a filtering switch?
    """

    def __init__(self, logger_module, min_level="INFO"):
        """Remember the values, check min_level is known.

        Use min_level of "CRITICAL" or "NONE" to disable logging entirely.

        :param logger_module: robot.api.logger, or a compatible object.
        :param min_level: Minimal level to log, lower levels are ignored.
        :type logger_module: Object with .write(msg, level="INFO") signature.
        :type min_level: str
        :raises KeyError: If given min_level is not supported.
        """
        self.logger_module = logger_module
        self.min_level_num = _LEVELS(min_level.upper())

    def write(self, message, level="INFO"):
        """Forwards the message to logger if min_level is reached.

        :param message: Message to log.
        :param level: Level to possible lyg with.
        :type message: str
        :type level: str
        """
        if _LEVELS[level.upper()] >= self.min_level_num:
            self.logger_module.write(message, level=level)

    def trace(self, message):
        """Forward the message using the ``TRACE`` level."""
        self.write(message, "TRACE")

    def debug(self, message):
        """Forward the message using the ``DEBUG`` level."""
        self.write(message, "DEBUG")

    def info(self, message):
        """Forward the message using the ``INFO`` level."""
        self.write(message, "INFO")

    def warn(self, message):
        """Forward the message using the ``WARN`` level."""
        self.write(message, "WARN")

    def error(self, message):
        """Forward the message using the ``ERROR`` level."""
        self.write(message, "ERROR")
