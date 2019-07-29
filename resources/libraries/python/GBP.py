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

from resources.libraries.python.PapiExecutor import PapiSocketExecutor
from resources.libraries.python.topology import Topology


class GBP(object):
    """GBP utilities."""

    @staticmethod
    def gbp_route_domain_add(node, rd_id=1, is_ipv6=False):
        """Add GBP route domain.

        :param node: Node to add BGP route domain on.
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
            rd={
                'rd_id': rd_id,
                'ip4_table_id': int(is_ipv6 == False),
                'ip6_table_id': int(is_ipv6 == True),
                'ip4_uu_sw_if_index': NONE,
                'ip6_uu_sw_if_index': NONE
            }
        )

        with PapiSocketExecutor(node) as papi_exec:
            papi_exec.add(cmd, **args_in).get_reply(err_msg)

    @staticmethod
    def gbp_bridge_domain_add(node, bvi_sw_if_index, bd_id=1):
        """Add GBP bridge domain.

        :param node: Node to add BGP bridge domain on.
        :param bvi_sw_if_index: SW index of BVI interface.
        :param bd_id: GBP route domain ID.
        :type node: dict
        :type bvi_sw_if_index: int
        :type bd_id: int
        """
        cmd = 'gbp_bridge_domain_add'
        err_msg = 'Failed to add GBP route domain on {node}!'\
                  .format(node=node['host'])

        args_in = dict(
            bd={
                'flags': 0,
                'bvi_sw_if_index': bvi_sw_if_index,
                'uu_fwd_sw_if_index': NONE,
                'bm_flood_sw_if_index': NONE,
                'bd_id': bd_id
                }
            )
        )

        with PapiSocketExecutor(node) as papi_exec:
            papi_exec.add(cmd, **args_in).get_reply(err_msg)

    @staticmethod
    def gbp_endpoint_add(node, bd_id=1, rd_id=1, vnid=1, sclass=100):
        """Add GBP endpoint

        :param node: Node to add BGP bridge domain on.
        :param bd_id: SW index of BVI interface.
        :param rd_id: GBP route domain ID.
        :type node: dict
        :type bd_id: int
        :type rd_id: int
        """
        cmd = 'gbp_endpoint_add'
        err_msg = 'Failed to add GBP endpoint on {node}!'\
                  .format(node=node['host'])

        args_in = dict(
            'epg': {
                'uplink_sw_if_index': NONE,
                'bd_id': bd,
                'rd_id': rd,
                'vnid': vnid,
                'sclass': sclass,
                'retention': {
                    'remote_ep_timeout': NONE
                }
            }
        )

        with PapiSocketExecutor(node) as papi_exec:
            papi_exec.add(cmd, **args_in).get_reply(err_msg)
