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

"""Classify utilities library."""

from robot.api import logger

from resources.libraries.python.VatExecutor import VatExecutor, VatTerminal
from resources.libraries.python.topology import Topology


class Classify(object):
    """Classify utilities."""

    @staticmethod
    def vpp_creates_classify_table_l3(node, ip_version, direction):
        """Create classify table for IP address filtering.

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
        :raises RuntimeError: If VPP can't create table.
        """

        output = VatExecutor.cmd_from_template(node, "classify_add_table.vat",
                                               ip_version=ip_version,
                                               direction=direction)

        if output[0]["retval"] == 0:
            table_index = output[0]["new_table_index"]
            skip_n = output[0]["skip_n_vectors"]
            match_n = output[0]["match_n_vectors"]
            logger.trace('Classify table with table_index {} created on node {}'
                         .format(table_index, node['host']))
        else:
            raise RuntimeError('Unable to create classify table on node {}'
                               .format(node['host']))

        return table_index, skip_n, match_n

    @staticmethod
    def vpp_creates_classify_table_l2(node, direction):
        """Create classify table for MAC address filtering.

        :param node: VPP node to create classify table.
        :param direction: Direction of traffic - src/dst.
        :type node: dict
        :type direction: str
        :returns: (table_index, skip_n, match_n)
            table_index: Classify table index.
            skip_n: Number of skip vectors.
            match_n: Number of match vectors.
        :rtype: tuple(int, int, int)
        :raises RuntimeError: If VPP can't create table.
        """
        output = VatExecutor.cmd_from_template(node,
                                               "classify_add_table_l2.vat",
                                               direction=direction)

        if output[0]["retval"] == 0:
            table_index = output[0]["new_table_index"]
            skip_n = output[0]["skip_n_vectors"]
            match_n = output[0]["match_n_vectors"]
            logger.trace('Classify table with table_index {} created on node {}'
                         .format(table_index, node['host']))
        else:
            raise RuntimeError('Unable to create classify table on node {}'
                               .format(node['host']))

        return table_index, skip_n, match_n

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
        :raises RuntimeError: If VPP can't create table.
        """
        output = VatExecutor.cmd_from_template(node,
                                               "classify_add_table_hex.vat",
                                               hex_mask=hex_mask)

        if output[0]["retval"] == 0:
            table_index = output[0]["new_table_index"]
            skip_n = output[0]["skip_n_vectors"]
            match_n = output[0]["match_n_vectors"]
            logger.trace('Classify table with table_index {} created on node {}'
                         .format(table_index, node['host']))
        else:
            raise RuntimeError('Unable to create classify table on node {}'
                               .format(node['host']))

        return table_index, skip_n, match_n

    @staticmethod
    def vpp_configures_classify_session_l3(node, acl_method, table_index,
                                           skip_n, match_n, ip_version,
                                           direction, address):
        """Configuration of classify session for IP address filtering.

        :param node: VPP node to setup classify session.
        :param acl_method: ACL method - deny/permit.
        :param table_index: Classify table index.
        :param skip_n: Number of skip vectors based on mask.
        :param match_n: Number of match vectors based on mask.
        :param ip_version: Version of IP protocol.
        :param direction: Direction of traffic - src/dst.
        :param address: IPv4 or IPv6 address.
        :type node: dict
        :type acl_method: str
        :type table_index: int
        :type skip_n: int
        :type match_n: int
        :type ip_version: str
        :type direction: str
        :type address: str
        """
        with VatTerminal(node) as vat:
            vat.vat_terminal_exec_cmd_from_template("classify_add_session.vat",
                                                    acl_method=acl_method,
                                                    table_index=table_index,
                                                    skip_n=skip_n,
                                                    match_n=match_n,
                                                    ip_version=ip_version,
                                                    direction=direction,
                                                    address=address)

    @staticmethod
    def vpp_configures_classify_session_l2(node, acl_method, table_index,
                                           skip_n, match_n, direction, address):
        """Configuration of classify session for MAC address filtering.

        :param node: VPP node to setup classify session.
        :param acl_method: ACL method - deny/permit.
        :param table_index: Classify table index.
        :param skip_n: Number of skip vectors based on mask.
        :param match_n: Number of match vectors based on mask.
        :param direction: Direction of traffic - src/dst.
        :param address: IPv4 or IPv6 address.
        :type node: dict
        :type acl_method: str
        :type table_index: int
        :type skip_n: int
        :type match_n: int
        :type direction: str
        :type address: str
        """
        with VatTerminal(node) as vat:
            vat.vat_terminal_exec_cmd_from_template(
                "classify_add_session_l2.vat",
                acl_method=acl_method,
                table_index=table_index,
                skip_n=skip_n,
                match_n=match_n,
                direction=direction,
                address=address)

    @staticmethod
    def vpp_configures_classify_session_hex(node, acl_method, table_index,
                                            skip_n, match_n, hex_value):
        """Configuration of classify session with hex value.

        :param node: VPP node to setup classify session.
        :param acl_method: ACL method - deny/permit.
        :param table_index: Classify table index.
        :param skip_n: Number of skip vectors based on mask.
        :param match_n: Number of match vectors based on mask.
        :param hex_value: Classify hex value.
        :type node: dict
        :type acl_method: str
        :type table_index: int
        :type skip_n: int
        :type match_n: int
        :type hex_value: str
        """
        with VatTerminal(node) as vat:
            vat.vat_terminal_exec_cmd_from_template(
                "classify_add_session_hex.vat",
                acl_method=acl_method,
                table_index=table_index,
                skip_n=skip_n,
                match_n=match_n,
                hex_value=hex_value)

    @staticmethod
    def vpp_configures_classify_session_generic(node, session_type, table_index,
                                                skip_n, match_n, match,
                                                match2=''):
        """Configuration of classify session.

        :param node: VPP node to setup classify session.
        :param session_type: Session type - hit-next, l2-hit-next, acl-hit-next
            or policer-hit-next, and their respective parameters.
        :param table_index: Classify table index.
        :param skip_n: Number of skip vectors based on mask.
        :param match_n: Number of match vectors based on mask.
        :param match: Match value - l2, l3, l4 or hex, and their
            respective parameters.
        :param match2: Additional match values, to avoid using overly long
            variables in RobotFramework.
        :type node: dict
        :type session_type: str
        :type table_index: int
        :type skip_n: int
        :type match_n: int
        :type match: str
        :type match2: str
        """

        match = ' '.join((match, match2))

        with VatTerminal(node) as vat:
            vat.vat_terminal_exec_cmd_from_template(
                "classify_add_session_generic.vat",
                type=session_type,
                table_index=table_index,
                skip_n=skip_n,
                match_n=match_n,
                match=match,
            )

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
        if protocol == 'TCP' or protocol == 'UDP':
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
        with VatTerminal(node) as vat:
            data = vat.vat_terminal_exec_cmd_from_template(
                "classify_session_dump.vat",
                table_id=table_index
            )
        if session_index is not None:
            return data[0][session_index]
        else:
            return data[0]

    @staticmethod
    def vpp_log_plugin_acl_settings(node):
        """Retrieve configured settings from the ACL plugin
         and write to robot log.

        :param node: VPP node.
        :type node: dict
        """
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

        :param node: VPP node.
        :type node: dict
        """
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

        :param node: VPP node to set ACL on.
        :param interface: Interface name or sw_if_index.
        :param acl_type: Type of ACL(s) - input or output.
        :param acl_idx: Index(ies) of ACLs to be applied on the interface.
        :type node: dict
        :type interface: str or int
        :type acl_type: str
        :type acl_idx: list
        :raises RuntimeError: If unable to set ACL list for the interface.
        """
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
    def add_replace_acl(node, acl_idx=None, ip_ver="ipv4", action="permit",
                        src=None, dst=None, sport=None, dport=None, proto=None,
                        tcpflg_val=None, tcpflg_mask=None):
        """Add a new ACL or replace the existing one. To replace an existing
        ACL, pass the ID of this ACL.

        :param node: VPP node to set ACL on.
        :param acl_idx: ID of ACL. (Optional)
        :param ip_ver: IP version. (Optional)
        :param action: ACL action. (Optional)
        :param src: Source IP in format IP/plen. (Optional)
        :param dst: Destination IP in format IP/plen. (Optional)
        :param sport: Source port or ICMP4/6 type - range format X-Y allowed.
         (Optional)
        :param dport: Destination port or ICMP4/6 code - range format X-Y
         allowed. (Optional)
        :param proto: L4 protocol (http://www.iana.org/assignments/protocol-
         numbers/protocol-numbers.xhtml). (Optional)
        :param tcpflg_val: TCP flags value. (Optional)
        :param tcpflg_mask: TCP flags mask. (Optional)
        :type node: dict
        :type acl_idx: int
        :type ip_ver: str
        :type action: str
        :type src: str
        :type dst: str
        :type sport: str or int
        :type dport: str or int
        :type proto: int
        :type tcpflg_val: int
        :type tcpflg_mask: int
        :raises RuntimeError: If unable to add or replace ACL.
        """
        acl_idx = '{0}'.format(acl_idx) if acl_idx else ''

        src = 'src {0}'.format(src) if src else ''

        dst = 'dst {0}'.format(dst) if dst else ''

        sport = 'sport {0}'.format(sport) if sport else ''

        dport = 'dport {0}'.format(dport) if dport else ''

        proto = 'proto {0}'.format(proto) if proto else ''

        tcpflags = 'tcpflags {0} {1}'.format(tcpflg_val, tcpflg_mask) \
            if tcpflg_val and tcpflg_mask else ''

        try:
            with VatTerminal(node, json_param=False) as vat:
                vat.vat_terminal_exec_cmd_from_template(
                    "acl_plugin/acl_add_replace.vat", acl_idx=acl_idx,
                    ip_ver=ip_ver, action=action, src=src, dst=dst, sport=sport,
                    dport=dport, proto=proto, tcpflags=tcpflags)
        except RuntimeError:
            raise RuntimeError("Adding or replacing of ACL failed on "
                               "node {0}".format(node['host']))

    @staticmethod
    def add_replace_acl_multi_entries(node, acl_idx=None, rules=None):
        """Add a new ACL or replace the existing one. To replace an existing
        ACL, pass the ID of this ACL.

        :param node: VPP node to set ACL on.
        :param acl_idx: ID of ACL. (Optional)
        :param rules: Required rules. (Optional)
        :type node: dict
        :type acl_idx: int
        :type rules: str
        :raises RuntimeError: If unable to add or replace ACL.
        """
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
    def delete_acl(node, idx):
        """Delete required ACL.

        :param node: VPP node to delete ACL on.
        :param idx: Index of ACL to be deleted.
        :type node: dict
        :type idx: int or str
        :raises RuntimeError: If unable to delete ACL.
        """
        try:
            with VatTerminal(node, json_param=False) as vat:
                vat.vat_terminal_exec_cmd_from_template(
                    "acl_plugin/acl_delete.vat", idx=idx)
        except RuntimeError:
            raise RuntimeError("Deletion of ACL failed on node {0}".
                               format(node['host']))

    @staticmethod
    def cli_show_acl(node, acl_idx=None):
        """Show ACLs.

        :param node: VPP node to show ACL on.
        :param acl_idx: Index of ACL to be shown.
        :type node: dict
        :type acl_idx: int or str
        :raises RuntimeError: If unable to delete ACL.
        """
        acl_idx = '{0}'.format(acl_idx) if acl_idx else ''

        try:
            with VatTerminal(node, json_param=False) as vat:
                vat.vat_terminal_exec_cmd_from_template(
                    "acl_plugin/show_acl.vat", idx=acl_idx)
        except RuntimeError:
            raise RuntimeError("Failed to show ACL on node {0}".
                               format(node['host']))

    @staticmethod
    def add_macip_acl(node, ip_ver="ipv4", action="permit", src_ip=None,
                      src_mac=None, src_mac_mask=None):
        """Add a new MACIP ACL.

        :param node: VPP node to set MACIP ACL on.
        :param ip_ver: IP version. (Optional)
        :param action: ACL action. (Optional)
        :param src_ip: Source IP in format IP/plen. (Optional)
        :param src_mac: Source MAC address in format with colons. (Optional)
        :param src_mac_mask: Source MAC address mask in format with colons.
         00:00:00:00:00:00 is a wildcard mask. (Optional)
        :type node: dict
        :type ip_ver: str
        :type action: str
        :type src_ip: str
        :type src_mac: str
        :type src_mac_mask: str
        :raises RuntimeError: If unable to add MACIP ACL.
        """
        src_ip = 'ip {0}'.format(src_ip) if src_ip else ''

        src_mac = 'mac {0}'.format(src_mac) if src_mac else ''

        src_mac_mask = 'mask {0}'.format(src_mac_mask) if src_mac_mask else ''

        try:
            with VatTerminal(node, json_param=False) as vat:
                vat.vat_terminal_exec_cmd_from_template(
                    "acl_plugin/macip_acl_add.vat", ip_ver=ip_ver,
                    action=action, src_ip=src_ip, src_mac=src_mac,
                    src_mac_mask=src_mac_mask)
        except RuntimeError:
            raise RuntimeError("Adding of MACIP ACL failed on node {0}".
                               format(node['host']))

    @staticmethod
    def add_macip_acl_multi_entries(node, rules=None):
        """Add a new MACIP ACL.

        :param node: VPP node to set MACIP ACL on.
        :param rules: Required MACIP rules. (Optional)
        :type node: dict
        :type rules: str
        :raises RuntimeError: If unable to add MACIP ACL.
        """
        rules = '{0}'.format(rules) if rules else ''

        try:
            with VatTerminal(node, json_param=False) as vat:
                vat.vat_terminal_exec_cmd_from_template(
                    "acl_plugin/macip_acl_add.vat", ip_ver=rules, action='',
                    src_ip='', src_mac='', src_mac_mask='')
        except RuntimeError:
            raise RuntimeError("Adding of MACIP ACL failed on node {0}".
                               format(node['host']))

    @staticmethod
    def delete_macip_acl(node, idx):
        """Delete required MACIP ACL.

        :param node: VPP node to delete MACIP ACL on.
        :param idx: Index of ACL to be deleted.
        :type node: dict
        :type idx: int or str
        :raises RuntimeError: If unable to delete MACIP ACL.
        """
        try:
            with VatTerminal(node, json_param=False) as vat:
                vat.vat_terminal_exec_cmd_from_template(
                    "acl_plugin/macip_acl_delete.vat", idx=idx)
        except RuntimeError:
            raise RuntimeError("Deletion of MACIP ACL failed on node {0}".
                               format(node['host']))

    @staticmethod
    def vpp_log_macip_acl_settings(node):
        """Retrieve configured MACIP settings from the ACL plugin
         and write to robot log.

        :param node: VPP node.
        :type node: dict
        """
        try:
            VatExecutor.cmd_from_template(
                node, "acl_plugin/macip_acl_dump.vat")
        except (ValueError, RuntimeError):
            # Fails to parse JSON data in response, but it is still logged
            pass

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

        try:
            with VatTerminal(node, json_param=False) as vat:
                vat.vat_terminal_exec_cmd_from_template(
                    "acl_plugin/macip_acl_interface_add_del.vat",
                    sw_if_index=sw_if_index, action=action, acl_idx=acl_idx)
        except RuntimeError:
            raise RuntimeError("Setting of MACIP ACL index for interface {0} "
                               "failed on node {1}".
                               format(interface, node['host']))

    @staticmethod
    def vpp_log_macip_acl_interface_assignment(node):
        """Get interface list and associated MACIP ACLs and write to robot log.

        :param node: VPP node.
        :type node: dict
        """
        try:
            VatExecutor.cmd_from_template(
                node, "acl_plugin/macip_acl_interface_get.vat", json_out=False)
        except RuntimeError:
            # Fails to parse response, but it is still logged
            pass
