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

"""Common IP utilities library."""

import re

from socket import AF_INET, AF_INET6, inet_ntop, inet_pton

from ipaddress import IPv4Network, IPv6Address, ip_address
from ipaddress import AddressValueError, NetmaskValueError

from resources.libraries.python.ssh import SSH
from resources.libraries.python.Constants import Constants
from resources.libraries.python.InterfaceUtil import InterfaceUtil
from resources.libraries.python.PapiExecutor import PapiExecutor
from resources.libraries.python.ssh import exec_cmd_no_error, exec_cmd
from resources.libraries.python.topology import Topology


class IPUtil(object):
    """Common IP utilities"""

    @staticmethod
    def ip_to_int(ip_str):
        """Convert IP address from string format (e.g. 10.0.0.1) to integer
        representation (167772161).

        :param ip_str: IP address in string representation.
        :type ip_str: str
        :returns: Integer representation of IP address.
        :rtype: int
        """
        return int(ip_address(unicode(ip_str)))

    @staticmethod
    def int_to_ip(ip_int):
        """Convert IP address from integer representation (e.g. 167772161) to
        string format (10.0.0.1).

        :param ip_int: IP address in integer representation.
        :type ip_int: int
        :returns: String representation of IP address.
        :rtype: str
        """
        return str(ip_address(ip_int))

    @staticmethod
    def vpp_get_interface_ip_addresses(node, interface, ip_version):
        """Get list of IP addresses from an interface on a VPP node.

        :param node: VPP node to get data from.
        :param interface: Name of an interface on the VPP node.
        :param ip_version: IP protocol version (ipv4 or ipv6).
        :type node: dict
        :type interface: str
        :type ip_version: str
        :returns: List of dictionaries, each containing IP address, subnet
            prefix length and also the subnet mask for ipv4 addresses.
            Note: A single interface may have multiple IP addresses assigned.
        :rtype: list
        """

        try:
            sw_if_index = Topology.convert_interface_reference(
                node, interface, 'sw_if_index')
        except RuntimeError:
            if isinstance(interface, basestring):
                sw_if_index = InterfaceUtil.get_sw_if_index(node, interface)
            else:
                raise

        is_ipv6 = 1 if ip_version == 'ipv6' else 0

        cmd = 'ip_address_dump'
        cmd_reply = 'ip_address_details'
        args = dict(sw_if_index=sw_if_index,
                    is_ipv6=is_ipv6)
        err_msg = 'Failed to get L2FIB dump on host {host}'.format(
            host=node['host'])
        with PapiExecutor(node) as papi_exec:
            papi_resp = papi_exec.add(cmd, **args).get_dump(err_msg)

        data = list()
        for item in papi_resp.reply[0]['api_reply']:
            item[cmd_reply]['ip'] = inet_ntop(AF_INET6, item[cmd_reply]['ip']) \
                if is_ipv6 else inet_ntop(AF_INET, item[cmd_reply]['ip'][0:4])
            data.append(item[cmd_reply])

        if ip_version == 'ipv4':
            for item in data:
                item['netmask'] = convert_ipv4_netmask_prefix(
                    item['prefix_length'])
        return data

    @staticmethod
    def get_interface_vrf_table(node, interface, ip_version='ipv4'):
        """Get vrf ID for the given interface.

        :param node: VPP node.
        :param interface: Name or sw_if_index of a specific interface.
        :type node: dict
        :param ip_version: IP protocol version (ipv4 or ipv6).
        :type interface: str or int
        :type ip_version: str
        :returns: vrf ID of the specified interface.
        :rtype: int
        """
        if isinstance(interface, basestring):
            sw_if_index = InterfaceUtil.get_sw_if_index(node, interface)
        else:
            sw_if_index = interface

        is_ipv6 = 1 if ip_version == 'ipv6' else 0

        cmd = 'sw_interface_get_table'
        args = dict(sw_if_index=sw_if_index,
                    is_ipv6=is_ipv6)
        err_msg = 'Failed to get VRF id assigned to interface {ifc}'.format(
            ifc=interface)
        with PapiExecutor(node) as papi_exec:
            papi_resp = papi_exec.add(cmd, **args).get_replies(err_msg). \
                verify_reply(err_msg=err_msg)

        return papi_resp['vrf_id']

    @staticmethod
    def vpp_ip_source_check_setup(node, if_name):
        """Setup Reverse Path Forwarding source check on interface.

        :param node: Node to setup RPF source check.
        :param if_name: Interface name to setup RPF source check.
        :type node: dict
        :type if_name: str
        """

        cmd = 'ip_source_check_interface_add_del'
        args = dict(
            sw_if_index=InterfaceUtil.get_interface_index(node, if_name),
            is_add=1,
            loose=0)
        err_msg = 'Failed to enable source check on interface {ifc}'.format(
            ifc=if_name)
        with PapiExecutor(node) as papi_exec:
            papi_exec.add(cmd, **args).get_replies(err_msg). \
                verify_reply(err_msg=err_msg)

    @staticmethod
    def vpp_ip_probe(node, interface, addr):
        """Run ip probe on VPP node.

        :param node: VPP node.
        :param interface: Interface key or name.
        :param addr: IPv4/IPv6 address.
        :type node: dict
        :type interface: str
        :type addr: str
        """

        cmd = 'ip_probe_neighbor'
        args = dict(
            sw_if_index=InterfaceUtil.get_interface_index(node, interface),
            dst=addr)
        err_msg = 'VPP ip probe {dev} {ip} failed on {h}'.format(
            dev=interface, ip=addr, h=node['host'])

        with PapiExecutor(node) as papi_exec:
            papi_exec.add(cmd, **args).get_replies(err_msg). \
                verify_reply(err_msg=err_msg)
            
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
                                ip_addr, prefix):
        """Setup namespace on given node and attach interface and IP to
        this namespace. Applicable also on TG node.

        :param node: Node to set namespace on.
        :param namespace_name: Namespace name.
        :param interface_name: Interface name.
        :param ip_addr: IP address of namespace's interface.
        :param prefix: IP address prefix length.
        :type node: dict
        :type namespace_name: str
        :type vhost_if: str
        :type ip_addr: str
        :type prefix: int
        """
        cmd = ('ip netns add {0}'.format(namespace_name))
        exec_cmd_no_error(node, cmd, sudo=True)

        cmd = ('ip link set dev {0} up netns {1}'.format(interface_name,
                                                         namespace_name))
        exec_cmd_no_error(node, cmd, sudo=True)

        cmd = ('ip netns exec {0} ip addr add {1}/{2} dev {3}'.format(
            namespace_name, ip_addr, prefix, interface_name))
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
    def get_linux_interface_name(node, pci_addr):
        """Get the interface name.

        :param node: Node where to execute command.
        :param pci_addr: PCI address
        :type node: dict
        :type pci_addr: str
        :returns: Interface name
        :rtype: str
        :raises RuntimeError: If cannot get the information about interfaces.
        """

        regex_intf_info = r"pci@" \
                          r"([0-9a-f]{4}:[0-9a-f]{2}:[0-9a-f]{2}.[0-9a-f])\s*" \
                          r"([a-zA-Z0-9]*)\s*network"

        cmd = "lshw -class network -businfo"
        ret_code, stdout, stderr = exec_cmd(node, cmd, timeout=30, sudo=True)
        if ret_code != 0:
            raise RuntimeError('Could not get information about interfaces, '
                               'reason:{0}'.format(stderr))

        for line in stdout.splitlines()[2:]:
            try:
                if re.search(regex_intf_info, line).group(1) == pci_addr:
                    return re.search(regex_intf_info, line).group(2)
            except AttributeError:
                continue
        return None

    @staticmethod
    def set_linux_interface_up(node, interface):
        """Set the specified interface up.

        :param node: Node where to execute command.
        :param interface: Interface in namespace.
        :type node: dict
        :type interface: str
        :raises RuntimeError: If the interface could not be set up.
        """

        cmd = "ip link set {0} up".format(interface)
        ret_code, _, stderr = exec_cmd(node, cmd, timeout=30, sudo=True)
        if ret_code != 0:
            raise RuntimeError('Could not set the interface up, reason:{0}'.
                               format(stderr))

    @staticmethod
    def set_linux_interface_ip(node, interface, ip_addr, prefix,
                               namespace=None):
        """Set IP address to interface in linux.

        :param node: Node where to execute command.
        :param interface: Interface in namespace.
        :param ip_addr: IP to be set on interface.
        :param prefix: IP prefix.
        :param namespace: Execute command in namespace. Optional
        :type node: dict
        :type interface: str
        :type ip_addr: str
        :type prefix: int
        :type namespace: str
        :raises RuntimeError: IP could not be set.
        """
        if namespace is not None:
            cmd = 'ip netns exec {} ip addr add {}/{} dev {}'.format(
                namespace, ip_addr, prefix, interface)
        else:
            cmd = 'ip addr add {}/{} dev {}'.format(ip_addr, prefix, interface)
        (ret_code, _, stderr) = exec_cmd(node, cmd, timeout=5, sudo=True)
        if ret_code != 0:
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
    :returns: Network mask or network prefix length.
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
