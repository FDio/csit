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

"""DHCP utilities for VPP."""


from resources.libraries.python.VatExecutor import VatExecutor
from resources.libraries.python.topology import Topology


class DhcpClient(object):
    """DHCP Client utilities."""

    @staticmethod
    def set_dhcp_client_on_interface(vpp_node, interface, hostname=None):
        """Set DHCP client on interface.

        :param vpp_node: VPP node to set DHCP client on.
        :param interface: Interface name to set DHCP client on.
        :param hostname: Hostname used in DHCP DISCOVER.
        :type vpp_node: dict
        :type interface: str
        :type hostname: str
        :raises RuntimeError: If unable to set DHCP client on interface.
        """
        sw_if_index = Topology.get_interface_sw_index(vpp_node, interface)
        interface = 'sw_if_index {}'.format(sw_if_index)
        hostname = 'hostname {}'.format(hostname) if hostname else ''
        output = VatExecutor.cmd_from_template(vpp_node,
                                               "dhcp_client.vat",
                                               interface=interface,
                                               hostname=hostname)
        output = output[0]

        if output["retval"] != 0:
            raise RuntimeError('Unable to set DHCP client on node {} and'
                               ' interface {}.'
                               .format(vpp_node, interface))

    @staticmethod
    def dhcp_proxy_config(vpp_node, server_address, source_address):
        """Set DHCP proxy.

        :param vpp_node: VPP node to set DHCP proxy.
        :param server_address: DHCP server IP address.
        :param source_address: DHCP proxy address.
        :type vpp_node: dict
        :type server_address: str
        :type source_address: str
        :raises RuntimeError: If unable to set DHCP proxy.
        """

        output = VatExecutor.cmd_from_template(vpp_node,
                                               "dhcp_proxy_config.vat",
                                               server_address=server_address,
                                               source_address=source_address)
        output = output[0]

        if output["retval"] != 0:
            raise RuntimeError('Unable to set DHCP proxy on node {}'
                               .format(vpp_node))
