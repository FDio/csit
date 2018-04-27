# Copyright (c) 2017 Cisco and/or its affiliates.
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

from copy import deepcopy

"""Test variables for BGP test suite."""

# Internal BGP peers for CRUD tests
address_internal = "192.168.0.2"
address_internal2 = "192.168.0.3"
holdtime_internal = 60
peer_internal = {
    "bgp-openconfig-extensions:neighbor": [{
        "neighbor-address": address_internal,
        "config": {
            "peer-type": "INTERNAL"
        },
        "timers": {
            "config": {
                "connect-retry": 3,
                "hold-time": holdtime_internal
            }
        },
        "transport": {
            "config": {
                "remote-port": 179,
                "passive-mode": False
            }
        },
        "afi-safis": {
            "afi-safi": [{
                "afi-safi-name": "openconfig-bgp-types:IPV4-UNICAST",
                "receive": True,
                "send-max": 0
                }]
            }
        }]
    }

peer_internal_update = {
    "bgp-openconfig-extensions:neighbor": [{
        "neighbor-address": address_internal,
        "config": {
            "peer-type": "INTERNAL"
        },
        "timers": {
            "config": {
                "connect-retry": 5,
                "hold-time": holdtime_internal*2
            }
        },
        "transport": {
            "config": {
                "remote-port": 180,
                "passive-mode": True
            }
        },
        "afi-safis": {
            "afi-safi": [{
                "afi-safi-name": "openconfig-bgp-types:IPV6-UNICAST",
                "receive": False,
                "send-max": 1
                }]
            }
        }]
    }

peer_internal2 = deepcopy(peer_internal)
peer_internal2["bgp-openconfig-extensions:neighbor"][0]["neighbor-address"] = \
    address_internal2

# Application BGP peer for CRUD test
address_application = "192.168.0.4"
peer_application = {
    "bgp-openconfig-extensions:neighbor": [{
        "neighbor-address": address_application,
        "config": {
            "peer-group": "application-peers"
        },
        "afi-safis": {
            "afi-safi": [
                {
                    "afi-safi-name": "openconfig-bgp-types:IPV4-UNICAST",
                    "receive": True,
                    "send-max": 0
                },
                {
                    "afi-safi-name":
                        "openconfig-bgp-types:IPV4-LABELLED-UNICAST",
                    "receive": True,
                    "send-max": 0
                }]
            }
        }]
    }

# IPv4 route for CRUD test
route_address_ipv4 = "192.168.0.5/32"
route_id_ipv4 = 0
route_data_ipv4 = {
    "bgp-inet:ipv4-route": [{
        "path-id": route_id_ipv4,
        "prefix": route_address_ipv4,
        "attributes": {
            "as-path": {},
            "origin": {
                "value": "igp"
            },
            "local-pref": {
                "pref": 100
            },
            "ipv4-next-hop": {
                "global": "192.168.1.1"
            }
        }
    }]
}

# IPv4 route for testing Update operation
route_data_ipv4_update = {
    "bgp-inet:ipv4-route": [{
        "path-id": route_id_ipv4,
        "prefix": route_address_ipv4,
        "attributes": {
            "as-path": {},
            "origin": {
                "value": "egp"
            },
            "local-pref": {
                "pref": 200
            },
            "ipv4-next-hop": {
                "global": "192.168.1.2"
            }
        }
    }]
}

# IPv4 route for testing multiple routes
route_address_ipv4_2 = "192.168.0.6/32"
route_id_ipv4_2 = 1
route_data_ipv4_2 = {
    "bgp-inet:ipv4-route": [{
        "path-id": route_id_ipv4_2,
        "prefix": route_address_ipv4_2,
        "attributes": {
            "as-path": {},
            "origin": {
                "value": "igp"
            },
            "local-pref": {
                "pref": 100
            },
            "ipv4-next-hop": {
                "global": "192.168.1.2"
            }
        }
    }]
}

# IPv6 route for CRUD test
route_address_ipv6 = "3ffe:62::1/64"
route_id_ipv6 = 0
route_data_ipv6 = {
    "bgp-inet:ipv6-route": [{
        "path-id": route_id_ipv6,
        "prefix": route_address_ipv6,
        "attributes": {
            "as-path": {},
            "origin": {
                "value": "igp"
            },
            "local-pref": {
                "pref": 100
            },
            "ipv6-next-hop": {
                "global": "3ffe:63::1"
            }
        }
    }]
}

# IPv4 route operational data in routing table
table1_oper = {
    "destination-prefix": route_address_ipv4,
    "next-hop": "192.168.1.1",
    "vpp-ipv4-unicast-routing:vpp-ipv4-route": {'classify-table': 'classify-table-0'}
}

# Peer configurations for traffic test
dut1_peer = {
    "bgp-openconfig-extensions:neighbor": [{
        "neighbor-address": "192.168.1.1",
        "config": {
            "peer-type": "INTERNAL"
        },
        "timers": {
            "config": {
                "connect-retry": 3,
                "hold-time": 60
            }
        },
        "transport": {
            "config": {
                "remote-port": 179,
                "passive-mode": False
            }
        },
        "afi-safis": {
            "afi-safi": [
                {
                    "afi-safi-name": "openconfig-bgp-types:IPV4-UNICAST",
                    "receive": True,
                    "send-max": 0},
                {
                    "afi-safi-name": "openconfig-bgp-types:IPV6-UNICAST",
                    "receive": True,
                    "send-max": 0},
                {
                    "afi-safi-name": "LINKSTATE"
                }
            ]
        }
    }]
}

dut2_peer = {
    "bgp-openconfig-extensions:neighbor": [{
        "neighbor-address": "192.168.1.2",
        "config": {
            "peer-type": "INTERNAL"
        },
        "timers": {
            "config": {
                "connect-retry": 3,
                "hold-time": 60
            }
        },
        "transport": {
            "config": {
                "remote-port": 179,
                "passive-mode": True
            }
        },
        "afi-safis": {
            "afi-safi": [
                {
                    "afi-safi-name": "openconfig-bgp-types:IPV4-UNICAST",
                    "receive": True,
                    "send-max": 0},
                {
                    "afi-safi-name": "openconfig-bgp-types:IPV6-UNICAST",
                    "receive": True,
                    "send-max": 0},
                {
                    "afi-safi-name": "LINKSTATE"
                }
            ]
        }
    }]
}

# IPv4 route for traffic test
dut1_route_address = "192.168.0.5/32"
dut1_route_id = 1
dut1_route = {
    "bgp-inet:ipv4-route": [{
        "path-id": dut1_route_id,
        "prefix": dut1_route_address,
        "attributes": {
            "as-path": {},
            "origin": {
                "value": "igp"
            },
            "local-pref": {
                "pref": 100
            },
            "ipv4-next-hop": {
                "global": "192.168.1.3"
            }
        }
    }]
}

# IPv4 route in peer operational data
rib_operational = {
    "loc-rib": {"tables": [
        {
            "afi": "bgp-types:ipv4-address-family",
            "safi": "bgp-types:unicast-subsequent-address-family",
            "bgp-inet:ipv4-routes": {
                "ipv4-route": dut1_route["bgp-inet:ipv4-route"]
            }
        }
    ]}
}

route_operational = {
    "vpp-ipv4-unicast-routing:vpp-ipv4-route": {'classify-table': 'classify-table-0'},
    "next-hop-address": "192.168.1.3",
    "destination-prefix": dut1_route_address
}

# IPv6 route for traffic test
dut1_route_ip6_address = "3ffe:62::1/64"
dut1_route_ip6_id = 1
dut1_route_ip6 = {
    "bgp-inet:ipv6-route": [{
        "path-id": dut1_route_ip6_id,
        "prefix": dut1_route_ip6_address,
        "attributes": {
            "as-path": {},
            "origin": {
                "value": "igp"
            },
            "local-pref": {
                "pref": 100
            },
            "ipv6-next-hop": {
                "global": "3ffe:63::1"
            }
        }
    }]
}

# IPv6 route in peer operational data
rib_ip6_operational = {
    "loc-rib": {"tables": [
        {
            "afi": "bgp-types:ipv6-address-family",
            "safi": "bgp-types:unicast-subsequent-address-family",
            "bgp-inet:ipv6-routes": {
                "ipv6-route": dut1_route_ip6["bgp-inet:ipv6-route"]
            }
        }
    ]}
}

route_ip6_operational = {
    "vpp-ipv6-unicast-routing:vpp-ipv6-route": {'classify-table': 'classify-table-0'},
    "next-hop-address": "3ffe:63::1",
    "destination-prefix": dut1_route_ip6_address
}
