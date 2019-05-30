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

import binascii

import logging

from resources.libraries.python.PapiExecutor import PapiExecutor
from resources.libraries.python.topology import NodeType, Topology
from resources.libraries.python.InterfaceUtil import InterfaceUtil


class VhostUser(object):
    """Vhost-user interfaces"""

    @staticmethod
    def _sw_interface_vhost_user_dump(node):
        """Get the Vhost dump on the given node.

        :param node: Given node to get Vhost dump from.
        :type node: dict
        :returns: List of vhosts extracted from Papi response.
        :rtype: list
        """
        with PapiExecutor(node) as papi_exec:
            dump = papi_exec.add("sw_interface_vhost_user_dump").get_dump()

        key = "sw_interface_vhost_user_details"
        data = list()
        for item in dump.reply[0]["api_reply"]:
            item[key]["interface_name"] = \
                item[key]["interface_name"].rstrip('\x00')
            item[key]["sock_filename"] = \
                item[key]["sock_filename"].rstrip('\x00')
            data.append(item)

        logging.debug("VhostUser data:\n{data}".format(data))

        return data

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
        cmd = 'create_vhost_user_if'
        err_msg = 'Failed to create Vhost-user interface on host {host}'.format(
            host=node['host'])
        args = dict(
            sock_filename=str(socket)
        )
        with PapiExecutor(node) as papi_exec:
            data = papi_exec.add(cmd, **args).get_replies(err_msg). \
                verify_reply(err_msg=err_msg)

        # Extract sw_if_idx:
        sw_if_idx = data["sw_if_index"]

        # Update the Topology:
        if_key = Topology.add_new_port(node, 'vhost')
        Topology.update_interface_sw_if_index(node, if_key, sw_if_idx)

        ifc_name = InterfaceUtil.vpp_get_interface_name(node, sw_if_idx)
        Topology.update_interface_name(node, if_key, ifc_name)

        ifc_mac = InterfaceUtil.vpp_get_interface_mac(node, sw_if_idx)
        Topology.update_interface_mac_address(node, if_key, ifc_mac)

        Topology.update_interface_vhost_socket(node, if_key, socket)

        return sw_if_idx

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
        :returns: l2_address of the given interface.
        :rtype: str
        """

        return InterfaceUtil.vpp_get_interface_mac(node, sw_if_index)

    @staticmethod
    def vpp_show_vhost(node):
        """Get vhost-user data for the given node.

        :param node: VPP node to get interface data from.
        :type node: dict
        :returns: nothing
        """
        VhostUser._sw_interface_vhost_user_dump(node)

    @staticmethod
    def show_vpp_vhost_on_all_duts(nodes):
        """Show Vhost User on all DUTs.

        :param nodes: VPP nodes.
        :type nodes: dict
        """
        for node in nodes.values():
            if node['type'] == NodeType.DUT:
                VhostUser.vpp_show_vhost(node)
