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

"""Keywords used to connect to Honeycomb through Netconf, send messages
 and receive replies."""

from time import time

import paramiko
from robot.api import logger
from interruptingcow import timeout

from resources.libraries.python.honeycomb.HoneycombUtil import HoneycombError


class Netconf(object):
    """Implements methods for creating and managing Netconf sessions."""

    def __init__(self):
        """Initializer.

        Note: Passing the channel object as a robotframework argument closes
        the channel. Class variables are used instead,
        to persist the connection channel throughout test cases.
        """

        self.client = None
        self.channel = None

    def create_session(self, node, hello, time_out=10):
        """Create an SSH session, connect to Honeycomb on the specified node,
        open a communication channel to the Netconf subsystem and exchange hello
        messages.

        :param node: Honeycomb node.
        :param hello: Hello message and capability list to be sent to Honeycomb.
        :param time_out: Timeout value for the connection in seconds.
        :type node: dict
        :type hello: str
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
        self.get_response(
            size=131072,
            time_out=time_out,
            err="Timeout on getting hello message."
        )

        self.channel.send(hello)
        if not self.channel.active:
            raise HoneycombError("Channel closed on capabilities exchange.")

    def get_response(self, size=4096, time_out=10, err="Unspecified Error."):
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
            raise HoneycombError(err + " Content of buffer: {0}".format(reply))

        logger.trace(reply)
        return reply

    def get_all_responses(self, size=4096, time_out=10):
        """Read responses from the receive buffer and catenate together
         until a read operation times out.

        :param size: Maximum number of bytes to read in one iteration.
        :param time_out: Timeout value for getting the complete response.
        :type size:int
        :type time_out:int
        :return: Content of response.
        :rtype: str
        """

        response = ""
        err = "Expected timeout occurred."

        while True:
            try:
                response += self.get_response(size, time_out, err)
            except HoneycombError:
                break

        return response

    def send(self, message):
        """Sends provided message through the channel.

        :param message: Message to be sent to Honeycomb.
        :type message: str
        """

        self.channel.send(message)
