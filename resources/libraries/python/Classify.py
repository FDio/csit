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

"""Classify utilities library."""

import binascii
import re

from ipaddress import ip_address

from robot.api import logger

from resources.libraries.python.topology import Topology
from resources.libraries.python.PapiExecutor import PapiSocketExecutor


class Classify(object):
    """Classify utilities."""

    @staticmethod
    def _build_mac_mask(dst_mac='', src_mac='', ether_type=''):
        """Build MAC ACL mask data in hexstring format.

        :param dst_mac: Source MAC address <0-ffffffffffff>.
        :param src_mac: Destination MAC address <0-ffffffffffff>.
        :param ether_type: Ethernet type <0-ffff>.
        :type dst_mac: str
        :type src_mac: str
        :type ether_type: str
        :returns MAC ACL mask in hexstring format.
        :rtype: str
        """
        if ether_type:
            end = 28
        elif src_mac:
            end = 24
        else:
            end = 12

        return ('{!s:0>12}{!s:0>12}{!s:0>4}'.format(
            dst_mac.replace(':', ''), src_mac.replace(':', ''),
            ether_type))[0:end]

    @staticmethod
    def _build_ip_mask(proto='', src_ip='', dst_ip='', src_port='',
                       dst_port=''):
        """Build IP ACL mask data in hexstring format.

        :param proto: Protocol number <0-ff>.
        :param src_ip: Source ip address <0-ffffffff>.
        :param dst_ip: Destination ip address <0-ffffffff>.
        :param src_port: Source port number <0-ffff>.
        :param str dst_port: Destination port number <0-ffff>.
        :type proto: str
        :type src_ip: str
        :type dst_ip: str
        :type src_port: str
        :type dst_port:src
        :returns: IP mask in hexstring format.
        :rtype: str
        """
        if dst_port:
            end = 48
        elif src_port:
            end = 44
        elif dst_ip:
            end = 40
        elif src_ip:
            end = 32
        else:
            end = 20

        return ('{!s:0>20}{!s:0>12}{!s:0>8}{!s:0>4}{!s:0>4}'.format(
            proto, src_ip, dst_ip, src_port, dst_port))[0:end]

    @staticmethod
    def _build_ip6_mask(next_hdr='', src_ip='', dst_ip='', src_port='',
                        dst_port=''):
        """Build IPv6 ACL mask data in hexstring format.

        :param next_hdr: Next header number <0-ff>.
        :param src_ip: Source ip address <0-ffffffff>.
        :param dst_ip: Destination ip address <0-ffffffff>.
        :param src_port: Source port number <0-ffff>.
        :param dst_port: Destination port number <0-ffff>.
        :type next_hdr: str
        :type src_ip: str
        :type dst_ip: str
        :type src_port: str
        :type dst_port: str
        :returns: IPv6 ACL mask in hexstring format.
        :rtype: str
        """
        if dst_port:
            end = 88
        elif src_port:
            end = 84
        elif dst_ip:
            end = 80
        elif src_ip:
            end = 48
        else:
            end = 14

        return ('{!s:0>14}{!s:0>34}{!s:0>32}{!s:0>4}{!s:0>4}'.format(
            next_hdr, src_ip, dst_ip, src_port, dst_port))[0:end]

    @staticmethod
    def _build_mac_match(dst_mac='', src_mac='', ether_type=''):
        """Build MAC ACL match data in  hexstring format.

        :param dst_mac: Source MAC address <x:x:x:x:x:x>.
        :param src_mac: Destination MAC address <x:x:x:x:x:x>.
        :param ether_type: Ethernet type <0-ffff>.
        :type dst_mac: str
        :type src_mac: str
        :type ether_type: str
        :returns: MAC ACL match data in hexstring format.
        :rtype: str
        """
        if ether_type:
            end = 28
        elif src_mac:
            end = 24
        else:
            end = 12

        return ('{!s:0>12}{!s:0>12}{!s:0>4}'.format(
            dst_mac.replace(':', ''), src_mac.replace(':', ''),
            ether_type))[0:end]

    @staticmethod
    def _build_ip_match(proto=0, src_ip='', dst_ip='', src_port=0, dst_port=0):
        """Build IP ACL match data in hexstring format.

        :param proto: Protocol number with valid option "x".
        :param src_ip: Source ip address with format of "x.x.x.x".
        :param dst_ip: Destination ip address with format of "x.x.x.x".
        :param src_port: Source port number "x".
        :param dst_port: Destination port number "x".
        :type proto: int
        :type src_ip: str
        :type dst_ip: str
        :type src_port: int
        :type dst_port: int
        :returns: IP ACL match data in hexstring format.
        :rtype: str
        """
        if src_ip:
            src_ip = binascii.hexlify(ip_address(unicode(src_ip)).packed)
        if dst_ip:
            dst_ip = binascii.hexlify(ip_address(unicode(dst_ip)).packed)
        if dst_port:
            end = 48
        elif src_port:
            end = 44
        elif dst_ip:
            end = 40
        elif src_ip:
            end = 32
        else:
            end = 20

        return ('{!s:0>20}{!s:0>12}{!s:0>8}{!s:0>4}{!s:0>4}'.format(
            hex(proto)[2:], src_ip, dst_ip, hex(src_port)[2:],
            hex(dst_port)[2:]))[0:end]

    @staticmethod
    def _build_ip6_match(next_hdr=0, src_ip='', dst_ip='', src_port=0,
                         dst_port=0):
        """Build IPv6 ACL match data in hexstring format.

        :param next_hdr: Next header number with valid option "x".
        :param src_ip: Source ip6 address with format of "xxxx:xxxx::xxxx".
        :param dst_ip: Destination ip6 address with format of
            "xxxx:xxxx::xxxx".
        :param src_port: Source port number "x".
        :param dst_port: Destination port number "x".
        :type next_hdr: int
        :type src_ip: str
        :type dst_ip: str
        :type src_port: int
        :type dst_port: int
        :returns: IPv6 ACL match data in hexstring format.
        :rtype: str
        """
        if src_ip:
            src_ip = binascii.hexlify(ip_address(unicode(src_ip)).packed)
        if dst_ip:
            dst_ip = binascii.hexlify(ip_address(unicode(dst_ip)).packed)
        if dst_port:
            end = 88
        elif src_port:
            end = 84
        elif dst_ip:
            end = 80
        elif src_ip:
            end = 48
        else:
            end = 14

        return ('{!s:0>14}{!s:0>34}{!s:0>32}{!s:0>4}{!s:0>4}'.format(
            hex(next_hdr)[2:], src_ip, dst_ip, hex(src_port)[2:],
            hex(dst_port)[2:]))[0:end]

    @staticmethod
    def _classify_add_del_table(node, is_add, mask, match_n_vectors=1,
                                table_index=0xFFFFFFFF, nbuckets=2,
                                memory_size=2097152, skip_n_vectors=0,
                                next_table_index=0xFFFFFFFF,
                                miss_next_index=0xFFFFFFFF, current_data_flag=0,
                                current_data_offset=0):
        """Add or delete a classify table.

        :param node: VPP node to create classify table.
        :param is_add: If 1 the table is added, if 0 the table is deleted.
        :param mask: ACL mask in hexstring format.
        :param match_n_vectors: Number of vectors to match (Default value = 1).
        :param table_index: Index of the classify table.
            (Default value = 0xFFFFFFFF)
        :param nbuckets: Number of buckets when adding a table.
            (Default value = 2)
        :param memory_size: Memory size when adding a table.
            (Default value = 2097152)
        :param skip_n_vectors: Number of skip vectors (Default value = 0).
        :param next_table_index: Index of next table.
            (Default value = 0xFFFFFFFF)
        :param miss_next_index: Index of miss table.
            (Default value = 0xFFFFFFFF)
        :param current_data_flag: Option to use current node's packet payload
            as the starting point from where packets are classified.
            This option is only valid for L2/L3 input ACL for now.
            0: by default, classify data from the buffer's start location
            1: classify packets from VPP node's current data pointer.
        :param current_data_offset: A signed value to shift the start location
            of the packet to be classified.
            For example, if input IP ACL node is used, L2 header's first byte
            can be accessible by configuring current_data_offset to -14
            if there is no vlan tag.
            This is valid only if current_data_flag is set to 1.
            (Default value = 0)
        :type node: dict
        :type is_add: int
        :type mask: str
        :type match_n_vectors: int
        :type table_index: int
        :type nbuckets: int
        :type memory_size: int
        :type skip_n_vectors: int
        :type next_table_index: int
        :type miss_next_index: int
        :type current_data_flag: int
        :type current_data_offset: int
        :returns: (table_index, skip_n, match_n)
            table_index: Classify table index.
            skip_n: Number of skip vectors.
            match_n: Number of match vectors.
        :rtype: tuple(int, int, int)
        """
        mask_len = ((len(mask) - 1) / 16 + 1) * 16
        mask = mask + '\0' * (mask_len - len(mask))

        args = dict(
            is_add=is_add,
            table_index=table_index,
            nbuckets=nbuckets,
            memory_size=memory_size,
            skip_n_vectors=skip_n_vectors,
            match_n_vectors=match_n_vectors,
            next_table_index=next_table_index,
            miss_next_index=miss_next_index,
            current_data_flag=current_data_flag,
            current_data_offset=current_data_offset,
            mask_len=mask_len,
            mask=mask
        )

        cmd = 'classify_add_del_table'
        err_msg = "Failed to create a classify table on host {host}".format(
            host=node['host'])

        with PapiSocketExecutor(node) as papi_exec:
            reply = papi_exec.add(cmd, **args).get_reply(err_msg)

        return int(reply["new_table_index"]), int(reply["skip_n_vectors"]),\
            int(reply["match_n_vectors"])

    @staticmethod
    def _classify_add_del_session(node, is_add, table_index, match,
                                  opaque_index=0xFFFFFFFF,
                                  hit_next_index=0xFFFFFFFF, advance=0,
                                  action=0, metadata=0):
        """Add or delete a classify session.

        :param node: VPP node to create classify session.
        :param is_add: If 1 the session is added, if 0 the session is deleted.
        :param table_index: Index of the table to add/del the session.
        :param match: For add, match value for session, required, needs to
            include bytes in front with length of skip_n_vectors of target table
            times sizeof (u32x4) (values of those bytes will be ignored).
        :param opaque_index: For add, opaque_index of new session.
            (Default value = 0xFFFFFFFF)
        :param hit_next_index: For add, hit_next_index of new session.
            (Default value = 0xFFFFFFFF)
        :param advance: For add, advance value for session. (Default value = 0)
        :param action: 0: No action (by default) metadata is not used.
            1: Classified IP packets will be looked up from the specified ipv4
               fib table (configured by metadata as VRF id).
               Only valid for L3 input ACL node
            2: Classified IP packets will be looked up from the specified ipv6
               fib table (configured by metadata as VRF id).
               Only valid for L3 input ACL node
            3: Classified packet will be steered to source routig policy of
               given index (in metadata).
               This is only valid for IPv6 packets redirected to a source
               routing node.
        :param metadata: Valid only if action != 0
            VRF id if action is 1 or 2. SR policy index if action is 3.
            (Default value = 0)
        :type node: dict
        :type is_add: int
        :type table_index: int
        :type match: str
        :type opaque_index: int
        :type hit_next_index: int
        :type advance: int
        :type action: int
        :type metadata: int
        """

        match_len = ((len(match) - 1) / 16 + 1) * 16
        match = match + '\0' * (match_len - len(match))
        args = dict(
            is_add=is_add,
            table_index=table_index,
            hit_next_index=hit_next_index,
            opaque_index=opaque_index,
            advance=advance,
            action=action,
            metadata=metadata,
            match_len=match_len,
            match=match
        )
        cmd = 'classify_add_del_session'
        err_msg = "Failed to create a classify session on host {host}".format(
            host=node['host'])

        with PapiSocketExecutor(node) as papi_exec:
            papi_exec.add(cmd, **args).get_reply(err_msg)

    @staticmethod
    def _macip_acl_add(node, rules, tag=""):
        """Add MACIP ACL.

        :param node: VPP node to add MACIP ACL.
        :param rules: List of rules for given ACL.
        :param tag: ACL tag.
        :type node: dict
        :type rules: list
        :type tag: str
        """
        cmd = "macip_acl_add"
        args = dict(
            r=rules,
            count=len(rules),
            tag=tag
        )

        err_msg = "Failed to create a classify session on host {host}".format(
            host=node['host'])

        with PapiSocketExecutor(node) as papi_exec:
            papi_exec.add(cmd, **args).get_reply(err_msg)

    @staticmethod
    def _acl_interface_set_acl_list(node, sw_if_index, acl_type, acls):
        """Set ACL list for interface.

        :param node: VPP node to set ACL list for interface.
        :param sw_if_index: sw_if_index of the used interface.
        :param acl_type: Type of ACL(s) - input or output.
        :param acls: List of ACLs.
        :type node: dict
        :type sw_if_index: int
        :type acl_type: str
        :type acls: list
        """
        cmd = "acl_interface_set_acl_list"
        n_input = len(acls) if acl_type == "input" else 0
        args = dict(
            sw_if_index=sw_if_index,
            acls=acls,
            n_input=n_input,
            count=len(acls)
        )

        err_msg = "Failed to set acl list for interface {idx} on host {host}".\
            format(idx=sw_if_index, host=node['host'])

        with PapiSocketExecutor(node) as papi_exec:
            papi_exec.add(cmd, **args).get_reply(err_msg)

    @staticmethod
    def _acl_add_replace(node, acl_idx, rules, tag=""):
        """ Add/replace ACLs.

        :param node: VPP node to add MACIP ACL.
        :param acl_idx: ACL index.
        :param rules: List of rules for given ACL.
        :param tag: ACL tag.
        :type node: dict
        :type acl_idx: int
        :type rules: list
        :type tag: str
        """
        cmd = "acl_add_replace"
        args = dict(
            tag=tag,
            acl_index=4294967295 if acl_idx is None else acl_idx,
            count=len(rules),
            r=rules
        )

        err_msg = "Failed to add/replace acls on host {host}".format(
            host=node['host'])

        with PapiSocketExecutor(node) as papi_exec:
            papi_exec.add(cmd, **args).get_reply(err_msg)

    @staticmethod
    def vpp_creates_classify_table_l3(node, ip_version, direction, ip_addr):
        """Create classify table for IP address filtering.

        :param node: VPP node to create classify table.
        :param ip_version: Version of IP protocol.
        :param direction: Direction of traffic - src/dst.
        :param ip_addr: IPv4 or Ipv6 (depending on the parameter 'ip_version')
            address.
        :type node: dict
        :type ip_version: str
        :type direction: str
        :type ip_addr: str
        :returns: (table_index, skip_n, match_n)
            table_index: Classify table index.
            skip_n: Number of skip vectors.
            match_n: Number of match vectors.
        :rtype: tuple(int, int, int)
        :raises ValueError: If the parameters 'ip_version' or 'direction' have
            incorrect values.
        """
        mask_f = dict(
            ip4=Classify._build_ip_mask,
            ip6=Classify._build_ip6_mask
        )
        if ip_version == "ip4" or ip_version == "ip6":
            ip_addr = binascii.hexlify(ip_address(unicode(ip_addr)).packed)
        else:
            raise ValueError("IP version {ver} is not supported.".
                             format(ver=ip_version))

        if direction == "src":
            mask = mask_f[ip_version](src_ip=ip_addr)
        elif direction == "dst":
            mask = mask_f[ip_version](dst_ip=ip_addr)
        else:
            raise ValueError("Direction {dir} is not supported.".
                             format(dir=direction))

        return Classify._classify_add_del_table(
            node,
            is_add=1,
            mask=binascii.unhexlify(mask),
            match_n_vectors=(len(mask) - 1) // 32 + 1
        )

    @staticmethod
    def vpp_creates_classify_table_l2(node, direction, mac=""):
        """Create classify table for MAC address filtering.

        :param node: VPP node to create classify table.
        :param direction: Direction of traffic - src/dst.
        :param mac: Source or destination (depending on the parameter
            'direction') MAC address.
        :type node: dict
        :type direction: str
        :type mac: str
        :returns: (table_index, skip_n, match_n)
            table_index: Classify table index.
            skip_n: Number of skip vectors.
            match_n: Number of match vectors.
        :rtype: tuple(int, int, int)
        :raises ValueError: If the parameter 'direction' has incorrect value.
        """
        if direction == "src":
            mask = Classify._build_mac_mask(src_mac=mac)
        elif direction == "dst":
            mask = Classify._build_mac_mask(dst_mac=mac)
        else:
            raise ValueError("Direction {dir} is not supported.".
                             format(dir=direction))

        return Classify._classify_add_del_table(
            node,
            is_add=1,
            mask=binascii.unhexlify(mask),
            match_n_vectors=(len(mask) - 1) // 32 + 1
        )

    @staticmethod
    def vpp_creates_classify_table_hex(node, hex_mask):
        """Create classify table with hex mask.

        :param node: VPP node to create classify table based on hex mask.
        :param hex_mask: Classify hex mask.
        :type node: dict
        :type hex_mask: str
        :returns: (table_index, skip_n, match_n)
            table_index: Classify table index.
            skip_n: Number of skip vectors.
            match_n: Number of match vectors.
        :rtype: tuple(int, int, int)
        """
        return Classify._classify_add_del_table(
            node,
            is_add=1,
            mask=binascii.unhexlify(hex_mask),
            match_n_vectors=(len(hex_mask) - 1) // 32 + 1
        )

    @staticmethod
    def vpp_configures_classify_session_l3(node, acl_method, table_index,
                                           ip_version, direction, address):
        """Configuration of classify session for IP address filtering.

        :param node: VPP node to setup classify session.
        :param acl_method: ACL method - deny/permit.
        :param table_index: Classify table index.
        :param ip_version: Version of IP protocol.
        :param direction: Direction of traffic - src/dst.
        :param address: IPv4 or IPv6 address.
        :type node: dict
        :type acl_method: str
        :type table_index: int
        :type ip_version: str
        :type direction: str
        :type address: str
        :raises ValueError: If the parameter 'direction' has incorrect value.
        """
        match_f = dict(
            ip4=Classify._build_ip_match,
            ip6=Classify._build_ip6_match
        )
        if direction == "src":
            match = match_f[ip_version](src_ip=address)
        elif direction == "dst":
            match = match_f[ip_version](dst_ip=address)
        else:
            raise ValueError("Direction {dir} is not supported.".
                             format(dir=direction))
        action = dict(
            permit=0,
            deny=1
        )
        Classify._classify_add_del_session(
            node,
            is_add=1,
            table_index=table_index,
            match=binascii.unhexlify(match),
            action=action[acl_method])

    @staticmethod
    def vpp_configures_classify_session_l2(node, acl_method, table_index,
                                           direction, address):
        """Configuration of classify session for MAC address filtering.

        :param node: VPP node to setup classify session.
        :param acl_method: ACL method - deny/permit.
        :param table_index: Classify table index.
        :param direction: Direction of traffic - src/dst.
        :param address: MAC address.
        :type node: dict
        :type acl_method: str
        :type table_index: int
        :type direction: str
        :type address: str
        :raises ValueError: If the parameter 'direction' has incorrect value.
        """
        if direction == "src":
            match = Classify._build_mac_match(src_mac=address)
        elif direction == "dst":
            match = Classify._build_mac_match(dst_mac=address)
        else:
            raise ValueError("Direction {dir} is not supported.".
                             format(dir=direction))
        action = dict(
            permit=0,
            deny=1
        )
        Classify._classify_add_del_session(
            node,
            is_add=1,
            table_index=table_index,
            match=binascii.unhexlify(match),
            action=action[acl_method])

    @staticmethod
    def vpp_configures_classify_session_hex(node, acl_method, table_index,
                                            hex_value):
        """Configuration of classify session with hex value.

        :param node: VPP node to setup classify session.
        :param acl_method: ACL method - deny/permit.
        :param table_index: Classify table index.
        :param hex_value: Classify hex value.
        :type node: dict
        :type acl_method: str
        :type table_index: int
        :type hex_value: str
        """
        action = dict(
            permit=0,
            deny=1
        )
        Classify._classify_add_del_session(
            node,
            is_add=1,
            table_index=table_index,
            match=binascii.unhexlify(hex_value),
            action=action[acl_method])

    @staticmethod
    def compute_classify_hex_mask(ip_version, protocol, direction):
        """Compute classify hex mask for TCP or UDP packet matching.

        :param ip_version: Version of IP protocol.
        :param protocol: Type of protocol.
        :param direction: Traffic direction.
        :type ip_version: str
        :type protocol: str
        :type direction: str
        :returns: Classify hex mask.
        :rtype: str
        :raises ValueError: If protocol is not TCP or UDP.
        :raises ValueError: If direction is not source or destination or
            source + destination.
        """
        if protocol in ('TCP', 'UDP'):
            base_mask = Classify._compute_base_mask(ip_version)

            if direction == 'source':
                return base_mask + 'FFFF0000'
            elif direction == 'destination':
                return base_mask + '0000FFFF'
            elif direction == 'source + destination':
                return base_mask + 'FFFFFFFF'
            else:
                raise ValueError("Invalid direction!")
        else:
            raise ValueError("Invalid protocol!")

    @staticmethod
    def compute_classify_hex_value(hex_mask, source_port, destination_port):
        """Compute classify hex value for TCP or UDP packet matching.

        :param hex_mask: Classify hex mask.
        :param source_port: Source TCP/UDP port.
        :param destination_port: Destination TCP/UDP port.
        :type hex_mask: str
        :type source_port: str
        :type destination_port: str
        :returns: Classify hex value.
        :rtype: str
        """
        source_port_hex = Classify._port_convert(source_port)
        destination_port_hex = Classify._port_convert(destination_port)

        return hex_mask[:-8] + source_port_hex + destination_port_hex

    @staticmethod
    def _port_convert(port):
        """Convert port number for classify hex table format.

        :param port: TCP/UDP port number.
        :type port: str
        :returns: TCP/UDP port number in 4-digit hexadecimal format.
        :rtype: str
        """
        return '{0:04x}'.format(int(port))

    @staticmethod
    def _compute_base_mask(ip_version):
        """Compute base classify hex mask based on IP version.

        :param ip_version: Version of IP protocol.
        :type ip_version: str
        :returns: Base hex mask.
        :rtype: str
        """
        if ip_version == 'ip4':
            return 68 * '0'
            # base value of classify hex table for IPv4 TCP/UDP ports
        elif ip_version == 'ip6':
            return 108 * '0'
            # base value of classify hex table for IPv6 TCP/UDP ports
        else:
            raise ValueError("Invalid IP version!")

    @staticmethod
    def get_classify_table_data(node, table_index):
        """Retrieve settings for classify table by ID.

        :param node: VPP node to retrieve classify data from.
        :param table_index: Index of a specific classify table.
        :type node: dict
        :type table_index: int
        :returns: Classify table settings.
        :rtype: dict
        """
        cmd = 'classify_table_info'
        err_msg = "Failed to get 'classify_table_info' on host {host}".format(
            host=node['host'])
        args = dict(
            table_id=int(table_index)
        )
        with PapiSocketExecutor(node) as papi_exec:
            reply = papi_exec.add(cmd, **args).get_reply(err_msg)
        return reply

    @staticmethod
    def get_classify_session_data(node, table_index):
        """Retrieve settings for all classify sessions in a table.

        :param node: VPP node to retrieve classify data from.
        :param table_index: Index of a classify table.
        :type node: dict
        :type table_index: int
        :returns: List of classify session settings.
        :rtype: list or dict
        """
        cmd = "classify_session_dump"
        args = dict(
            table_id=int(table_index)
        )
        with PapiSocketExecutor(node) as papi_exec:
            details = papi_exec.add(cmd, **args).get_details()

        return details

    @staticmethod
    def vpp_log_plugin_acl_settings(node):
        """Retrieve configured settings from the ACL plugin and write to robot
        log.

        :param node: VPP node.
        :type node: dict
        """
        PapiSocketExecutor.dump_and_log(node, ["acl_dump", ])

    @staticmethod
    def vpp_log_plugin_acl_interface_assignment(node):
        """Retrieve interface assignment from the ACL plugin and write to robot
        log.

        :param node: VPP node.
        :type node: dict
        """
        PapiSocketExecutor.dump_and_log(node, ["acl_interface_list_dump", ])

    @staticmethod
    def set_acl_list_for_interface(node, interface, acl_type, acl_idx=None):
        """Set the list of input or output ACLs applied to the interface. It
        unapplies any previously applied ACLs.

        :param node: VPP node to set ACL on.
        :param interface: Interface name or sw_if_index.
        :param acl_type: Type of ACL(s) - input or output.
        :param acl_idx: Index(ies) of ACLs to be applied on the interface.
        :type node: dict
        :type interface: str or int
        :type acl_type: str
        :type acl_idx: list
        """
        if isinstance(interface, basestring):
            sw_if_index = Topology.get_interface_sw_index(node, interface)
        else:
            sw_if_index = int(interface)

        acls = acl_idx if isinstance(acl_idx, list) else list()

        Classify._acl_interface_set_acl_list(node=node,
                                             sw_if_index=sw_if_index,
                                             acl_type=acl_type,
                                             acls=acls)

    @staticmethod
    def add_replace_acl_multi_entries(node, acl_idx=None, rules=None, tag=""):
        """Add a new ACL or replace the existing one. To replace an existing
        ACL, pass the ID of this ACL.

        :param node: VPP node to set ACL on.
        :param acl_idx: ID of ACL. (Optional)
        :param rules: Required rules. (Optional)
        :param tag: ACL tag (Optional).
        :type node: dict
        :type acl_idx: int
        :type rules: str
        :type tag: str
        """
        reg_ex_src_ip = re.compile(r'(src [0-9a-fA-F.:/\d{1,2}]*)')
        reg_ex_dst_ip = re.compile(r'(dst [0-9a-fA-F.:/\d{1,2}]*)')
        reg_ex_sport = re.compile(r'(sport \d{1,5})')
        reg_ex_dport = re.compile(r'(dport \d{1,5})')
        reg_ex_proto = re.compile(r'(proto \d{1,5})')

        acl_rules = list()
        for rule in rules.split(", "):
            acl_rule = dict()
            acl_rule["is_permit"] = 1 if "permit" in rule else 0
            acl_rule["is_ipv6"] = 1 if "ipv6" in rule else 0

            groups = re.search(reg_ex_src_ip, rule)
            if groups:
                grp = groups.group(1).split(' ')[1].split('/')
                acl_rule["src_ip_addr"] = ip_address(unicode(grp[0])).packed
                acl_rule["src_ip_prefix_len"] = int(grp[1])

            groups = re.search(reg_ex_dst_ip, rule)
            if groups:
                grp = groups.group(1).split(' ')[1].split('/')
                acl_rule["dst_ip_addr"] = ip_address(unicode(grp[0])).packed
                acl_rule["dst_ip_prefix_len"] = int(grp[1])

            groups = re.search(reg_ex_sport, rule)
            if groups:
                port = int(groups.group(1).split(' ')[1])
                acl_rule["srcport_or_icmptype_first"] = port
                acl_rule["srcport_or_icmptype_last"] = port
            else:
                acl_rule["srcport_or_icmptype_first"] = 0
                acl_rule["srcport_or_icmptype_last"] = 65535

            groups = re.search(reg_ex_dport, rule)
            if groups:
                port = int(groups.group(1).split(' ')[1])
                acl_rule["dstport_or_icmpcode_first"] = port
                acl_rule["dstport_or_icmpcode_last"] = port
            else:
                acl_rule["dstport_or_icmpcode_first"] = 0
                acl_rule["dstport_or_icmpcode_last"] = 65535

            groups = re.search(reg_ex_proto, rule)
            if groups:
                proto = int(groups.group(1).split(' ')[1])
                acl_rule["proto"] = proto
            else:
                acl_rule["proto"] = 0

            acl_rules.append(acl_rule)

        Classify._acl_add_replace(
            node, acl_idx=acl_idx, rules=acl_rules, tag=tag)

    @staticmethod
    def add_macip_acl_multi_entries(node, rules=""):
        """Add a new MACIP ACL.

        :param node: VPP node to set MACIP ACL on.
        :param rules: Required MACIP rules.
        :type node: dict
        :type rules: str
        """
        reg_ex_ip = re.compile(r'(ip [0-9a-fA-F.:/\d{1,2}]*)')
        reg_ex_mac = re.compile(r'(mac \S\S:\S\S:\S\S:\S\S:\S\S:\S\S)')
        reg_ex_mask = re.compile(r'(mask \S\S:\S\S:\S\S:\S\S:\S\S:\S\S)')

        acl_rules = list()
        for rule in rules.split(", "):
            acl_rule = dict()
            acl_rule["is_permit"] = 1 if "permit" in rule else 0
            acl_rule["is_ipv6"] = 1 if "ipv6" in rule else 0

            groups = re.search(reg_ex_mac, rule)
            if groups:
                mac = groups.group(1).split(' ')[1].replace(':', '')
                acl_rule["src_mac"] = unicode(mac)

            groups = re.search(reg_ex_mask, rule)
            if groups:
                mask = groups.group(1).split(' ')[1].replace(':', '')
                acl_rule["src_mac_mask"] = unicode(mask)

            groups = re.search(reg_ex_ip, rule)
            if groups:
                grp = groups.group(1).split(' ')[1].split('/')
                acl_rule["src_ip_addr"] = ip_address(unicode(grp[0])).packed
                acl_rule["src_ip_prefix_len"] = int(grp[1])

            acl_rules.append(acl_rule)

        Classify._macip_acl_add(node=node, rules=acl_rules)

    @staticmethod
    def vpp_log_macip_acl_settings(node):
        """Retrieve configured MACIP settings from the ACL plugin and write to
        robot log.

        :param node: VPP node.
        :type node: dict
        """
        PapiSocketExecutor.dump_and_log(node, ["macip_acl_dump", ])

    @staticmethod
    def add_del_macip_acl_interface(node, interface, action, acl_idx):
        """Apply/un-apply the MACIP ACL to/from a given interface.

        :param node: VPP node to set MACIP ACL on.
        :param interface: Interface name or sw_if_index.
        :param action: Required action - add or del.
        :param acl_idx: ACL index to be applied on the interface.
        :type node: dict
        :type interface: str or int
        :type action: str
        :type acl_idx: str or int
        :raises RuntimeError: If unable to set MACIP ACL for the interface.
        """
        if isinstance(interface, basestring):
            sw_if_index = Topology.get_interface_sw_index(node, interface)
        else:
            sw_if_index = interface

        is_add = 1 if action == "add" else 0

        cmd = 'macip_acl_interface_add_del'
        err_msg = "Failed to get 'macip_acl_interface' on host {host}".format(
            host=node['host'])
        args = dict(
            is_add=is_add,
            sw_if_index=int(sw_if_index),
            acl_index=int(acl_idx)
        )
        with PapiSocketExecutor(node) as papi_exec:
            papi_exec.add(cmd, **args).get_reply(err_msg)

    @staticmethod
    def vpp_log_macip_acl_interface_assignment(node):
        """Get interface list and associated MACIP ACLs and write to robot log.

        :param node: VPP node.
        :type node: dict
        """
        cmd = 'macip_acl_interface_get'
        err_msg = "Failed to get 'macip_acl_interface' on host {host}".format(
            host=node['host'])
        with PapiSocketExecutor(node) as papi_exec:
            reply = papi_exec.add(cmd).get_reply(err_msg)
        logger.info(reply)
