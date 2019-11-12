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

"""NAT utilities library."""

from pprint import pformat
from socket import AF_INET, inet_pton
from enum import IntEnum

from robot.api import logger

from resources.libraries.python.InterfaceUtil import InterfaceUtil
from resources.libraries.python.PapiExecutor import PapiSocketExecutor


class NATConfigFlags(IntEnum):
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


class NATUtil(object):
    """This class defines the methods to set NAT."""

    def __init__(self):
        pass

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
        cmd = u"nat44_interface_add_del_feature"

        int_in_idx = InterfaceUtil.get_sw_if_index(node, int_in)
        err_msg = f"Failed to set inside interface {int_in} for NAT44 " \
            f"on host {node[u'host']}"
        args_in = dict(
            sw_if_index=int_in_idx,
            is_add=1,
            flags=getattr(NATConfigFlags, u"NAT_IS_INSIDE").value
        )

        with PapiSocketExecutor(node) as papi_exec:
            papi_exec.add(cmd, **args_in).get_reply(err_msg)

        int_out_idx = InterfaceUtil.get_sw_if_index(node, int_out)
        err_msg = f"Failed to set outside interface {int_out} for NAT44 " \
            f"on host {node[u'host']}"
        args_in = dict(
            sw_if_index=int_out_idx,
            is_add=1,
            flags=getattr(NATConfigFlags, u"NAT_IS_OUTSIDE").value
        )

        with PapiSocketExecutor(node) as papi_exec:
            papi_exec.add(cmd, **args_in).get_reply(err_msg)

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
            in_addr=inet_pton(AF_INET, str(ip_in)),
            in_plen=int(subnet_in),
            out_addr=inet_pton(AF_INET, str(ip_out)),
            out_plen=int(subnet_out)
        )

        with PapiSocketExecutor(node) as papi_exec:
            papi_exec.add(cmd, **args_in).get_reply(err_msg)

    @staticmethod
    def show_nat(node):
        """Show the NAT configuration and data.

        Used data sources:

            nat_show_config
            nat_worker_dump
            nat44_interface_addr_dump
            nat44_address_dump
            nat44_static_mapping_dump
            nat44_user_dump
            nat44_interface_dump
            nat44_user_session_dump
            nat_det_map_dump

        :param node: DUT node.
        :type node: dict
        """
        cmd = u"nat_show_config"
        err_msg = f"Failed to get NAT configuration on host {node[u'host']}"

        with PapiSocketExecutor(node) as papi_exec:
            reply = papi_exec.add(cmd).get_reply(err_msg)

        logger.debug(f"NAT Configuration:\n{pformat(reply)}")

        cmds = [
            u"nat_worker_dump",
            u"nat44_interface_addr_dump",
            u"nat44_address_dump",
            u"nat44_static_mapping_dump",
            u"nat44_user_dump",
            u"nat44_interface_dump",
            u"nat44_user_session_dump",
            u"nat_det_map_dump"
        ]
        PapiSocketExecutor.dump_and_log(node, cmds)
