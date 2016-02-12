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

*** Settings ***
| Resource | resources/libraries/robot/default.robot
| Library | resources/libraries/python/SetupFramework.py
| Library | resources.libraries.python.topology.Topology
| Suite Setup | Run Keywords | Setup Framework | ${nodes}
| ...         | AND          | Start VPP Service On All DUTs | ${nodes}
| ...         | AND          | Update All Interface Data On All Nodes | ${nodes}

