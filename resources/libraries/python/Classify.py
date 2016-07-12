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


from robot.api import logger

from resources.libraries.python.VatExecutor import VatExecutor, VatTerminal


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
        :return (table_index, skip_n, match_n)
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
        :return (table_index, skip_n, match_n)
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
        :return (table_index, skip_n, match_n)
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
    def vpp_configures_classify_session_l3(node, acl_method, table_index, skip_n,
                                          match_n, ip_version, direction,
                                          address):
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
    def vpp_configures_classify_session_l2(node, acl_method, table_index, skip_n,
                                          match_n, direction, address):
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
            vat.vat_terminal_exec_cmd_from_template("classify_add_session_l2.vat",
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
    def compute_classify_hex_mask(ip_version, protocol, direction):
        """Compute classify hex mask for TCP or UDP packet matching.

        :param ip_version: Version of IP protocol.
        :param protocol: Type of protocol.
        :param direction: Traffic direction.
        :type ip_version: str
        :type protocol: str
        :type direction: str
        :return: Classify hex mask.
        :rtype : str
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
        :return: Classify hex value.
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
        :return: TCP/UDP port number in 4-digit hexadecimal format.
        :rtype: str
        """
        return '{0:04x}'.format(int(port))

    @staticmethod
    def _compute_base_mask(ip_version):
        """Compute base classify hex mask based on IP version.

        :param ip_version: Version of IP protocol.
        :type ip_version: str
        :return: Base hex mask.
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
        :return: Classify table settings.
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
        :return: List of classify session settings, or a dictionary of settings
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
