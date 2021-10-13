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


Latency forward
^^^^^^^^^^^^^^^

Value of this entry is a mapping with structured results
related to latency part of NDRPDR test, for forward traffic diration.
It is the direction used in unidirectional traffic profiles.

See latency_forward subdirectory for its entries.

ASTF profiles and IMIX STL profile do not support latency information,
so for those tests this mapping is missing (info output)
or artificial (debug output).

Version
~~~~~~~

This structured entry is present since version 0.2.0,
last patch update in version 0.2.0.
