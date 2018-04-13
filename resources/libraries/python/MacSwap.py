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

"""Macswap sample_plugin util library"""

from resources.libraries.python.topology import NodeType, Topology
from resources.libraries.python.VatExecutor import VatExecutor

class MacSwap(object):
    """Macswap sample plugin API"""

    @staticmethod
    def enable_disable_macswap_vat(node, interface):
        """Enable/Disable macswap on interface.

        Function can be used on a VPP node with macswap plugin.

        :param node: Node where the interface is.
        :param interface: Interface id.
        :type node: dict
        :type interface: str or int
        :returns: nothing
        """
        if node['type'] == NodeType.DUT:
            sw_if_index = Topology.get_interface_sw_index(node, interface)

            VatExecutor.cmd_from_template(node, 'macswap.vat',
                                          sw_if_index=sw_if_index)
        else:
            raise ValueError('Node {} has not DUT NodeType: "{}"'.
                             format(node['host'], node['type']))

    @staticmethod
    def enable_disable_macswap_vat_exec(node, interface_name):
        """Enable/Disable macswap on interface.

        Function can be used on a VPP node with macswap plugin.

        :param node: Node where the interface is.
        :param interface_name: Interface name.
        :type node: dict
        :type interface_name: str or int
        :returns: nothing
        """
        if node['type'] == NodeType.DUT:

            VatExecutor.cmd_from_template(node, 'macswap_exec.vat',
                                          if_name=interface_name)
        else:
            raise ValueError('Node {} has not DUT NodeType: "{}"'.
                             format(node['host'], node['type']))


