# Copyright (c) 2018 Cisco and/or its affiliates.
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


import ipaddress

from resources.libraries.python.VatExecutor import VatExecutor


class Map(object):
    """Utilities for manipulating MAP feature in VPP."""

    @staticmethod
    def map_add_domain(vpp_node, ip4_pfx, ip6_pfx, ip6_src, ea_bits_len,
                       psid_offset, psid_len, map_t=False):
        """Add map domain on node.

        :param vpp_node: VPP node to add map domain on.
        :param ip4_pfx: Rule IPv4 prefix.
        :param ip6_pfx: Rule IPv6 prefix.
        :param ip6_src: MAP domain IPv6 BR address / Tunnel source.
        :param ea_bits_len: Embedded Address bits length.
        :param psid_offset: Port Set Identifier (PSID) offset.
        :param psid_len: Port Set Identifier (PSID) length.
        :param map_t: Mapping using translation instead of encapsulation.
            Default False.
        :type vpp_node: dict
        :type ip4_pfx: str
        :type ip6_pfx: str
        :type ip6_src: str
        :type ea_bits_len: int
        :type psid_offset: int
        :type psid_len: int
        :type map_t: bool
        :returns: Index of created map domain.
        :rtype: int
        :raises RuntimeError: If unable to add map domain.
        """
        translate = 'map-t' if map_t else ''

        output = VatExecutor.cmd_from_template(vpp_node, "map_add_domain.vat",
                                               ip4_pfx=ip4_pfx,
                                               ip6_pfx=ip6_pfx,
                                               ip6_src=ip6_src,
                                               ea_bits_len=ea_bits_len,
                                               psid_offset=psid_offset,
                                               psid_len=psid_len,
                                               map_t=translate)
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
        """Return PSID from port.::

                              0                   1
                              0 1 2 3 4 5 6 7 8 9 0 1 2 3 4 5
                             +-----------+-----------+-------+
               Ports in      |     A     |    PSID   |   j   |
            the CE port set  |    > 0    |           |       |
                             +-----------+-----------+-------+
                             |  a bits   |  k bits   |m bits |


        :param port: Port to compute PSID from.
        :param psid_len: PSID length.
        :param psid_offset: PSID offset.
        :type port: int
        :type psid_len: int
        :type psid_offset: int
        :returns: PSID.
        :rtype: int
        """
        ones = 2**16-1
        mask = ones >> (16 - psid_len)
        psid = port >> (16 - psid_len - psid_offset)
        psid &= mask
        return psid

    @staticmethod
    def _make_ea_bits(ipv4_net, ipv4_host, ea_bit_len, psid_len, psid):
        """
        _note_: host(or prefix) part of destination ip in rule prefix, + psid

        :param ipv4_net: IPv4 domain prefix.
        :param ipv4_host: Destination IPv4 address.
        :param ea_bit_len: EA bit length.
        :param psid_len: PSID length.
        :param psid: PSID.
        :type ipv4_net: ipaddress.IPv4Network
        :type ipv4_host: ipaddress.IPv4Address
        :type ea_bit_len: int
        :type psid_len: int
        :type psid: int
        :returns: Number representing EA bit field of destination IPv6 address.
        :rtype: int
        """
        v4_suffix_len = ipv4_net.max_prefixlen - ipv4_net.prefixlen
        v4_suffix = int(ipv4_net.network_address) ^ int(ipv4_host)

        if ipv4_net.prefixlen + ea_bit_len <= 32:
            ea_bits = v4_suffix >> (v4_suffix_len - ea_bit_len)
            return ea_bits
        else:
            q_len = ea_bit_len - v4_suffix_len
            # p_bits = v4_suffix << q_len  # option 1: psid right padded
            p_bits = v4_suffix << psid_len  # option 2: psid left padded
            if q_len < psid_len:
                raise Exception("invalid configuration: q_len < psid_len")
            ea_bits = p_bits | psid
            ea_bits <<= q_len - psid_len  # option 2: psid left padded
            return ea_bits

    @staticmethod
    def _make_interface_id(rule_net, dst_ip, ea_bit_len, psid):
        """
        _note_: if prefix or complete ip (<= 32), psid is 0

        :param rule_net: IPv4 domain prefix.
        :param dst_ip: Destination IPv4 address.
        :param ea_bit_len: EA bit length.
        :param psid: PSID.
        :type rule_net: ipaddress.IPv4Network
        :type dst_ip: ipaddress.IPv4Address
        :type ea_bit_len: int
        :type psid: int
        :returns: Number representing interface id field of destination IPv6
            address.
        :rtype: int
        """
        if rule_net.prefixlen + ea_bit_len < 32:
            v4_suffix_len = rule_net.max_prefixlen - rule_net.prefixlen
            v4_suffix = int(rule_net.network_address) ^ int(dst_ip)
            ea_bits = v4_suffix >> (v4_suffix_len - ea_bit_len)
            address = int(rule_net.network_address) >> v4_suffix_len
            address <<= ea_bit_len
            address |= ea_bits
            address <<= 32 - rule_net.prefixlen - ea_bit_len
            address <<= 16
        elif rule_net.prefixlen + ea_bit_len == 32:
            address = int(dst_ip) << 16
        else:
            address = int(dst_ip) << 16
            address |= psid
            return address

        return address

    @staticmethod
    def compute_ipv6_map_destination_address(ipv4_pfx, ipv6_pfx, ea_bit_len,
                                             psid_offset, psid_len, ipv4_dst,
                                             dst_port):
        """Compute IPv6 destination address from IPv4 address for MAP algorithm.
        (RFC 7597)::

          |     n bits         |  o bits   | s bits  |   128-n-o-s bits      |
          +--------------------+-----------+---------+-----------------------+
          |  Rule IPv6 prefix  |  EA bits  |subnet ID|     interface ID      |
          +--------------------+-----------+---------+-----------------------+
          |<---  End-user IPv6 prefix  --->|

        :param ipv4_pfx: Domain IPv4 preffix.
        :param ipv6_pfx: Domain IPv6 preffix.
        :param ea_bit_len: Domain EA bits length.
        :param psid_offset: Domain PSID offset.
        :param psid_len: Domain PSID length.
        :param ipv4_dst: Destination IPv4 address.
        :param dst_port: Destination port number or ICMP ID.
        :type ipv4_pfx: str
        :type ipv6_pfx: str
        :type ea_bit_len: int
        :type psid_offset: int
        :type psid_len: int
        :type ipv4_dst: str
        :type dst_port: int
        :returns: Computed IPv6 address.
        :rtype: str
        """
        ipv6_net = ipaddress.ip_network(unicode(ipv6_pfx))
        ipv4_net = ipaddress.ip_network(unicode(ipv4_pfx))
        ipv4_host = ipaddress.ip_address(unicode(ipv4_dst))

        ipv6_host_len = ipv6_net.max_prefixlen - ipv6_net.prefixlen
        end_user_v6_pfx_len = ipv6_net.prefixlen + ea_bit_len
        psid = Map.get_psid_from_port(dst_port, psid_len, psid_offset)

        rule_v6_pfx = int(ipv6_net.network_address) >> ipv6_host_len
        ea_bits = Map._make_ea_bits(ipv4_net, ipv4_host, ea_bit_len, psid_len,
                                    psid)
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

    @staticmethod
    def compute_ipv6_map_source_address(ipv6_pfx, ipv4_src):
        """Compute IPv6 source address from IPv4 address for MAP-T algorithm.

        :param ipv6_pfx: 96 bit long IPv6 prefix.
        :param ipv4_src: IPv4 source address
        :type ipv6_pfx: str
        :type ipv4_src: str
        :returns: IPv6 address, combination of IPv6 prefix and IPv4 address.
        :rtype: str
        """
        ipv6_net = ipaddress.ip_network(unicode(ipv6_pfx))
        ipv4_host = ipaddress.ip_address(unicode(ipv4_src))

        address = int(ipv6_net.network_address)
        address |= int(ipv4_host)

        return str(ipaddress.ip_address(address))
