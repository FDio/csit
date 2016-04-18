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

"""COP utilities library."""

from resources.libraries.python.VatExecutor import VatTerminal
from resources.libraries.python.topology import Topology


class Cop(object):
    """Cop utilities."""

    @staticmethod
    def cop_add_whitelist_entry(node, interface, ip_format, fib_id):
        """Add cop whitelisted entry.

        :param node: Node to add cop whitelist on.
        :param interface: Interface of the node where the cop is added
        :param ip_format: Ip format : ipv4 or ipv6 are valid formats
        :param fib_id: Specify the fib table id
        :type node: dict
        :type interface: str
        :type ip_format: str
        :type fib_id: int
        """
        sw_if_index = Topology.get_interface_sw_index(node, interface)
        with VatTerminal(node) as vat:
            vat.vat_terminal_exec_cmd_from_template('cop_whitelist.vat',
                                                    sw_if_index=sw_if_index,
                                                    ip=ip_format,
                                                    fib_id=fib_id)

    @staticmethod
    def cop_interface_enable_or_disable(node, interface, state):
        """Enable or disable cop interface.

        :param node: Node to add cop whitelist on.
        :param interface: Interface of the node where the cop is added
        :param state: disable/enable cop interface
        :type node: dict
        :type interface: str
        :type state: str
        """
        if state != 'disable':
            state = ''
        sw_if_index = Topology.get_interface_sw_index(node, interface)
        with VatTerminal(node) as vat:
            vat.vat_terminal_exec_cmd_from_template('cop_interface.vat',
                                                    sw_if_index=sw_if_index,
                                                    state=state)
