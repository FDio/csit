# Copyright (c) 2020 Cisco and/or its affiliates.
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
from resources.libraries.python.IPAddress import IPAddress
from resources.libraries.python.PapiExecutor import PapiSocketExecutor
from resources.libraries.python.ssh import exec_cmd_no_error, exec_cmd
from resources.libraries.python.topology import Topology
from resources.libraries.python.VatExecutor import VatTerminal
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
    # TODO: Name too long for pylint, fix in VPP.
    FIB_PATH_FLAG_RESOLVE_VIA_ATTACHED = 1
    FIB_PATH_FLAG_RESOLVE_VIA_HOST = 2


class FibPathNhProto(IntEnum):
    """FIB path next-hop protocol."""
    FIB_PATH_NH_PROTO_IP4 = 0
    FIB_PATH_NH_PROTO_IP6 = 1
    FIB_PATH_NH_PROTO_MPLS = 2
    FIB_PATH_NH_PROTO_ETHERNET = 3
    FIB_PATH_NH_PROTO_BIER = 4


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

        # TODO: CSIT currently looks only whether the list is empty.
        # Add proper value processing if values become important.

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
    def set_linux_interface_up(node, interface):
        """Set the specified interface up.

        :param node: VPP/TG node.
        :param interface: Interface in namespace.
        :type node: dict
        :type interface: str
        :raises RuntimeError: If the interface could not be set up.
        """
        cmd = f"ip link set {interface} up"
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
        # TODO: Refactor command execution in namespaces into central
        # methods (e.g. Namespace.exec_cmd_in_namespace)
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
        ip_addr = ip_address(address)

        cmd = u"sw_interface_add_del_address"
        args = dict(
            sw_if_index=InterfaceUtil.get_interface_index(node, interface),
            is_add=True,
            del_all=False,
            prefix=IPUtil.create_prefix_object(
                ip_addr,
                prefix_length if prefix_length else 128
                if ip_addr.version == 6 else 32
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
    def create_prefix_object(ip_addr, addr_len):
        """Create prefix object.

        :param ip_addr: IPv4 or IPv6 address.
        :para, addr_len: Length of IP address.
        :type ip_addr: IPv4Address or IPv6Address
        :type addr_len: int
        :returns: Prefix object.
        :rtype: dict
        """
        addr = IPAddress.create_ip_address_object(ip_addr)

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
        interface = kwargs.get(u"interface", u"")
        gateway = kwargs.get(u"gateway", u"")

        net_addr = ip_address(network)

        prefix = IPUtil.create_prefix_object(net_addr, prefix_len)

        paths = list()
        n_hop = dict(
            address=IPAddress.union_addr(ip_address(gateway)) if gateway else 0,
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
            type=getattr(
                FibPathType, u"FIB_PATH_TYPE_LOCAL"
                if kwargs.get(u"local", False)
                else u"FIB_PATH_TYPE_NORMAL"
            ).value,
            flags=getattr(FibPathFlags, u"FIB_PATH_FLAG_NONE").value,
            proto=getattr(
                FibPathNhProto, u"FIB_PATH_NH_PROTO_IP6"
                if net_addr.version == 6
                else u"FIB_PATH_NH_PROTO_IP4"
            ).value,
            nh=n_hop,
            n_labels=0,
            label_stack=list(0 for _ in range(16))
        )
        paths.append(path)

        route = dict(
            table_id=int(kwargs.get(u"vrf", 0)),
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
        net_addr = ip_address(network)
        cmd = u"ip_route_add_del"
        args = dict(
            is_add=True,
            is_multipath=kwargs.get(u"multipath", False),
            route=None
        )
        err_msg = f"Failed to add route(s) on host {node[u'host']}"

        with PapiSocketExecutor(node, do_async=True) as papi_exec:
            for i in range(count):
                args[u"route"] = IPUtil.compose_vpp_route_structure(
                    node, net_addr + i, prefix_len, **kwargs
                )
                history = bool(not 1 < i < kwargs.get(u"count", 1))
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
