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

    @staticmethod
    def vpp_route_add(node, network, prefix_len, gateway=None,
                      interface=None, use_sw_index=True, resolve_attempts=10,
                      count=1, vrf=None, lookup_vrf=None, multipath=False,
                      weight=None, local=False):
        """Add route to the VPP node.

        :param node: Node to add route on.
        :param network: Route destination network address.
        :param prefix_len: Route destination network prefix length.
        :param gateway: Route gateway address.
        :param interface: Route interface.
        :param vrf: VRF table ID (Optional).
        :param use_sw_index: Use sw_if_index in VAT command.
        :param resolve_attempts: Resolve attempts IP route add parameter.
        :param count: number of IP addresses to add starting from network IP
        :param local: The route is local
            with same prefix (increment is 1). If None, then is not used.
        :param lookup_vrf: VRF table ID for lookup.
        :param multipath: Enable multipath routing.
        :param weight: Weight value for unequal cost multipath routing.
        :type node: dict
        :type network: str
        :type prefix_len: int
        :type gateway: str
        :type interface: str
        :type use_sw_index: bool
        :type resolve_attempts: int
        :type count: int
        :type vrf: int
        :type lookup_vrf: int
        :type multipath: bool
        :type weight: int
        :type local: bool
        """
        if interface:
            if use_sw_index:
                int_cmd = ('sw_if_index {}'.
                           format(Topology.get_interface_sw_index(node,
                                                                  interface)))
            else:
                int_cmd = interface
        else:
            int_cmd = ''

        rap = 'resolve-attempts {}'.format(resolve_attempts) \
            if resolve_attempts else ''

        via = 'via {}'.format(gateway) if gateway else ''

        cnt = 'count {}'.format(count) \
            if count else ''

        vrf = 'vrf {}'.format(vrf) if vrf else ''

        lookup_vrf = 'lookup-in-vrf {}'.format(lookup_vrf) if lookup_vrf else ''

        multipath = 'multipath' if multipath else ''

        weight = 'weight {}'.format(weight) if weight else ''

        local = 'local' if local else ''

        with VatTerminal(node, json_param=False) as vat:
            vat.vat_terminal_exec_cmd_from_template('add_route.vat',
                                                    network=network,
                                                    prefix_length=prefix_len,
                                                    via=via,
                                                    vrf=vrf,
                                                    interface=int_cmd,
                                                    resolve_attempts=rap,
                                                    count=cnt,
                                                    lookup_vrf=lookup_vrf,
                                                    multipath=multipath,
                                                    weight=weight,
                                                    local=local)

    @staticmethod
    def add_fib_table(node, table_id, ipv6=False):
        """Create new FIB table according to ID.

        :param node: Node to add FIB on.
        :param table_id: FIB table ID.
        :param ipv6: Is this an IPv6 table
        :type node: dict
        :type table_id: int
        :type ipv6: bool
        """
        with VatTerminal(node) as vat:
            vat.vat_terminal_exec_cmd_from_template('add_fib_table.vat',
                                                    table_id=table_id,
                                                    ipv6="ipv6" if ipv6 else "")

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
