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

"""Test variables for LISP GPE test suite."""

negative_mapping_ip4 = {
    "id": "lispgpe_negative",
    "dp-table": 1,
    "vni": 0,
    "local-eid": {
        "address-type": "ietf-lisp-address-types:ipv4-prefix-afi",
        "virtual-network-id": 0,
        "ipv4-prefix": "192.168.0.0/24"
    },
    "remote-eid": {
        "address-type": "ietf-lisp-address-types:ipv4-prefix-afi",
        "virtual-network-id": 0,
        "ipv4-prefix": "192.168.1.0/24"
    },
    "action": "send-map-request"
}

# used for update operation
negative_mapping_ip4_edit = {
    "id": "lispgpe_negative",
    "dp-table": 1,
    "vni": 0,
    "local-eid": {
        "address-type": "ietf-lisp-address-types:ipv4-prefix-afi",
        "virtual-network-id": 0,
        "ipv4-prefix": "192.168.2.0/24"
    },
    "remote-eid": {
        "address-type": "ietf-lisp-address-types:ipv4-prefix-afi",
        "virtual-network-id": 0,
        "ipv4-prefix": "192.168.3.0/24"
    },
    "action": "send-map-request"
}

# used for multiple entries
negative_mapping_ip4_2 = {
    "id": "lispgpe_negative_2",
    "dp-table": 1,
    "vni": 0,
    "local-eid": {
        "address-type": "ietf-lisp-address-types:ipv4-prefix-afi",
        "virtual-network-id": 0,
        "ipv4-prefix": "192.168.2.0/24"
    },
    "remote-eid": {
        "address-type": "ietf-lisp-address-types:ipv4-prefix-afi",
        "virtual-network-id": 0,
        "ipv4-prefix": "192.168.3.0/24"
    },
    "action": "send-map-request"
}

positive_mapping_ip4 = {
    "id": "lispgpe_positive",
    "dp-table": 1,
    "vni": 0,
    "local-eid": {
        "address-type": "ietf-lisp-address-types:ipv4-prefix-afi",
        "virtual-network-id": 0,
        "ipv4-prefix": "192.168.4.0/24"
    },
    "remote-eid": {
        "address-type": "ietf-lisp-address-types:ipv4-prefix-afi",
        "virtual-network-id": 0,
        "ipv4-prefix": "192.168.5.0/24"
    },
    "locator-pair": [
      {
            "local-locator": "192.168.6.2",
            "remote-locator": "192.168.7.3",
            "weight": 0

      },
    {
            "local-locator": "192.168.5.2",
            "remote-locator": "192.168.5.3",
            "weight": 1
        }

    ]
}

negative_mapping_ip6 = {
    "id": "lispgpe_negative6",
    "dp-table": 1,
    "vni": 0,
    "local-eid": {
        "address-type": "ietf-lisp-address-types:ipv6-prefix-afi",
        "virtual-network-id": 0,
        "ipv6-prefix": "10::/64"
    },
    "remote-eid": {
        "address-type": "ietf-lisp-address-types:ipv6-prefix-afi",
        "virtual-network-id": 0,
        "ipv6-prefix": "11::/64"
    },
    "action": "send-map-request"
}

positive_mapping_ip6 = {
    "id": "lispgpe_positive6",
    "dp-table": 1,
    "vni": 0,
    "local-eid": {
        "address-type": "ietf-lisp-address-types:ipv6-prefix-afi",
        "virtual-network-id": 0,
        "ipv6-prefix": "12::/64"
    },
    "remote-eid": {
        "address-type": "ietf-lisp-address-types:ipv6-prefix-afi",
        "virtual-network-id": 0,
        "ipv6-prefix": "13::/64"
    },
    "locator-pair": [
      {
            "local-locator": "13::10",
            "remote-locator": "13::11",
            "weight": 0
      },
      {
            "local-locator": "14::10",
            "remote-locator": "14::11",
            "weight": 1
      }
    ]
}

# variables for traffic test
dut_to_tg_if1_ip4 = "192.168.0.1"
dut_to_tg_if2_ip4 = "192.168.1.1"
tg_to_dut_if2_ip4 = "192.168.1.2"
src_ip4 = "192.168.0.2"
dst_ip4 = "192.168.2.2"
prefix_len4 = 24

local_eid4 = "192.168.0.0/24"
remote_eid4 = "192.168.2.0/24"
src_rloc4 = dut_to_tg_if2_ip4
dst_rloc4 = tg_to_dut_if2_ip4

lisp_traffic_ip4 = {
    "id": "lispgpe_traffic_ip4",
    "dp-table": 0,
    "vni": 0,
    "local-eid": {
        "address-type": "ietf-lisp-address-types:ipv4-prefix-afi",
        "virtual-network-id": 0,
        "ipv4-prefix": local_eid4
    },
    "remote-eid": {
        "address-type": "ietf-lisp-address-types:ipv4-prefix-afi",
        "virtual-network-id": 0,
        "ipv4-prefix": remote_eid4
    },
    "locator-pair": [
      {
            "local-locator": src_rloc4,
            "remote-locator": dst_rloc4,
            "weight": 0
      }
    ]
}

dut_to_tg_if1_ip6 = "10::1"
dut_to_tg_if2_ip6 = "11::1"
tg_to_dut_if2_ip6 = "11::2"
src_ip6 = "10::2"
dst_ip6 = "12::2"
prefix_len6 = 64

local_eid6 = "10::/64"
remote_eid6 = "12::/64"
src_rloc6 = dut_to_tg_if2_ip6
dst_rloc6 = tg_to_dut_if2_ip6

lisp_traffic_ip6 = {
    "id": "lispgpe_traffic_ip6",
    "dp-table": 0,
    "vni": 0,
    "local-eid": {
        "address-type": "ietf-lisp-address-types:ipv6-prefix-afi",
        "virtual-network-id": 0,
        "ipv6-prefix": local_eid6
    },
    "remote-eid": {
        "address-type": "ietf-lisp-address-types:ipv6-prefix-afi",
        "virtual-network-id": 0,
        "ipv6-prefix": remote_eid6
    },
    "locator-pair": [
      {
            "local-locator": src_rloc6,
            "remote-locator": dst_rloc6,
            "weight": 0
      }
    ]
}
