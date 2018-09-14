# Copyright (c) 2018 Cisco and/or its affiliates.
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

# This file does not have executable flag nor shebang.
# This file should be executed from tox, as the assumend working directory
# is different from where this file is located.

function die () {
    echo "${1:-Previous command returned nonzero code. Aborting.}" >&2
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
    echo "Autogen conflict diff nonzero lines: ${lines}"
    # TODO: Disable if output size does more harm than good.
    cat "autogen.log"
    echo
    echo "Autogen checker: FAIL"
    exit 1
fi

echo
echo "Autogen checker: PASS"
