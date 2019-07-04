# Copyright (c) 2019 Cisco and/or its affiliates.
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

from resources.libraries.python.PapiExecutor import PapiSocketExecutor
from resources.libraries.python.topology import Topology


class Cop(object):
    """COP utilities."""

    @staticmethod
    def cop_add_whitelist_entry(node, interface, ip_format, fib_id,
                                default_cop=0):
        """Add cop whitelisted entry.

        :param node: Node to add COP whitelist on.
        :param interface: Interface of the node where the COP is added.
        :param ip_format: IP format : ip4 or ip6 are valid formats.
        :param fib_id: Specify the fib table ID.
        :param default_cop: 1 => enable non-ip4, non-ip6 filtration.
        :type node: dict
        :type interface: str
        :type ip_format: str
        :type fib_id: int
        :type default_cop: int
        """
        if ip_format not in ('ip4', 'ip6'):
            raise ValueError("Ip not in correct format!")
        ip4 = ip6 = 0
        if ip_format == 'ip4':
            ip4 = 1
        else:
            ip6 = 1
        sw_if_index = Topology.get_interface_sw_index(node, interface)
        cmd = 'cop_whitelist_enable_disable'
        err_msg = 'Failed to add COP whitelist on ifc {ifc}'\
                  .format(ifc=interface)
        args_in = dict(
            sw_if_index=int(sw_if_index),
            fib_id=int(fib_id),
            ip4=ip4,
            ip6=ip6,
            default_cop=default_cop
        )

        with PapiSocketExecutor(node) as papi_exec:
            papi_exec.add(cmd, **args_in).get_reply(err_msg)

    @staticmethod
    def cop_interface_enable_or_disable(node, interface, state):
        """Enable or disable COP on the interface.

        :param node: Node to add COP whitelist on.
        :param interface: Interface of the node where the COP is added.
        :param state: disable/enable COP on the interface.
        :type node: dict
        :type interface: str
        :type state: str
        """
        state = state.lower()
        if state in ('enable', 'disable'):
            if state == 'enable':
                enable_disable = 1
            else:
                enable_disable = 0
            sw_if_index = Topology.get_interface_sw_index(node, interface)
            cmd = 'cop_interface_enable_disable'
            err_msg = 'Failed to enable or disable on {ifc}'\
                      .format(ifc=interface)

            args_in = dict(
                sw_if_index=int(sw_if_index),
                enable_disable=enable_disable
            )

            with PapiSocketExecutor(node) as papi_exec:
                papi_exec.add(cmd, **args_in).get_reply(err_msg)

        else:
            raise ValueError(
                "Possible values are 'enable' or 'disable'!"
            )
