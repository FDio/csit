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

"""Routing utilities library."""

from resources.libraries.python.VatExecutor import VatTerminal
from resources.libraries.python.topology import Topology


class Routing(object):
    """Routing utilities."""

    @staticmethod
    def vpp_route_add(node, network, prefix_len, gateway, interface):
        """Add route to the VPP node.

        :param node: Node to add route on.
        :param network: Route destination network address.
        :param prefix_len: Route destination network prefix length.
        :param gateway: Route gateway address.
        :param interface: Route interface.
        :type node: dict
        :type network: str
        :type prefix_len: int
        :type gateway: str
        :type interface: str
        """
        sw_if_index = Topology.get_interface_sw_index(node, interface)
        with VatTerminal(node) as vat:
            vat.vat_terminal_exec_cmd_from_template('add_route.vat',
                                                    network=network,
                                                    prefix_length=prefix_len,
                                                    gateway=gateway,
                                                    sw_if_index=sw_if_index)
