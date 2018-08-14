# Copyright (c) 2017 Cisco and/or its affiliates.
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

"""Implementation of exceptions used in the Presentation and analytics layer.
"""

import sys
import logging


class PresentationError(Exception):
    """Exception(s) raised by the presentation module.

    When raising this exception, put this information to the message in this
    order:
     - short description of the encountered problem (parameter msg),
     - relevant messages if there are any collected, e.g., from caught
       exception (optional parameter details),
     - relevant data if there are any collected (optional parameter details).
    """

    log_exception = {"DEBUG": logging.debug,
                     "INFO": logging.info,
                     "WARNING": logging.warning,
                     "ERROR": logging.error,
                     "CRITICAL": logging.critical}

    def __init__(self, msg, details='', level="CRITICAL"):
        """Sets the exception message and the level.

        :param msg: Short description of the encountered problem.
        :param details: Relevant messages if there are any collected, e.g.,
        from caught exception (optional parameter details), or relevant data if
        there are any collected (optional parameter details).
        :param level: Level of the error, possible choices are: "DEBUG", "INFO",
        "WARNING", "ERROR" and "CRITICAL".
        :type msg: str
        :type details: str
        :type level: str
        """

        super(PresentationError, self).__init__()
        self._msg = msg
        self._details = details
        self._level = level

        try:
            self.log_exception[self._level](self._msg)
            if self._details:
                self.log_exception[self._level](self._details)
        except KeyError:
            print("Wrong log level.")
            sys.exit(1)

    def __repr__(self):
        return (
            "PresentationError(msg={msg!r},details={dets!r},level={level!r})".
            format(msg=self._msg, dets=self._details, level=self._level))

    def __str__(self):
        return str(self._msg)

    @property
    def level(self):
        """Getter - logging level.

        :returns: Logging level.
        :rtype: str
        """
        return self._level
