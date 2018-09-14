# Copyright (c) 2019 Cisco and/or its affiliates.
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

set -exuo pipefail

# This file should be executed from tox, as the assumend working directory
# is different from where this file is located.
# This file does not have executable flag nor shebang,
# to dissuade non-tox callers.

# This script runs pylint and propagates its exit code.
# Config is taken from pylint.cfg, and proper virtualenv is assumed to be active.
# The pylint output stored to pylint.log (overwriting).

# Only if and echo are used. Include common.sh if die-worthy command is added.

pylint_args=("--rcfile=pylint.cfg" "resources/" "tests/")
if pylint "${pylint_args[@]}" > "pylint.log"; then
    echo
    echo "Pylint checker: PASS"
else
    # TODO: Decide which text goes to stdout and which to stderr.
    echo "Pylint exited with nonzero status."
    ## TODO: Enable when output size does more good than harm.
    # cat "pylint.log"
    echo
    echo "Pylint checker: FAIL"
    exit 1
fi
