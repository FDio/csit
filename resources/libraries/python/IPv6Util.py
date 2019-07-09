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

"""IPv6 utilities library."""

from resources.libraries.python.InterfaceUtil import InterfaceUtil
from resources.libraries.python.IPUtil import IPUtil
from resources.libraries.python.PapiExecutor import PapiSocketExecutor
from resources.libraries.python.topology import NodeType


class IPv6Util(object):
    """IPv6 utilities"""

    @staticmethod
    def vpp_ra_suppress_link_layer(node, interface):
        """Suppress ICMPv6 router advertisement message for link scope address.

        :param node: VPP node.
        :param interface: Interface name.
        :type node: dict
        :type interface: str
        """
        cmd = 'sw_interface_ip6nd_ra_config'
        args = dict(
            sw_if_index=InterfaceUtil.get_interface_index(node, interface),
            suppress=1)
        err_msg = 'Failed to suppress ICMPv6 router advertisement message on ' \
                  'interface {ifc}'.format(ifc=interface)

        with PapiSocketExecutor(node) as papi_exec:
            papi_exec.add(cmd, **args).get_reply(err_msg)

    @staticmethod
    def vpp_ra_send_after_interval(node, interface, interval=2):
        """Setup vpp router advertisement(RA) in such way it sends RA packet
        after every interval value.

        :param node: VPP node.
        :param interface: Interface name.
        :param interval: Interval in seconds for RA resend.
        :type node: dict
        :type interface: str
        :type interval: int
        """
        cmd = 'sw_interface_ip6nd_ra_config'
        args = dict(
            sw_if_index=InterfaceUtil.get_interface_index(node, interface),
            initial_interval=int(interval))
        err_msg = 'Failed to set router advertisement interval on ' \
                  'interface {ifc}'.format(ifc=interface)

        with PapiSocketExecutor(node) as papi_exec:
            papi_exec.add(cmd, **args).get_reply(err_msg)

    @staticmethod
    def vpp_all_ra_suppress_link_layer(nodes):
        """Suppress ICMPv6 router advertisement message for link scope address
        on all VPP nodes in the topology.

        :param nodes: Nodes of the test topology.
        :type nodes: dict
        """
        for node in nodes.values():
            if node['type'] == NodeType.TG:
                continue
            for port_k in node['interfaces'].keys():
                ip6_addr_list = IPUtil.vpp_get_interface_ip_addresses(
                    node, port_k, 'ipv6')
                if ip6_addr_list:
                    IPv6Util.vpp_ra_suppress_link_layer(node, port_k)
