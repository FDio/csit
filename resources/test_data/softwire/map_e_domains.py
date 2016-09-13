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
# limitations under the License.l

"""Variables for MAP-e feature tests."""

from resources.libraries.python.Map import Map
from random import sample, randint
from itertools import product


def get_variables(count):
    """Generate variables with random generated MAP-E configuration sets and
    IP test sets.

    domain_set = [IPv4_prefix, IPv6_prefix, IPv6_source, 16, 0, 0]
    ip_set = [IPv4_dst_address, IPv6_dst_address, dst_port, IPv6_src_address]

    :param count: Generate "count" map domain configuration parameters.
    :type count: int
    :return: Variable dictionary with domain_sets and ip_sets.
    :rtype: dict
    """
    domain_sets = []
    ip_sets = []

    for n1, n2 in sample(list(product(xrange(2, 224), xrange(0, 256))), count):
        v4_pfx = '{}.{}.0.0/16'.format(n1, n2)
        v6_pfx = '2001:{:x}{:x}::/48'.format(n1, n2)
        ipv6_br = '2001:ffff::1'
        domain_set = [v4_pfx,
                      v6_pfx,
                      ipv6_br, 16, 0, 0]
        port = randint(1025, 65500)
        ipv4_addr = '{}.{}.20.30'.format(n1, n2)
        ipv6_addr = Map.compute_ipv6_map_destination_address(
            v4_pfx, v6_pfx, 16, 0, 0, ipv4_addr, port)
        domain_sets.append(domain_set)
        ip_sets.append([ipv4_addr, ipv6_addr, port, ipv6_br])

    variables = {
        "domain_sets": domain_sets,
        "ip_sets": ip_sets
    }
    return variables
