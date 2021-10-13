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


CSIT model
^^^^^^^^^^

This document describes what is currently implemented in CSIT,
especially the export side (UTI), not import side (PAL).

Version
~~~~~~~

This document tree is valid for CSIT model version OUTDATED 0_4_0.

It is recommended to use semantic versioning: https://semver.org/
That means, if the new model misses a field present in the old model,
bump the major version. If the new model adds a field
not present in the old model, bump the minor version.
Any other edit in the implmenetation (or documentation) bumps the patch version.
If you change value type or formatting,
consider whether the parser (PAL) understands the new value correctly.
Renaming a field is the same as adding a new one and removing the old one.
Parser (PAL) has to know exact major version and minimal minor version,
and unless bugs, it can ignore patch version and bumped minor version.

UTI
~~~

UTI stands for Unified Test Interface.
It mainly focuses on exporting information gathered during test run
into JSON output files.

Output Structure
-----------------

UTI outputs come in filesystem tree structure, where directories
correspond to suites and files correspond to suite setup, suite teardown
or any test case at this level of suite.
The directory name comes from SUITE_NAME Robot variable (the last part
as the previous parts are higher level suites), it is in CamelCase.
If the suite name contains spaces (Robot converts underscores to spaces),
they are replaced with underscores.

For the naming of the files in the directories, see file documentation.

Generally, files come in two variants. The "debug" variant is suitable
for debugging, while the "info" variant is suitable for processing by PAL.
Their structure is mostly identical, documentation mentions
if a particular node of the output is not identical in the two files.

Documentation structure
-----------------------

UTI documentation is following a tree structure.
Each node of the tree is one .rst file. If the node has children nodes,
they are placed in a subdirectory corresponding to their parent's name.
If the file name (without .rst) matches directory name,
the file describes the whole container (and not just one of its entries
as other files).

The node can be describing an output file, a JSON entry (of a mapping),
a JSON element (of a list), each of those can have scalar,
list or mapping value.
