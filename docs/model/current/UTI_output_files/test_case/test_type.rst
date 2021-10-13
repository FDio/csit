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


Test type
^^^^^^^^^

This entry has a string value, set individually by tests.
Some tests may not set this, the entry is not present in that case
(test type is unknown, probably not one of the known types).

Currently implemented values are "mrr", "ndrpdr" and "soak".

As the result mapping contains a sub-mapping named after the test type,
this information is derived, so this entry appears only in info output.

Version
~~~~~~~

This scalar entry is present since version 0.2.0,
last patch update in version 0.2.0.
