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
        """
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
                       timeout=time_out,
                       )

        logger.trace('connect took {0} seconds'.format(time() - start))
        logger.debug('new ssh: {0}'.format(client))
        logger.debug('Connect peer: {0}'.
                     format(client.get_transport().getpeername()))
        logger.debug(client)

        self.client = client

    def add_notification_listener(self, time_out=10):
        """Open a new channel on the SSH session, connect to Netconf subsystem
        and subscribe to receive Honeycomb notifications.

        :param time_out: Timeout value for each read operation in seconds.
        :type time_out: int
        :raises HoneycombError: If subscription to notifications fails.
        """

        channel = self.client.get_transport().open_session()
        channel.settimeout(time_out)
        channel.get_pty()
        channel.invoke_subsystem("netconf")
        logger.debug(channel)

        # read OpenDaylight's hello message and capability list
        reply = ''
        try:
            with timeout(time_out, exception=RuntimeError):
                while not reply.endswith(']]>]]>'):
                    if channel.recv_ready():
                        reply = channel.recv(131072)
        except RuntimeError:
            raise HoneycombError("Timeout on getting hello message.")

        channel.send(self.hello)
        channel.send(self.subscription)

        reply = ''
        try:
            with timeout(time_out, exception=RuntimeError):
                while not reply.endswith(']]>]]>'):
                    if channel.recv_ready():
                        reply = channel.recv(4096)
        except RuntimeError:
            raise HoneycombError("Timeout on notifications subscription.")

        if "<ok/>" not in reply:
            raise HoneycombError("Notifications subscription failed with"
                                 " message: {0}".format(reply))

        self.channel = channel

    def get_notification(self, time_out=10):
        """Read and return the next message in the SSH channel's read buffer.
        :param time_out: Timeout value for the read operation in seconds.
        :type time_out: int
        :return: Data received from buffer.
        :rtype: str
        :raises HoneycombError: If the read process times out.
        """

        logger.debug("Getting notification.")

        reply = ''
        try:
            with timeout(time_out, exception=RuntimeError):
                while not reply.endswith(']]>]]>'):
                    if self.channel.recv_ready():
                        reply += self.channel.recv(4096)
        except RuntimeError:
            raise HoneycombError("Timeout on getting notification.")

        logger.debug(reply)
        return reply
