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
from netaddr.ip import IPNetwork

from resources.libraries.python.ssh import SSH
from resources.libraries.python.constants import Constants


class IPUtil(object):
    """Common IP utilities"""

    @staticmethod
    def vpp_ip_probe(node, interface, addr):
        """Run ip probe on VPP node.

        :param node: VPP node.
        :param interface: Interface name.
        :param addr: IPv4/IPv6 address.
        :type node: dict
        :type interface: str
        :type addr: str
        """
        ssh = SSH()
        ssh.connect(node)

        cmd = "{c}".format(c=Constants.VAT_BIN_NAME)
        cmd_input = 'exec ip probe {dev} {ip}'.format(dev=interface, ip=addr)
        (ret_code, _, _) = ssh.exec_command_sudo(cmd, cmd_input)
        if int(ret_code) != 0:
            raise Exception('VPP ip probe {dev} {ip} failed on {h}'.format(
                dev=interface, ip=addr, h=node['host']))


def convert_netmask_prefix(subnet, ip_version):
    """Convert subnet mask to equivalent subnet prefix length or vice versa.

    Example: mask 255.255.0.0 -> prefix length 16
    :param subnet: subnet mask or subnet prefix length.
    :param ip_version: IP protocol version (ipv4 or ipv6).
    :type subnet: str or int
    :type ip_version: str
    :return: subnet mask or subnet prefix length.
    :rtype: str or int
    """
    ip_version = int(ip_version[-1])
    if ip_version == 4:
        temp_address = "192.168.0.2"
    elif ip_version == 6:
        temp_address = "0:0:0:0:0:ffff:c0a8:2"
    else:
        raise Exception("IP version {0} is not valid. "
                        "Valid options are: ipv4, ipv6".format(ip_version))
    net = IPNetwork(temp_address, subnet, ip_version)

    if isinstance(subnet, int):
        return net.netmask
    elif isinstance(subnet, basestring):
        return net.prefixlen
