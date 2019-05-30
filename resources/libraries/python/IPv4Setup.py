# Copyright (c) 2018 Cisco and/or its affiliates.
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

"""IPv4 setup library"""

from socket import inet_ntoa
from struct import pack
from abc import ABCMeta, abstractmethod

from robot.api.deco import keyword

from resources.libraries.python.ssh import exec_cmd_no_error
from resources.libraries.python.Routing import Routing
from resources.libraries.python.topology import NodeType, Topology
from resources.libraries.python.VatExecutor import VatExecutor


class IPv4Node(object):
    """Abstract class of a node in a topology."""
    __metaclass__ = ABCMeta

    def __init__(self, node_info):
        self.node_info = node_info

    @staticmethod
    def _get_netmask(prefix_length):
        """Convert IPv4 network prefix length into IPV4 network mask.

        :param prefix_length: Length of network prefix.
        :type prefix_length: int
        :returns: Network mask.
        :rtype: str
        """

        bits = 0xffffffff ^ (1 << 32 - prefix_length) - 1
        return inet_ntoa(pack('>I', bits))

    @abstractmethod
    def ping(self, destination_address, source_interface):
        """Send an ICMP request to destination node.

        :param destination_address: Address to send the ICMP request.
        :param source_interface: Source interface name.
        :type destination_address: str
        :type source_interface: str
        :returns: nothing
        """
        pass


class Tg(IPv4Node):
    """Traffic generator node"""

    pass


class Dut(IPv4Node):
    """Device under test"""

    # Implicit contructor is inherited.

    def exec_vat(self, script, **args):
        """Wrapper for VAT executor.

        :param script: Script to execute.
        :param args: Parameters to the script.
        :type script: str
        :type args: dict
        :returns: nothing
        """
        # TODO: check return value
        VatExecutor.cmd_from_template(self.node_info, script, **args)

    def arp_ping(self, destination_address, source_interface):
        """Does nothing."""
        pass

    def ping(self, destination_address, source_interface):
        pass


def get_node(node_info):
    """Creates a class instance derived from Node based on type.

    :param node_info: Dictionary containing information on nodes in topology.
    :type node_info: dict
    :returns: Class instance that is derived from Node.
    """
    if node_info['type'] == NodeType.TG:
        return Tg(node_info)
    elif node_info['type'] == NodeType.DUT:
        return Dut(node_info)
    else:
        raise NotImplementedError('Node type "{}" unsupported!'.
                                  format(node_info['type']))


class IPv4Setup(object):
    """IPv4 setup in topology."""

    pass
