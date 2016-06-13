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

"""Tap utilities library."""

from resources.libraries.python.VatExecutor import VatTerminal
from resources.libraries.python.topology import Topology


class Tap(object):
    """COP utilities."""

    @staticmethod
    def add_tap_interface(node, tap_name, mac=None):
        """Add cop whitelisted entry.

        :param node: Node to add COP whitelist on.
        :param interface: Interface of the node where the COP is added.
        :param ip_format: IP format : ip4 or ip6 are valid formats.
        :param fib_id: Specify the fib table ID.
        :type node: dict
        :type interface: str
        :type ip_format: str
        :type fib_id: int
        """
        name = 'connect'
        if mac is not None:
            args = 'tapname {0} mac {1}'.format(tap_name, mac)
        else:
            args = 'tapname {0}'.format(tap_name)
        with VatTerminal(node) as vat:
            resp = vat.vat_terminal_exec_cmd_from_template('tap.vat',
                                                    tap_command=name,
                                                    tap_arguments=args)
            interface = resp[0]['sw_if_index']
            return  interface
