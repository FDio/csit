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

"""Common IP utilities library."""

import re

from enum import IntEnum
from ipaddress import ip_address

from resources.libraries.python.Constants import Constants
from resources.libraries.python.InterfaceUtil import InterfaceUtil
from resources.libraries.python.PapiExecutor import PapiSocketExecutor
from resources.libraries.python.ssh import exec_cmd_no_error, exec_cmd
from resources.libraries.python.topology import Topology
from resources.libraries.python.VatExecutor import VatTerminal


# from vpp/src/vnet/vnet/mpls/mpls_types.h
MPLS_IETF_MAX_LABEL = 0xfffff
MPLS_LABEL_INVALID = MPLS_IETF_MAX_LABEL + 1


class AddressFamily(IntEnum):
    """IP address family."""
    ADDRESS_IP4 = 0
    ADDRESS_IP6 = 1


class FibPathType(IntEnum):
    """FIB path types."""
    FIB_PATH_TYPE_NORMAL = 0
    FIB_PATH_TYPE_LOCAL = 1
    FIB_PATH_TYPE_DROP = 2
    FIB_PATH_TYPE_UDP_ENCAP = 3
    FIB_PATH_TYPE_BIER_IMP = 4
    FIB_PATH_TYPE_ICMP_UNREACH = 5
    FIB_PATH_TYPE_ICMP_PROHIBIT = 6
    FIB_PATH_TYPE_SOURCE_LOOKUP = 7
    FIB_PATH_TYPE_DVR = 8
    FIB_PATH_TYPE_INTERFACE_RX = 9
    FIB_PATH_TYPE_CLASSIFY = 10


class FibPathFlags(IntEnum):
    """FIB path flags."""
    FIB_PATH_FLAG_NONE = 0
    FIB_PATH_FLAG_RESOLVE_VIA_ATTACHED = 1  #pylint: disable=invalid-name
    FIB_PATH_FLAG_RESOLVE_VIA_HOST = 2


class FibPathNhProto(IntEnum):
    """FIB path next-hop protocol."""
    FIB_PATH_NH_PROTO_IP4 = 0
    FIB_PATH_NH_PROTO_IP6 = 1
    FIB_PATH_NH_PROTO_MPLS = 2
    FIB_PATH_NH_PROTO_ETHERNET = 3
    FIB_PATH_NH_PROTO_BIER = 4


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

        :param node: VPP node.
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
        sw_if_index = InterfaceUtil.get_interface_index(node, interface)

        if not sw_if_index:
            return list()

        is_ipv6 = 1 if ip_version == 'ipv6' else 0

        cmd = 'ip_address_dump'
        args = dict(sw_if_index=sw_if_index,
                    is_ipv6=is_ipv6)
        err_msg = 'Failed to get L2FIB dump on host {host}'.format(
            host=node['host'])

        with PapiSocketExecutor(node) as papi_exec:
            details = papi_exec.add(cmd, **args).get_details(err_msg)

        # TODO: CSIT currently looks only whether the list is empty.
        # Add proper value processing if values become important.

        return details

    @staticmethod
    def vpp_get_ip_tables(node):
        """Get dump of all IP FIB tables on a VPP node.

        :param node: VPP node.
        :type node: dict
        """

        PapiSocketExecutor.run_cli_cmd(node, 'show ip fib')
        PapiSocketExecutor.run_cli_cmd(node, 'show ip fib summary')
        PapiSocketExecutor.run_cli_cmd(node, 'show ip6 fib')
        PapiSocketExecutor.run_cli_cmd(node, 'show ip6 fib summary')

    @staticmethod
    def vpp_get_ip_tables_prefix(node, address):
        """Get dump of all IP FIB tables on a VPP node.

        :param node: VPP node.
        :param address: IP address.
        :type node: dict
        :type address: str
        """
        addr = ip_address(unicode(address))

        PapiSocketExecutor.run_cli_cmd(
            node, 'show {ip_ver} fib {addr}/{addr_len}'.format(
                ip_ver='ip6' if addr.version == 6 else 'ip',
                addr=addr,
                addr_len=addr.max_prefixlen))

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
        sw_if_index = InterfaceUtil.get_interface_index(node, interface)

        cmd = 'sw_interface_get_table'
        args = dict(
            sw_if_index=sw_if_index,
            is_ipv6=True if ip_version == 'ipv6' else False
        )
        err_msg = 'Failed to get VRF id assigned to interface {ifc}'.format(
            ifc=interface)

        with PapiSocketExecutor(node) as papi_exec:
            reply = papi_exec.add(cmd, **args).get_reply(err_msg)

        return reply['vrf_id']

    @staticmethod
    def vpp_ip_source_check_setup(node, if_name):
        """Setup Reverse Path Forwarding source check on interface.

        :param node: VPP node.
        :param if_name: Interface name to setup RPF source check.
        :type node: dict
        :type if_name: str
        """
        cmd = 'ip_source_check_interface_add_del'
        args = dict(
            sw_if_index=InterfaceUtil.get_interface_index(node, if_name),
            is_add=1,
            loose=0
        )
        err_msg = 'Failed to enable source check on interface {ifc}'.format(
            ifc=if_name)
        with PapiSocketExecutor(node) as papi_exec:
            papi_exec.add(cmd, **args).get_reply(err_msg)

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
            dst=str(addr))
        err_msg = 'VPP ip probe {dev} {ip} failed on {h}'.format(
            dev=interface, ip=addr, h=node['host'])

        with PapiSocketExecutor(node) as papi_exec:
            papi_exec.add(cmd, **args).get_reply(err_msg)

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

        :param node: VPP node.
        :param namespace_name: Namespace name.
        :param interface_name: Interface name.
        :param ip_addr: IP address of namespace's interface.
        :param prefix: IP address prefix length.
        :type node: dict
        :type namespace_name: str
        :type interface_name: str
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

        :param node: VPP node.
        :param ip_ver: IP version, 'ipv4' or 'ipv6'.
        :type node: dict
        :type ip_ver: str
        """
        cmd = 'sysctl -w net.{0}.ip_forward=1'.format(ip_ver)
        exec_cmd_no_error(node, cmd, sudo=True)

    @staticmethod
    def get_linux_interface_name(node, pci_addr):
        """Get the interface name.

        :param node: VPP/TG node.
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
            raise RuntimeError('Could not get information about interfaces:\n'
                               '{err}'.format(err=stderr))

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

        :param node: VPP/TG node.
        :param interface: Interface in namespace.
        :type node: dict
        :type interface: str
        :raises RuntimeError: If the interface could not be set up.
        """
        cmd = "ip link set {0} up".format(interface)
        exec_cmd_no_error(node, cmd, timeout=30, sudo=True)

    @staticmethod
    def set_linux_interface_ip(node, interface, ip_addr, prefix,
                               namespace=None):
        """Set IP address to interface in linux.

        :param node: VPP/TG node.
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
            cmd = 'ip netns exec {ns} ip addr add {ip}/{p} dev {dev}'.format(
                ns=namespace, ip=ip_addr, p=prefix, dev=interface)
        else:
            cmd = 'ip addr add {ip}/{p} dev {dev}'.format(
                ip=ip_addr, p=prefix, dev=interface)

        exec_cmd_no_error(node, cmd, timeout=5, sudo=True)

    @staticmethod
    def add_linux_route(node, ip_addr, prefix, gateway, namespace=None):
        """Add linux route in namespace.

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

    @staticmethod
    def vpp_interface_set_ip_address(node, interface, address,
                                     prefix_length=None):
        """Set IP address to VPP interface.

        :param node: VPP node.
        :param interface: Interface name.
        :param address: IP address.
        :param prefix_length: Prefix length.
        :type node: dict
        :type interface: str
        :type address: str
        :type prefix_length: int
        """
        ip_addr = ip_address(unicode(address))

        cmd = 'sw_interface_add_del_address'
        args = dict(
            sw_if_index=InterfaceUtil.get_interface_index(node, interface),
            is_add=True,
            del_all=False,
            prefix=IPUtil.create_prefix_object(
                ip_addr,
                prefix_length if prefix_length else 128
                if ip_addr.version == 6 else 32)
        )
        err_msg = 'Failed to add IP address on interface {ifc}'.format(
            ifc=interface)
        with PapiSocketExecutor(node) as papi_exec:
            papi_exec.add(cmd, **args).get_reply(err_msg)

    @staticmethod
    def vpp_add_ip_neighbor(node, iface_key, ip_addr, mac_address):
        """Add IP neighbor on DUT node.

        :param node: VPP node.
        :param iface_key: Interface key.
        :param ip_addr: IP address of the interface.
        :param mac_address: MAC address of the interface.
        :type node: dict
        :type iface_key: str
        :type ip_addr: str
        :type mac_address: str
        """
        dst_ip = ip_address(unicode(ip_addr))

        neighbor = dict(
            sw_if_index=Topology.get_interface_sw_index(node, iface_key),
            flags=0,
            mac_address=str(mac_address),
            ip_address=str(dst_ip))
        cmd = 'ip_neighbor_add_del'
        args = dict(
            is_add=1,
            neighbor=neighbor)
        err_msg = 'Failed to add IP neighbor on interface {ifc}'.format(
            ifc=iface_key)
        with PapiSocketExecutor(node) as papi_exec:
            papi_exec.add(cmd, **args).get_reply(err_msg)

    @staticmethod
    def union_addr(ip_addr):
        """Creates union IP address.

        :param ip_addr: IPv4 or IPv6 address.
        :type ip_addr: IPv4Address or IPv6Address
        :returns: Union IP address.
        :rtype: dict
        """
        return dict(ip6=ip_addr.packed) if ip_addr.version == 6 \
            else dict(ip4=ip_addr.packed)

    @staticmethod
    def create_ip_address_object(ip_addr):
        """Create IP address object.

        :param ip_addr: IPv4 or IPv6 address
        :type ip_addr: IPv4Address or IPv6Address
        :returns: IP address object.
        :rtype: dict
        """
        return dict(
            af=getattr(
                AddressFamily, 'ADDRESS_IP6' if ip_addr.version == 6
                else 'ADDRESS_IP4').value,
            un=IPUtil.union_addr(ip_addr))

    @staticmethod
    def create_prefix_object(ip_addr, addr_len):
        """Create prefix object.

        :param ip_addr: IPv4 or IPv6 address.
        :para, addr_len: Length of IP address.
        :type ip_addr: IPv4Address or IPv6Address
        :type addr_len: int
        :returns: Prefix object.
        :rtype: dict
        """
        addr = IPUtil.create_ip_address_object(ip_addr)

        return dict(
            len=int(addr_len),
            address=addr
        )

    @staticmethod
    def compose_vpp_route_structure(node, network, prefix_len, **kwargs):
        """Create route object for ip_route_add_del api call.

        :param node: VPP node.
        :param network: Route destination network address.
        :param prefix_len: Route destination network prefix length.
        :param kwargs: Optional key-value arguments:

            gateway: Route gateway address. (str)
            interface: Route interface. (str)
            vrf: VRF table ID. (int)
            count: number of IP addresses to add starting from network IP (int)
            local: The route is local with same prefix (increment is 1).
                If None, then is not used. (bool)
            lookup_vrf: VRF table ID for lookup. (int)
            multipath: Enable multipath routing. (bool)
            weight: Weight value for unequal cost multipath routing. (int)

        :type node: dict
        :type network: str
        :type prefix_len: int
        :type kwargs: dict
        :returns: route parameter basic structure
        :rtype: dict
        """
        interface = kwargs.get('interface', '')
        gateway = kwargs.get('gateway', '')

        net_addr = ip_address(unicode(network))

        prefix = IPUtil.create_prefix_object(net_addr, prefix_len)

        paths = list()
        n_hop = dict(
            address=IPUtil.union_addr(ip_address(unicode(gateway))) if gateway
            else 0,
            via_label=MPLS_LABEL_INVALID,
            obj_id=Constants.BITWISE_NON_ZERO
        )
        path = dict(
            sw_if_index=InterfaceUtil.get_interface_index(node, interface)
            if interface else Constants.BITWISE_NON_ZERO,
            table_id=int(kwargs.get('lookup_vrf', 0)),
            rpf_id=Constants.BITWISE_NON_ZERO,
            weight=int(kwargs.get('weight', 1)),
            preference=1,
            type=getattr(
                FibPathType, 'FIB_PATH_TYPE_LOCAL'
                if kwargs.get('local', False)
                else 'FIB_PATH_TYPE_NORMAL').value,
            flags=getattr(FibPathFlags, 'FIB_PATH_FLAG_NONE').value,
            proto=getattr(
                FibPathNhProto, 'FIB_PATH_NH_PROTO_IP6'
                if net_addr.version == 6
                else 'FIB_PATH_NH_PROTO_IP4').value,
            nh=n_hop,
            n_labels=0,
            label_stack=list(0 for _ in range(16))
        )
        paths.append(path)

        route = dict(
            table_id=int(kwargs.get('vrf', 0)),
            prefix=prefix,
            n_paths=len(paths),
            paths=paths
        )
        return route

    @staticmethod
    def vpp_route_add(node, network, prefix_len, **kwargs):
        """Add route to the VPP node.

        :param node: VPP node.
        :param network: Route destination network address.
        :param prefix_len: Route destination network prefix length.
        :param kwargs: Optional key-value arguments:

            gateway: Route gateway address. (str)
            interface: Route interface. (str)
            vrf: VRF table ID. (int)
            count: number of IP addresses to add starting from network IP (int)
            local: The route is local with same prefix (increment is 1).
                If None, then is not used. (bool)
            lookup_vrf: VRF table ID for lookup. (int)
            multipath: Enable multipath routing. (bool)
            weight: Weight value for unequal cost multipath routing. (int)

        :type node: dict
        :type network: str
        :type prefix_len: int
        :type kwargs: dict
        """
        count = kwargs.get("count", 1)

        if count > 100:
            gateway = kwargs.get("gateway", '')
            interface = kwargs.get("interface", '')
            vrf = kwargs.get("vrf", None)
            multipath = kwargs.get("multipath", False)

            with VatTerminal(node, json_param=False) as vat:
                vat.vat_terminal_exec_cmd_from_template(
                    'vpp_route_add.vat',
                    network=network,
                    prefix_length=prefix_len,
                    via='via {}'.format(gateway) if gateway else '',
                    sw_if_index='sw_if_index {}'.format(
                        InterfaceUtil.get_interface_index(node, interface))
                    if interface else '',
                    vrf='vrf {}'.format(vrf) if vrf else '',
                    count='count {}'.format(count) if count else '',
                    multipath='multipath' if multipath else '')
            return

        net_addr = ip_address(unicode(network))
        cmd = 'ip_route_add_del'
        args = dict(
            is_add=1,
            is_multipath=int(kwargs.get('multipath', False)),
            route=None
        )

        err_msg = 'Failed to add route(s) on host {host}'.format(
            host=node['host'])
        with PapiSocketExecutor(node) as papi_exec:
            for i in xrange(kwargs.get('count', 1)):
                args['route'] = IPUtil.compose_vpp_route_structure(
                    node, net_addr + i, prefix_len, **kwargs)
                history = False if 1 < i < kwargs.get('count', 1) else True
                papi_exec.add(cmd, history=history, **args)
            papi_exec.get_replies(err_msg)

    @staticmethod
    def flush_ip_addresses(node, interface):
        """Flush all IP addresses from specified interface.

        :param node: VPP node.
        :param interface: Interface name.
        :type node: dict
        :type interface: str
        """
        cmd = 'sw_interface_add_del_address'
        args = dict(
            sw_if_index=InterfaceUtil.get_interface_index(node, interface),
            is_add=False,
            del_all=True
        )
        err_msg = 'Failed to flush IP address on interface {ifc}'.format(
            ifc=interface)
        with PapiSocketExecutor(node) as papi_exec:
            papi_exec.add(cmd, **args).get_reply(err_msg)

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
        cmd = 'ip_table_add_del'
        table = dict(
            table_id=int(table_id),
            is_ip6=int(ipv6))
        args = dict(
            table=table,
            is_add=1)
        err_msg = 'Failed to add FIB table on host {host}'.format(
            host=node['host'])
        with PapiSocketExecutor(node) as papi_exec:
            papi_exec.add(cmd, **args).get_reply(err_msg)
