# Copyright (c) 2016 Cisco and/or its affiliates.
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

"""Map utilities for VPP."""


from resources.libraries.python.VatExecutor import VatExecutor


class Map(object):
    """TBD."""

    @staticmethod
    def map_add_domain(vpp_node, ip4_pfx, ip6_pfx, ip6_src, ea_bits_len,
                       psid_offset, psid_len):
        """Add map domain on node.

        :param vpp_node: VPP node to add map domain on.
        :param ip4_pfx:
        :param ip6_pfx:
        :param ip6_src:
        :param ea_bits_len:
        :param psid_offset:
        :param psid_len:
        :type vpp_node: dict
        :type ip4_pfx: str
        :type ip6_pfx: str
        :type ip6_src: str
        :type ea_bits_len: int
        :type psid_offset: int
        :type psid_len: int
        :return: Index of created map domain.
        :rtype: int
        :raises RuntimeError: If unable to add map domain.
        """
        output = VatExecutor.cmd_from_template(vpp_node, "map_add_domain.vat",
                                               ip4_pfx=ip4_pfx,
                                               ip6_pfx=ip6_pfx,
                                               ip6_src=ip6_src,
                                               ea_bits_len=ea_bits_len,
                                               psid_offset=psid_offset,
                                               psid_len=psid_len)
        if output[0]["retval"] == 0:
            return output[0]["index"]
        else:
            raise RuntimeError('Unable to add map domain on node {}'
                               .format(vpp_node['host']))

    @staticmethod
    def map_add_rule(vpp_node, index, psid, dst, delete):
        """Add or delete map rule on node.

        :param vpp_node:
        :param index:
        :param psid:
        :param dst:
        :param delete:
        :type vpp_node: dict
        :type index: int
        :type psid: int
        :type dst: str
        :type delete: bool
        :raises RuntimeError: If unable to add map rule.
        """
        output = VatExecutor.cmd_from_template(vpp_node, "map_add_del_rule.vat",
                                               index=index,
                                               psid=psid,
                                               dst=dst,
                                               delete='del' if delete else '')

        if output[0]["retval"] != 0:
            raise RuntimeError('Unable to add map rule on node {}'
                               .format(vpp_node['host']))
