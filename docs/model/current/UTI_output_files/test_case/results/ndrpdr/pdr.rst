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


Pdr
^^^

Value of this entry is a mapping with structured results.

The results refer to search for PDR (Partial Drop Rate).
The accepted loss ratio for PDR is half a percent.
Note that packets the Traffic Generator did not send
are also counted as lost packets.

See pdr subdirectory for description of its entries.

Version
~~~~~~~

This scalar entry is present since version 0.2.0,
last patch update in version 0.2.0.
