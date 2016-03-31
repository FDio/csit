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

from resources.libraries.python.VatExecutor import VatExecutor


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
