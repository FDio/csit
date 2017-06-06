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

from resources.libraries.python.VatExecutor import VatExecutor, VatTerminal


class Memif(object):
    """Memif interface class."""

    def __init__(self):
        pass

    @staticmethod
    def create_memif_interface(node, socket, key="0x1", role="master"):
        """Create Memif interface on the given node.

        :param node: Given node to create Memif interface on.
        :param socket: Memif interface socket path.
        :param key: Memif interface key.
        :param role: Memif interface role [master|slave]. Default is master.
        :type node: dict
        :type socket: str
        :type key: str
        :type role: str
        :return: SW interface index.
        :rtype: int
        :raises RuntimeError: If command 'create memif' fails.
        """

        try:
            with VatTerminal(node) as vat:
                response = vat.vat_terminal_exec_cmd_from_template(
                    'memif_create.vat',
                    socket=socket, key=key, role=role)
                if response[0].get('retval') == 0:
                    return response[0].get('sw_if_index')
        except:
            raise RuntimeError('Create Memif interface failed on node "{}"'
                               .format(node['host']))

        return None

    @staticmethod
    def show_memif(node):
        """Show Memif data for the given node.

        :param node: Given node to show Memif data on.
        :type node: dict
        :return: nothing
        """
        vat = VatExecutor()
        vat.execute_script("memif_dump.vat", node, json_out=False)
