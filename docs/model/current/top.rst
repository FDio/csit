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

This document is valid for CSIT model version 0.2.2.

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

Generally, files come in two variants. The "debug" variant is suitable
for debugging, while the "info" variant is suitable for processing by PAL.
Their structure is mostly identical, model definition mentions
if a particular node of the output is not identical in the two files.

JSON schema
-----------

CSIT model is formally defined as a collection of JSON schema documents,
one for each output file type.

The current version specifies only one output file type:
Info output for test case.

The authoritative JSON schema documents are in JSON format.
Git repository also contain YAML formatted document and conversion utilities,
which help with creating the JSON document (but are not authoritative).
