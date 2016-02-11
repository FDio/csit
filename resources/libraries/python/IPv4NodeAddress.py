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

# Default list of IPv4 subnets
IPV4_NETWORKS = ['20.20.20.0/24',
                 '10.10.10.0/24',
                 '1.1.1.0/30']


class IPv4NetworkGenerator(object):
    """IPv4 network generator."""
    def __init__(self, networks):
        """
        :param networks: list of strings containing IPv4 subnet
        with prefix length
        """
        self._networks = list()
        for network in networks:
            net = IPv4Network(unicode(network))
            subnet, _ = network.split('/')
            self._networks.append((net, subnet))
        if len(self._networks) == 0:
            raise Exception('No IPv4 networks')

    def next_network(self):
        """
        :return: next network in form (IPv4Network, subnet)
        """
        if len(self._networks):
            return self._networks.pop()
        else:
            raise StopIteration()


def get_variables(networks=IPV4_NETWORKS[:]):
    """
    Create dictionary of IPv4 addresses generated from provided subnet list.

    Example of returned dictionary:
        network = {
        'NET1': {
            'subnet': '192.168.1.0',
            'prefix': 24,
            'port1': {
                'addr': '192.168.1.1',
            },
            'port2': {
                'addr': '192.168.1.0',
            },
        },
        'NET2': {
            'subnet': '192.168.2.0',
            'prefix': 24,
            'port1': {
                'addr': '192.168.2.1',
            },
            'port2': {
                'addr': '192.168.2.2',
            },
        },
    }

    This function is called by RobotFramework automatically.

    :param networks: list of subnets in form a.b.c.d/length
    :return: Dictionary of IPv4 addresses
    """
    net_object = IPv4NetworkGenerator(networks)

    network = {}
    interface_count_per_node = 2

    for subnet_num in range(len(networks)):
        net, net_str = net_object.next_network()
        key = 'NET{}'.format(subnet_num + 1)
        network[key] = {
            'subnet': net_str,
            'prefix': net.prefixlen,
        }
        hosts = net.hosts()
        for port_num in range(interface_count_per_node):
            port = 'port{}'.format(port_num + 1)
            network[key][port] = {
                'addr': str(next(hosts)),
            }

    return {'DICT__nodes_ipv4_addr': network}
