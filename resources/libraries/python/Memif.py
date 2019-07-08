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

"""Memif interface library."""


from enum import IntEnum
from robot.api import logger

from resources.libraries.python.topology import NodeType, Topology
from resources.libraries.python.PapiExecutor import PapiExecutor
from resources.libraries.python.L2Util import L2Util


class MemifRole(IntEnum):
    """Memif interface roles"""
    MASTER = 0
    SLAVE = 1


class Memif(object):
    """Memif interface class"""

    def __init__(self):
        pass

    @staticmethod
    def _memif_details(node):
        """Get the memif dump details on the given node.

        :param node: Given node to get Memif dump from.
        :type node: dict
        :returns: List of memif interfaces extracted from Papi response.
        :rtype: list
        """
        with PapiExecutor(node) as papi_exec:
            details = papi_exec.add("memif_dump").get_details()

        for memif in details:
            memif["if_name"] = memif["if_name"].rstrip('\x00')
            memif["hw_addr"] = L2Util.bin_to_mac(memif["hw_addr"])

        logger.debug("MEMIF details:\n{details}".format(details=details))

        return details

    @staticmethod
    def _memif_socket_filename_add_del(node, is_add, filename, sid):
        """Create Memif socket on the given node.

        :param node: Given node to create Memif socket on.
        :param is_add: If True, socket is added, otherwise deleted.
        :param filename: Memif interface socket filename.
        :param sid: Socket ID.
        :type node: dict
        :type is_add: bool
        :type filename: str
        :type sid: str
        :returns: Verified data from PAPI response. In this case, the response
            includes only retval.
        :rtype: dict
        """
        cmd = 'memif_socket_filename_add_del'
        err_msg = 'Failed to create memif socket on host {host}'.format(
            host=node['host'])
        args = dict(
            is_add=int(is_add),
            socket_id=int(sid),
            socket_filename=str('/tmp/' + filename)
        )
        with PapiExecutor(node) as papi_exec:
            return papi_exec.add(cmd, **args).get_reply(err_msg)

    @staticmethod
    def _memif_create(node, mid, sid, rxq=1, txq=1, role=1):
        """Create Memif interface on the given node, return its sw_if_index.

        :param node: Given node to create Memif interface on.
        :param mid: Memif interface ID.
        :param sid: Socket ID.
        :param rxq: Number of RX queues; 0 means do not set.
        :param txq: Number of TX queues; 0 means do not set.
        :param role: Memif interface role [master=0|slave=1]. Default is slave.
        :type node: dict
        :type mid: str
        :type sid: str
        :type rxq: int
        :type txq: int
        :type role: int
        :returns: sw_if_index
        :rtype: int
        """
        cmd = 'memif_create'
        err_msg = 'Failed to create memif interface on host {host}'.format(
            host=node['host'])
        args = dict(
            role=role,
            rx_queues=int(rxq),
            tx_queues=int(txq),
            socket_id=int(sid),
            id=int(mid)
        )
        with PapiExecutor(node) as papi_exec:
            return papi_exec.add(cmd, **args).get_sw_if_index(err_msg)

    @staticmethod
    def create_memif_interface(node, filename, mid, sid, rxq=1, txq=1,
                               role="SLAVE"):
        """Create Memif interface on the given node.

        :param node: Given node to create Memif interface on.
        :param filename: Memif interface socket filename.
        :param mid: Memif interface ID.
        :param sid: Socket ID.
        :param rxq: Number of RX queues; 0 means do not set.
        :param txq: Number of TX queues; 0 means do not set.
        :param role: Memif interface role [master=0|slave=1]. Default is master.
        :type node: dict
        :type filename: str
        :type mid: str
        :type sid: str
        :type rxq: int
        :type txq: int
        :type role: str
        :returns: SW interface index.
        :rtype: int
        :raises ValueError: If command 'create memif' fails.
        """

        role = getattr(MemifRole, role.upper()).value

        # Create socket
        Memif._memif_socket_filename_add_del(node, True, filename, sid)

        # Create memif
        sw_if_index = Memif._memif_create(
            node, mid, sid, rxq=rxq, txq=txq, role=role)

        # Update Topology
        if_key = Topology.add_new_port(node, 'memif')
        Topology.update_interface_sw_if_index(node, if_key, sw_if_index)

        ifc_name = Memif.vpp_get_memif_interface_name(node, sw_if_index)
        Topology.update_interface_name(node, if_key, ifc_name)

        ifc_mac = Memif.vpp_get_memif_interface_mac(node, sw_if_index)
        Topology.update_interface_mac_address(node, if_key, ifc_mac)

        Topology.update_interface_memif_socket(node, if_key, '/tmp/' + filename)
        Topology.update_interface_memif_id(node, if_key, mid)
        Topology.update_interface_memif_role(node, if_key, str(role))

        return sw_if_index

    @staticmethod
    def show_memif(node):
        """Show Memif data for the given node.

        :param node: Given node to show Memif data on.
        :type node: dict
        """

        Memif._memif_details(node)

    @staticmethod
    def show_memif_on_all_duts(nodes):
        """Show Memif data on all DUTs.

        :param nodes: Topology nodes.
        :type nodes: dict
        """
        for node in nodes.values():
            if node['type'] == NodeType.DUT:
                Memif.show_memif(node)

    @staticmethod
    def vpp_get_memif_interface_name(node, sw_if_index):
        """Get Memif interface name from Memif interfaces dump.

        :param node: DUT node.
        :param sw_if_index: DUT node.
        :type node: dict
        :type sw_if_index: int
        :returns: Memif interface name, or None if not found.
        :rtype: str
        """

        details = Memif._memif_details(node)

        for memif in details:
            if memif["sw_if_index"] == sw_if_index:
                return memif["if_name"]
        return None

    @staticmethod
    def vpp_get_memif_interface_mac(node, sw_if_index):
        """Get Memif interface MAC address from Memif interfaces dump.

        :param node: DUT node.
        :param sw_if_index: DUT node.
        :type node: dict
        :type sw_if_index: int
        :returns: Memif interface MAC address, or None if not found.
        :rtype: str
        """

        details = Memif._memif_details(node)

        for memif in details:
            if memif["sw_if_index"] == sw_if_index:
                return memif["hw_addr"]
        return None
