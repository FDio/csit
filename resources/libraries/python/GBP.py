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

"""GBP utilities library."""

from enum import IntEnum
from ipaddress import ip_address

from resources.libraries.python.IPUtil import IPUtil
from resources.libraries.python.L2Util import L2Util
from resources.libraries.python.PapiExecutor import PapiSocketExecutor
from resources.libraries.python.topology import Topology


class GBPEndpointFlags(IntEnum):
    """GBP Endpoint Flags."""
    GBP_API_ENDPOINT_FLAG_NONE = 0
    GBP_API_ENDPOINT_FLAG_BOUNCE = 1
    GBP_API_ENDPOINT_FLAG_REMOTE = 2
    GBP_API_ENDPOINT_FLAG_LEARNT = 4
    GBP_API_ENDPOINT_FLAG_EXTERNAL = 8


class GBPBridgeDomainFlags(IntEnum):
    """GBP Bridge Domain Flags."""
    GBP_BD_API_FLAG_NONE = 0,
    GBP_BD_API_FLAG_DO_NOT_LEARN = 1,
    GBP_BD_API_FLAG_UU_FWD_DROP = 2,
    GBP_BD_API_FLAG_MCAST_DROP = 4,
    GBP_BD_API_FLAG_UCAST_ARP = 8,


class GBPSubnetType(IntEnum):
    """GBP Subnet Type."""
    GBP_API_SUBNET_TRANSPORT = 0
    GBP_API_SUBNET_STITCHED_INTERNAL = 1
    GBP_API_SUBNET_STITCHED_EXTERNAL = 2
    GBP_API_SUBNET_L3_OUT = 3
    GBP_API_SUBNET_ANON_L3_OUT = 4


class GBPExtItfFlags(IntEnum):
    """GBP External Interface Flags."""
    GBP_API_EXT_ITF_F_NONE = 0
    GBP_API_EXT_ITF_F_ANON = 1


class GBPRuleAction(IntEnum):
    """GBP Rule Action."""
    GBP_API_RULE_PERMIT = 0
    GBP_API_RULE_DENY = 1
    GBP_API_RULE_REDIRECT = 2


class GBP(object):
    """GBP utilities."""

    @staticmethod
    def gbp_route_domain_add(node, rd_id=1, is_ipv6=False):
        """Add GBP route domain.

        :param node: Node to add GBP route domain on.
        :param rd_id: GBP route domain ID.
        :param is_ipv6: If route domain is IPv6.
        :type node: dict
        :type rd_id: int
        :type is_ipv6: bool
        """
        cmd = 'gbp_route_domain_add'
        err_msg = 'Failed to add GBP route domain on {node}!'\
                  .format(node=node['host'])

        args_in = dict(
            rd = dict (
                rd_id = rd_id,
                ip4_table_id = int(is_ipv6 == False),
                ip6_table_id = int(is_ipv6 == True),
                ip4_uu_sw_if_index = NONE,
                ip6_uu_sw_if_index = NONE
            )
        )

        with PapiSocketExecutor(node) as papi_exec:
            papi_exec.add(cmd, **args_in).get_reply(err_msg)

    @staticmethod
    def gbp_bridge_domain_add(node, bvi_sw_if_index, bd_id=1):
        """Add GBP bridge domain.

        :param node: Node to add GBP bridge domain on.
        :param bvi_sw_if_index: SW index of BVI/loopback interface.
        :param bd_id: GBP bridge domain ID.
        :type node: dict
        :type bvi_sw_if_index: int
        :type bd_id: int
        """
        cmd = 'gbp_bridge_domain_add'
        err_msg = 'Failed to add GBP route domain on {node}!'\
                  .format(node=node['host'])

        args_in = dict(
            bd = dict(
                flags = getattr(GBPEndpointFlags,
                                GBP_API_ENDPOINT_FLAG_NONE).value,
                bvi_sw_if_index = bvi_sw_if_index,
                uu_fwd_sw_if_index = NONE,
                bm_flood_sw_if_index = NONE,
                bd_id = bd_id
            }
        )

        with PapiSocketExecutor(node) as papi_exec:
            papi_exec.add(cmd, **args_in).get_reply(err_msg)

    @staticmethod
    def gbp_endpoint_group_add(node, bd_id=1, rd_id=1, vnid=1, sclass=100):
        """Add GBP endpoint group.

        :param node: Node to add GBP endpoint group on.
        :param bd_id: GBP bridge domain ID.
        :param rd_id: GBP route domain ID.
        :param vnid: VNID.
        :param sclass: SCLASS.
        :type node: dict
        :type bd_id: int
        :type rd_id: int
        :type vnid: int
        :type sclass: int
        """
        cmd = 'gbp_endpoint_group_add'
        err_msg = 'Failed to add GBP endpoint group on {node}!'\
                  .format(node=node['host'])

        args_in = dict(
            epg = dict (
                uplink_sw_if_index = NONE,
                bd_id = bd_id,
                rd_id = rd_id,
                vnid = vnid,
                sclass = sclass,
                retention = dict (
                    remote_ep_timeout = NONE
                )
            )
        )

        with PapiSocketExecutor(node) as papi_exec:
            papi_exec.add(cmd, **args_in).get_reply(err_msg)

    @staticmethod
    def gbp_endpoint_add(node, sw_if_index, ip_addr, mac_addr, sclass=100):
        """Add GBP endpoint.

        :param node: Node to add GBP endpoint on.
        :param sw_if_index: SW index of interface.
        :param ip_addr: GBP route domain ID.
        :param mac_addr: MAC address.
        :param sclass: SCLASS.
        :type node: dict
        :type sw_if_index: int
        :type ip_addr: str
        :type mac_addr: str
        :type sclass: int
        """
        cmd = 'gbp_endpoint_add'
        err_msg = 'Failed to add GBP endpoint on {node}!'\
                  .format(node=node['host'])

        ips = list(IPUtil.create_ip_address_object(ip_address(unicode(ip_addr)))
        tun_src = IPUtil.create_ip_address_object(ip_address(unicode('0.0.0.0'))
        tun_dst = IPUtil.create_ip_address_object(ip_address(unicode('0.0.0.0'))

        args_in = dict(
            endpoint = dict(
                sw_if_index = sw_if_index,
                ips = ips,
                n_ips = len(ips),
                mac = L2Util.mac_to_bin(mac_addr),
                sclass = sclass,
                flags = getattr(GBPEndpointFlags,
                                GBP_API_ENDPOINT_FLAG_EXTERNAL).value,
                tun = dict(
                    src = tun_src,
                    dst = tun_src
                )
            )
        )

        with PapiSocketExecutor(node) as papi_exec:
            papi_exec.add(cmd, **args_in).get_reply(err_msg)

    @staticmethod
    def gbp_ext_itf_add_del(node, sw_if_index, bd_id=1, rd_id=1):
        """Add external interface to GBP.

        :param node: Node to add external GBP interface on.
        :param sw_if_index: SW index of interface.
        :param bd_id: GBP bridge domain ID.
        :param rd_id: GBP route domain ID.
        :type node: dict
        :type sw_if_index: int
        :type bd_id: int
        :type rd_id: int
        """
        cmd = 'gbp_ext_itf_add_del'
        err_msg = 'Failed to add external GBP interface on {node}!'\
                  .format(node=node['host'])

        args_in = dict(
            is_add = 1,
            ext_itf = dict(
                sw_if_index = sw_if_index,
                bd_id = bd_id,
                rd_id = rd_id,
                flags = getattr(GBPExtItfFlags,
                                GBP_API_EXT_ITF_F_NONE).value
            )
        )

        with PapiSocketExecutor(node) as papi_exec:
            papi_exec.add(cmd, **args_in).get_reply(err_msg)

    @staticmethod
    def gbp_subnet_add_del(node, address, address_length, rd_id=1, sclass=100):
        """Add external interface to GBP.

        :param node: Node to add GBP subnet on.
        :param address: IPv4 adddress.
        :param address_length: IPv4 address subnet.
        :param rd_id: GBP route domain ID.
        :param sclass: SCLASS.
        :type node: dict
        :type address: int
        :type address_length: int
        :type rd_id: int
        :type sclass: int
        """
        cmd = 'gbp_subnet_add_del'
        err_msg = 'Failed to add GBP subnet on {node}!'\
                  .format(node=node['host'])

        args_in = dict(
            is_add = 1,
            subnet = dict(
                type = getattr(GBPSubnetType,
                               GBP_API_SUBNET_L3_OUT).value,
                sw_if_index = NONE,
                sclass = sclass,
                prefix = dict(
                    address = address,
                    address_length = address_length
                ),
                rd_id = rd_id
            }
        )

        with PapiSocketExecutor(node) as papi_exec:
            papi_exec.add(cmd, **args_in).get_reply(err_msg)

    @staticmethod
    def gbp_contract_add_del(node, address, address_length, rd_id=1, sclass=100):
        """Add GBP contract.

        :param node: Node to add GBP contract on.
        :param address: IPv4 adddress.
        :param address_length: IPv4 address subnet.
        :param rd_id: GBP route domain ID.
        :param sclass: SCLASS.
        :type node: dict
        :type address: int
        :type address_length: int
        :type rd_id: int
        :type sclass: int
        """
        cmd = 'gbp_contract_add_del'
        err_msg = 'Failed to add GBP contract on {node}!'\
                  .format(node=node['host'])

        rule_permit = dict(
            action = getattr(GBPRuleAction,
                             GBP_API_RULE_PERMIT).value,
            nh_set = dict(
                hash_mode = list(),
                n_nhs = 8,
                nhs = list(dict())*8,
            )
        )

        args_in = dict(
            is_add = 1,
            contract = dict(
                acl_index = acl,
                sclass = sclass,
                dclass = dclass,
                n_rules = 2,
                rules = list(rule_permit, rule_permit),
                n_ether_types = 16,
                allowed_ethertypes = list(0x800, 0x86dd) + list(0)*14
            )
        )

        with PapiSocketExecutor(node) as papi_exec:
            papi_exec.add(cmd, **args_in).get_reply(err_msg)
