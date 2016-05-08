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

"""Common IP utilities library."""
from ipaddress import IPv4Network

from resources.libraries.python.ssh import SSH
from resources.libraries.python.constants import Constants

from resources.libraries.python.topology import Topology

class IPUtil(object):
    """Common IP utilities"""

    @staticmethod
    def vpp_ip_probe(node, iface_key, addr):
        """Run ip probe on VPP node.

        :param node: VPP node.
        :param iface_key: Interface key based on topology.
        :param addr: IPv4/IPv6 address.
        :type node: dict
        :type iface_key: str
        :type addr: str
        """
        ssh = SSH()
        ssh.connect(node)

        cmd = "{c}".format(c=Constants.VAT_BIN_NAME)
        iface_name = Topology.get_interface_name(node, iface_key)
        cmd_input = 'exec ip probe {dev} {ip}'.format(dev=iface_name, ip=addr)
        (ret_code, _, _) = ssh.exec_command_sudo(cmd, cmd_input)
        if int(ret_code) != 0:
            raise Exception('VPP ip probe {dev} {ip} failed on {h}'.format(
                dev=iface_name, ip=addr, h=node['host']))


def convert_ipv4_netmask_prefix(network):
    """Convert network mask to equivalent network prefix length or vice versa.

    Example: mask 255.255.0.0 -> prefix length 16
    :param network: Network mask or network prefix length.
    :type network: str or int
    :return: Network mask or network prefix length.
    :rtype: str or int
    """
    temp_address = "0.0.0.0"
    net = IPv4Network(u"{0}/{1}".format(temp_address, network), False)

    if isinstance(network, int) and (0 < network < 33):
        return str(net.netmask)
    elif isinstance(network, basestring):
        return int(net.prefixlen)
    else:
        raise Exception("Value {0} is not a valid ipv4 netmask or network"
                        " prefix length".format(network))
