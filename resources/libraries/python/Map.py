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

"""Map utilities library."""


from resources.libraries.python.VatExecutor import VatExecutor
import ipaddress


class Map(object):
    """Utilities for manipulating MAP feature in VPP."""

    @staticmethod
    def map_add_domain(vpp_node, ip4_pfx, ip6_pfx, ip6_src, ea_bits_len,
                       psid_offset, psid_len):
        """Add map domain on node.

        :param vpp_node: VPP node to add map domain on.
        :param ip4_pfx: Rule IPv4 prefix.
        :param ip6_pfx: Rule IPv6 prefix.
        :param ip6_src: MAP domain IPv6 BR address / Tunnel source.
        :param ea_bits_len: Embedded Address bits length.
        :param psid_offset: Port Set Identifier (PSID) offset.
        :param psid_len: Port Set Identifier (PSID) length.
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
    def map_add_rule(vpp_node, index, psid, dst, delete=False):
        """Add or delete map rule on node.

        :param vpp_node: VPP node to add map rule on.
        :param index: Map domain index to add rule to.
        :param psid: Port Set Identifier.
        :param dst: MAP CE IPv6 address.
        :param delete: If set to True, delete rule. Default False.
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

    @staticmethod
    def map_del_domain(vpp_node, index):
        """Delete map domain on node.

        :param vpp_node: VPP node to delete map domain on.
        :param index: Index of the map domain.
        :type vpp_node: dict
        :type index: int
        :raises RuntimeError: If unable to delete map domain.
        """
        output = VatExecutor.cmd_from_template(vpp_node, "map_del_domain.vat",
                                               index=index)
        if output[0]["retval"] != 0:
            raise RuntimeError('Unable to delete map domain {} on node {}'
                               .format(index, vpp_node['host']))

    @staticmethod
    def get_psid_from_port(port, psid_len, psid_offset):
        """
                              0                   1
                              0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5
                             +-----------+-----------+-------+
               Ports in      |     A     |    PSID   |   j   |
            the CE port set  |    > 0    |           |       |
                             +-----------+-----------+-------+
                             |  a bits   |  k bits   |m bits |


        :param port:
        :param psid_len:
        :param psid_offset:
        :type port: int
        :type psid_len: int
        :type psid_offset: int

        :return: PSID.
        :rtype: int
        """
        ones = 2**16-1
        mask = ones >> (16 - psid_len)
        psid = port >> (16 - psid_len - psid_offset)
        psid = psid & mask
        return psid

    @staticmethod
    def _make_ea_bits(ipv4_net, ipv4_host, ea_bit_len, psid_len, psid):
        v4_suffix_len = ipv4_net._max_prefixlen - ipv4_net.prefixlen
        v4_suffix = ipv4_net._ip ^ ipv4_host._ip

        if ipv4_net.prefixlen + ea_bit_len <= 32:
            ea_bits = v4_suffix >> (v4_suffix_len - ea_bit_len)
            return ea_bits
        else:
            q_len = ea_bit_len - v4_suffix_len
            p_bits = v4_suffix << q_len
            if q_len < psid_len:
                raise Exception("invalid configuration: q_len < psid_len")
            ea_bits = p_bits | psid
            return ea_bits

    @staticmethod
    def _make_interface_id(rule_net, dst_ip, ea_bit_len, psid):
        if rule_net.prefixlen + ea_bit_len < 32:
            v4_suffix_len = rule_net._max_prefixlen - rule_net.prefixlen
            v4_suffix = rule_net._ip ^ dst_ip._ip
            ea_bits = v4_suffix >> (v4_suffix_len - ea_bit_len)
            address = rule_net._ip >> rule_net.prefixlen
            address <<= ea_bit_len
            address |= ea_bits
            address <<= 32 - rule_net.prefixlen - ea_bit_len
            # psid_field = 0
            # address = address | psid_field
        elif rule_net.prefixlen + ea_bit_len == 32:
            address = dst_ip._ip << 16
            # psid_field = 0
            # address = address | psid_field
        else:
            address = dst_ip._ip << 16
            address |= psid
            return address

        return address

    @staticmethod
    def compute_ipv6_map_destination_address(ipv4_pfx, ipv6_pfx, ea_bit_len, psid_offset, psid_len, ipv4_dst, dst_port):
        # ipv4_pfx, ipv6_pfx, ea_bit_len, psid_offset, psid_len, ipv4_dst, dst_port = u'20.0.0.0/16', u'2001:db8::/32', 16, 6, 8,  u'20.0.6.5', 1232
        """

       |     n bits         |  o bits   | s bits  |   128-n-o-s bits      |
       +--------------------+-----------+---------+-----------------------+
       |  Rule IPv6 prefix  |  EA bits  |subnet ID|     interface ID      |
       +--------------------+-----------+---------+-----------------------+
       |<---  End-user IPv6 prefix  --->|


        :param ipv4_pfx:
        :param ipv6_pfx:
        :param ea_bit_len:
        :param psid_offset:
        :param psid_len:
        :param ipv4_dst:
        :param dst_port:
        :return:
        """
        ipv6_net = ipaddress.ip_network(unicode(ipv6_pfx))
        ipv4_net = ipaddress.ip_network(unicode(ipv4_pfx))
        ipv4_host = ipaddress.ip_address(unicode(ipv4_dst))

        ipv6_host_len = ipv6_net._max_prefixlen - ipv6_net.prefixlen
        ipv4_host_len = ipv4_net._max_prefixlen - ipv4_net.prefixlen
        end_user_v6_pfx_len = ipv6_host_len + ea_bit_len
        psid = Map.get_psid_from_port(dst_port, psid_len, psid_offset)

        rule_v6_pfx = ipv6_net.network_address._ip >> ipv6_host_len
        ea_bits = Map._make_ea_bits(ipv4_net, ipv4_host, ea_bit_len, psid_len,
                                    psid)
        subnet_id = 0
        interface_id = Map._make_interface_id(ipv4_net, ipv4_host, ea_bit_len,
                                              psid)

        address = rule_v6_pfx << ea_bit_len
        address |= ea_bits  # add EA bits

        if end_user_v6_pfx_len > 64:
            # If the End-user IPv6 prefix length is larger than 64,
            # the most significant parts of the interface identifier are
            # overwritten by the prefix.
            mask = (2**128-1) >> end_user_v6_pfx_len
            interface_id &= mask
        address <<= (128 - end_user_v6_pfx_len)
        address |= interface_id  # add Interface ID bits

        return str(ipaddress.ip_address(address))
