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

"""Vhost-user interfaces library."""

from resources.libraries.python.VatExecutor import VatExecutor, VatTerminal
from resources.libraries.python.topology import NodeType


class VhostUser(object):
    """Vhost-user interfaces"""

    @staticmethod
    def vpp_create_vhost_user_interface(node, socket):
        """Create Vhost-user interface on VPP node.

        :param node: Node to create Vhost-user interface on.
        :param socket: Vhost-user interface socket path.
        :type node: dict
        :type socket: str
        :return: SW interface index.
        :rtype: int
        """
        out = VatExecutor.cmd_from_template(node, "create_vhost_user_if.vat",
                                            sock=socket)
        if out[0].get('retval') == 0:
            return out[0].get('sw_if_index')
        else:
            raise RuntimeError('Create Vhost-user interface failed on node '
                               '"{}"'.format(node['host']))

    @staticmethod
    def get_vhost_user_if_name_by_sock(node, socket):
        """Get Vhost-user interface name by socket.

        :param node: Node to get Vhost-user interface name on.
        :param socket: Vhost-user interface socket path.
        :type node: dict
        :type socket: str
        :return: Interface name or None if not found.
        :rtype: str
        """
        for interface in node['interfaces'].values():
            if interface.get('socket') == socket:
                return interface.get('name')
        return None

    @staticmethod
    def get_vhost_user_mac_by_sw_index(node, sw_if_index):
        """Get Vhost-user l2_address for the given interface from actual
        interface dump.

        :param node: VPP node to get interface data from.
        :param sw_if_index: Idx of the specific interface.
        :type node: dict
        :type sw_if_index: str
        :return: l2_address of the given interface.
        :rtype: str
        """

        with VatTerminal(node) as vat:
            if_data = vat.vat_terminal_exec_cmd_from_template(
                "interface_dump.vat")
        for iface in if_data[0]:
            if iface["sw_if_index"] == sw_if_index:
                return ':'.join("%02x" % (b) for b in iface["l2_address"][:6])

        return None

    @staticmethod
    def vpp_show_vhost(node):
        """Get vhost-user data for the given node.

        :param node: VPP node to get interface data from.
        :type node: dict
        :return: nothing
        """
        vat = VatExecutor()
        vat.execute_script("show_vhost.vat", node, json_out=False)

    @staticmethod
    def show_vpp_vhost_on_all_duts(nodes):
        """Show Vhost User on all DUTs.

        :param nodes: VPP nodes
        :type nodes: dict
        """
        for node in nodes.values():
            if node['type'] == NodeType.DUT:
                VhostUser.vpp_show_vhost(node)
