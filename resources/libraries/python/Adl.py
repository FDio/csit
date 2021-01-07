# Copyright (c) 2021 Cisco and/or its affiliates.
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

"""ADL utilities library."""

from resources.libraries.python.PapiSocketExecutor import PapiSocketExecutor
from resources.libraries.python.topology import Topology


class Adl:
    """ADL utilities."""

    @staticmethod
    def adl_add_allowlist_entry(
            node, interface, ip_version, fib_id, default_adl=0):
        """Add adl allowlisted entry.

        :param node: Node to add ADL allowlist on.
        :param interface: Interface of the node where the ADL is added.
        :param ip_version: IP version. 'ip4' and 'ip6' are valid values.
        :param fib_id: Specify the fib table ID.
        :param default_adl: 1 => enable non-ip4, non-ip6 filtration,
            0 => disable it.
        :type node: dict
        :type interface: str
        :type ip_version: str
        :type fib_id: int
        :type default_adl: int
        :raises ValueError: If parameter 'ip_version' has incorrect value.
        """
        if ip_version not in (u"ip4", u"ip6"):
            raise ValueError(u"IP version is not in correct format")

        cmd = u"adl_allowlist_enable_disable"
        err_msg = f"Failed to add ADL allowlist on interface {interface} " \
            f"on host {node[u'host']}"
        args = dict(
            sw_if_index=Topology.get_interface_sw_index(node, interface),
            fib_id=int(fib_id),
            ip4=bool(ip_version == u"ip4"),
            ip6=bool(ip_version == u"ip6"),
            default_adl=default_adl
        )

        with PapiSocketExecutor(node) as papi_exec:
            papi_exec.add(cmd, **args).get_reply(err_msg)

    @staticmethod
    def adl_interface_enable_or_disable(node, interface, state):
        """Enable or disable ADL on the interface.

        :param node: Node to add ADL allowlist on.
        :param interface: Interface of the node where the ADL is added.
        :param state: Enable or disable ADL on the interface.
        :type node: dict
        :type interface: str
        :type state: str
        :raises ValueError: If parameter 'state' has incorrect value.
        """
        state = state.lower()
        if state in (u"enable", u"disable"):
            enable = bool(state == u"enable")
        else:
            raise ValueError(u"Possible state values are 'enable' or 'disable'")

        cmd = u"adl_interface_enable_disable"
        err_msg = f"Failed to enable/disable ADL on interface {interface} " \
            f"on host {node[u'host']}"
        args = dict(
            sw_if_index=Topology.get_interface_sw_index(node, interface),
            enable_disable=enable
        )

        with PapiSocketExecutor(node) as papi_exec:
            papi_exec.add(cmd, **args).get_reply(err_msg)
