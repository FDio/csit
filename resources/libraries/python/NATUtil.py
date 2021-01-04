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

"""NAT utilities library."""

from math import log2, modf
from pprint import pformat
from enum import IntEnum

from ipaddress import IPv4Address
from robot.api import logger

from resources.libraries.python.Constants import Constants
from resources.libraries.python.InterfaceUtil import InterfaceUtil
from resources.libraries.python.topology import Topology
from resources.libraries.python.PapiExecutor import PapiSocketExecutor


class NatConfigFlags(IntEnum):
    """Common NAT plugin APIs"""
    NAT_IS_NONE = 0x00
    NAT_IS_TWICE_NAT = 0x01
    NAT_IS_SELF_TWICE_NAT = 0x02
    NAT_IS_OUT2IN_ONLY = 0x04
    NAT_IS_ADDR_ONLY = 0x08
    NAT_IS_OUTSIDE = 0x10
    NAT_IS_INSIDE = 0x20
    NAT_IS_STATIC = 0x40
    NAT_IS_EXT_HOST_VALID = 0x80


class NatAddrPortAllocAlg(IntEnum):
    """NAT Address and port assignment algorithms."""
    NAT_ALLOC_ALG_DEFAULT = 0
    NAT_ALLOC_ALG_MAP_E = 1
    NAT_ALLOC_ALG_PORT_RANGE = 2


class NATUtil:
    """This class defines the methods to set NAT."""

    def __init__(self):
        pass

    @staticmethod
    def set_nat44_interface(node, interface, flag):
        """Set inside and outside interfaces for NAT44.

        :param node: DUT node.
        :param interface: NAT44 interface.
        :param flag: Interface NAT configuration flag name.
        :type node: dict
        :type interface: str
        :type flag: str
        """
        cmd = u"nat44_interface_add_del_feature"

        err_msg = f"Failed to set {flag} interface {interface} for NAT44 " \
            f"on host {node[u'host']}"
        args_in = dict(
            sw_if_index=InterfaceUtil.get_sw_if_index(node, interface),
            is_add=1,
            flags=getattr(NatConfigFlags, flag).value
        )

        with PapiSocketExecutor(node) as papi_exec:
            papi_exec.add(cmd, **args_in).get_reply(err_msg)

    @staticmethod
    def set_nat44_interfaces(node, int_in, int_out):
        """Set inside and outside interfaces for NAT44.

        :param node: DUT node.
        :param int_in: Inside interface.
        :param int_out: Outside interface.
        :type node: dict
        :type int_in: str
        :type int_out: str
        """
        NATUtil.set_nat44_interface(node, int_in, u"NAT_IS_INSIDE")
        NATUtil.set_nat44_interface(node, int_out, u"NAT_IS_OUTSIDE")

    @staticmethod
    def set_nat44_address_range(
            node, start_ip, end_ip, vrf_id=Constants.BITWISE_NON_ZERO,
            flag=u"NAT_IS_NONE"):
        """Set NAT44 address range.

        :param node: DUT node.
        :param start_ip: IP range start.
        :param end_ip: IP range end.
        :param vrf_id: VRF index (Optional).
        :param flag: NAT flag name.
        :type node: dict
        :type start_ip: str
        :type end_ip: str
        :type vrf_id: int
        :type flag: str
        """
        cmd = u"nat44_add_del_address_range"
        err_msg = f"Failed to set NAT44 address range on host {node[u'host']}"
        args_in = dict(
            is_add=True,
            first_ip_address=IPv4Address(str(start_ip)).packed,
            last_ip_address=IPv4Address(str(end_ip)).packed,
            vrf_id=vrf_id,
            flags=getattr(NatConfigFlags, flag).value
        )

        with PapiSocketExecutor(node) as papi_exec:
            papi_exec.add(cmd, **args_in).get_reply(err_msg)

    @staticmethod
    def show_nat_config(node):
        """Show the NAT configuration.

        :param node: DUT node.
        :type node: dict
        """
        cmd = u"nat_show_config"
        err_msg = f"Failed to get NAT configuration on host {node[u'host']}"

        with PapiSocketExecutor(node) as papi_exec:
            reply = papi_exec.add(cmd).get_reply(err_msg)

        logger.debug(f"NAT Configuration:\n{pformat(reply)}")

    @staticmethod
    def show_nat44_summary(node):
        """Show NAT44 summary on the specified topology node.

        :param node: Topology node.
        :type node: dict
        :returns: NAT44 summary data.
        :rtype: str
        """
        return PapiSocketExecutor.run_cli_cmd(node, u"show nat44 summary")

    @staticmethod
    def show_nat_base_data(node):
        """Show the NAT base data.

        Used data sources:

            nat_worker_dump
            nat44_interface_addr_dump
            nat44_address_dump
            nat44_static_mapping_dump
            nat44_interface_dump

        :param node: DUT node.
        :type node: dict
        """
        cmds = [
            u"nat_worker_dump",
            u"nat44_interface_addr_dump",
            u"nat44_address_dump",
            u"nat44_static_mapping_dump",
            u"nat44_interface_dump",
        ]
        PapiSocketExecutor.dump_and_log(node, cmds)

    @staticmethod
    def show_nat_user_data(node):
        """Show the NAT user data.

        Used data sources:

            nat44_user_dump
            nat44_user_session_dump

        :param node: DUT node.
        :type node: dict
        """
        cmds = [
            u"nat44_user_dump",
            u"nat44_user_session_dump",
        ]
        PapiSocketExecutor.dump_and_log(node, cmds)

    @staticmethod
    def compute_max_translations_per_thread(sessions, threads):
        """Compute value of max_translations_per_thread NAT44 parameter based on
        total number of worker threads.

        :param sessions: Required number of NAT44 sessions.
        :param threads: Number of worker threads.
        :type sessions: int
        :type threads: int
        :returns: Value of max_translations_per_thread NAT44 parameter.
        :rtype: int
        """
        rest, mult = modf(log2(sessions/(10*threads)))
        return 2 ** (int(mult) + (1 if rest else 0)) * 10

    @staticmethod
    def get_nat44_sessions_number(node, proto):
        """Get number of established NAT44 sessions from actual NAT44 mapping
        data.

        :param node: DUT node.
        :param proto: Required protocol - TCP/UDP/ICMP.
        :type node: dict
        :type proto: str
        :returns: Number of established NAT44 sessions.
        :rtype: int
        :raises ValueError: If not supported protocol.
        """
        nat44_data = dict()
        if proto in [u"UDP", u"TCP", u"ICMP"]:
            for line in NATUtil.show_nat44_summary(node).splitlines():
                sum_k, sum_v = line.split(u":") if u":" in line \
                    else (line, None)
                nat44_data[sum_k] = sum_v.strip() if isinstance(sum_v, str) \
                    else sum_v
        else:
            raise ValueError(f"Unsupported protocol: {proto}!")
        return nat44_data.get(f"total {proto.lower()} sessions", 0)

    # DET44 PAPI calls
    # DET44 means deterministic mode of NAT44
    @staticmethod
    def enable_det44_plugin(node, inside_vrf=0, outside_vrf=0):
        """Enable DET44 plugin.

        :param node: DUT node.
        :param inside_vrf: Inside VRF ID.
        :param outside_vrf: Outside VRF ID.
        :type node: dict
        :type inside_vrf: str or int
        :type outside_vrf: str or int
        """
        cmd = u"det44_plugin_enable_disable"
        err_msg = f"Failed to enable DET44 plugin on the host {node[u'host']}!"
        args_in = dict(
            enable=True,
            inside_vrf=int(inside_vrf),
            outside_vrf=int(outside_vrf)
        )

        with PapiSocketExecutor(node) as papi_exec:
            papi_exec.add(cmd, **args_in).get_reply(err_msg)

    @staticmethod
    def set_det44_interface(node, if_key, is_inside):
        """Enable DET44 feature on the interface.

        :param node: DUT node.
        :param if_key: Interface key from topology file of interface
            to enable DET44 feature on.
        :param is_inside: True if interface is inside, False if outside.
        :type node: dict
        :type if_key: str
        :type is_inside: bool
        """
        cmd = u"det44_interface_add_del_feature"
        err_msg = f"Failed to enable DET44 feature on the interface {if_key} " \
            f"on the host {node[u'host']}!"
        args_in = dict(
            is_add=True,
            is_inside=is_inside,
            sw_if_index=Topology.get_interface_sw_index(node, if_key)
        )

        with PapiSocketExecutor(node) as papi_exec:
            papi_exec.add(cmd, **args_in).get_reply(err_msg)

    @staticmethod
    def set_det44_mapping(node, ip_in, subnet_in, ip_out, subnet_out):
        """Set DET44 mapping.

        :param node: DUT node.
        :param ip_in: Inside IP.
        :param subnet_in: Inside IP subnet.
        :param ip_out: Outside IP.
        :param subnet_out: Outside IP subnet.
        :type node: dict
        :type ip_in: str
        :type subnet_in: str or int
        :type ip_out: str
        :type subnet_out: str or int
        """
        cmd = u"det44_add_del_map"
        err_msg = f"Failed to set DET44 mapping on the host {node[u'host']}!"
        args_in = dict(
            is_add=True,
            in_addr=IPv4Address(str(ip_in)).packed,
            in_plen=int(subnet_in),
            out_addr=IPv4Address(str(ip_out)).packed,
            out_plen=int(subnet_out)
        )

        with PapiSocketExecutor(node) as papi_exec:
            papi_exec.add(cmd, **args_in).get_reply(err_msg)

    @staticmethod
    def get_det44_mapping(node):
        """Get DET44 mapping data.

        :param node: DUT node.
        :type node: dict
        :returns: Dictionary of DET44 mapping data.
        :rtype: dict
        """
        cmd = u"det44_map_dump"
        err_msg = f"Failed to get DET44 mapping data on the host " \
            f"{node[u'host']}!"
        args_in = dict()
        with PapiSocketExecutor(node) as papi_exec:
            details = papi_exec.add(cmd, **args_in).get_reply(err_msg)

        return details

    @staticmethod
    def get_det44_sessions_number(node):
        """Get number of established DET44 sessions from actual DET44 mapping
        data.

        :param node: DUT node.
        :type node: dict
        :returns: Number of established DET44 sessions.
        :rtype: int
        """
        det44_data = NATUtil.get_det44_mapping(node)

        return det44_data.get(u"ses_num", 0)

    @staticmethod
    def show_det44(node):
        """Show DET44 data.

        Used data sources:

            det44_interface_dump
            det44_map_dump
            det44_session_dump

        :param node: DUT node.
        :type node: dict
        """
        cmds = [
            u"det44_interface_dump",
            u"det44_map_dump",
            u"det44_session_dump",
        ]
        PapiSocketExecutor.dump_and_log(node, cmds)

    @staticmethod
    def show_det44_timeouts(node):
        """Show timeout values for DET44 sessions.

        :param node: DUT node.
        :type node: dict
        """
        PapiSocketExecutor.dump_and_log(node, [u"det44_get_timeouts"])
