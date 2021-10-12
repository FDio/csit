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


Hoststack
^^^^^^^^^

Value of this entry is a list, holding result items for "hoststack" test type.
Each result item is a mapping, see hoststack subdirectory for its entries.

Currently, all tests in hoststack directory, except VSAP which uses "ab",
are using "hoststack" result type.

The type covers several subtypes differing in the server or client program.
Some subtypes gather outputs from both client and server programs
(appearing as two result items in this list),
some gather only output from the client program.

Even the same client program can produce outputs of different structure,
e.g. iperf3 counting retransmits only in TCP mode, not in UDP mode.
To accomodate adding more clients and servers in the future,
most of the output is intentionally not parsed, just copied as a string.

Version
~~~~~~~

This list entry is present since version 0.4.0,
last patch update in version 0.4.0.
