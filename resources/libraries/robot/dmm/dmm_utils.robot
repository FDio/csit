# Copyright (c) 2018 Huawei Technologies Co.,Ltd.
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
| Library | resources.libraries.python.NodePath
| Documentation | *Utilities for the path computing, pcap reading*
| ...
| ... | Utilities for the path computing, pcap file reading and also the port
| ... | selection.

*** Keywords ***
| Path for 2-node testing is set
| | [Documentation] | Compute the path for the 2 node testing.
| | ...
| | ... | *Arguments:*
| | ... | - dut1_node - DUT1 node. Type: dictionary
| | ... | - dut2_node - DUT2 node. Type: dictionary
| | ...
| | ... | *Return:*
| | ... | - No value returned.
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Path for 2-node testing is set \| ${nodes['DUT1']} \
| | ... | \| ${nodes['DUT2'] \|
| | ...
| | [Arguments] | ${dut1_node} | ${dut2_node}
| | Append Nodes | ${dut1_node} | ${dut2_node}
| | Compute Path

| Pick out the port used to execute test
| | [Documentation] | Pick out the port used to execute the test.
| | ...
| | ... | *Arguments:*
| | ... | - No arguments.
| | ...
| | ... | *Return:*
| | ... | - No value returned.
| | ...
| | ... | *Example:*
| | ...
| | ... | \| Pick out the port used to execute test \|
| | ...
| | ${tg_port} | ${tg_node}= | First Interface
| | ${dut1_port} | ${dut1_node}= | Next Interface
| | ${dut2_port} | ${dut2_node}= | Last Interface
| | Set Suite Variable | ${tg_node}
| | Set Suite Variable | ${dut1_node}
| | Set Suite Variable | ${dut2_node}
| | Set Suite Variable | ${tg_port}
| | Set Suite Variable | ${dut1_port}
| | Set Suite Variable | ${dut2_port}

