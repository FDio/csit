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


class Memif(object):
    """Memif interface class."""

    def __init__(self):
        pass

    @staticmethod
    def create_memif_interface(node, socket, mid, role="master"):
        """Create Memif interface on the given node.

        :param node: Given node to create Memif interface on.
        :param socket: Memif interface socket path.
        :param mid: Memif interface ID.
        :param role: Memif interface role [master|slave]. Default is master.
        :type node: dict
        :type socket: str
        :type mid: str
        :type role: str
        :returns: SW interface index.
        :rtype: int
        :raises ValueError: If command 'create memif' fails.
        """

        with VatTerminal(node, json_param=False) as vat:
            vat.vat_terminal_exec_cmd_from_template(
                'memif_create.vat',
                socket=socket, id=mid, role=role)
            if 'sw_if_index' in vat.vat_stdout:
                try:
                    return int(vat.vat_stdout.split()[4])
                except KeyError:
                    raise ValueError('Create Memif interface failed on node '
                                     '{}"'.format(node['host']))
            else:
                raise ValueError('Create Memif interface failed on node '
                                 '{}"'.format(node['host']))

    @staticmethod
    def show_memif(node):
        """Show Memif data for the given node.

        :param node: Given node to show Memif data on.
        :type node: dict
        """
        vat = VatExecutor()
        vat.execute_script("memif_dump.vat", node, json_out=False)

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
