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

"""Library to set up cross-connect in topology."""

from resources.libraries.python.VatExecutor import VatExecutor
from resources.libraries.python.topology import Topology

__all__ = ['CrossConnectSetup']

class CrossConnectSetup(object):
    """Crossconnect setup in topology."""

    def __init__(self):
        pass

    @staticmethod
    def vpp_setup_bidirectional_cross_connect(node, interface1, interface2):
        """Create crossconnect between 2 interfaces on vpp node.

        :param node: Node to add bidirectional crossconnect
        :param interface1: first interface
        :param interface2: second interface
        :type node: dict
        :type interface1: str
        :type interface2: str
        """
        sw_iface1 = Topology().get_interface_sw_index(node, interface1)
        sw_iface2 = Topology().get_interface_sw_index(node, interface2)
        VatExecutor.cmd_from_template(node, "l2_xconnect.vat",
                                      interface1=sw_iface1,
                                      interface2=sw_iface2)
        VatExecutor.cmd_from_template(node, "l2_xconnect.vat",
                                      interface1=sw_iface2,
                                      interface2=sw_iface1)
