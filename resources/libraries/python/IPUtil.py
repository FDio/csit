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

from ipaddress import IPv4Network, ip_address

from resources.libraries.python.ssh import SSH
from resources.libraries.python.constants import Constants
from resources.libraries.python.ssh import exec_cmd_no_error, exec_cmd
from resources.libraries.python.topology import Topology


class IPUtil(object):
    """Common IP utilities"""

    @staticmethod
    def vpp_ip_probe(node, interface, addr, if_type="key"):
        """Run ip probe on VPP node.

        :param node: VPP node.
        :param interface: Interface key or name.
        :param addr: IPv4/IPv6 address.
        :param if_type: Interface type
        :type node: dict
        :type interface: str
        :type addr: str
        :type if_type: str
        :raises ValueError: If the if_type is unknown.
        :raises Exception: If vpp probe fails.
        """
        ssh = SSH()
        ssh.connect(node)

        if if_type == "key":
            iface_name = Topology.get_interface_name(node, interface)
        elif if_type == "name":
            iface_name = interface
        else:
            raise ValueError("if_type unknown: {0}".format(if_type))

        cmd = "{c}".format(c=Constants.VAT_BIN_NAME)
        cmd_input = 'exec ip probe {dev} {ip}'.format(dev=iface_name, ip=addr)
        (ret_code, _, _) = ssh.exec_command_sudo(cmd, cmd_input)
        if int(ret_code) != 0:
            raise Exception('VPP ip probe {dev} {ip} failed on {h}'.format(
                dev=iface_name, ip=addr, h=node['host']))

    @staticmethod
    def ip_addresses_should_be_equal(ip1, ip2):
        """Fails if the given IP addresses are unequal.

        :param ip1: IPv4 or IPv6 address.
        :param ip2: IPv4 or IPv6 address.
        :type ip1: str
        :type ip2: str
        """

        addr1 = ip_address(unicode(ip1))
        addr2 = ip_address(unicode(ip2))

        if addr1 != addr2:
            raise AssertionError('IP addresses are not equal: {0} != {1}'.
                                 format(ip1, ip2))

    @staticmethod
    def setup_network_namespace(node, namespace_name, interface_name,
                                ip_address, prefix):
        """Setup namespace on given node and attach interface and IP to
        this namespace. Applicable also on TG node.

        :param node: Node to set namespace on.
        :param namespace_name: Namespace name.
        :param interface_name: Interface name.
        :param ip_address: IP address of namespace's interface.
        :param prefix: IP address prefix length.
        :type node: dict
        :type namespace_name: str
        :type vhost_if: str
        :type ip_address: str
        :type prefix: int
        """
        cmd = ('ip netns add {0}'.format(namespace_name))
        exec_cmd_no_error(node, cmd, sudo=True)

        cmd = ('ip link set dev {0} up netns {1}'.format(interface_name,
                                                         namespace_name))
        exec_cmd_no_error(node, cmd, sudo=True)

        cmd = ('ip netns exec {0} ip addr add {1}/{2} dev {3}'.format(
            namespace_name, ip_address, prefix, interface_name))
        exec_cmd_no_error(node, cmd, sudo=True)

    @staticmethod
    def linux_enable_forwarding(node, ip_ver='ipv4'):
        """Enable forwarding on a Linux node, e.g. VM.

        :param node: Node to enable forwarding on.
        :param ip_ver: IP version, 'ipv4' or 'ipv6'.
        :type node: dict
        :type ip_ver: str
        """
        cmd = 'sysctl -w net.{0}.ip_forward=1'.format(ip_ver)
        exec_cmd_no_error(node, cmd, sudo=True)

    @staticmethod
    def set_linux_interface_ip(node, interface, ip, prefix, namespace=None):
        """Set IP address to interface in linux.

        :param node: Node where to execute command.
        :param interface: Interface in namespace.
        :param ip: IP to be set on interface.
        :param prefix: IP prefix.
        :param namespace: Execute command in namespace. Optional
        :type node: dict
        :type interface: str
        :type ip: str
        :type prefix: int
        :type namespace: str
        :raises RuntimeError: IP could not be set.
        """
        if namespace is not None:
            cmd = 'ip netns exec {} ip addr add {}/{} dev {}'.format(
                namespace, ip, prefix, interface)
        else:
            cmd = 'ip addr add {}/{} dev {}'.format(ip, prefix, interface)
        (rc, _, stderr) = exec_cmd(node, cmd, timeout=5, sudo=True)
        if rc != 0:
            raise RuntimeError(
                'Could not set IP for interface, reason:{}'.format(stderr))

    @staticmethod
    def set_linux_interface_route(node, interface, route, namespace=None):
        """Set route via interface in linux.

        :param node: Node where to execute command.
        :param interface: Interface in namespace.
        :param route: Route to be added via interface.
        :param namespace: Execute command in namespace. Optional parameter.
        :type node: dict
        :type interface: str
        :type route: str
        :type namespace: str
        """
        if namespace is not None:
            cmd = 'ip netns exec {} ip route add {} dev {}'.format(
                namespace, route, interface)
        else:
            cmd = 'ip route add {} dev {}'.format(route, interface)
        exec_cmd_no_error(node, cmd, sudo=True)


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
