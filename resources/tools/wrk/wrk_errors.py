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

"""Implementation of exceptions used in the wrk traffic generator.
"""


from robot.api import logger


class WrkError(Exception):
    """Exception(s) raised by the wrk traffic generator.

    When raising this exception, put this information to the message in this
    order:
     - short description of the encountered problem (parameter msg),
     - relevant messages if there are any collected, e.g., from caught
       exception (optional parameter details),
     - relevant data if there are any collected (optional parameter details).
    """

    def __init__(self, msg, details=u""):
        """Sets the exception message and the level.

        :param msg: Short description of the encountered problem.
        :param details: Relevant messages if there are any collected, e.g.:
        from caught exception (optional parameter details), or relevant data if
        there are any collected (optional parameter details).
        :type msg: str
        :type details: str
        """

        super(WrkError, self).__init__()
        self._msg = msg
        self._details = details

        logger.error(self._msg)
        if self._details:
            logger.error(self._details)

    def __repr__(self):
        return repr(self._msg)

    def __str__(self):
        return str(self._msg)
