from resources.libraries.python.Map import Map
from random import sample, randint
from itertools import product


def get_variables(arg):
    domain_sets = []
    ip_sets = []

    for n1, n2 in sample(list(product(xrange(2, 255), xrange(0, 256))), arg):
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
