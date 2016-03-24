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
from ssh import SSH


class IPv6Util(object):
    """IPv6 utilities"""

    def __init__(self):
        pass

    @staticmethod
    def ipv6_ping(src_node, dst_addr, count=3, data_size=56, timeout=1):
        """IPv6 ping.

           Args:
              src_node (Dict): Node where ping run.
              dst_addr (str): Destination IPv6 address.
              count (Optional[int]): Number of echo requests.
              data_size (Optional[int]): Number of the data bytes.
              timeout (Optional[int]): Time to wait for a response, in seconds.

           Returns:
              Number of lost packets.
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

           Args:
              nodes_ip (Dict): Nodes IPv6 addresses.
              src_node (Dict): Node where ping run.
              dst_node (Dict): Destination node.
              port (str): Port on the destination node.
              cnt (Optional[int]): Number of echo requests.
              size (Optional[int]): Number of the data bytes.
              timeout (Optional[int]): Time to wait for a response, in seconds.

           Returns:
              Number of lost packets.
        """
        dst_ip = IPv6Util.get_node_port_ipv6_address(dst_node, port, nodes_ip)
        return IPv6Util.ipv6_ping(src_node, dst_ip, cnt, size, timeout)

    @staticmethod
    def get_node_port_ipv6_address(node, interface, nodes_addr):
        """Return IPv6 address of the node port.

           Args:
               node (Dict): Node in the topology.
               interface (str): Interface name of the node.
               nodes_addr (Dict): Nodes IPv6 addresses.

           Returns:
               IPv6 address string.
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
