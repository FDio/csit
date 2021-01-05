# Copyright (c) 2020 Intel and/or its affiliates.
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
| Library | resources.libraries.python.vsap.ab
|
| Documentation | L2 keywords to set up ab and to measure performance
| ... | parameters using ab.

*** Variables ***
| ${ab_ip_prefix}= | 24
| @{ab_ip_addrs}= | 192.168.10.2


*** Keywords ***
| Measure TLS requests or connections per second
| | [Documentation]
| | ... | Measure number of requests or connections per second using ab.
| |
| | ... | *Arguments:*
| | ... | - ${ciphers} - Specify SSL/TLS cipher suite
| | ... | - ${files} - Filename to be requested from the servers
| |
| | ... | *Example:*
| |
| | ... | \| Measure TLS requests or connections per second
| | ... | \| AES128-SHA \| 64 \| tls \| rps \|
| |
| | [Arguments] | ${ciphers} | ${files} | ${tls_tcp} | ${mode}
| |
| | ${output}= | Run ab | ${tg} | ${tls_tcp} | ${ciphers} | ${files} | ${mode}
| | Set test message | ${output}
