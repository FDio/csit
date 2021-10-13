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


Bytes
^^^^^

Value of this entry is an int, as reported by iperf3.
It is the amount of data transferred during the test.

TODO: Is this upload, download, or sum of both?
TODO: Which layer is used when computing this,
e.g. do retransmits or TCP/UDP/IP/Ethernet headers count?

Version
~~~~~~~

This scalar entry is present since version 0.4.0,
last patch update in version 0.4.0.
