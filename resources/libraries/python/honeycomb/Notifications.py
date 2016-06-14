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

import socket
import paramiko
from robot.api import logger

from resources.libraries.python.honeycomb.HoneycombUtil import HoneycombError


class Notifications(object):
    """Implements keywords for managing Honeycomb notifications.

    The keywords implemented in this class make it possible to:
    - establish SSH session to Honeycomb host
    - receive notifications from Honeycomb
    - read received notifications
    """

    def __init__(self):
        """Note: Passing the channel object as a robotframework argument closes
        the channel. Class variables are used instead,
        to persist the connection channel throughout the test case.
        """

        self.client = None
        self.channel = None

    def create_session(self, node):
        """Create an SSH session and connect to Honeycomb on the specified node.

        :param node: Honeycomb node.
        :type node: dict
        """

        start = time()
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        client.connect(node['host'],
                       username=node['honeycomb']['user'],
                       password=node['honeycomb']['passwd'],
                       pkey=None,
                       port=2830,
                       timeout=10,
                       )

        logger.trace('connect took {} seconds'.format(time() - start))
        logger.debug('new ssh: {0}'.format(client))
        logger.debug('Connect peer: {0}'.
                     format(client.get_transport().getpeername()))
        logger.debug(client)

        self.client = client

    def add_notification_listener(self, timeout=10):
        """Open a new channel on the SSH session, connect to netconf subsystem
        and subscribe to receive Honeycomb notifications.

        :param timeout: Seconds to wait for each read operation.
        :type timeout: int
        :raises HoneycombError: If subscription to notifications fails.
        """

        channel = self.client.get_transport().open_session()
        channel.settimeout(timeout)
        channel.get_pty()
        channel.invoke_subsystem("netconf")
        logger.debug(channel)

        # read OpenDaylight's hello message and capability list
        channel.recv(1048576)

        # send hello message
        channel.send('<hello xmlns="urn:ietf:params:xml:ns:netconf:base:1.0">'
                     '<capabilities><capability>urn:ietf:params:netconf:base'
                     ':1.0'
                     '</capability></capabilities></hello>]]>]]>'
                     )

        # subscribe to notifications
        channel.send('<netconf:rpc netconf:message-id="101" xmlns:netconf'
                     '="urn:ietf:params:xml:ns:netconf:base:1.0">'
                     '<create-subscription xmlns'
                     '="urn:ietf:params:xml:ns:netconf:notification:1.0">'
                     '<stream>honeycomb</stream></create-subscription>'
                     '</netconf:rpc>]]>]]>'
                     )

        reply = channel.recv(4096)
        if "<ok/>" not in reply:
            raise HoneycombError("Notifications subscription failed with"
                                 " message: {0}".format(reply))

        self.channel = channel

    def get_notification(self):
        """Read and return the next entry in the SSH channel's read buffer.
        :return: Data received from buffer.
        :rtype: string
        :raises HoneycombError: If the read process times out.
        """

        logger.debug("Getting notification.")

        reply = self.channel.recv(4096)

        logger.debug(reply)
        return reply
