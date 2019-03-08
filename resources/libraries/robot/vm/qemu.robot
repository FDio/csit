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
| Library | resources.libraries.python.QemuUtils

*** Keywords ***
| Stop and clear QEMU
| | [Documentation]
| | ... | Stop QEMU, clear used sockets and close SSH connection running on
| | ... | ${dut}, ${vm} is VM node info dictionary returned by qemu_start.
| | [Arguments] | ${dut} | ${vm}
| | Run Keyword | ${vm}.Qemu Set Node | ${dut}
| | Run Keyword | ${vm}.Qemu Kill
| | Run Keyword | ${vm}.Qemu Clear Socks
