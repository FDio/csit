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

Create dictionary variable nodes_ipv4_addr of IPv4 addresses from
available networks.
"""

from ipaddress import IPv4Network

from resources.libraries.python.topology import Topology

# Default list of IPv4 subnets
IPV4_NETWORKS = ['192.168.{}.0/24'.format(i) for i in range(1, 100)]


class IPv4NetworkGenerator(object):  # pylint: disable=too-few-public-methods
    """IPv4 network generator."""
    def __init__(self, networks):
        """
        :param networks: List of strings containing IPv4 subnet
        with prefix length.
        :type networks: list
        """
        self._networks = list()
        for network in networks:
            net = IPv4Network(unicode(network))
            self._networks.append(net)
        if len(self._networks) == 0:
            raise Exception('No IPv4 networks')

    def next_network(self):
        """
        :return: Next network in form (IPv4Network, subnet).
        :raises: StopIteration if there are no more elements.
        """
        if len(self._networks):
            return self._networks.pop()
        else:
            raise StopIteration()


def get_variables(nodes, networks=IPV4_NETWORKS[:]):  # pylint: disable=too-many-locals
    """Special robot framework method that returns dictionary nodes_ipv4_addr,
    mapping of node and interface name to IPv4 address.

    :param nodes: Nodes of the test topology.
    :param networks: List of available IPv4 networks.
    :type nodes: dict
    :type networks: list

    .. note::
       Robot framework calls it automatically.
    """
    topo = Topology()
    links = topo.get_links(nodes)

    if len(links) > len(networks):
        raise Exception('Not enough available IPv4 networks for topology.')

    ip4_n = IPv4NetworkGenerator(networks)

    nets = {}

    for link in links:
        ip4_net = ip4_n.next_network()
        net_hosts = ip4_net.hosts()
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
        nets.update({link: {'net_addr': str(ip4_net.network_address),
                            'prefix': ip4_net.prefixlen,
                            'ports': ports}})

    return {'DICT__nodes_ipv4_addr': nets}
