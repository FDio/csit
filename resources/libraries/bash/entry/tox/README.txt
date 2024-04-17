# Copyright (c) 2024 Cisco and/or its affiliates.
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at:
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

This directory contains tox scripts and other files they need.
Generally, a tox script is either a checker (suitable for automated verify)
or a fixer (manually started, risky as uncommitted edits can be lost).

In the tox verify job we want to avoid running fixers,
as they can affect what other checkers see
(e.g. autogen fixer could add more too long lines).
That is why we keep fixers separate from checkers in principle,
even for fairly safe tasks (e.g. bumping copyright years).

Each tox script is assumed to be run from tox,
when working directory is set to ${CSIT_DIR}.

Each checker script should:
+ Return nonzero exit code when it fails.
++ The tox might ignore the code when the check is not blocking.
+ Write less verbose output to stderr.
+ Write (to stderr) PASSED or FAILED to help with debugging.
+ Direct more verbose output to appropriately named .log file.
+ Only the output suitable for automated processing by an external caller
  should be written to stdout.
++ The level of "less verbose" depends on check and state of codebase.

Each fixer script should:
+ Perform edits on current filesystem
+ Not assume git is clean (there may be uncommitted edits).
+ Use "git diff HEAD~" to get both comitted and uncomitted edits to analyze.
+ Output whatever it wants (possibly nothing).
