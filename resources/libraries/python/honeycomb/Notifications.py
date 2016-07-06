# Copyright (c) 2016 Cisco and/or its affiliates.
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

"""Implementation of keywords for managing Honeycomb notifications."""

from robot.api import logger

from resources.libraries.python.honeycomb.HoneycombUtil import HoneycombError
from resources.libraries.python.honeycomb.Netconf import Netconf


class Notifications(Netconf):
    """Implements keywords for receiving Honeycomb notifications.

    The keywords implemented in this class make it possible to:
    - receive notifications from Honeycomb
    - read received notifications
    """

    def add_notification_listener(self, subscription, time_out=10):
        """Open a new channel on the SSH session, connect to Netconf subsystem
        and subscribe to receive Honeycomb notifications.

        :param subscription: RPC for subscription to notifications.
        :param time_out: Timeout value for each read operation in seconds.
        :type subscription: str
        :type time_out: int
        :raises HoneycombError: If subscription to notifications fails.
        """

        logger.debug(subscription)
        self.send(subscription)

        reply = self.get_response(
            time_out=time_out,
            err="Timeout on notifications subscription."
        )

        if "<ok/>" not in reply:
            raise HoneycombError("Notifications subscription failed with"
                                 " message: {0}".format(reply))

        logger.debug("Notifications subscription successful.")

    def get_notification(self, time_out=10):
        """Read and return the next notification message.

        :param time_out: Timeout value for the read operation in seconds.
        :type time_out: int
        :return: Data received from buffer.
        :rtype: str
        """

        logger.debug("Getting notification. Timeout set to {0} seconds."
                     .format(time_out))

        reply = self.get_response(
            time_out=time_out,
            err="Timeout on getting notification."
        )

        return reply
