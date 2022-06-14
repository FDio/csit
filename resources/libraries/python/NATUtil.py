# Copyright (c) 2022 Cisco and/or its affiliates.
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
    """NAT plugin configuration flags"""
    NAT_IS_NONE = 0x00
    NAT_IS_TWICE_NAT = 0x01
    NAT_IS_SELF_TWICE_NAT = 0x02
    NAT_IS_OUT2IN_ONLY = 0x04
    NAT_IS_ADDR_ONLY = 0x08
    NAT_IS_OUTSIDE = 0x10
    NAT_IS_INSIDE = 0x20
    NAT_IS_STATIC = 0x40
    NAT_IS_EXT_HOST_VALID = 0x80


class Nat44ConfigFlags(IntEnum):
    """NAT44 configuration flags"""
    NAT44_IS_ENDPOINT_INDEPENDENT = 0x00
    NAT44_IS_ENDPOINT_DEPENDENT = 0x01
    NAT44_IS_STATIC_MAPPING_ONLY = 0x02
    NAT44_IS_CONNECTION_TRACKING = 0x04
    NAT44_IS_OUT2IN_DPO = 0x08


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
    def enable_nat44_ed_plugin(
            node, inside_vrf=0, outside_vrf=0, sessions=0, session_memory=0,
            mode=u""):
        """Enable NAT44 plugin.

        :param node: DUT node.
        :param inside_vrf: Inside VRF ID.
        :param outside_vrf: Outside VRF ID.
        :param sessions: Maximum number of sessions.
        :param session_memory: Session memory size - overwrite auto calculated
            hash allocation parameter if non-zero.
        :param mode: NAT44 mode. Valid values:
            - endpoint-independent
            - endpoint-dependent
            - static-mapping-only
            - connection-tracking
            - out2in-dpo
        :type node: dict
        :type inside_vrf: str or int
        :type outside_vrf: str or int
        :type sessions: str or int
        :type session_memory: str or int
        :type mode: str
        """
        cmd = u"nat44_ed_plugin_enable_disable"
        err_msg = f"Failed to enable NAT44 plugin on the host {node[u'host']}!"
        args_in = dict(
            enable=True,
            inside_vrf=int(inside_vrf),
            outside_vrf=int(outside_vrf),
            sessions=int(sessions),
            session_memory=int(session_memory),
            flags=getattr(
                Nat44ConfigFlags,
                f"NAT44_IS_{mode.replace(u'-', u'_').upper()}"
            ).value
        )

        with PapiSocketExecutor(node) as papi_exec:
            papi_exec.add(cmd, **args_in).get_reply(err_msg)

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

        The return value is a callable (zero argument Python function)
        which can be used to reset NAT state, so repeated trial measurements
        hit the same slow path.

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
        :returns: Resetter of the NAT state.
        :rtype: Callable[[], None]
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

        # A closure, accessing the variables above.
        def resetter():
            """Delete and re-add the NAT range setting."""
            with PapiSocketExecutor(node) as papi_exec:
                args_in[u"is_add"] = False
                papi_exec.add(cmd, **args_in)
                args_in[u"is_add"] = True
                papi_exec.add(cmd, **args_in)
                papi_exec.get_replies(err_msg)

        return resetter

    @staticmethod
    def show_nat44_config(node):
        """Show the NAT44 plugin running configuration.

        :param node: DUT node.
        :type node: dict
        """
        cmd = u"nat44_show_running_config"
        err_msg = f"Failed to get NAT44 configuration on host {node[u'host']}"

        with PapiSocketExecutor(node) as papi_exec:
            reply = papi_exec.add(cmd).get_reply(err_msg)

        logger.debug(f"NAT44 Configuration:\n{pformat(reply)}")

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
        # vpp-device tests have not dedicated physical core so
        # ${dp_count_int} == 0 but we need to use one thread
        threads = 1 if not int(threads) else int(threads)
        rest, mult = modf(log2(sessions/(10*threads)))
        return 2 ** (int(mult) + (1 if rest else 0)) * 10

    @staticmethod
    def get_nat44_sessions_number(node, proto):
        """Get number of expected NAT44 sessions from NAT44 mapping data.

        This keyword uses output from a CLI command,
        so it can start failing when VPP changes the output format.
        TODO: Switch to API (or stat segment) when available.

        The current implementation supports both 2202 and post-2202 format.
        (The Gerrit number changing the output format is 34877.)

        For TCP proto, the expected state after rampup is
        some number of sessions in transitory state (VPP has seen the FINs),
        and some number of sessions in established state (meaning
        some FINs were lost in the last trial).
        While the two states may need slightly different number of cycles
        to process next packet, the current implementation considers
        both of them the "fast path", so they are both counted as expected.

        As the tests should fail if a session is timed-out,
        the logic substracts timed out sessions for the returned value
        (only available for post-2202 format).

        TODO: Investigate if it is worth to insert additional rampup trials
        in TPUT tests to ensure all sessions are transitory before next
        measurement.

        :param node: DUT node.
        :param proto: Required protocol - TCP/UDP/ICMP.
        :type node: dict
        :type proto: str
        :returns: Number of active established NAT44 sessions.
        :rtype: int
        :raises ValueError: If not supported protocol.
        :raises RuntimeError: If output is not formatted as expected.
        """
        proto_l = proto.strip().lower()
        if proto_l not in [u"udp", u"tcp", u"icmp"]:
            raise ValueError(f"Unsupported protocol: {proto}!")
        summary_text = NATUtil.show_nat44_summary(node)
        summary_lines = summary_text.splitlines()
        # Output from VPP v22.02 and before, delete when no longer needed.
        pattern_2202 = f"total {proto_l} sessions:"
        if pattern_2202 in summary_text:
            for line in summary_lines:
                if pattern_2202 not in line:
                    continue
                return int(line.split(u":", 1)[1].strip())
        # Post-2202, the proto info and session info are not on the same line.
        found = False
        for line in summary_lines:
            if not found:
                if f"{proto_l} sessions:" in line:
                    found = True
                continue
            # Proto is found, find the line we are interested in.
            if u"total" not in line:
                raise RuntimeError(f"show nat summary: no {proto} total.")
            # We have the line with relevant numbers.
            total_part, timed_out_part = line.split(u"(", 1)
            timed_out_part = timed_out_part.split(u")", 1)[0]
            total_count = int(total_part.split(u":", 1)[1].strip())
            timed_out_count = int(timed_out_part.split(u":", 1)[1].strip())
            active_count = total_count - timed_out_count
            return active_count
        raise RuntimeError(u"Unknown format of show nat44 summary")

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

        The return value is a callable (zero argument Python function)
        which can be used to reset NAT state, so repeated trial measurements
        hit the same slow path.

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

        # A closure, accessing the variables above.
        def resetter():
            """Delete and re-add the deterministic NAT mapping."""
            with PapiSocketExecutor(node) as papi_exec:
                args_in[u"is_add"] = False
                papi_exec.add(cmd, **args_in)
                args_in[u"is_add"] = True
                papi_exec.add(cmd, **args_in)
                papi_exec.get_replies(err_msg)

        return resetter

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
