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

# This script run every executable *.py script anywhere within tests/ dir,
# the working directory temporarily changed to where the *.py file is.
# Proper virtualenv is assumed to be active.
# If "git diff" sees any change, this script fails.
# The diff output stored to autogen.log (overwriting).
# The *.py files are assumed to be robot suite generators,
# any change means the contribution does not match the generated code.

# "set -eu" handles failures from the following two lines.
BASH_CHECKS_DIR="$(dirname $(readlink -e "${BASH_SOURCE[0]}"))"
BASH_FUNCTION_DIR="$(readlink -e "${BASH_CHECKS_DIR}/../../function")"
source "${BASH_FUNCTION_DIR}/common.sh" || {
    echo "Source failed." >&2
    exit 1
}

work_dir="$(pwd)" || die
trap "cd '${work_dir}'" EXIT || die
file_list="$(find ./tests -type f -executable -name '*.py')" || die

for gen in ${file_list}; do
    directory="$(dirname "${gen}")" || die
    filename="$(basename "${gen}")" || die
    pushd "${directory}" || die
    ./"${filename}" || die
    popd || die
done

lines="$(git diff | tee "autogen.log" | wc -l)" || die
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
