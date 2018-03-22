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
| Library | resources.libraries.python.Trace
| Library | resources.libraries.python.TrafficScriptExecutor
| Library | resources.libraries.python.DMM.SingleCliSer
| Resource | resources/libraries/robot/shared/default.robot
| Resource | resources/libraries/robot/shared/interfaces.robot
| Resource | resources/libraries/robot/shared/counters.robot
| Resource | resources/libraries/robot/dmm/dmm_utils.robot
| Force Tags | 3_NODE_SINGLE_LINK_TOPO | VM_ENV | FUNCTEST | DMM
| Documentation | *DMM vs epoll test suite.*
| ...
| ... | Test suite uses 3-node topology TG - DUT1 - DUT2 - TG with single link
| ... | between nodes. From this topology only DUT1 and DUT2 nodes are used.
| ... | here we test the 1. test the vs_epool and vc_epoll

*** Test Cases ***
| TC01: DMM base vs epoll test case
| | Given Path for 2-node testing is set | ${nodes['DUT1']} | ${nodes['DUT2']}
| | And Pick out the port used to execute test
| | When Exec the base vs epoll test | ${dut1_node} | ${dut2_node}
| | Echo DMM logs | ${dut2_node}
| | ${no_packet_loss} = | Get the test result | ${dut2_node}
| | Then Should Not Be Equal As Integers | ${no_packet_loss} | 0