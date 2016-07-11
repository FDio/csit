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

from time import time

import paramiko
from robot.api import logger
from interruptingcow import timeout

from resources.libraries.python.honeycomb.HoneycombUtil import HoneycombError


class Notifications(object):
    """Implements keywords for managing Honeycomb notifications.

    The keywords implemented in this class make it possible to:
    - establish SSH session to Honeycomb host
    - receive notifications from Honeycomb
    - read received notifications
    """

    def __init__(self, hello, subscription):
        """Initializer.
        :param hello: Hello message to be sent to Honeycomb.
        :param subscription: rpc command to subscribe to Honeycomb notifications
        over Netconf.
        :type hello: str
        :type subscription: str

        Note: Passing the channel object as a robotframework argument closes
        the channel. Class variables are used instead,
        to persist the connection channel throughout the test case.
        """

        self.client = None
        self.channel = None
        self.hello = hello
        self.subscription = subscription

    def create_session(self, node, time_out=10):
        """Create an SSH session and connect to Honeycomb on the specified node.

        :param node: Honeycomb node.
        :param time_out: Timeout value for the connection in seconds.
        :type node: dict
        :type time_out: int
        """

        start = time()
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        client.connect(node['host'],
                       username=node['honeycomb']['user'],
                       password=node['honeycomb']['passwd'],
                       pkey=None,
                       port=node['honeycomb']['netconf_port'],
                       timeout=time_out)

        logger.trace('Connect took {0} seconds'.format(time() - start))
        logger.debug('New ssh: {0}'.format(client))
        logger.debug('Connect peer: {0}'.
                     format(client.get_transport().getpeername()))
        logger.debug(client)

        channel = client.get_transport().open_session()
        channel.settimeout(time_out)
        channel.get_pty()
        channel.invoke_subsystem("netconf")
        logger.debug(channel)

        self.client = client
        self.channel = channel

        # read OpenDaylight's hello message and capability list
        self._get_response(
            size=131072,
            time_out=time_out,
            err="Timeout on getting hello message."
        )

        self.channel.send(self.hello)
        if not self.channel.active:
            raise HoneycombError("Channel closed on capabilities exchange.")

    def _get_response(self, size=4096, time_out=10, err="Unspecified Error."):
        """Iteratively read data from the receive buffer and catenate together
        until message ends with the message delimiter, or
        until timeout is reached.

        :param size: Maximum number of bytes to read in one iteration.
        :param time_out: Timeout value for getting the complete response.
        :param err: Error message to provide when timeout is reached.
        :type size:int
        :type time_out:int
        :type err:str
        :return: Content of response.
        :rtype: str
        :raises HoneycombError: If the read process times out.
        """

        reply = ''

        try:
            with timeout(time_out, exception=RuntimeError):
                while not reply.endswith(']]>]]>'):
                    if self.channel.recv_ready():
                        reply += self.channel.recv(size)

        except RuntimeError:
            raise HoneycombError(err+" Content of buffer: {0}".format(reply))

        logger.trace(reply)
        return reply

    def add_notification_listener(self, time_out=10):
        """Open a new channel on the SSH session, connect to Netconf subsystem
        and subscribe to receive Honeycomb notifications.

        :param time_out: Timeout value for each read operation in seconds.
        :type time_out: int
        :raises HoneycombError: If subscription to notifications fails.
        """

        self.channel.send(self.subscription)

        reply = self._get_response(
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

        logger.debug("Getting notification.")

        reply = self._get_response(
            time_out=time_out,
            err="Timeout on getting notification."
        )

        return reply
