# Copyright (c) 2019 Intel and/or its affiliates.
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

*** Settings ***
| Library | Collections
| Library | String

| Library | resources.libraries.python.InterfaceUtil
| Library | resources.libraries.python.IPUtil
| Library | resources.libraries.python.topology.Topology
| Library | resources.libraries.python.LoadBalancerUtil
| Library | resources.libraries.python.NodePath
| ...
| Resource | resources/libraries/robot/ip/ip4.robot
| Resource | resources/libraries/robot/performance/performance_configuration.robot
| ...
| Documentation | LoadBalancer suite keywords - configuration

*** Keywords ***
| Initialize lb maglev
| | [Documentation]
| | ... | Set UP state on VPP interfaces in path on nodes in 2-node
| | ... | circular topology. Get the interface MAC addresses and setup ARP on
| | ... | all VPP interfaces. Setup IPv4 addresses with /24 prefix on DUT-TG
| | ... | links.
| | ...
| | Set interfaces in path up
| | ...
| | ${fib_table}= | Set Variable | ${0}
| | Add Fib Table | ${dut1} | ${fib_table}
| | Assign Interface To Fib Table | ${dut1} | ${dut1_if1} | ${fib_table}
| | Assign Interface To Fib Table | ${dut1} | ${dut1_if2} | ${fib_table}
| | ...
| | ${tg1_if1_mac}= | Get Interface MAC | ${tg} | ${tg_if1}
| | ${tg1_if2_mac}= | Get Interface MAC | ${tg} | ${tg_if2}
| | ${dut1_if1_mac}= | Get Interface MAC | ${dut1} | ${dut1_if1}
| | ${dut1_if2_mac}= | Get Interface MAC | ${dut1} | ${dut1_if2}
| | ...
| | Configure IP addresses on interfaces | ${dut1} | ${dut1_if1}
| | ... | 192.168.50.72 | 24
| | Configure IP addresses on interfaces | ${dut1} | ${dut1_if2}
| | ... | 192.168.60.73 | 24
| | ...
| | VPP Add IP Neighbor | ${dut1} | ${dut1_if2} | 192.168.60.74 | ${tg1_if2_mac}
| | VPP Add IP Neighbor | ${dut1} | ${dut1_if2} | 192.168.60.75 | ${tg1_if2_mac}
| | VPP Add IP Neighbor | ${dut1} | ${dut1_if2} | 192.168.60.76 | ${tg1_if2_mac}
| | VPP Add IP Neighbor | ${dut1} | ${dut1_if2} | 192.168.60.77 | ${tg1_if2_mac}
| | VPP Add IP Neighbor | ${dut1} | ${dut1_if2} | 192.168.60.78 | ${tg1_if2_mac}
| | VPP Add IP Neighbor | ${dut1} | ${dut1_if2} | 192.168.60.79 | ${tg1_if2_mac}
| | ...
| | Vpp Route Add | ${dut1} | 192.168.60.0 | 24 | interface=${dut1_if2}
| | ...
| | Vpp Lb Conf | ${dut1} | ip4_src_addr=192.168.60.73 | buckets_per_core=${128}
| | Vpp Lb Add Del Vip | ${dut1} | vip_addr=90.1.2.1 | encap=0 | new_len=${1024}
| | Vpp Lb Add Del As | ${dut1} | vip_addr=90.1.2.1 | as_addr=192.168.60.74
| | Vpp Lb Add Del As | ${dut1} | vip_addr=90.1.2.1 | as_addr=192.168.60.75
| | Vpp Lb Add Del As | ${dut1} | vip_addr=90.1.2.1 | as_addr=192.168.60.76
| | Vpp Lb Add Del As | ${dut1} | vip_addr=90.1.2.1 | as_addr=192.168.60.77
| | Vpp Lb Add Del As | ${dut1} | vip_addr=90.1.2.1 | as_addr=192.168.60.78
| | Vpp Lb Add Del As | ${dut1} | vip_addr=90.1.2.1 | as_addr=192.168.60.79
