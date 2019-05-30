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

"""IPv6 utilities library."""

import re

from resources.libraries.python.ssh import SSH
from resources.libraries.python.VatExecutor import VatTerminal
from resources.libraries.python.topology import Topology


class IPv6Util(object):
    """IPv6 utilities"""

    @staticmethod
    def add_ip_neighbor(node, interface, ip_address, mac_address):
        """Add IP neighbor.

        :param node: VPP node to add ip neighbor.
        :param interface: Interface name or sw_if_index.
        :param ip_address: IP address.
        :param mac_address: MAC address.
        :type node: dict
        :type interface: str or int
        :type ip_address: str
        :type mac_address: str
        """
        if isinstance(interface, basestring):
            sw_if_index = Topology.get_interface_sw_index(node, interface)
        else:
            sw_if_index = interface

        with VatTerminal(node) as vat:
            vat.vat_terminal_exec_cmd_from_template("add_ip_neighbor.vat",
                                                    sw_if_index=sw_if_index,
                                                    ip_address=ip_address,
                                                    mac_address=mac_address)
