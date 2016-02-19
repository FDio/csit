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

"""Interface util library"""

from resources.libraries.python.ssh import exec_cmd_no_error
from resources.libraries.python.topology import NodeType, Topology
from resources.libraries.python.VatExecutor import VatExecutor


class InterfaceUtil(object):
    """General utilities for managing interfaces"""

    @staticmethod
    def set_interface_state(node, interface, state):
        """Set interface state on a node.

        Function can be used for DUTs as well as for TGs.

        :param node: node where the interface is
        :param interface: interface name
        :param state: one of 'up' or 'down'
        :type node: dict
        :type interface: str
        :type state: str
        :return: nothing
        """
        if node['type'] == NodeType.DUT:
            if state == 'up':
                state = 'admin-up'
            elif state == 'down':
                state = 'admin-down'
            else:
                raise Exception('Unexpected interface state: {}'.format(state))

            sw_if_index = Topology.get_interface_sw_index(node, interface)
            VatExecutor.cmd_from_template(node, 'set_if_state.vat',
                                          sw_if_index=sw_if_index, state=state)

        elif node['type'] == NodeType.TG:
            cmd = 'ip link set {} {}'.format(interface, state)
            exec_cmd_no_error(node, cmd, sudo=True)
        else:
            raise Exception('Unknown NodeType: "{}"'.format(node['type']))
