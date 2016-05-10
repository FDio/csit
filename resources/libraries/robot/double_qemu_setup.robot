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

*** Keywords ***
| Setup QEMU Vhost and Run
| | [Documentation] | Setup 4 Qemu vhosts and 4 namespaces.Each call will be
| | ...             | different object instance.
| | ...
| | ... | *Arguments:*
| | ... | - node - Node where to setup qemu. Type: dict
| | ... | - sock1 - Socket path for first Vhost-User interface. Type: string
| | ... | - sock2 - Socket path for second Vhost-User interface. Type: string
| | ... | - sock3 - Socket path for third Vhost-User interface. Type: string
| | ... | - sock4 - Socket path for forth Vhost-User interface. Type: string
| | ... | - ip1 - IP address for namespace 1. Type: string
| | ... | - ip2 - IP address for namespace 2. Type: string
| | ... | - ip3 - IP address for namespace 3. Type: string
| | ... | - ip4 - IP address for namespace 4. Type: string
| | ... | - prefix_length - IP prefix length. Type: int
| | ... | - qemu_name - Qemu instance name by which the object will be accessed.
| | ... |               Type: string
| | ... | - mac_ID - MAC address ID used to differentiate qemu instances and
| | ... | namespaces assigned to them. Type: string
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Setup QEMU Vhost And Run\| {nodes['DUT1']} \| /tmp/sock1 \
| | ... | \| /tmp/sock2 \| /tmp/sock3 \| /tmp/sock4 \| 16.0.0.1 \| 16.0.0.2 \
| | ... | \| 16.0.0.3 \| 16.0.0.4 \| 24 \| qemu_instance_1 \| 06
| | ...
| | [Arguments] | ${node} | ${sock1} | ${sock2} | ${sock3} | ${sock4} | ${ip1}
| | ... | ${ip2} | ${ip3} | ${ip4} | ${prefix_length} | ${qemu_name} | ${mac_ID}
| | Import Library | resources.libraries.python.QemuUtils \
| | ... | WITH NAME | ${qemu_name}
| | ${qemu_add_vhost}= | Replace Variables | ${qemu_name}.Qemu Add Vhost User If
| | ${qemu_set_node}= | Replace Variables | ${qemu_name}.Qemu Set Node
| | ${qemu_start}= | Replace Variables | ${qemu_name}.Qemu Start
| | Run keyword | ${qemu_add_vhost} | ${sock1} | mac=52:54:00:00:${mac_ID}:01
| | Run keyword | ${qemu_add_vhost} | ${sock2} | mac=52:54:00:00:${mac_ID}:02
| | Run keyword | ${qemu_add_vhost} | ${sock3} | mac=52:54:00:00:${mac_ID}:03
| | Run keyword | ${qemu_add_vhost} | ${sock4} | mac=52:54:00:00:${mac_ID}:04
| | Run keyword | ${qemu_set_node} | ${node}
| | ${vm}= | Run keyword | ${qemu_start}
| | ${vhost1}= | Get Vhost User If Name By Sock | ${vm} | ${sock1}
| | ${vhost2}= | Get Vhost User If Name By Sock | ${vm} | ${sock2}
| | ${vhost3}= | Get Vhost User If Name By Sock | ${vm} | ${sock3}
| | ${vhost4}= | Get Vhost User If Name By Sock | ${vm} | ${sock4}
| | Set Interface State | ${vm} | ${vhost1} | up
| | Set Interface State | ${vm} | ${vhost2} | up
| | Set Interface State | ${vm} | ${vhost3} | up
| | Set Interface State | ${vm} | ${vhost4} | up
| | Setup Network Namespace
| | ... | ${vm} | nmspace1 | ${vhost1} | ${ip1} | ${prefix_length}
| | Setup Network Namespace
| | ... | ${vm} | nmspace2 | ${vhost2} | ${ip2} | ${prefix_length}
| | Setup Network Namespace
| | ... | ${vm} | nmspace3 | ${vhost3} | ${ip3} | ${prefix_length}
| | Setup Network Namespace
| | ... | ${vm} | nmspace4 | ${vhost4} | ${ip4} | ${prefix_length}
| | Set Test Variable | ${${qemu_name}} | ${vm}

| Qemu Teardown
| | [Documentation] | Stop specific qemu instance
| | ...             | running on ${dut_node}, ${vm} is VM node info dictionary
| | ...             | returned by qemu_start or None.
| | ... | *Arguments:*
| | ... | - dut_node - Node where to clean qemu. Type: dict
| | ... | - vm - VM node info dictionary. Type: string
| | ... | - qemu_name - Qemu instance by name. Type: string
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Qemu Teardown \| ${node['DUT1']} \| ${vm} \| qemu_node_1
| | ...
| | [Arguments] | ${dut_node} | ${vm} | ${qemu_name}
| | ${set_node}= | Replace Variables | ${qemu_name}.Qemu Set Node
| | ${sys_status}= | Replace Variables | ${qemu_name}.Qemu System Status
| | ${kill}= | Replace Variables | ${qemu_name}.Qemu Kill
| | ${sys_pd}= | Replace Variables | ${qemu_name}.Qemu System Powerdown
| | ${quit}= | Replace Variables | ${qemu_name}.Qemu Quit
| | ${clear_socks}= | Replace Variables | ${qemu_name}.Qemu Clear Socks
| | Run Keyword | ${set_node} | ${dut_node}
| | ${status} | ${value}= | Run Keyword And Ignore Error | ${sys_status}
| | Run Keyword If | "${status}" == "FAIL" | ${kill}
| | ... | ELSE IF | "${value}" == "running" | ${sys_pd}
| | ... | ELSE | ${quit}
| | Run Keyword | ${clear_socks}
| | Run Keyword If | ${vm} is not None | Disconnect | ${vm}