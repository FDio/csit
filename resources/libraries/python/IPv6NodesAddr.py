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

"""Robot framework variable file.

Create dictionary variable nodes_ipv6_addr with IPv6 addresses from available
networks.
"""

from resources.libraries.python.IPv6Setup import IPv6Networks
from resources.libraries.python.topology import Topology

# Default list of available IPv6 networks
IPV6_NETWORKS = ['3ffe:{0:04x}::/64'.format(i) for i in range(1, 100)]


def get_variables(nodes, networks=IPV6_NETWORKS):  # pylint: disable=too-many-locals
    """Special robot framework method that returns dictionary nodes_ipv6_addr,
    mapping of node and interface name to IPv6 address.

    :param nodes: Nodes of the test topology.
    :param networks: List of available IPv6 networks.
    :type nodes: dict
    :type networks: list

    .. note::
       Robot framework calls it automatically.
    """
    topo = Topology()
    links = topo.get_links(nodes)

    if len(links) > len(networks):
        raise Exception('Not enough available IPv6 networks for topology.')

    ip6_n = IPv6Networks(networks)

    nets = {}

    for link in links:
        ip6_net = ip6_n.next_network()
        net_hosts = ip6_net.hosts()
        port_idx = 0
        ports = {}
        for node in nodes.values():
            if_key = topo.get_interface_by_link_name(node, link)
            if_name = topo.get_interface_name(node, if_key)
            if if_name is not None:
                port = {'addr': str(next(net_hosts)),
                        'node': node['host'],
                        'if': if_name}
                port_idx += 1
                port_id = 'port{0}'.format(port_idx)
                ports.update({port_id: port})
        nets.update({link: {'net_addr': str(ip6_net.network_address),
                            'prefix': ip6_net.prefixlen,
                            'ports': ports}})

    return {'DICT__nodes_ipv6_addr': nets}
