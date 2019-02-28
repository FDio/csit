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

# This script starts with copying ${CSIT_DIR}/tests to ${GENERATED_DIR}/.
# Then the script runs every executable *.py script anywhere in the copied dir,
# the working directory temporarily changed to where the *.py file is.
# Proper virtualenv is assumed to be active.
# Then another directory in ${GENERATED_DIR} is created, where
# the just generated content is copied and then overwitten by the non-generated.
# If "diff -dur" sees any changes by the overwrite, this script fails.
# The diff output is stored to autogen.log (overwriting).
# The executed *.py files are assumed to be robot suite generators,
# any change means the contribution is not consistent with the regenerated code.

# "set -eu" handles failures from the following two lines.
BASH_CHECKS_DIR="$(dirname $(readlink -e "${BASH_SOURCE[0]}"))"
BASH_FUNCTION_DIR="$(readlink -e "${BASH_CHECKS_DIR}/../../function")"
source "${BASH_FUNCTION_DIR}/common.sh" || {
    echo "Source failed." >&2
    exit 1
}
common_dirs
work_dir="$(pwd)" || die
trap "cd '${work_dir}'" EXIT || die

generate_tests

rm -rf "${GENERATED_DIR}/tests_tmp"
cp -r "${GENERATED_DIR}/tests" "${GENERATED_DIR}/tests_tmp"
# Default cp behavior is to put inside a targed dir, not to override.
cp -rf "${CSIT_DIR}/tests"/* "${GENERATED_DIR}/tests_tmp"/
# TODO: Do we want to archive ${GENERATED_DIR}?
# I think archiving the diff is enough.

diff_cmd=("diff" "-dur" "${GENERATED_DIR}/tests_tmp" "${GENERATED_DIR}/tests")
lines="$("${diff_cmd[@]}" | tee "autogen.log" | wc -l)" || die
if [ "${lines}" != "0" ]; then
    # TODO: Decide which text goes to stdout and which to stderr.
    warn "Autogen conflict diff nonzero lines: ${lines}"
    # TODO: Disable if output size does more harm than good.
    cat "autogen.log" >&2
    warn
    warn "Autogen checker: FAIL"
    exit 1
fi

warn
warn "Autogen checker: PASS"
