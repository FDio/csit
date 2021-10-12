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


Samples
^^^^^^^

Value of this entry is a list of floats.

Each item of the list is a receive rate for one MRR trial.
For rate unit, see "unit" entry.

Currently, the tests are exporting approximated receive rate.
That means the actual trial duration is measured
(as opposed to trusting traffic generator to honot its target duration),
so the resulting values contain noise from time measurement
and can be lower than the real performance (due to various time overheads).

Version
~~~~~~~

This scalar entry is present since version 0.2.0,
last patch update in version 0.2.0.
