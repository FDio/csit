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

#TODO: documentation

*** Settings ***
| Resource | resources/libraries/robot/interfaces.robot

*** Keywords ***
| GRE tunnel interface is created and up
| | [Documentation] | TBD
#TODO: documentation
| | [Arguments] | ${dut} | ${source_ip_address} | ${destination_ip_address}
| | ${name} | ${index}= | Create GRE Tunnel Interface
| | | | ... | ${dut} | ${source_ip_address} | ${destination_ip_address}
| | Set Interface State | ${dut} | ${index} | up
| | [Return] | ${name} | ${index}