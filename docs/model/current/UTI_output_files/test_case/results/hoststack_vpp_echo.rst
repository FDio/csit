..
   Copyright (c) 2021 Cisco and/or its affiliates.
   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at:
..
       http://www.apache.org/licenses/LICENSE-2.0
..
   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.


Hoststack VPP echo
^^^^^^^^^^^^^^^^^^

Value of this entry is a list, holding result items for hoststack_vpp_echo
test type. Each result item is a mapping,
see hoststack_vpp_echo subdirectory for its entries.

This output type is used mainly for udpquic tests,
as iperf3 does not support QUIC.

Tests with vpp_echo utility gather outputs from both client and server programs,
appearing as two result items in this list.
The items are distinguishible by "role" sub-entry, but only if the program
passes. Failed programs are not necessarily distinguishable.

TODO: Refactor keywords so even failed program outputs know their role.

Version
~~~~~~~

This list entry is present since version 0.4.0,
last patch update in version 0.4.0.
