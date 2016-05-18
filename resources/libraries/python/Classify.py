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

    _BASE_MASK = 68 * '0'  # base value of classify hex table for TCP/UDP ports

    @staticmethod
    def vpp_create_classify_table(node, ip_version, direction):
        """Create classify table.

        :param node: VPP node to create classify table.
        :param ip_version: Version of IP protocol.
        :param direction: Direction of traffic - src/dst.
        :type node: dict
        :type ip_version: str
        :type direction: str
        :return table_index: Classify table index.
        :return skip_n: Number of skip vectors.
        :return match_n: Number of match vectors.
        :rtype table_index: int
        :rtype skip_n: int
        :rtype match_n: int
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
    def vpp_create_classify_table_hex(node, hex_mask):
        """Create classify table.

        :param node: VPP node to create classify table based on hex mask.
        :param hex_mask:
        :type node: dict
        :type hex_mask: str
        :return table_index: Classify table index.
        :return skip_n: Number of skip vectors.
        :return match_n: Number of match vectors.
        :rtype table_index: int
        :rtype skip_n: int
        :rtype match_n: int
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
    def vpp_configure_classify_session(node, acl_method, table_index, skip_n,
                                       match_n, ip_version, direction, address):
        """Configuration of classify session.

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
    def vpp_configure_classify_session_hex(node, acl_method, table_index,
                                           skip_n, match_n, hex_value):
        """Configuration of classify session.

        :param node: VPP node to setup classify session.
        :param acl_method: ACL method - deny/permit.
        :param table_index: Classify table index.
        :param skip_n: Number of skip vectors based on mask.
        :param match_n: Number of match vectors based on mask.
        :type node: dict
        :type acl_method: str
        :type table_index: int
        :type skip_n: int
        :type match_n: int
        :type hex_value:
        """
        with VatTerminal(node) as vat:
            vat.vat_terminal_exec_cmd_from_template(
                "classify_add_session_hex.vat",
                acl_method=acl_method,
                table_index=table_index,
                skip_n=skip_n,
                match_n=match_n,
                hex_value=hex_value)

    def compute_classify_hex_mask(self, protocol, direction):
        """Compute classify hex mask for TCP or UDP packet matching.

        :param protocol: Type of protocol.
        :param direction: Traffic direction.
        :return: Classify hex mask.
        :type protocol: str
        :type direction str
        :rtype : str
        """
        if protocol == 'TCP' or protocol == 'UDP':
            if direction == 'source':
                return self._BASE_MASK + 'FFFF0000'
            elif direction == 'destination':
                return self._BASE_MASK + '0000FFFF'
            elif direction == 'source + destination':
                return self._BASE_MASK + 'FFFFFFFF'
            else:
                raise ValueError("Invalid direction!")
        else:
            raise ValueError("Invalid protocol!")

    def compute_classify_hex_value(self, source_port, destination_port):
        """Compute classify hex value for TCP or UDP packet matching.

        :param source_port: Source TCP/UDP port.
        :param destination_port: Destination TCP/UDP port.
        :return: Classify hex value.
        :type source_port: str
        :type destination_port: str
        :rtype: str
        """
        source_port_hex = self._port_convert(source_port)
        destination_port_hex = self._port_convert(destination_port)

        return self._BASE_MASK + source_port_hex + destination_port_hex

    @staticmethod
    def _port_convert(port):
        """Convert port number for classify hex table format.

        :param port: TCP/UDP port number.
        :return hex_port: TCP/UDP port number in 4-digit hexadecimal format.
        :type port: str
        :rtype: str
        """
        try:
            hex_port = str(hex(int(port))).replace("0x", "")
            if len(hex_port) != 4:
                for i in (range(4 - len(hex_port))):
                    hex_port = '0' + hex_port
        except ValueError:
            raise ValueError("Invalid port number!")

        return hex_port
