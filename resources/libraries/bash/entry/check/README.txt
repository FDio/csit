# Copyright (c) 2021 Cisco and/or its affiliates.
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

This directory contains checker scripts and other files they need.
Each checker script is assumed to be run from tox,
when working directory is set to ${CSIT_DIR}.
Each script should:
+ Return nonzero exit code when it fails.
++ The tox might ignore the code when the check is not blocking.
+ Write less verbose output to stderr.
+ Write (to stderr) PASSED or FAILED to help with debugging.
+ Direct more verbose output to appropriately named .log file.
+ Only the output suitable for automated processing by an external caller
  should be written to stdout.
++ The level of "less verbose" depends on check and state of codebase.
+ TODO: Should we carefully document which files are
  whitelisted/blacklisted for a particulat check?
