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

set -exuo pipefail

# This file should be executed from tox, as the assumed working directory
# is different from where this file is located.
# This file does not have executable flag nor shebang,
# to dissuade non-tox callers.

# This script assumes we are in a git repo and investigates commit message
# of HEAD. The first line should contain colon exactly once.
# The part of line preceding the colon is called prefix,
# and it has to contain exactly one uppercase letter.
# This rejects "DO_NOT_MERGE" and "WiP".
# TODO: Improve the criterion even more, to reject "Wip".

# The intended use is for this to be the first check a commit is subjected to,
# and to avoid more expensive checks if this one fails.

# "set -eu" handles failures from the following two lines.
BASH_CHECKS_DIR="$(dirname $(readlink -e "${BASH_SOURCE[0]}"))"
BASH_FUNCTION_DIR="$(readlink -e "${BASH_CHECKS_DIR}/../../function")"
source "${BASH_FUNCTION_DIR}/common.sh" || {
    echo "Source failed." >&2
    exit 1
}

first_line=$(git show -s --format=%s --no-color)
# Character counting taken from https://stackoverflow.com/a/41119233
colon_count=$(echo "${first_line}" | tr -cd ':' | wc -c)
if [[ "${colon_count}" != "1" ]]; then
    warn "First line of commit message has to contain colon once!"
    warn "Commit message checker: FAIL"
    exit 1
fi
prefix="${first_line%%:*}"
uppercase_count=$(echo "${prefix}" | tr -dc 'A-Z' | wc -c)
if [[ "${uppercase_count}" != "1" ]]; then
    warn "Prefix of commit message has to contain exactly one uppercase letter!"
    warn "Commit message checker: FAIL"
    exit 1
fi

warn
warn "Commit message checker: PASS"
