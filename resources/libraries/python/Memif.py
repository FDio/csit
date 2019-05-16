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

# TODO: Not used, remove?
# from resources.libraries.python.ssh import SSH
from resources.libraries.python.VatExecutor import VatExecutor, VatTerminal
from resources.libraries.python.topology import NodeType, Topology
from resources.libraries.python.PapiExecutor import PapiExecutor


class Memif(object):
    """Memif interface class."""

    def __init__(self):
        pass

    @staticmethod
    def _memif_dump(node):
        """Get the memif dump on the given node.

        :param node: Given node to get Memif dump from.
        :type node: dict
        :returns: Papi response including: papi reply, stdout, stderr and
            return code.
        :rtype: PapiResponse
        """
        with PapiExecutor(node) as papi_exec:
            dump = papi_exec.add("memif_dump").get_dump()

        return dump.reply

    # @staticmethod
    # def _memif_socket_filename_dump(node):
    #     """Get the memif socket file name dump on the given node.
    #
    #     :param node: Given node to get Memif socket file name dump from.
    #     :type node: dict
    #     :returns: Papi response including: papi reply, stdout, stderr and
    #         return code.
    #     :rtype: PapiResponse
    #     """
    #     with PapiExecutor(node) as papi_exec:
    #         dump = papi_exec.add("memif_socket_filename_dump").get_dump()
    #     return dump.reply

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
            data = papi_exec.add(cmd, **args).get_replies(err_msg).\
                verify_reply(err_msg=err_msg)
        return data

    @staticmethod
    def _memif_create(node, mid, sid, rxq=1, txq=1, role=0):
        """Create Memif interface on the given node.

        :param node: Given node to create Memif interface on.
        :param mid: Memif interface ID.
        :param sid: Socket ID.
        :param rxq: Number of RX queues; 0 means do not set.
        :param txq: Number of TX queues; 0 means do not set.
        :param role: Memif interface role [master=0|slave=1]. Default is master.
        :type node: dict
        :type mid: str
        :type sid: str
        :type rxq: int
        :type txq: int
        :type role: int
        :returns: Verified data from PAPI response. In this case, the response
            includes only retval.
        :rtype: dict
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
            data = papi_exec.add(cmd, **args).get_replies(err_msg).\
                verify_reply(err_msg=err_msg)
        return data

    @staticmethod
    def create_memif_interface(node, filename, mid, sid, rxq=1, txq=1, role=1):
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
        :type role: int
        :returns: SW interface index.
        :rtype: int
        :raises ValueError: If command 'create memif' fails.
        """

        # Create socket
        Memif._memif_socket_filename_add_del(node, True, filename, sid)

        # Create memif
        rsp = Memif._memif_create(node, mid, sid, rxq=rxq, txq=txq, role=role)

        sw_if_idx = rsp["sw_if_index"]

        # Update Topology
        if_key = Topology.add_new_port(node, 'memif')
        Topology.update_interface_sw_if_index(node, if_key, sw_if_idx)

        ifc_name = Memif.vpp_get_memif_interface_name(node, sw_if_idx)
        Topology.update_interface_name(node, if_key, ifc_name)

        ifc_mac = Memif.vpp_get_memif_interface_mac(node, sw_if_idx)
        Topology.update_interface_mac_address(node, if_key, ifc_mac)

        Topology.update_interface_memif_socket(node, if_key, '/tmp/' + filename)
        Topology.update_interface_memif_id(node, if_key, mid)
        Topology.update_interface_memif_role(node, if_key, str(role))

        return sw_if_idx

    @staticmethod
    def show_memif(node):
        """Show Memif data for the given node.

        :param node: Given node to show Memif data on.
        :type node: dict
        """

        Memif._memif_dump(node)

    @staticmethod
    def show_memif_on_all_duts(nodes):
        """Show Memif data on all DUTs.

        :param nodes: Topology nodes.
        :type nodes: dict
        """
        for node in nodes.values():
            if node['type'] == NodeType.DUT:
                Memif.show_memif(node)

    # @staticmethod
    # def parse_memif_dump_data(memif_data):
    #     """Convert Memif data to dictionary.
    #
    #     :param memif_data: Dump of Memif interfaces data.
    #     :type memif_data: str
    #     :returns: Memif interfaces data in dictionary.
    #     :rtype: dict
    #     :raises RuntimeError: If there is no memif interface name found in
    #         provided data.
    #     """
    #     memif_name = None
    #     memif_dict = dict()
    #     memif_data = str(memif_data)
    #     values = dict()
    #
    #     clutter = ['vat#']
    #     for garbage in clutter:
    #         memif_data = memif_data.replace(garbage, '')
    #
    #     for line in memif_data.splitlines():
    #         if not line or line.startswith('Sending'):
    #             continue
    #         elif line.startswith('memif'):
    #             if memif_name:
    #                 memif_dict[memif_name] = values
    #             line_split = line.split(':', 1)
    #             memif_name = str(line_split[0])
    #             values = dict()
    #             line = line_split[1]
    #         line_split = line.split()
    #         for i in range(0, len(line_split), 2):
    #             key = str(line_split[i])
    #             try:
    #                 value = line_split[i+1]
    #             except IndexError:
    #                 value = None
    #             values[key] = value
    #     if memif_name:
    #         memif_dict[memif_name] = values
    #     else:
    #         raise RuntimeError('No memif interface name found')
    #
    #     return memif_dict

    @staticmethod
    def vpp_get_memif_interface_name(node, sw_if_idx):
        """Get Memif interface name from Memif interfaces dump.

        :param node: DUT node.
        :param sw_if_idx: DUT node.
        :type node: dict
        :type sw_if_idx: int
        :returns: Memif interface name, or None if not found.
        :rtype: str
        """

        dump = Memif._memif_dump(node)

        for item in dump:
            print(item)
            if item["memif_details"]["sw_if_index"] == sw_if_idx:
                return item["if_name"]
        return None

    @staticmethod
    def vpp_get_memif_interface_mac(node, sw_if_idx):
        """Get Memif interface MAC address from Memif interfaces dump.

        :param node: DUT node.
        :param sw_if_idx: DUT node.
        :type node: dict
        :type sw_if_idx: int
        :returns: Memif interface MAC address, or None if not found.
        :rtype: str
        """

        dump = Memif._memif_dump(node)

        for item in dump.papi_reply:
            print(item)
            if item["memif_details"]["sw_if_index"] == sw_if_idx:
                return item["hw_addr"]
        return None
