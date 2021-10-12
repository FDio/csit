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


Rx bits per second
^^^^^^^^^^^^^^^^^^

Value of this entry is a float, as reported by vpp_echo.
May be not present if other client programs (e.g. iperf3) are used.
If it is present, "tx_bits_per_second" should also be present.
One of the two may be zero, if the user traffic is unidirectional.

Version
~~~~~~~

This scalar or structured entry is present since version 0.4.0,
last patch update in version 0.4.0.
