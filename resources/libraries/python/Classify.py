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
