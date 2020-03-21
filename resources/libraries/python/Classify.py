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

"""Classify utilities library."""

import re

from ipaddress import ip_address

from robot.api import logger

from resources.libraries.python.Constants import Constants
from resources.libraries.python.InterfaceUtil import InterfaceUtil
from resources.libraries.python.IPUtil import IPUtil
from resources.libraries.python.PapiExecutor import PapiSocketExecutor


class Classify:
    """Classify utilities."""

    @staticmethod
    def _build_mac_mask(dst_mac=u"", src_mac=u"", ether_type=u""):
        """Build MAC ACL mask data in bytes format.

        :param dst_mac: Source MAC address <0-ffffffffffff>.
        :param src_mac: Destination MAC address <0-ffffffffffff>.
        :param ether_type: Ethernet type <0-ffff>.
        :type dst_mac: str
        :type src_mac: str
        :type ether_type: str
        :returns MAC ACL mask in bytes format.
        :rtype: bytes
        """
        return bytes.fromhex(
            f"{dst_mac.replace(u':', u'')!s:0>12}"
            f"{src_mac.replace(u':', u'')!s:0>12}"
            f"{ether_type!s:0>4}"
        ).rstrip(b'\0')

    @staticmethod
    def _build_ip_mask(
            proto=u"", src_ip=u"", dst_ip=u"", src_port=u"", dst_port=u""):
        """Build IP ACL mask data in bytes format.

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
        :returns: IP mask in bytes format.
        :rtype: bytes
        """
        return bytes.fromhex(
            f"{proto!s:0>20}{src_ip!s:0>12}{dst_ip!s:0>8}{src_port!s:0>4}"
            f"{dst_port!s:0>4}"
        ).rstrip(b'\0')

    @staticmethod
    def _build_ip6_mask(
            next_hdr=u"", src_ip=u"", dst_ip=u"", src_port=u"", dst_port=u""):
        """Build IPv6 ACL mask data in bytes format.

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
        :returns: IPv6 ACL mask in bytes format.
        :rtype: bytes
        """
        return bytes.fromhex(
            f"{next_hdr!s:0>14}{src_ip!s:0>34}{dst_ip!s:0>32}{src_port!s:0>4}"
            f"{dst_port!s:0>4}"
        ).rstrip(b'\0')

    @staticmethod
    def _build_mac_match(dst_mac=u"", src_mac=u"", ether_type=u""):
        """Build MAC ACL match data in  bytes format.

        :param dst_mac: Source MAC address <x:x:x:x:x:x>.
        :param src_mac: Destination MAC address <x:x:x:x:x:x>.
        :param ether_type: Ethernet type <0-ffff>.
        :type dst_mac: str
        :type src_mac: str
        :type ether_type: str
        :returns: MAC ACL match data in bytes format.
        :rtype: bytes
        """
        return bytes.fromhex(
            f"{dst_mac.replace(u':', u'')!s:0>12}"
            f"{src_mac.replace(u':', u'')!s:0>12}"
            f"{ether_type!s:0>4}"
        ).rstrip(b'\0')

    @staticmethod
    def _build_ip_match(
            proto=0, src_ip=4*b"\0", dst_ip=4*b"\0", src_port=0, dst_port=0):
        """Build IP ACL match data in bytes format.

        :param proto: Protocol number with valid option "x".
        :param src_ip: Source ip address in packed format.
        :param dst_ip: Destination ip address in packed format.
        :param src_port: Source port number "x".
        :param dst_port: Destination port number "x".
        :type proto: int
        :type src_ip: bytes
        :type dst_ip: bytes
        :type src_port: int
        :type dst_port: int
        :returns: IP ACL match data in byte-string format.
        :rtype: str
        """
        return bytes.fromhex(
            f"{hex(proto)[2:]!s:0>20}{src_ip.hex()!s:0>12}{dst_ip.hex()!s:0>8}"
            f"{hex(src_port)[2:]!s:0>4}{hex(dst_port)[2:]!s:0>4}"
        ).rstrip(b'\0')

    @staticmethod
    def _build_ip6_match(
            next_hdr=0, src_ip=16*b"\0", dst_ip=16*b"\0", src_port=0,
            dst_port=0):
        """Build IPv6 ACL match data in byte-string format.

        :param next_hdr: Next header number with valid option "x".
        :param src_ip: Source ip6 address in packed format.
        :param dst_ip: Destination ip6 address in packed format.
        :param src_port: Source port number "x".
        :param dst_port: Destination port number "x".
        :type next_hdr: int
        :type src_ip: bytes
        :type dst_ip: bytes
        :type src_port: int
        :type dst_port: int
        :returns: IPv6 ACL match data in bytes format.
        :rtype: bytes
        """
        return bytes.fromhex(
            f"{hex(next_hdr)[2:]!s:0>14}{src_ip.hex()!s:0>34}"
            f"{dst_ip.hex()!s:0>32}{hex(src_port)[2:]!s:0>4}"
            f"{hex(dst_port)[2:]!s:0>4}"
        ).rstrip(b'\0')

    @staticmethod
    def _classify_add_del_table(
            node, is_add, mask, match_n_vectors=Constants.BITWISE_NON_ZERO,
            table_index=Constants.BITWISE_NON_ZERO, nbuckets=2,
            memory_size=2097152, skip_n_vectors=Constants.BITWISE_NON_ZERO,
            next_table_index=Constants.BITWISE_NON_ZERO,
            miss_next_index=Constants.BITWISE_NON_ZERO,
            current_data_flag=0, current_data_offset=0):
        """Add or delete a classify table.

        :param node: VPP node to create classify table.
        :param is_add: If True the table is added, if False table is deleted.
        :param mask: ACL mask in hexstring format.
        :param match_n_vectors: Number of vectors to match (Default value = ~0).
        :param table_index: Index of the classify table. (Default value = ~0)
        :param nbuckets: Number of buckets when adding a table.
            (Default value = 2)
        :param memory_size: Memory size when adding a table.
            (Default value = 2097152)
        :param skip_n_vectors: Number of skip vectors (Default value = ~0).
        :param next_table_index: Index of next table. (Default value = ~0)
        :param miss_next_index: Index of miss table. (Default value = ~0)
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
        :type is_add: bool
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
        cmd = u"classify_add_del_table"
        args = dict(
            is_add=is_add,
            del_chain=False,
            table_index=table_index,
            nbuckets=nbuckets,
            memory_size=memory_size,
            skip_n_vectors=skip_n_vectors,
            match_n_vectors=match_n_vectors,
            next_table_index=next_table_index,
            miss_next_index=miss_next_index,
            current_data_flag=current_data_flag,
            current_data_offset=current_data_offset,
            mask_len=len(mask),
            mask=mask
        )
        err_msg = f"Failed to create a classify table on host {node[u'host']}"

        with PapiSocketExecutor(node) as papi_exec:
            reply = papi_exec.add(cmd, **args).get_reply(err_msg)

        return int(reply[u"new_table_index"]), int(reply[u"skip_n_vectors"]),\
            int(reply[u"match_n_vectors"])

    @staticmethod
    def _classify_add_del_session(
            node, is_add, table_index, match,
            opaque_index=Constants.BITWISE_NON_ZERO,
            hit_next_index=Constants.BITWISE_NON_ZERO, advance=0,
            action=0, metadata=0):
        """Add or delete a classify session.

        :param node: VPP node to create classify session.
        :param is_add: If True the session is added, if False the session
            is deleted.
        :param table_index: Index of the table to add/del the session.
        :param match: For add, match value for session, required, needs to
            include bytes in front with length of skip_n_vectors of target table
            times sizeof (u32x4) (values of those bytes will be ignored).
        :param opaque_index: For add, opaque_index of new session.
            (Default value = ~0)
        :param hit_next_index: For add, hit_next_index of new session.
            (Default value = ~0)
        :param advance: For add, advance value for session. (Default value = 0)
        :param action: 0: No action (by default) metadata is not used.
            1: Classified IP packets will be looked up from the specified ipv4
               fib table (configured by metadata as VRF id).
               Only valid for L3 input ACL node
            2: Classified IP packets will be looked up from the specified ipv6
               fib table (configured by metadata as VRF id).
               Only valid for L3 input ACL node
            3: Classified packet will be steered to source routing policy of
               given index (in metadata).
               This is only valid for IPv6 packets redirected to a source
               routing node.
        :param metadata: Valid only if action != 0. VRF id if action is 1 or 2.
            SR policy index if action is 3. (Default value = 0)
        :type node: dict
        :type is_add: bool
        :type table_index: int
        :type match: bytes
        :type opaque_index: int
        :type hit_next_index: int
        :type advance: int
        :type action: int
        :type metadata: int
        """
        cmd = u"classify_add_del_session"
        args = dict(
            is_add=is_add,
            table_index=table_index,
            hit_next_index=hit_next_index,
            opaque_index=opaque_index,
            advance=advance,
            action=action,
            metadata=metadata,
            match_len=len(match),
            match=match
        )
        err_msg = f"Failed to create a classify session on host {node[u'host']}"

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
        cmd = u"macip_acl_add"
        args = dict(
            r=rules,
            count=len(rules),
            tag=tag
        )

        err_msg = f"Failed to add MACIP ACL on host {node[u'host']}"

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
        cmd = u"acl_interface_set_acl_list"
        args = dict(
            sw_if_index=sw_if_index,
            acls=acls,
            n_input=len(acls) if acl_type == u"input" else 0,
            count=len(acls)
        )

        err_msg = f"Failed to set acl list for interface {sw_if_index} " \
            f"on host {node[u'host']}"

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
        cmd = u"acl_add_replace"
        args = dict(
            tag=tag,
            acl_index=4294967295 if acl_idx is None else acl_idx,
            count=len(rules),
            r=rules
        )

        err_msg = f"Failed to add/replace ACLs on host {node[u'host']}"

        with PapiSocketExecutor(node) as papi_exec:
            papi_exec.add(cmd, **args).get_reply(err_msg)

    @staticmethod
    def vpp_creates_classify_table_l3(node, ip_version, direction, netmask):
        """Create classify table for IP address filtering.

        :param node: VPP node to create classify table.
        :param ip_version: Version of IP protocol.
        :param direction: Direction of traffic - src/dst.
        :param netmask: IPv4 or Ipv6 (depending on the parameter 'ip_version')
            netmask (decimal, e.g. 255.255.255.255).
        :type node: dict
        :type ip_version: str
        :type direction: str
        :type netmask: str
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

        if ip_version in (u"ip4", u"ip6"):
            netmask = ip_address(netmask).packed
        else:
            raise ValueError(f"IP version {ip_version} is not supported.")

        if direction == u"src":
            mask = mask_f[ip_version](src_ip=netmask.hex())
        elif direction == u"dst":
            mask = mask_f[ip_version](dst_ip=netmask.hex())
        else:
            raise ValueError(f"Direction {direction} is not supported.")

        # Add l2 ethernet header to mask
        mask = 14 * b'\0' + mask

        # Get index of the first significant mask octet
        i = len(mask) - len(mask.lstrip(b'\0'))

        # Compute skip_n parameter
        skip_n = i // 16
        # Remove octets to be skipped from the mask
        mask = mask[skip_n*16:]
        # Pad mask to an even multiple of the vector size
        mask = mask + (16 - len(mask) % 16 if len(mask) % 16 else 0) * b'\0'
        # Compute match_n parameter
        match_n = len(mask) // 16

        return Classify._classify_add_del_table(
            node,
            is_add=True,
            mask=mask,
            match_n_vectors=match_n,
            skip_n_vectors=skip_n
        )

    @staticmethod
    def vpp_configures_classify_session_l3(
            node, acl_method, table_index, skip_n, match_n, ip_version,
            direction, address, hit_next_index=None,
            opaque_index=Constants.BITWISE_NON_ZERO, action=0, metadata=0):
        """Configuration of classify session for IP address filtering.

        :param node: VPP node to setup classify session.
        :param acl_method: ACL method - deny/permit.
        :param table_index: Classify table index.
        :param skip_n: Number of skip vectors.
        :param match_n: Number of vectors to match.
        :param ip_version: Version of IP protocol.
        :param direction: Direction of traffic - src/dst.
        :param address: IPv4 or IPv6 address.
        :param hit_next_index: hit_next_index of new session.
            (Default value = None)
        :param opaque_index: opaque_index of new session. (Default value = ~0)
        :param action: 0: No action (by default) metadata is not used.
            1: Classified IP packets will be looked up from the specified ipv4
               fib table (configured by metadata as VRF id).
               Only valid for L3 input ACL node
            2: Classified IP packets will be looked up from the specified ipv6
               fib table (configured by metadata as VRF id).
               Only valid for L3 input ACL node
            3: Classified packet will be steered to source routing policy of
               given index (in metadata).
               This is only valid for IPv6 packets redirected to a source
               routing node.
        :param metadata: Valid only if action != 0. VRF id if action is 1 or 2.
            SR policy index if action is 3. (Default value = 0)
        :type node: dict
        :type acl_method: str
        :type table_index: int
        :type skip_n: int
        :type match_n: int
        :type ip_version: str
        :type direction: str
        :type address: str
        :type hit_next_index: int
        :type opaque_index: int
        :type action: int
        :type metadata: int
        :raises ValueError: If the parameter 'direction' has incorrect value.
        """
        match_f = dict(
            ip4=Classify._build_ip_match,
            ip6=Classify._build_ip6_match
        )
        acl_hit_next_index = dict(
            permit=Constants.BITWISE_NON_ZERO,
            deny=0
        )

        if ip_version in (u"ip4", u"ip6"):
            address = ip_address(address).packed
        else:
            raise ValueError(f"IP version {ip_version} is not supported.")

        if direction == u"src":
            match = match_f[ip_version](src_ip=address)
        elif direction == u"dst":
            match = match_f[ip_version](dst_ip=address)
        else:
            raise ValueError(f"Direction {direction} is not supported.")

        # Prepend match with l2 ethernet header part
        match = 14 * b'\0' + match

        # Pad match to match skip_n_vector + match_n_vector size
        match = match + ((match_n + skip_n) * 16 - len(match)
                         if len(match) < (match_n + skip_n) * 16
                         else 0) * b'\0'

        Classify._classify_add_del_session(
            node,
            is_add=True,
            table_index=table_index,
            hit_next_index=hit_next_index if hit_next_index is not None
            else acl_hit_next_index[acl_method],
            opaque_index=opaque_index,
            match=match,
            action=action,
            metadata=metadata
        )

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
        cmd = u"classify_table_info"
        err_msg = f"Failed to get 'classify_table_info' on host {node[u'host']}"
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
        cmd = u"classify_session_dump"
        args = dict(
            table_id=int(table_index)
        )
        with PapiSocketExecutor(node) as papi_exec:
            details = papi_exec.add(cmd, **args).get_details()

        return details

    @staticmethod
    def show_classify_tables_verbose(node):
        """Show classify tables verbose.

        :param node: Topology node.
        :type node: dict
        :returns: Classify tables verbose data.
        :rtype: str
        """
        return PapiSocketExecutor.run_cli_cmd(
            node, u"show classify tables verbose"
        )

    @staticmethod
    def vpp_log_plugin_acl_settings(node):
        """Retrieve configured settings from the ACL plugin and write to robot
        log.

        :param node: VPP node.
        :type node: dict
        """
        PapiSocketExecutor.dump_and_log(node, [u"acl_dump", ])

    @staticmethod
    def vpp_log_plugin_acl_interface_assignment(node):
        """Retrieve interface assignment from the ACL plugin and write to robot
        log.

        :param node: VPP node.
        :type node: dict
        """
        PapiSocketExecutor.dump_and_log(node, [u"acl_interface_list_dump", ])

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
        Classify._acl_interface_set_acl_list(
            node=node,
            sw_if_index=int(InterfaceUtil.get_interface_index(node, interface)),
            acl_type=acl_type,
            acls=acl_idx if isinstance(acl_idx, list) else list()
        )

    @staticmethod
    def add_replace_acl_multi_entries(node, acl_idx=None, rules=None, tag=u""):
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
        reg_ex_src_ip = re.compile(r"(src [0-9a-fA-F.:/\d{1,2}]*)")
        reg_ex_dst_ip = re.compile(r"(dst [0-9a-fA-F.:/\d{1,2}]*)")
        reg_ex_sport = re.compile(r"(sport \d{1,5})")
        reg_ex_dport = re.compile(r"(dport \d{1,5})")
        reg_ex_proto = re.compile(r"(proto \d{1,5})")

        acl_rules = list()
        for rule in rules.split(u", "):
            acl_rule = dict(
                is_permit=2 if u"permit+reflect" in rule
                else 1 if u"permit" in rule else 0,
                src_prefix=0,
                dst_prefix=0,
                proto=0,
                srcport_or_icmptype_first=0,
                srcport_or_icmptype_last=65535,
                dstport_or_icmpcode_first=0,
                dstport_or_icmpcode_last=65535,
                tcp_flags_mask=0,
                tcp_flags_value=0
            )

            groups = re.search(reg_ex_src_ip, rule)
            if groups:
                grp = groups.group(1).split(u" ")[1].split(u"/")
                acl_rule[u"src_prefix"] = IPUtil.create_prefix_object(
                    ip_address(grp[0]).packed, int(grp[1])
                )

            groups = re.search(reg_ex_dst_ip, rule)
            if groups:
                grp = groups.group(1).split(u" ")[1].split(u"/")
                acl_rule[u"dst_prefix"] = IPUtil.create_prefix_object(
                    ip_address(grp[0]).packed, int(grp[1])
                )

            groups = re.search(reg_ex_sport, rule)
            if groups:
                port = int(groups.group(1).split(u" ")[1])
                acl_rule[u"srcport_or_icmptype_first"] = port
                acl_rule[u"srcport_or_icmptype_last"] = port

            groups = re.search(reg_ex_dport, rule)
            if groups:
                port = int(groups.group(1).split(u" ")[1])
                acl_rule[u"dstport_or_icmpcode_first"] = port
                acl_rule[u"dstport_or_icmpcode_last"] = port

            groups = re.search(reg_ex_proto, rule)
            if groups:
                proto = int(groups.group(1).split(' ')[1])
                acl_rule[u"proto"] = proto

            acl_rules.append(acl_rule)

        Classify._acl_add_replace(
            node, acl_idx=acl_idx, rules=acl_rules, tag=tag
        )

    @staticmethod
    def add_macip_acl_multi_entries(node, rules=u""):
        """Add a new MACIP ACL.

        :param node: VPP node to set MACIP ACL on.
        :param rules: Required MACIP rules.
        :type node: dict
        :type rules: str
        """
        reg_ex_ip = re.compile(r"(ip [0-9a-fA-F.:/\d{1,2}]*)")
        reg_ex_mac = re.compile(r"(mac \S\S:\S\S:\S\S:\S\S:\S\S:\S\S)")
        reg_ex_mask = re.compile(r"(mask \S\S:\S\S:\S\S:\S\S:\S\S:\S\S)")

        acl_rules = list()
        for rule in rules.split(u", "):
            acl_rule = dict(
                is_permit=2 if u"permit+reflect" in rule
                else 1 if u"permit" in rule else 0,
                src_mac=6*b'0',
                src_mac_mask=6*b'0',
                prefix=0
            )

            groups = re.search(reg_ex_mac, rule)
            if groups:
                mac = groups.group(1).split(u" ")[1].replace(u":", u"")
                acl_rule[u"src_mac"] = bytes.fromhex(mac)

            groups = re.search(reg_ex_mask, rule)
            if groups:
                mask = groups.group(1).split(u" ")[1].replace(u":", u"")
                acl_rule[u"src_mac_mask"] = bytes.fromhex(mask)

            groups = re.search(reg_ex_ip, rule)
            if groups:
                grp = groups.group(1).split(u" ")[1].split(u"/")
                acl_rule[u"src_prefix"] = IPUtil.create_prefix_object(
                    ip_address((grp[0])).packed, int(grp[1])
                )

            acl_rules.append(acl_rule)

        Classify._macip_acl_add(node=node, rules=acl_rules)

    @staticmethod
    def vpp_log_macip_acl_settings(node):
        """Retrieve configured MACIP settings from the ACL plugin and write to
        robot log.

        :param node: VPP node.
        :type node: dict
        """
        PapiSocketExecutor.dump_and_log(node, [u"macip_acl_dump", ])

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
        cmd = u"macip_acl_interface_add_del"
        err_msg = f"Failed to get 'macip_acl_interface' on host {node[u'host']}"
        args = dict(
            is_add=bool(action == u"add"),
            sw_if_index=int(InterfaceUtil.get_interface_index(node, interface)),
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
        cmd = u"macip_acl_interface_get"
        err_msg = f"Failed to get 'macip_acl_interface' on host {node[u'host']}"
        with PapiSocketExecutor(node) as papi_exec:
            reply = papi_exec.add(cmd).get_reply(err_msg)
        logger.info(reply)
