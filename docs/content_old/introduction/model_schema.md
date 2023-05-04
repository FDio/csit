---
bookHidden: true
title: "Model Schema"
---

# Model Schema

This document describes what is currently implemented in CSIT,
especially the export side (UTI), not import side (PAL).

## Version

This document is valid for CSIT model version 1.4.0.

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

## UTI

UTI stands for Unified Test Interface.
It mainly focuses on exporting information gathered during test run
into JSON output files.

### Output Structure

UTI outputs come in filesystem tree structure (single tree), where directories
correspond to suite levels and files correspond to suite setup, suite teardown
or any test case at this level of suite.
The directory name comes from SUITE_NAME Robot variable (the last part
as the previous parts are higher level suites), converted to lowercase.
If the suite name contains spaces (Robot converts underscores to spaces),
they are replaced with underscores.

The filesystem tree is rooted under tests/ (as suites in git are there),
and for each component (test case, suite setup, suite teardown).

Although we expect only ASCII text in the exported files,
we manipulate files using UTF-8 encoding,
so if Robot Framework uses a non-ascii character, it will be handled.

### JSON schemas

CSIT model is formally defined as a collection of JSON schema documents,
one for each output file type.

The current version specifies only one output file type:
Info output for test case.

The authoritative JSON schema documents are in JSON format.
Git repository also contains YAML formatted document and conversion utility,
which simplifies maintaining of the JSON document
(no need to track brackets and commas), but are not authoritative.
