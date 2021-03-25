# Copyright (c) 2021 Inter and/or its affiliates.
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
| Resource | resources/libraries/robot/shared/default.robot
|
| Library | resources.libraries.python.SetupFramework
| Library | resources.libraries.python.NGINX.NGINXTools
| Library | resources.libraries.python.NginxUtil
|
| Suite Setup | NGINX Setup
|
| Suite Teardown | Cleanup Nginx Framework On All Duts | ${nodes}

*** Keywords ***
| NGINX Setup
| | [Documentation]
| | ... | Setup suite Variables. Variables are used across performance testing.
| |
| | Run Keywords | Install NGINX framework on all DUTs | ${nodes}
| | ... | AND | Copy Nginx Conf | ${nodes}
