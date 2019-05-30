# Copyright (c) 2018 Cisco and/or its affiliates.
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

"""Routing utilities library."""

from resources.libraries.python.VatExecutor import VatTerminal
from resources.libraries.python.topology import Topology
from resources.libraries.python.ssh import exec_cmd_no_error


class Routing(object):
    """Routing utilities."""

    # @staticmethod
    # def add_fib_table(node, table_id, ipv6=False):
    #     """Create new FIB table according to ID.
    #
    #     :param node: Node to add FIB on.
    #     :param table_id: FIB table ID.
    #     :param ipv6: Is this an IPv6 table
    #     :type node: dict
    #     :type table_id: int
    #     :type ipv6: bool
    #     """
    #     with VatTerminal(node) as vat:
    #         vat.vat_terminal_exec_cmd_from_template('add_fib_table.vat',
    #                                                 table_id=table_id,
    #                                                 ipv6="ipv6" if ipv6 else "")

    @staticmethod
    def add_route(node, ip_addr, prefix, gateway, namespace=None):
        """Add route in namespace.

        :param node: Node where to execute command.
        :param ip_addr: Route destination IP address.
        :param prefix: IP prefix.
        :param namespace: Execute command in namespace. Optional.
        :param gateway: Gateway address.
        :type node: dict
        :type ip_addr: str
        :type prefix: int
        :type gateway: str
        :type namespace: str
        """
        if namespace is not None:
            cmd = 'ip netns exec {} ip route add {}/{} via {}'.format(
                namespace, ip_addr, prefix, gateway)
        else:
            cmd = 'ip route add {}/{} via {}'.format(ip_addr, prefix, gateway)
        exec_cmd_no_error(node, cmd, sudo=True)
