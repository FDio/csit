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

"""Vhost-user interfaces library."""

from robot.api import logger

from resources.libraries.python.PapiExecutor import PapiSocketExecutor
from resources.libraries.python.topology import NodeType, Topology
from resources.libraries.python.InterfaceUtil import InterfaceUtil


class VhostUser:
    """Vhost-user interfaces L1 library."""

    @staticmethod
    def vpp_create_vhost_user_interface(node, socket):
        """Create Vhost-user interface on VPP node.

        :param node: Node to create Vhost-user interface on.
        :param socket: Vhost-user interface socket path.
        :type node: dict
        :type socket: str
        :returns: SW interface index.
        :rtype: int
        """
        cmd = u"create_vhost_user_if"
        err_msg = f"Failed to create Vhost-user interface " \
            f"on host {node[u'host']}"
        args = dict(
            sock_filename=str(socket)
        )

        with PapiSocketExecutor(node) as papi_exec:
            sw_if_index = papi_exec.add(cmd, **args).get_sw_if_index(err_msg)

        # Update the Topology:
        if_key = Topology.add_new_port(node, u"vhost")
        Topology.update_interface_sw_if_index(node, if_key, sw_if_index)

        ifc_name = InterfaceUtil.vpp_get_interface_name(node, sw_if_index)
        Topology.update_interface_name(node, if_key, ifc_name)

        ifc_mac = InterfaceUtil.vpp_get_interface_mac(node, sw_if_index)
        Topology.update_interface_mac_address(node, if_key, ifc_mac)

        Topology.update_interface_vhost_socket(node, if_key, socket)

        return sw_if_index

    @staticmethod
    def get_vhost_user_if_name_by_sock(node, socket):
        """Get Vhost-user interface name by socket.

        :param node: Node to get Vhost-user interface name on.
        :param socket: Vhost-user interface socket path.
        :type node: dict
        :type socket: str
        :returns: Interface name or None if not found.
        :rtype: str
        """
        for interface in node[u"interfaces"].values():
            if interface.get(u"socket") == socket:
                return interface.get(u"name")
        return None

    @staticmethod
    def get_vhost_user_mac_by_sw_index(node, sw_if_index):
        """Get Vhost-user l2_address for the given interface from actual
        interface dump.

        :param node: VPP node to get interface data from.
        :param sw_if_index: SW index of the specific interface.
        :type node: dict
        :type sw_if_index: str
        :returns: l2_address of the given interface.
        :rtype: str
        """
        return InterfaceUtil.vpp_get_interface_mac(node, sw_if_index)

    @staticmethod
    def show_vpp_vhost_on_all_duts(nodes):
        """Show Vhost-user on all DUTs.

        :param nodes: VPP nodes.
        :type nodes: dict
        """
        for node in nodes.values():
            if node[u"type"] == NodeType.DUT:
                VhostUser.vhost_user_dump(node)

    @staticmethod
    def vhost_user_dump(node):
        """Get vhost-user data for the given node.

        :param node: VPP node to get interface data from.
        :type node: dict
        :returns: List of dictionaries with all vhost-user interfaces.
        :rtype: list
        """
        cmd = u"sw_interface_vhost_user_dump"
        err_msg = f"Failed to get vhost-user dump on host {node['host']}"

        with PapiSocketExecutor(node) as papi_exec:
            details = papi_exec.add(cmd).get_details(err_msg)

        logger.debug(f"Vhost-user details:\n{details}")
        return details
