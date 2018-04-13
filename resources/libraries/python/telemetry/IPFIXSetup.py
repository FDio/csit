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

"""IPFIX setup library"""

from resources.libraries.python.topology import Topology
from resources.libraries.python.VatExecutor import VatTerminal


class IPFIXSetup(object):
    """Class contains methods for seting up IPFIX reporting on DUTs."""

    def __init__(self):
        """Initializer."""
        pass

    @staticmethod
    def setup_ipfix_exporter(node, collector, source, fib=None, mtu=None,
                             interval=None):
        """Setup an IPFIX exporter on node to export collected flow data.

        :param node: DUT node.
        :param collector: IP address of flow data collector.
        :param source: IP address of local interface to send flow data from.
        :param fib: fib table ID.
        :param mtu: Maximum transfer unit of path to collector.
        :param interval: Frequency of sending template packets, in seconds.
        :type node: dict
        :type collector: str
        :type source: str
        :type fib: int
        :type mtu: int
        :type interval: int
        """

        fib = "vrf_id {0}".format(fib) if fib else ''
        mtu = "path_mtu {0}".format(mtu) if mtu else ''
        interval = "template_interval {0}".format(interval) if interval else ''

        with VatTerminal(node, json_param=False) as vat:
            vat.vat_terminal_exec_cmd_from_template('ipfix_exporter_set.vat',
                                                    collector=collector,
                                                    source=source,
                                                    fib=fib,
                                                    mtu=mtu,
                                                    interval=interval)

    @staticmethod
    def assign_interface_to_flow_table(node, interface, table_id,
                                       ip_version='ip4'):
        """Assigns a VPP interface to the specified classify table for IPFIX
        flow data collection.

        :param node: DUT node.
        :param interface: An interface on the DUT node.
        :param table_id: ID of a classify table.
        :param ip_version: Version of IP protocol. Valid options are ip4, ip6.
        :type node: dict
        :type interface: str or int
        :type table_id: int
        :type ip_version: str
        """

        if isinstance(interface, basestring):
            sw_if_index = Topology.get_interface_sw_index(node, interface)
        elif isinstance(interface, int):
            sw_if_index = interface
        else:
            raise TypeError

        table = "{0}-table {1}".format(ip_version, table_id)

        with VatTerminal(node, json_param=False) as vat:
            vat.vat_terminal_exec_cmd_from_template(
                "ipfix_interface_enable.vat",
                interface=sw_if_index,
                table=table,
                delete='')

    @staticmethod
    def set_ipfix_stream(node, domain=None, src_port=None):
        """Set an IPFIX export stream. Can be used to break up IPFIX reports
        into separate reporting domains.

        :param node: DUT node.
        :param domain: Desired index number of exporting domain.
        :param src_port: Source port to use when sending IPFIX packets. Default
            is the standard IPFIX port 4739.
        :type node: dict
        :type domain: int
        :type src_port: int
        """

        domain = "domain {0}".format(domain) if domain else ''
        src_port = "src_port {0}".format(src_port) if src_port else ''

        with VatTerminal(node, json_param=False) as vat:
            vat.vat_terminal_exec_cmd_from_template("ipfix_stream_set.vat",
                                                    domain=domain,
                                                    src_port=src_port)

    @staticmethod
    def assign_classify_table_to_exporter(node, table_id, ip_version='ip4'):
        """Assign a classify table to an IPFIX exporter. Classified packets will
        be included in the IPFIX flow report.

        :param node: DUT node.
        :param table_id: ID of a classify table.
        :param ip_version: Version of IP protocol. Valid options are ip4, ip6.
        :type node: dict
        :type table_id: int
        :type ip_version: str
        """

        with VatTerminal(node, json_param=False) as vat:
            vat.vat_terminal_exec_cmd_from_template("ipfix_table_add.vat",
                                                    table=table_id,
                                                    ip_version=ip_version,
                                                    add_del='add')
