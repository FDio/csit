# Copyright (c) 2017 Cisco and/or its affiliates.
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

from resources.libraries.python.ssh import SSH
from resources.libraries.python.VatExecutor import VatExecutor, VatTerminal
from resources.libraries.python.topology import Topology


class Memif(object):
    """Memif interface class."""

    def __init__(self):
        pass

    @staticmethod
    def create_memif_interface(node, filename, mid, sid, rxq=1, txq=1,
                               role='slave'):
        """Create Memif interface on the given node.

        :param node: Given node to create Memif interface on.
        :param filename: Memif interface socket filename.
        :param mid: Memif interface ID.
        :param sid: Socket ID.
        :param rxq: Number of RX queues.
        :param txq: Number of TX queues.
        :param role: Memif interface role [master|slave]. Default is master.
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

        with VatTerminal(node, json_param=False) as vat:
            vat.vat_terminal_exec_cmd_from_template(
                'memif_socket_filename_add_del.vat',
                add_del='add', id=sid, filename='/tmp/'+filename)
            vat.vat_terminal_exec_cmd_from_template(
                'memif_create.vat', id=mid, socket=sid, rxq=rxq, txq=txq,
                role=role)
            if 'sw_if_index' in vat.vat_stdout:
                try:
                    sw_if_idx = int(vat.vat_stdout.split()[4])
                    if_key = Topology.add_new_port(node, 'memif')
                    Topology.update_interface_sw_if_index(
                        node, if_key, sw_if_idx)
                    ifc_name = Memif.vpp_get_memif_interface_name(
                        node, sw_if_idx)
                    Topology.update_interface_name(node, if_key, ifc_name)
                    ifc_mac = Memif.vpp_get_memif_interface_mac(node, sw_if_idx)
                    Topology.update_interface_mac_address(node, if_key, ifc_mac)
                    Topology.update_interface_memif_socket(node, if_key,
                                                           '/tmp/'+filename)
                    Topology.update_interface_memif_id(node, if_key, mid)
                    Topology.update_interface_memif_role(node, if_key, role)
                    return sw_if_idx
                except KeyError:
                    raise ValueError('Create Memif interface failed on node '
                                     '{}'.format(node['host']))
            else:
                raise ValueError('Create Memif interface failed on node '
                                 '{}'.format(node['host']))

    @staticmethod
    def dump_memif(node):
        """Dump Memif data for the given node.

        :param node: Given node to show Memif data on.
        :type node: dict
        """
        vat = VatExecutor()
        vat.execute_script("memif_dump.vat", node, json_out=False)

    @staticmethod
    def show_memif(node):
        """Show Memif data for the given node.

        :param node: Given node to show Memif data on.
        :type node: dict
        """
        vat = VatExecutor()
        vat.execute_script("show_memif.vat", node, json_out=False)

    @staticmethod
    def clear_memif_socks(node, *socks):
        """Clear Memif sockets for the given node.

        :param node: Given node to clear Memif sockets on.
        :param socks: Memif sockets.
        :type node: dict
        :type socks: list
        """
        ssh = SSH()
        ssh.connect(node)

        for sock in socks:
            ssh.exec_command_sudo('rm -f {}'.format(sock))

    @staticmethod
    def parse_memif_dump_data(memif_data):
        """Convert Memif data to dictionary.

        :param memif_data: Dump of Memif interfaces data.
        :type memif_data: str
        :returns: Memif interfaces data in dictionary.
        :rtype: dict
        :raises RuntimeError: If there is no memif interface name found in
            provided data.
        """
        memif_name = None
        memif_dict = dict()
        memif_data = str(memif_data)
        values = dict()

        clutter = ['vat#']
        for garbage in clutter:
            memif_data = memif_data.replace(garbage, '')

        for line in memif_data.splitlines():
            if line.startswith('Sending') or len(line) == 0:
                continue
            elif line.startswith('memif'):
                if memif_name:
                    memif_dict[memif_name] = values
                line_split = line.split(':', 1)
                memif_name = str(line_split[0])
                values = dict()
                line = line_split[1]
            line_split = line.split()
            for i in range(0, len(line_split), 2):
                key = str(line_split[i])
                try:
                    value = line_split[i+1]
                except IndexError:
                    value = None
                values[key] = value
        if memif_name:
            memif_dict[memif_name] = values
        else:
            raise RuntimeError('No memif interface name found')

        return memif_dict

    @staticmethod
    def vpp_get_memif_interface_name(node, sw_if_idx):
        """Get Memif interface name from Memif interfaces dump.

        :param node: DUT node.
        :param sw_if_idx: DUT node.
        :type node: dict
        :type sw_if_idx: int
        :returns: Memif interface name.
        :rtype: str
        """
        with VatTerminal(node, json_param=False) as vat:
            vat.vat_terminal_exec_cmd_from_template('memif_dump.vat')
            memif_data = Memif.parse_memif_dump_data(vat.vat_stdout)
            for item in memif_data:
                if memif_data[item]['sw_if_index'] == str(sw_if_idx):
                    return item
        return None

    @staticmethod
    def vpp_get_memif_interface_mac(node, sw_if_idx):
        """Get Memif interface MAC address from Memif interfaces dump.

        :param node: DUT node.
        :param sw_if_idx: DUT node.
        :type node: dict
        :type sw_if_idx: int
        :returns: Memif interface MAC address.
        :rtype: str
        """
        with VatTerminal(node, json_param=False) as vat:
            vat.vat_terminal_exec_cmd_from_template('memif_dump.vat')
            memif_data = Memif.parse_memif_dump_data(vat.vat_stdout)
            for item in memif_data:
                if memif_data[item]['sw_if_index'] == str(sw_if_idx):
                    return memif_data[item].get('mac', None)

    @staticmethod
    def vpp_get_memif_interface_socket(node, sw_if_idx):
        """Get Memif interface socket path from Memif interfaces dump.

        :param node: DUT node.
        :param sw_if_idx: DUT node.
        :type node: dict
        :type sw_if_idx: int
        :returns: Memif interface socket path.
        :rtype: str
        """
        with VatTerminal(node, json_param=False) as vat:
            vat.vat_terminal_exec_cmd_from_template('memif_dump.vat')
            memif_data = Memif.parse_memif_dump_data(vat.vat_stdout)
            for item in memif_data:
                if memif_data[item]['sw_if_index'] == str(sw_if_idx):
                    return memif_data[item].get('socket', None)

    @staticmethod
    def vpp_get_memif_interface_id(node, sw_if_idx):
        """Get Memif interface ID from Memif interfaces dump.

        :param node: DUT node.
        :param sw_if_idx: DUT node.
        :type node: dict
        :type sw_if_idx: int
        :returns: Memif interface ID.
        :rtype: int
        """
        with VatTerminal(node, json_param=False) as vat:
            vat.vat_terminal_exec_cmd_from_template('memif_dump.vat')
            memif_data = Memif.parse_memif_dump_data(vat.vat_stdout)
            for item in memif_data:
                if memif_data[item]['sw_if_index'] == str(sw_if_idx):
                    return int(memif_data[item].get('id', None))

    @staticmethod
    def vpp_get_memif_interface_role(node, sw_if_idx):
        """Get Memif interface role from Memif interfaces dump.

        :param node: DUT node.
        :param sw_if_idx: DUT node.
        :type node: dict
        :type sw_if_idx: int
        :returns: Memif interface role.
        :rtype: int
        """
        with VatTerminal(node, json_param=False) as vat:
            vat.vat_terminal_exec_cmd_from_template('memif_dump.vat')
            memif_data = Memif.parse_memif_dump_data(vat.vat_stdout)
            for item in memif_data:
                if memif_data[item]['sw_if_index'] == str(sw_if_idx):
                    return memif_data[item].get('role', None)
