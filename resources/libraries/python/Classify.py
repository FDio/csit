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

from socket import AF_INET, AF_INET6, inet_aton, inet_pton

from robot.api import logger

from resources.libraries.python.VatExecutor import VatExecutor, VatTerminal
from resources.libraries.python.topology import Topology
from resources.libraries.python.PapiExecutor import PapiExecutor


class Classify(object):
    """Classify utilities."""

    @staticmethod
    def _build_mac_mask(dst_mac='', src_mac='', ether_type=''):
        """Build MAC ACL mask data with hexstring format.

        :param dst_mac: source MAC address <0-ffffffffffff>.
        :param src_mac: destination MAC address <0-ffffffffffff>.
        :param ether_type: ethernet type <0-ffff>.
        :type dst_mac: str
        :type src_mac: str
        :type ether_type: str
        :returns MAC ACL mask in hexstring format.
        :rtype: str
        """
        return ('{!s:0>12}{!s:0>12}{!s:0>4}'.format(
            dst_mac, src_mac, ether_type)).rstrip('0').replace(':', '')

    @staticmethod
    def _build_ip_mask(proto='', src_ip='', dst_ip='',
                       src_port='', dst_port=''):
        """Build IP ACL mask data with hexstring format.

        :param proto: protocol number <0-ff>
        :param src_ip: source ip address <0-ffffffff>
        :param dst_ip: destination ip address <0-ffffffff>
        :param src_port: source port number <0-ffff>
        :param str dst_port: destination port number <0-ffff>
        :type proto: str
        :type src_ip: str
        :type dst_ip: str
        :type src_port: str
        :type dst_port:src
        :returns: IP mask in hexstring format.
        :rtype: str
        """
        return ('{!s:0>20}{!s:0>12}{!s:0>8}{!s:0>4}{!s:0>4}'.format(
            proto, src_ip, dst_ip, src_port, dst_port)).rstrip('0')

    @staticmethod
    def _build_ip6_mask(next_hdr='', src_ip='', dst_ip='',
                        src_port='', dst_port=''):
        """Build IPv6 ACL mask data with hexstring format.

        :param next_hdr: next header number <0-ff>.
        :param src_ip: source ip address <0-ffffffff>.
        :param dst_ip: destination ip address <0-ffffffff>.
        :param src_port: source port number <0-ffff>.
        :param dst_port: destination port number <0-ffff>.
        :type next_hdr: str
        :type src_ip: str
        :type dst_ip: str
        :type src_port: str
        :type dst_port: str
        :returns: IPv6 ACL mask in hexstring format.
        :rtype: str
        """
        return ('{!s:0>14}{!s:0>34}{!s:0>32}{!s:0>4}{!s:0>4}'.format(
            next_hdr, src_ip, dst_ip, src_port, dst_port)).rstrip('0')

    @staticmethod
    def _build_mac_match(dst_mac='', src_mac='', ether_type=''):
        """Build MAC ACL match data with hexstring format.

        :param dst_mac: source MAC address <x:x:x:x:x:x>
        :param src_mac: destination MAC address <x:x:x:x:x:x>
        :param ether_type: ethernet type <0-ffff>
        :type dst_mac: str
        :type src_mac: str
        :type ether_type: str
        :returns: MAC ACL match data in hexstring format.
        :rtype: str
        """
        if dst_mac:
            dst_mac = dst_mac.replace(':', '')
        if src_mac:
            src_mac = src_mac.replace(':', '')

        return ('{!s:0>12}{!s:0>12}{!s:0>4}'.format(
            dst_mac, src_mac, ether_type)).rstrip('0')

    @staticmethod
    def _build_ip_match(proto=0, src_ip='', dst_ip='',
                        src_port=0, dst_port=0):
        """Build IP ACL match data with hexstring format.

        :param int proto: protocol number with valid option "x"
        :param str src_ip: source ip address with format of "x.x.x.x"
        :param str dst_ip: destination ip address with format of "x.x.x.x"
        :param int src_port: source port number "x"
        :param int dst_port: destination port number "x"
        """
        if src_ip:
            src_ip = binascii.hexlify(inet_aton(src_ip))
        if dst_ip:
            dst_ip = binascii.hexlify(inet_aton(dst_ip))

        return ('{!s:0>20}{!s:0>12}{!s:0>8}{!s:0>4}{!s:0>4}'.format(
            hex(proto)[2:], src_ip, dst_ip, hex(src_port)[2:],
            hex(dst_port)[2:])).rstrip('0')

    @staticmethod
    def _build_ip6_match(next_hdr=0, src_ip='', dst_ip='',
                         src_port=0, dst_port=0):
        """Build IPv6 ACL match data with hexstring format.

        :param int next_hdr: next header number with valid option "x"
        :param str src_ip: source ip6 address with format of "xxx:xxxx::xxxx"
        :param str dst_ip: destination ip6 address with format of
            "xxx:xxxx::xxxx"
        :param int src_port: source port number "x"
        :param int dst_port: destination port number "x"
        """
        if src_ip:
            src_ip = binascii.hexlify(inet_pton(AF_INET6, src_ip))
        if dst_ip:
            dst_ip = binascii.hexlify(inet_pton(AF_INET6, dst_ip))

        return ('{!s:0>14}{!s:0>34}{!s:0>32}{!s:0>4}{!s:0>4}'.format(
            hex(next_hdr)[2:], src_ip, dst_ip, hex(src_port)[2:],
            hex(dst_port)[2:])).rstrip('0')

    @staticmethod
    def _classify_add_del_table(node, is_add, mask, match_n_vectors=1,
                                table_index=0xFFFFFFFF, nbuckets=2,
                                memory_size=2097152, skip_n_vectors=0,
                                next_table_index=0xFFFFFFFF,
                                miss_next_index=0xFFFFFFFF,current_data_flag=0,
                                current_data_offset=0):
        """Create Classify Table.

        :param node: VPP node to create classify table.
        :param is_add: If 1 the table is added, if 0 the table is deleted.
        :param mask: ACL mask in hexstring format.
        :param match_n_vectors: (Default value = 1)
        :param table_index: (Default value = 0xFFFFFFFF)
        :param nbuckets:  (Default value = 2)
        :param memory_size:  (Default value = 2097152)
        :param skip_n_vectors:  (Default value = 0)
        :param next_table_index:  (Default value = 0xFFFFFFFF)
        :param miss_next_index:  (Default value = 0xFFFFFFFF)
        :param current_data_flag:  (Default value = 0)
        :param current_data_offset:  (Default value = 0)
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

        with PapiExecutor(node) as papi_exec:
            data = papi_exec.add(cmd, **args).get_replies(err_msg).\
                verify_reply(err_msg=err_msg)

        return int(data["new_table_index"]), int(data["skip_n_vectors"]),\
            int(data["match_n_vectors"])

    @staticmethod
    def _classify_add_del_session(node, is_add, table_index, match,
                                  opaque_index=0xFFFFFFFF,
                                  hit_next_index=0xFFFFFFFF, advance=0,
                                  action=0, metadata=0):
        """
        :param node: VPP node to create classify session.
        :param is_add: If 1 the session is added, if 0 the session is deleted.
        :param table_index:
        :param match:
        :param opaque_index:  (Default value = 0xFFFFFFFF)
        :param hit_next_index:  (Default value = 0xFFFFFFFF)
        :param advance:  (Default value = 0)
        :param action:  (Default value = 0)
        :param metadata:  (Default value = 0)
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

        with PapiExecutor(node) as papi_exec:
            papi_exec.add(cmd, **args).get_replies(err_msg). \
                verify_reply(err_msg=err_msg)

    @staticmethod
    def _macip_acl_add(node, rules, tag=""):
        """ Add MACIP acl

        :param node: VPP node to add MACIP acl.
        :param rules: List of rules for given acl.
        :param tag: acl tag
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

        with PapiExecutor(node) as papi_exec:
            papi_exec.add(cmd, **args).get_replies(err_msg). \
                verify_reply(err_msg=err_msg)

    @staticmethod
    def vpp_creates_classify_table_l3(node, ip_version, direction, ip_addr):
        """Create classify table for IP address filtering.

        func, perf

        :param node: VPP node to create classify table.
        :param ip_version: Version of IP protocol.
        :param direction: Direction of traffic - src/dst.
        :type node: dict
        :type ip_version: str
        :type direction: str
        :returns: (table_index, skip_n, match_n)
            table_index: Classify table index.
            skip_n: Number of skip vectors.
            match_n: Number of match vectors.
        :rtype: tuple(int, int, int)
        """
        mask_f = dict(
            ip4=Classify._build_ip_mask,
            ip6=Classify._build_ip6_mask
        )
        if ip_version == "ip4":
            ip = binascii.hexlify(inet_aton(ip_addr))
        elif ip_version == "ip6":
            ip = binascii.hexlify(inet_pton(AF_INET6, ip_addr))
        else:
            raise ValueError("IP version {ver} is not supported.".
                             format(ver=ip_version))

        if direction == "src":
            mask = mask_f[ip_version](src_ip=ip)
        elif direction == "dst":
            mask = mask_f[ip_version](dst_ip=ip)
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

        Only func

        :param node: VPP node to create classify table.
        :param direction: Direction of traffic - src/dst.
        :type node: dict
        :type direction: str
        :returns: (table_index, skip_n, match_n)
            table_index: Classify table index.
            skip_n: Number of skip vectors.
            match_n: Number of match vectors.
        :rtype: tuple(int, int, int)
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

        Only func

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

        func, perf
        classify_add_session.vat

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

        Only func
        classify_add_session_l2.vat

        :param node: VPP node to setup classify session.
        :param acl_method: ACL method - deny/permit.
        :param table_index: Classify table index.
        :param direction: Direction of traffic - src/dst.
        :param address: IPv4 or IPv6 address.
        :type node: dict
        :type acl_method: str
        :type table_index: int
        :type direction: str
        :type address: str
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

        Only func

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

        Only HC func

        classify_table_info

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
        with PapiExecutor(node) as papi_exec:
            rpl = papi_exec.add(cmd, **args).get_replies(err_msg).\
                verify_reply(err_msg=err_msg)

        # TODO: Process and return the data

        # TODO: Remove
        with VatTerminal(node) as vat:
            data = vat.vat_terminal_exec_cmd_from_template(
                "classify_table_info.vat",
                table_id=table_index
            )
        return data[0]

    @staticmethod
    def get_classify_session_data(node, table_index, session_index=None):
        """Retrieve settings for all classify sessions in a table,
        or for a specific classify session.

        Only HC func

        classify_session_dump

        :param node: VPP node to retrieve classify data from.
        :param table_index: Index of a classify table.
        :param session_index: Index of a specific classify session. (Optional)
        :type node: dict
        :type table_index: int
        :type session_index: int
        :returns: List of classify session settings, or a dictionary of settings
         for a specific classify session.
        :rtype: list or dict
        """
        with PapiExecutor(node) as papi_exec:
            dump = papi_exec.add("classify_session_dump").get_dump()

        # TODO: Process and log the dump

        # TODO: Remove
        with VatTerminal(node) as vat:
            data = vat.vat_terminal_exec_cmd_from_template(
                "classify_session_dump.vat",
                table_id=table_index
            )
        if session_index is not None:
            return data[0][session_index]
        return data[0]

    @staticmethod
    def vpp_log_plugin_acl_settings(node):
        """Retrieve configured settings from the ACL plugin
         and write to robot log.

         perf, HC func

         acl_dump

        :param node: VPP node.
        :type node: dict
        """
        with PapiExecutor(node) as papi_exec:
            dump = papi_exec.add("acl_dump").get_dump()

        # TODO: Process and log the dump

        # TODO: Remove
        try:
            VatExecutor.cmd_from_template(
                node, "acl_plugin/acl_dump.vat")
        except (ValueError, RuntimeError):
            # Fails to parse JSON data in response, but it is still logged
            pass

    @staticmethod
    def vpp_log_plugin_acl_interface_assignment(node):
        """Retrieve interface assignment from the ACL plugin
        and write to robot log.

        perf (if test fails), HC func (verify-hc2vpp-func)

        acl_interface_list_dump

        :param node: VPP node.
        :type node: dict
        """
        with PapiExecutor(node) as papi_exec:
            dump = papi_exec.add("acl_interface_list_dump").get_dump()

        # TODO: Process and log the dump

        # TODO: Remove
        try:
            VatExecutor.cmd_from_template(
                node, "acl_plugin/acl_interface_dump.vat", json_out=False)
        except RuntimeError:
            # Fails to parse response, but it is still logged
            pass

    @staticmethod
    def set_acl_list_for_interface(node, interface, acl_type, acl_idx=None):
        """Set the list of input or output ACLs applied to the interface. It
        unapplies any previously applied ACLs.

        perf
        acl_plugin/acl_interface_set_acl_list.vat

        TODO: Create a list of acls

        :param node: VPP node to set ACL on.
        :param interface: Interface name or sw_if_index.
        :param acl_type: Type of ACL(s) - input or output.
        :param acl_idx: Index(ies) of ACLs to be applied on the interface.
        :type node: dict
        :type interface: str or int
        :type acl_type: str
        :type acl_idx: list
        """
        # if isinstance(interface, basestring):
        #     sw_if_index = Topology.get_interface_sw_index(node, interface)
        # else:
        #     sw_if_index = interface
        #
        # cmd = 'acl_interface_set_acl_list'
        # err_msg = "Failed to set acl list for interface on host {host}".\
        #     format(host=node['host'])
        # args = dict(
        #     sw_if_index=int(sw_if_index),
        #     count="TODO: specify",
        #     acls="TODO: Specify"
        # )
        # with PapiExecutor(node) as papi_exec:
        #     papi_exec.add(cmd, **args).get_replies(err_msg).\
        #         verify_reply(err_msg=err_msg)

        if isinstance(interface, basestring):
            sw_if_index = Topology.get_interface_sw_index(node, interface)
        else:
            sw_if_index = interface

        acl_list = acl_type + ' ' + ' '.join(str(idx) for idx in acl_idx) \
            if acl_idx else acl_type

        try:
            with VatTerminal(node, json_param=False) as vat:
                vat.vat_terminal_exec_cmd_from_template(
                    "acl_plugin/acl_interface_set_acl_list.vat",
                    interface=sw_if_index, acl_list=acl_list)
        except RuntimeError:
            raise RuntimeError("Setting of ACL list for interface {0} failed "
                               "on node {1}".format(interface, node['host']))

    @staticmethod
    def add_replace_acl_multi_entries(node, acl_idx=None, rules=None):
        """Add a new ACL or replace the existing one. To replace an existing
        ACL, pass the ID of this ACL.

        perf
        acl_plugin/acl_add_replace.vat

        TODO: Create a list of rules

        :param node: VPP node to set ACL on.
        :param acl_idx: ID of ACL. (Optional)
        :param rules: Required rules. (Optional)
        :type node: dict
        :type acl_idx: int
        :type rules: str
        """
        # cmd = 'acl_add_replace'
        # err_msg = "Failed to add or replace acl multi entries on host {host}".\
        #     format(host=node['host'])
        # args = dict(
        #     acl_index=int(acl_idx),
        #     rules="TODO: rules"
        # )
        # with PapiExecutor(node) as papi_exec:
        #     papi_exec.add(cmd, **args).get_replies(err_msg).\
        #         verify_reply(err_msg=err_msg)

        acl_idx = '{0}'.format(acl_idx) if acl_idx else ''

        rules = '{0}'.format(rules) if rules else ''

        try:
            with VatTerminal(node, json_param=False) as vat:
                vat.vat_terminal_exec_cmd_from_template(
                    "acl_plugin/acl_add_replace.vat", acl_idx=acl_idx,
                    ip_ver=rules, action='', src='', dst='', sport='',
                    dport='', proto='', tcpflags='')
        except RuntimeError:
            raise RuntimeError("Adding or replacing of ACL failed on "
                               "node {0}".format(node['host']))

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
            acl_rule["is_permit"] = 0 if "permit" in rule else 0
            acl_rule["is_ipv6"] = 1 if "ipv6" in rule else 0

            groups = re.search(reg_ex_mac, rule)
            mac = groups.group(1).split(' ')[1].replace(':', '')
            acl_rule["src_mac"] = unicode(mac)

            groups = re.search(reg_ex_mask, rule)
            mask = groups.group(1).split(' ')[1].replace(':', '')
            acl_rule["src_mac_mask"] = unicode(mask)

            groups = re.search(reg_ex_ip, rule)
            grp = groups.group(1).split(' ')[1].split('/')
            acl_rule["src_ip_addr"] = str(inet_pton(
                AF_INET6 if acl_rule["is_ipv6"] else AF_INET, grp[0]))
            acl_rule["src_ip_prefix_len"] = int(grp[1])

            acl_rules.append(acl_rule)

        Classify._macip_acl_add(node=node, rules=acl_rules)

    @staticmethod
    def vpp_log_macip_acl_settings(node):
        """Retrieve configured MACIP settings from the ACL plugin
        and write to robot log.

        perf/l2/10ge2p1x710-eth-l2bdbasemaclrn-macip-iacl10sl-100flows-ndrpdr.robot

        csit-3n-skx-perftest mrrANDnic_intel-x710ANDl2bdmaclrnANDmacipANDiaclANDacl_statelessANDacl10AND100k_flowsAND64bAND2c

        :param node: VPP node.
        :type node: dict
        """
        # TODO: Remove
        try:
            VatExecutor.cmd_from_template(
                node, "acl_plugin/macip_acl_dump.vat")
        except (ValueError, RuntimeError):
            # Fails to parse JSON data in response, but it is still logged
            pass

        with PapiExecutor(node) as papi_exec:
            dump = papi_exec.add("macip_acl_dump").get_dump()

        # TODO: Process and log the dump

    @staticmethod
    def add_del_macip_acl_interface(node, interface, action, acl_idx):
        """Apply/un-apply the MACIP ACL to/from a given interface.

        perf/l2/10ge2p1x710-eth-l2bdbasemaclrn-macip-iacl10sl-100flows-ndrpdr.robot

        csit-3n-skx-perftest mrrANDnic_intel-x710ANDl2bdmaclrnANDmacipANDiaclANDacl_statelessANDacl10AND100k_flowsAND64bAND2c

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
        with PapiExecutor(node) as papi_exec:
            papi_exec.add(cmd, **args).get_replies(err_msg).\
                verify_reply(err_msg=err_msg)

    @staticmethod
    def vpp_log_macip_acl_interface_assignment(node):
        """Get interface list and associated MACIP ACLs and write to robot log.

        perf/l2/10ge2p1x710-eth-l2bdbasemaclrn-macip-iacl10sl-100flows-ndrpdr.robot

        csit-3n-skx-perftest mrrANDnic_intel-x710ANDl2bdmaclrnANDmacipANDiaclANDacl_statelessANDacl10AND100k_flowsAND64bAND2c

        :param node: VPP node.
        :type node: dict
        """
        cmd = 'macip_acl_interface_get'
        err_msg = "Failed to get 'macip_acl_interface' on host {host}".format(
            host=node['host'])
        with PapiExecutor(node) as papi_exec:
            papi_exec.add(cmd).get_replies(err_msg)

        # TODO: Remove
        try:
            VatExecutor.cmd_from_template(
                node, "acl_plugin/macip_acl_interface_get.vat", json_out=False)
        except RuntimeError:
            # Fails to parse response, but it is still logged
            pass
