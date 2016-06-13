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

"""Routing utilities library."""

from resources.libraries.python.VatExecutor import VatTerminal
from resources.libraries.python.topology import Topology
from resources.libraries.python.ssh import exec_cmd_no_error

class Routing(object):

    """Routing utilities."""

    @staticmethod
    def vpp_route_add(node, network, prefix_len, gateway=None, interface=None,
                      use_sw_index=True, resolve_attempts=10, count=1):
        """Add route to the VPP node.

        :param node: Node to add route on.
        :param network: Route destination network address.
        :param prefix_len: Route destination network prefix length.
        :param gateway: Route gateway address.
        :param interface: Route interface.
        :param use_sw_index: Use sw_if_index in VAT command.
        :param resolve_attempts: Resolve attempts IP route add parameter.
        :param count: number of IP addresses to add starting from network IP
            with same prefix (increment is 1)
        If None, then is not used.
        :type node: dict
        :type network: str
        :type prefix_len: int
        :type gateway: str
        :type interface: str
        :type use_sw_index: bool
        :type resolve_attempts: int
        :type count: int
        """
        if use_sw_index:
            int_cmd = ('sw_if_index {}'.
                       format(Topology.get_interface_sw_index(node, interface)))
        else:
            int_cmd = interface

        rap = 'resolve-attempts {}'.format(resolve_attempts) \
            if resolve_attempts else ''

        via = 'via {}'.format(gateway) if gateway else ''

        cnt = 'count {}'.format(count) \
            if count else ''

        with VatTerminal(node, json_param=False) as vat:
            vat.vat_terminal_exec_cmd_from_template('add_route.vat',
                                                    network=network,
                                                    prefix_length=prefix_len,
                                                    via=via,
                                                    interface=int_cmd,
                                                    resolve_attempts=rap,
                                                    count=cnt)

    @staticmethod
    def add_fib_table(node, network, prefix_len, fib_id, place):
        """Create new FIB table according to ID.

        :param node: Node to add FIB on.
        :param network: IP address to add to the FIB table.
        :param prefix_len: IP address prefix length.
        :param fib_id: FIB table ID.
        :param place: Possible variants are local, drop.
        :type node: dict
        :type network: str
        :type prefix_len: int
        :type fib_id: int
        :type place: str
        """
        with VatTerminal(node) as vat:
            vat.vat_terminal_exec_cmd_from_template('add_fib_table.vat',
                                                    network=network,
                                                    prefix_length=prefix_len,
                                                    fib_number=fib_id,
                                                    where=place)

    @staticmethod
    def add_route(node, ip, prefix, gw, namespace=None):
        """Add route in namespace.

        :param node: Node where to execute command.
        :param ip: Route destination IP.
        :param prefix: IP prefix.
        :param namespace: Execute command in namespace. Optional
        :param gw: Gateway.
        :type node: dict
        :type ip: str
        :type prefix: int
        :type gw: str
        :type namespace: str
        """
        if namespace is not None:
            cmd = 'ip netns exec {} ip route add {}/{} via {}'.format(
                namespace, ip, prefix, gw)
        else:
            cmd = 'ip route add {}/{} via {}'.format(ip, prefix, gw)
        exec_cmd_no_error(node, cmd, sudo=True)
