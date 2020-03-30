# Copyright (c) 2020 Cisco and/or its affiliates.
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

# This file should be executed from tox, as the assumed working directory
# is different from where this file is located.
# This file does not have executable flag nor shebang,
# to dissuade non-tox callers.

# This script parses the commit message (for HEAD commit)
# and runs a few checks on its content.

# TODO: Add feature checking.

# "set -eu" handles failures from the following two lines.
BASH_CHECKS_DIR="$(dirname $(readlink -e "${BASH_SOURCE[0]}"))"
BASH_FUNCTION_DIR="$(readlink -e "${BASH_CHECKS_DIR}/../../function")"
source "${BASH_FUNCTION_DIR}/common.sh" || {
    echo "Source failed." >&2
    exit 1
}

known_types="feature fix refactor improvement style docs"
type=$(git show -s --format=%b --no-color | sed -ne 's/^Type:[[:space:]]*//p')

# Check that Message body contains valid Type: entry
is_known=false
for i in ${known_types}; do
    [ "${i}" = "${type}" ] && is_known=true
done
if [ ${is_known} = "false" ] ; then
    warn "Unknown commit type '${type}' in commit message body."
    warn "Commit message must contain known 'Type:' entry."
    warn "Known types are: ${known_types}"
    warn
    warn "Commit message checker: FAIL"
    exit 1
fi

warn
warn "Commit message checker: PASS"
