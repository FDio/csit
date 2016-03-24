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

"""IPv6 utilities library."""

import re

from resources.libraries.python.ssh import SSH


class IPv6Util(object):
    """IPv6 utilities"""

    @staticmethod
    def ipv6_ping(src_node, dst_addr, count=3, data_size=56, timeout=1):
        """IPv6 ping.

        :param src_node: Node where ping run.
        :param dst_addr: Destination IPv6 address.
        :param count: Number of echo requests. (Optional)
        :param data_size: Number of the data bytes. (Optional)
        :param timeout: Time to wait for a response, in seconds. (Optional)
        :type src_node: dict
        :type dst_addr: str
        :type count: int
        :type data_size: int
        :type timeout: int
        :return: Number of lost packets.
        """
        ssh = SSH()
        ssh.connect(src_node)

        cmd = "ping6 -c {c} -s {s} -W {W} {dst}".format(c=count, s=data_size,
                                                        W=timeout,
                                                        dst=dst_addr)
        (ret_code, stdout, _) = ssh.exec_command(cmd)

        regex = re.compile(r'(\d+) packets transmitted, (\d+) received')
        match = regex.search(stdout)
        sent, received = match.groups()
        packet_lost = int(sent) - int(received)

        return packet_lost

    @staticmethod
    def ipv6_ping_port(nodes_ip, src_node, dst_node, port, cnt=3,
                       size=56, timeout=1):
        """Send IPv6 ping to the node port.

        :param nodes_ip: Nodes IPv6 addresses.
        :param src_node: Node where ping run.
        :param dst_node: Destination node.
        :param port: Port on the destination node.
        :param cnt: Number of echo requests. (Optional)
        :param size: Number of the data bytes. (Optional)
        :param timeout: Time to wait for a response, in seconds. (Optional)
        :type nodes_ip: dict
        :type src_node: dict
        :type dst_node: dict
        :type port: str
        :type cnt: int
        :type size: int
        :type timeout: int
        :return: Number of lost packets.
        :rtype: int
        """
        dst_ip = IPv6Util.get_node_port_ipv6_address(dst_node, port, nodes_ip)
        return IPv6Util.ipv6_ping(src_node, dst_ip, cnt, size, timeout)

    @staticmethod
    def get_node_port_ipv6_address(node, interface, nodes_addr):
        """Return IPv6 address of the node port.

        :param node: Node in the topology.
        :param interface: Interface name of the node.
        :param nodes_addr: Nodes IPv6 addresses.
        :type node: dict
        :type interface: str
        :type nodes_addr: dict
        :return: IPv6 address string.
        """
        for net in nodes_addr.values():
            for port in net['ports'].values():
                host = port.get('node')
                dev = port.get('if')
                if host == node['host'] and dev == interface:
                    ip = port.get('addr')
                    if ip is not None:
                        return ip
                    else:
                        raise Exception(
                            'Node {n} port {p} IPv6 address is not set'.format(
                                n=node['host'], p=interface))

        raise Exception('Node {n} port {p} IPv6 address not found.'.format(
            n=node['host'], p=interface))
