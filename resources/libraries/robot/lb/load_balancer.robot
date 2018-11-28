# Copyright (c) 2018 Cisco and/or its affiliates.
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
| Variables | resources/libraries/python/topology.py
| Library | resources.libraries.python.topology.Topology
| Library | resources.libraries.python.LoadBalancerUtil

*** Keywords ***

| Initialize lb_maglev
| | [Documentation] | Start the load balancer maglev mode on each DUT.
| | ...
| | ${duts}= | Get Matches | ${nodes} | DUT*
| | :FOR | ${dut} | IN | @{duts}
| | | Vpp Setup Load Balancer | ${nodes} | ${nodes['${dut}']} | ${${dut}_if1}
| | | ... | ${${dut}_if2} | maglev

| Initialize lb_l3dsr
| | [Documentation] | Start the load balancer l3dsr mode on each DUT.
| | ...
| | ${duts}= | Get Matches | ${nodes} | DUT*
| | :FOR | ${dut} | IN | @{duts}
| | | Vpp Setup Load Balancer | ${nodes} | ${nodes['${dut}']} | ${${dut}_if1}
| | | ... | ${${dut}_if2} | l3dsr

| Initialize lb_nat
| | [Documentation] | Start the load balancer nat mode on each DUT.
| | ...
| | ${duts}= | Get Matches | ${nodes} | DUT*
| | :FOR | ${dut} | IN | @{duts}
| | | Vpp Setup Load Balancer | ${nodes} | ${nodes['${dut}']} | ${${dut}_if1}
| | | ... | ${${dut}_if2} | nat
