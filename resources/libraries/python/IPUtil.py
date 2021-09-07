# Copyright (c) 2021 Cisco and/or its affiliates.
# Copyright (c) 2021 PANTHEON.tech s.r.o.
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
import os

from enum import IntEnum

from ipaddress import ip_address, ip_network

from resources.libraries.python.Constants import Constants
from resources.libraries.python.IncrementUtil import ObjIncrement
from resources.libraries.python.InterfaceUtil import InterfaceUtil
from resources.libraries.python.ip_types import (
    AddressUnion, Address, AddressWithPrefix
)
from resources.libraries.python.PapiExecutor import PapiSocketExecutor
from resources.libraries.python.ssh import exec_cmd_no_error, exec_cmd
from resources.libraries.python.topology import Topology
from resources.libraries.python.VatExecutor import VatExecutor
from resources.libraries.python.Namespaces import Namespaces


# from vpp/src/vnet/vnet/mpls/mpls_types.h
MPLS_IETF_MAX_LABEL = 0xfffff
MPLS_LABEL_INVALID = MPLS_IETF_MAX_LABEL + 1


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
    FIB_PATH_FLAG_RESOLVE_VIA_ATTACHED = 1
    FIB_PATH_FLAG_RESOLVE_VIA_HOST = 2


class FibPathNhProto(IntEnum):
    """FIB path next-hop protocol."""
    FIB_PATH_NH_PROTO_IP4 = 0
    FIB_PATH_NH_PROTO_IP6 = 1
    FIB_PATH_NH_PROTO_MPLS = 2
    FIB_PATH_NH_PROTO_ETHERNET = 3
    FIB_PATH_NH_PROTO_BIER = 4

    @classmethod
    def for_version(cls, version):
        """Return instance suitable for given IP version.

        If version is neither 4 nor 6, return FIB_PATH_NH_PROTO_ETHERNET.

        :param version: IP version, 4 or 6 or anything other for ethernet.
        :type version: int
        :returns: Appropriate enum instance.
        :rtype: cls
        """
        if version == 4:
            return cls.FIB_PATH_NH_PROTO_IP4
        if version == 6:
            return cls.FIB_PATH_NH_PROTO_IP6
        return cls.FIB_PATH_NH_PROTO_ETHERNET


class IpDscp(IntEnum):
    """DSCP code points."""
    IP_API_DSCP_CS0 = 0
    IP_API_DSCP_CS1 = 8
    IP_API_DSCP_AF11 = 10
    IP_API_DSCP_AF12 = 12
    IP_API_DSCP_AF13 = 14
    IP_API_DSCP_CS2 = 16
    IP_API_DSCP_AF21 = 18
    IP_API_DSCP_AF22 = 20
    IP_API_DSCP_AF23 = 22
    IP_API_DSCP_CS3 = 24
    IP_API_DSCP_AF31 = 26
    IP_API_DSCP_AF32 = 28
    IP_API_DSCP_AF33 = 30
    IP_API_DSCP_CS4 = 32
    IP_API_DSCP_AF41 = 34
    IP_API_DSCP_AF42 = 36
    IP_API_DSCP_AF43 = 38
    IP_API_DSCP_CS5 = 40
    IP_API_DSCP_EF = 46
    IP_API_DSCP_CS6 = 48
    IP_API_DSCP_CS7 = 50


class NetworkIncrement(ObjIncrement):
    """
    An iterator object which accepts an IPv4Network or IPv6Network and
    returns a new network, its address part incremented by the increment
    number of network sizes, each time it is iterated or when inc_fmt is called.
    The increment may be positive, negative or 0
    (in which case the network is always the same).

    Both initial and subsequent IP address can have host bits set,
    check the initial value before creating instance if needed.
    String formatting is configurable via constructor argument.

    TODO: Unify with ip_types.py (or get rid of VAT and its dash formatting).
    """
    def __init__(self, initial_value, increment=1, format=u"dash"):
        """
        :param initial_value: The initial network. Can have host bits set.
        :param increment: The current network will be incremented by this
            amount of network sizes in each iteration/var_str call.
        :param format: Type of formatting to use, "dash" or "slash" or "addr".
        :type initial_value: Union[ipaddress.IPv4Network, ipaddress.IPv6Network]
        :type increment: int
        :type format: str
        """
        super().__init__(initial_value, increment)
        self._prefix_len = self._value.prefixlen
        host_len = self._value.max_prefixlen - self._prefix_len
        self._net_increment = self._increment * (1 << host_len)
        self._format = str(format).lower()

    def _incr(self):
        """
        Increment the network, e.g.:
        '30.0.0.0/24' incremented by 1 (the next network) is '30.0.1.0/24'.
        '30.0.0.0/24' incremented by 2 is '30.0.2.0/24'.
        """
        self._value = ip_network(
            f"{self._value.network_address + self._net_increment}"
            f"/{self._prefix_len}", strict=False
        )

    def _str_fmt(self):
        """
        The string representation of the network depends on format.

        Dash format is '<ip_address_start> - <ip_address_stop>',
        useful for 'ipsec policy add spd' CLI.

        Slash format is '<ip_address_start>/<prefix_length>',
        useful for other CLI.

        Addr format is '<ip_address_start>', useful for PAPI.

        :returns: Current value converted to string according to format.
        :rtype: str
        :raises RuntimeError: If the format is not supported.
        """
        if self._format == u"dash":
            return f"{self._value.network_address} - " \
                   f"{self._value.broadcast_address}"
        elif self._format == u"slash":
            return f"{self._value.network_address}/{self._prefix_len}"
        elif self._format == u"addr":
            return f"{self._value.network_address}"
        else:
            raise RuntimeError(f"Unsupported format {self._format}")


class IPUtil:
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
        return int(ip_address(ip_str))

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

        cmd = u"ip_address_dump"
        args = dict(
            sw_if_index=sw_if_index,
            is_ipv6=bool(ip_version == u"ipv6")
        )
        err_msg = f"Failed to get L2FIB dump on host {node[u'host']}"

        with PapiSocketExecutor(node) as papi_exec:
            details = papi_exec.add(cmd, **args).get_details(err_msg)

        return details

    @staticmethod
    def vpp_get_ip_tables(node):
        """Get dump of all IP FIB tables on a VPP node.

        :param node: VPP node.
        :type node: dict
        """
        PapiSocketExecutor.run_cli_cmd(node, u"show ip fib")
        PapiSocketExecutor.run_cli_cmd(node, u"show ip fib summary")
        PapiSocketExecutor.run_cli_cmd(node, u"show ip6 fib")
        PapiSocketExecutor.run_cli_cmd(node, u"show ip6 fib summary")

    @staticmethod
    def vpp_get_ip_table_summary(node):
        """Get IPv4 FIB table summary on a VPP node.

        :param node: VPP node.
        :type node: dict
        """
        PapiSocketExecutor.run_cli_cmd(node, u"show ip fib summary")

    @staticmethod
    def vpp_get_ip_table(node):
        """Get IPv4 FIB table on a VPP node.

        :param node: VPP node.
        :type node: dict
        """
        PapiSocketExecutor.run_cli_cmd(node, u"show ip fib")

    @staticmethod
    def vpp_get_ip_tables_prefix(node, address):
        """Get dump of all IP FIB tables on a VPP node.

        :param node: VPP node.
        :param address: IP address.
        :type node: dict
        :type address: str
        """
        addr = ip_address(address)
        ip_ver = u"ip6" if addr.version == 6 else u"ip"

        PapiSocketExecutor.run_cli_cmd(
            node, f"show {ip_ver} fib {addr}/{addr.max_prefixlen}"
        )

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

        cmd = u"sw_interface_get_table"
        args = dict(
            sw_if_index=sw_if_index,
            is_ipv6=bool(ip_version == u"ipv6")
        )
        err_msg = f"Failed to get VRF id assigned to interface {interface}"

        with PapiSocketExecutor(node) as papi_exec:
            reply = papi_exec.add(cmd, **args).get_reply(err_msg)

        return reply[u"vrf_id"]

    @staticmethod
    def vpp_ip_source_check_setup(node, if_name):
        """Setup Reverse Path Forwarding source check on interface.

        :param node: VPP node.
        :param if_name: Interface name to setup RPF source check.
        :type node: dict
        :type if_name: str
        """
        cmd = u"ip_source_check_interface_add_del"
        args = dict(
            sw_if_index=InterfaceUtil.get_interface_index(node, if_name),
            is_add=1,
            loose=0
        )
        err_msg = f"Failed to enable source check on interface {if_name}"
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
        cmd = u"ip_probe_neighbor"
        args = dict(
            sw_if_index=InterfaceUtil.get_interface_index(node, interface),
            dst=str(addr)
        )
        err_msg = f"VPP ip probe {interface} {addr} failed on {node[u'host']}"

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
        addr1 = ip_address(ip1)
        addr2 = ip_address(ip2)

        if addr1 != addr2:
            raise AssertionError(f"IP addresses are not equal: {ip1} != {ip2}")

    @staticmethod
    def setup_network_namespace(node, namespace_name, interface_name,
                                ip_addr_list, prefix_length):
        """Setup namespace on given node and attach interface and IP to
        this namespace. Applicable also on TG node.

        :param node: VPP node.
        :param namespace_name: Namespace name.
        :param interface_name: Interface name.
        :param ip_addr_list: List of IP addresses of namespace's interface.
        :param prefix_length: IP address prefix length.
        :type node: dict
        :type namespace_name: str
        :type interface_name: str
        :type ip_addr_list: list
        :type prefix_length: int
        """
        Namespaces.create_namespace(node, namespace_name)

        cmd = f"ip netns exec {namespace_name} ip link set {interface_name} up"
        exec_cmd_no_error(node, cmd, sudo=True)

        for ip_addr in ip_addr_list:
            cmd = f"ip netns exec {namespace_name} ip addr add " \
                f"{ip_addr}/{prefix_length} dev {interface_name}"
            exec_cmd_no_error(node, cmd, sudo=True)

    @staticmethod
    def linux_enable_forwarding(node, ip_ver=u"ipv4"):
        """Enable forwarding on a Linux node, e.g. VM.

        :param node: VPP node.
        :param ip_ver: IP version, 'ipv4' or 'ipv6'.
        :type node: dict
        :type ip_ver: str
        """
        cmd = f"sysctl -w net.{ip_ver}.ip_forward=1"
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
        regex_intf_info = \
            r"pci@([0-9a-f]{4}:[0-9a-f]{2}:[0-9a-f]{2}.[0-9a-f])\s" \
            r"*([a-zA-Z0-9]*)\s*network"

        cmd = u"lshw -class network -businfo"
        ret_code, stdout, stderr = exec_cmd(node, cmd, timeout=30, sudo=True)
        if ret_code != 0:
            raise RuntimeError(
                f"Could not get information about interfaces:\n{stderr}"
            )

        for line in stdout.splitlines()[2:]:
            try:
                if re.search(regex_intf_info, line).group(1) == pci_addr:
                    return re.search(regex_intf_info, line).group(2)
            except AttributeError:
                continue
        return None

    @staticmethod
    def set_linux_interface_up(
            node, interface, namespace=None):
        """Set the specified interface up.
        :param node: VPP/TG node.
        :param interface: Interface in namespace.
        :param namespace: Execute command in namespace. Optional
        :type node: dict
        :type interface: str
        :type namespace: str
        :raises RuntimeError: If the interface could not be set up.
        """
        if namespace is not None:
            cmd = f"ip netns exec {namespace} ip link set dev {interface} up"
        else:
            cmd = f"ip link set dev {interface} up"
        exec_cmd_no_error(node, cmd, timeout=30, sudo=True)


    @staticmethod
    def set_linux_interface_ip(
            node, interface, ip_addr, prefix, namespace=None):
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
            cmd = f"ip netns exec {namespace} ip addr add {ip_addr}/{prefix}" \
                f" dev {interface}"
        else:
            cmd = f"ip addr add {ip_addr}/{prefix} dev {interface}"

        exec_cmd_no_error(node, cmd, timeout=5, sudo=True)

    @staticmethod
    def delete_linux_interface_ip(
            node, interface, ip_addr, prefix_length, namespace=None):
        """Delete IP address from interface in linux.

        :param node: VPP/TG node.
        :param interface: Interface in namespace.
        :param ip_addr: IP to be deleted from interface.
        :param prefix_length: IP prefix length.
        :param namespace: Execute command in namespace. Optional
        :type node: dict
        :type interface: str
        :type ip_addr: str
        :type prefix_length: int
        :type namespace: str
        :raises RuntimeError: IP could not be deleted.
        """
        if namespace is not None:
            cmd = f"ip netns exec {namespace} ip addr del " \
                f"{ip_addr}/{prefix_length} dev {interface}"
        else:
            cmd = f"ip addr del {ip_addr}/{prefix_length} dev {interface}"

        exec_cmd_no_error(node, cmd, timeout=5, sudo=True)

    @staticmethod
    def linux_interface_has_ip(
            node, interface, ip_addr, prefix_length, namespace=None):
        """Return True if interface in linux has IP address.

        :param node: VPP/TG node.
        :param interface: Interface in namespace.
        :param ip_addr: IP to be queried on interface.
        :param prefix_length: IP prefix length.
        :param namespace: Execute command in namespace. Optional
        :type node: dict
        :type interface: str
        :type ip_addr: str
        :type prefix_length: int
        :type namespace: str
        :rtype boolean
        :raises RuntimeError: Request fails.
        """
        ip_addr_with_prefix = f"{ip_addr}/{prefix_length}"
        if namespace is not None:
            cmd = f"ip netns exec {namespace} ip addr show dev {interface}"
        else:
            cmd = f"ip addr show dev {interface}"

        cmd += u" | grep 'inet ' | awk -e '{print $2}'"
        cmd += f" | grep '{ip_addr_with_prefix}'"
        _, stdout, _ = exec_cmd(node, cmd, timeout=5, sudo=True)

        has_ip = stdout.rstrip()
        return bool(has_ip == ip_addr_with_prefix)

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
            cmd = f"ip netns exec {namespace} ip route add {ip_addr}/{prefix}" \
                f" via {gateway}"
        else:
            cmd = f"ip route add {ip_addr}/{prefix} via {gateway}"

        exec_cmd_no_error(node, cmd, sudo=True)

    @staticmethod
    def vpp_interface_set_ip_address(
            node, interface, address, prefix_length=None):
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
        cmd = u"sw_interface_add_del_address"
        address = Address(address)
        args = dict(
            sw_if_index=InterfaceUtil.get_interface_index(node, interface),
            is_add=True,
            del_all=False,
            prefix=AddressWithPrefix(
                address, prefix_length if prefix_length else 128
                if address.version == 6 else 32
            )
        )
        err_msg = f"Failed to add IP address on interface {interface}"

        with PapiSocketExecutor(node) as papi_exec:
            papi_exec.add(cmd, **args).get_reply(err_msg)

    @staticmethod
    def vpp_interface_set_ip_addresses(node, interface, ip_addr_list,
                                       prefix_length=None):
        """Set IP addresses to VPP interface.

        :param node: VPP node.
        :param interface: Interface name.
        :param ip_addr_list: IP addresses.
        :param prefix_length: Prefix length.
        :type node: dict
        :type interface: str
        :type ip_addr_list: list
        :type prefix_length: int
        """
        for ip_addr in ip_addr_list:
            IPUtil.vpp_interface_set_ip_address(node, interface, ip_addr,
                                                prefix_length)

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
        dst_ip = ip_address(ip_addr)

        neighbor = dict(
            sw_if_index=Topology.get_interface_sw_index(node, iface_key),
            flags=0,
            mac_address=str(mac_address),
            ip_address=str(dst_ip)
        )
        cmd = u"ip_neighbor_add_del"
        args = dict(
            is_add=True,
            neighbor=neighbor
        )
        err_msg = f"Failed to add IP neighbor on interface {iface_key}"

        with PapiSocketExecutor(node) as papi_exec:
            papi_exec.add(cmd, **args).get_reply(err_msg)

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
            weight: Weight value for unequal cost multipath routing. (int)
            (Multipath value enters at higher level.)

        :type node: dict
        :type network: str
        :type prefix_len: int
        :type kwargs: dict
        :returns: route parameter basic structure
        :rtype: dict
        """
        interface = kwargs.get(u"interface", u"")
        gateway = kwargs.get(u"gateway", u"")
        network_and_plen = AddressWithPrefix(network, prefix_len)

        paths = list()
        n_hop = dict(
            address=AddressUnion(gateway),
            via_label=MPLS_LABEL_INVALID,
            obj_id=Constants.BITWISE_NON_ZERO
        )
        path = dict(
            sw_if_index=InterfaceUtil.get_interface_index(node, interface)
            if interface else Constants.BITWISE_NON_ZERO,
            table_id=int(kwargs.get(u"lookup_vrf", 0)),
            rpf_id=Constants.BITWISE_NON_ZERO,
            weight=int(kwargs.get(u"weight", 1)),
            preference=1,
            type=FibPathType(kwargs.get(u"local", False)),
            flags=FibPathFlags.FIB_PATH_FLAG_NONE,
            proto=FibPathNhProto.for_version(network_and_plen.version),
            nh=n_hop,
            n_labels=0,
            label_stack=[0] * 16,
        )
        paths.append(path)

        route = dict(
            table_id=int(kwargs.get(u"vrf", 0)),
            prefix=network_and_plen,
            n_paths=len(paths),
            paths=paths
        )
        return route

    @staticmethod
    def vpp_route_add(node, network, prefix_len, strict=True, **kwargs):
        """Add route to the VPP node. Prefer multipath behavior.

        :param node: VPP node.
        :param network: Route destination network address.
        :param prefix_len: Route destination network prefix length.
        :param strict: If true, fail if address has host bits set.
        :param kwargs: Optional key-value arguments:

            gateway: Route gateway address. (str)
            interface: Route interface. (str)
            vrf: VRF table ID. (int)
            count: number of IP addresses to add starting from network IP (int)
            local: The route is local with same prefix (increment is 1 network)
                If None, then is not used. (bool)
            lookup_vrf: VRF table ID for lookup. (int)
            multipath: Enable multipath routing. (bool) Default: True.
            weight: Weight value for unequal cost multipath routing. (int)

        :type node: dict
        :type network: str
        :type prefix_len: int
        :type strict: bool
        :type kwargs: dict
        :raises RuntimeError: If the argument combination is not supported.
        """
        count = kwargs.get(u"count", 1)

        if count > 100:
            if not kwargs.get(u"multipath", True):
                raise RuntimeError(u"VAT exec supports only multipath behavior")
            gateway = kwargs.get(u"gateway", u"")
            interface = kwargs.get(u"interface", u"")
            local = kwargs.get(u"local", u"")
            if interface:
                interface = InterfaceUtil.vpp_get_interface_name(
                    node, InterfaceUtil.get_interface_index(
                        node, interface
                    )
                )
            vrf = kwargs.get(u"vrf", None)
            trailers = list()
            if vrf:
                trailers.append(f"table {vrf}")
            if gateway:
                trailers.append(f"via {gateway}")
                if interface:
                    trailers.append(interface)
            elif interface:
                trailers.append(f"via {interface}")
            if local:
                if gateway or interface:
                    raise RuntimeError(u"Unsupported combination with local.")
                trailers.append(u"local")
            trailer = u" ".join(trailers)
            command_parts = [u"exec ip route add", u"network goes here"]
            if trailer:
                command_parts.append(trailer)
            netiter = NetworkIncrement(
                ip_network(f"{network}/{prefix_len}", strict=strict),
                format=u"slash"
            )
            tmp_filename = u"/tmp/routes.config"
            with open(tmp_filename, u"w") as tmp_file:
                for _ in range(count):
                    command_parts[1] = netiter.inc_fmt()
                    print(u" ".join(command_parts), file=tmp_file)
            VatExecutor().execute_script(
                tmp_filename, node, timeout=1800, json_out=False,
                copy_on_execute=True, history=False
            )
            os.remove(tmp_filename)
            return

        cmd = u"ip_route_add_del"
        args = dict(
            is_add=True,
            is_multipath=kwargs.get(u"multipath", True),
            route=None
        )
        err_msg = f"Failed to add route(s) on host {node[u'host']}"

        netiter = NetworkIncrement(
            ip_network(f"{network}/{prefix_len}", strict=strict),
            format=u"addr"
        )
        with PapiSocketExecutor(node) as papi_exec:
            for i in range(count):
                args[u"route"] = IPUtil.compose_vpp_route_structure(
                    node, netiter.inc_fmt(), prefix_len, **kwargs
                )
                history = bool(not 0 < i < count - 1)
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
        cmd = u"sw_interface_add_del_address"
        args = dict(
            sw_if_index=InterfaceUtil.get_interface_index(node, interface),
            is_add=False,
            del_all=True
        )
        err_msg = f"Failed to flush IP address on interface {interface}"

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
        cmd = u"ip_table_add_del"
        table = dict(
            table_id=int(table_id),
            is_ip6=ipv6
        )
        args = dict(
            table=table,
            is_add=True
        )
        err_msg = f"Failed to add FIB table on host {node[u'host']}"

        with PapiSocketExecutor(node) as papi_exec:
            papi_exec.add(cmd, **args).get_reply(err_msg)
