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
peer_internal = {
    "bgp-openconfig-extensions:neighbor": [{
        "neighbor-address": address_internal,
        "config": {
            "peer-type": "INTERNAL"
        },
        "timers": {
            "config": {
                "connect-retry": 10,
                "hold-time": 60
            }
        },
        "transport": {
            "config": {
                "remote-port": 17900,
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
                "hold-time": 120
            }
        },
        "transport": {
            "config": {
                "remote-port": 17901,
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

# Application BGP peer for CRUD tests
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

table1_oper = {
    "destination-prefix": route_address_ipv4,
    "next-hop": "192.168.1.1",
    "vpp-ipv4-route-state": {}
}