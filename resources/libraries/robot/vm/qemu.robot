# Copyright (c) 2019 Cisco and/or its affiliates.
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
| Library | resources.libraries.python.IPUtil
| Library | resources.libraries.python.QemuUtils

*** Keywords ***
| Configure QEMU vhost and run it
| | [Documentation]
| | ... | Setup Qemu with 4 vhost-user interfaces and 4 namespaces.
| | ... | Each call will be different object instance.
| | ...
| | ... | *Arguments:*
| | ... | - dut_node - Node where to setup qemu. Type: dict
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
| | ... | \| 16.0.0.3 \| 16.0.0.4 \| 24 \| qemu_instance_1 \| 06 \|
| | ...
| | [Arguments] | ${dut_node} | ${sock1} | ${sock2} | ${sock3} | ${sock4}
| | ... | ${ip1} | ${ip2} | ${ip3} | ${ip4} | ${prefix_length}
| | ... | ${qemu_name} | ${mac_ID}=${None}
| | ...
| | Import Library | resources.libraries.python.QemuUtils \
| | ... | node=${dut_node} | WITH NAME | ${qemu_name}
| | Run keyword | ${qemu_name}.Qemu Add Vhost User If | ${sock1}
| | Run keyword | ${qemu_name}.Qemu Add Vhost User If | ${sock2}
| | Run keyword | ${qemu_name}.Qemu Add Vhost User If | ${sock3}
| | Run keyword | ${qemu_name}.Qemu Add Vhost User If | ${sock4}
| | ${vm}= | Run keyword | ${qemu_name}.Qemu Start
| | ${vhost1}= | Get Vhost User If Name By Sock | ${vm} | ${sock1}
| | ${vhost2}= | Get Vhost User If Name By Sock | ${vm} | ${sock2}
| | ${vhost3}= | Get Vhost User If Name By Sock | ${vm} | ${sock3}
| | ${vhost4}= | Get Vhost User If Name By Sock | ${vm} | ${sock4}
| | Set Interface State | ${vm} | ${vhost1} | up | if_type=name
| | Set Interface State | ${vm} | ${vhost2} | up | if_type=name
| | Set Interface State | ${vm} | ${vhost3} | up | if_type=name
| | Set Interface State | ${vm} | ${vhost4} | up | if_type=name
| | Setup Network Namespace
| | ... | ${vm} | nmspace1 | ${vhost1} | ${ip1} | ${prefix_length}
| | Setup Network Namespace
| | ... | ${vm} | nmspace2 | ${vhost2} | ${ip2} | ${prefix_length}
| | Setup Network Namespace
| | ... | ${vm} | nmspace3 | ${vhost3} | ${ip3} | ${prefix_length}
| | Setup Network Namespace
| | ... | ${vm} | nmspace4 | ${vhost4} | ${ip4} | ${prefix_length}
| | Set Test Variable | ${${qemu_name}} | ${vm}

| Tear down QEMU
| | [Documentation]
| | ... | Stop specific qemu instance running on ${dut_node}.
| | ...
| | ... | *Arguments:*
| | ... | - dut_node - Node where to clean qemu. Type: dict
| | ... | - qemu_name - Qemu instance by name. Type: string
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Tear down QEMU \| ${node['DUT1']} \| qemu_node_1 \|
| | ...
| | [Arguments] | ${dut_node} | ${qemu_name}
| | ...
| | Run Keyword | ${qemu_name}.Qemu Set Node | ${dut_node}
| | Run Keyword | ${qemu_name}.Qemu Kill

| Stop and clear QEMU
| | [Documentation]
| | ... | Stop QEMU, clear used sockets running on ${dut}.
| | ...
| | ... | *Arguments:*
| | ... | - dut_node - Node where to clean qemu. Type: dict
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Tear down QEMU \| ${node['DUT1']} \|
| | ...
| | [Arguments] | ${dut}
| | ...
| | Qemu Set Node | ${dut}
| | Qemu Kill
