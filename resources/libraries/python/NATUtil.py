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

from pprint import pformat
from enum import IntEnum

from ipaddress import IPv4Address
from robot.api import logger

from resources.libraries.python.Constants import Constants
from resources.libraries.python.InterfaceUtil import InterfaceUtil
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
        :param interface: Inside interface.
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
    def set_nat44_deterministic(node, ip_in, subnet_in, ip_out, subnet_out):
        """Set deterministic behaviour of NAT44.

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
        cmd = u"nat_det_add_del_map"
        err_msg = f"Failed to set deterministic behaviour of NAT " \
            f"on host {node[u'host']}"
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
    def set_nat_addr_port_alloc_alg(
            node, alg, start_port, end_port, psid_offset=0, psid_length=0,
            psid=0):
        """Set NAT address and port assignment algorithm.

        :param node: DUT node.
        :param alg: Address and port assignment algorithm:
            DEFAULT, MAP_E, PORT_RANGE.
        :param start_port: Port range start.
        :param end_port: Port range end.
        :param psid_offset: Number of offset bits (Optional, valid oly for MAP-E
            algorithm).
        :param psid_length: Length of PSID (Optional, valid oly for MAP-E
            algorithm).
        :param psid: Port Set Identifier value (Optional, valid oly for MAP-E
            algorithm).
        :type node: dict
        :type alg: str
        :type start_port: int
        :type end_port: int
        :type psid_offset: int
        :type psid_length: int
        :type psid: int
        """
        cmd = u"nat_set_addr_and_port_alloc_alg"
        err_msg = f"Failed to set NAT address and port assignment algorithm " \
            f"on host {node[u'host']}"
        args_in = dict(
            alg=getattr(
                NatAddrPortAllocAlg, f"NAT_ALLOC_ALG_{alg.upper()}"
            ).value,
            psid_offset=int(psid_offset),
            psid_length=int(psid_length),
            psid=int(psid),
            start_port=int(start_port),
            end_port=int(end_port)
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
        """
        PapiSocketExecutor.run_cli_cmd(node, u"show nat44 summary")

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
        cmd = u"nat_show_config"
        err_msg = f"Failed to get NAT base data on host {node[u'host']}"

        with PapiSocketExecutor(node) as papi_exec:
            reply = papi_exec.add(cmd).get_reply(err_msg)

        logger.debug(f"NAT Configuration:\n{pformat(reply)}")

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
        cmd = u"nat_show_config"
        err_msg = f"Failed to get NAT user data on host {node[u'host']}"

        with PapiSocketExecutor(node) as papi_exec:
            reply = papi_exec.add(cmd).get_reply(err_msg)

        logger.debug(f"NAT Configuration:\n{pformat(reply)}")

        cmds = [
            u"nat44_user_dump",
            u"nat44_user_session_dump",
        ]
        PapiSocketExecutor.dump_and_log(node, cmds)
