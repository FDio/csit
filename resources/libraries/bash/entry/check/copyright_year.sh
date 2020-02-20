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

# This file should be executed from tox, as the assumed working directory
# is different from where this file is located.
# This file does not have executable flag nor shebang,
# to dissuade non-tox callers.

# This script runs a few grep-based command and fails
# if it detects any file edited or added since HEAD~
# containing a copyright notice in first 3 lines,
# but not the current year (in the same line).
# The offending lines are stored to copyright_year.log (overwriting).
#
# 3 lines were chosen, because first two lines could be shebang and empty line,
# and more than 3 lines would start failing on files with multiple copyright
# holders. There, only the last updating entity needs to bump its year,
# and put other copyright lines below.

# "set -eu" handles failures from the following two lines.
BASH_CHECKS_DIR="$(dirname $(readlink -e "${BASH_SOURCE[0]}"))"
BASH_FUNCTION_DIR="$(readlink -e "${BASH_CHECKS_DIR}/../../function")"
source "${BASH_FUNCTION_DIR}/common.sh" || {
    echo "Source failed." >&2
    exit 1
}

year=$(date +'%Y')
IFS=$'\n'
files=($(git diff --name-only HEAD~ || true))
unset IFS
truncate -s 0 "copyright_year.log" || die
for fil in "${files[@]}"; do
    # Greps do "fail" on 0 line output, we need to ignore that
    # as 0 lines is good. We need both set +e to ensure everything executes,
    # and || true later to avoid dying on zero.
    piped_command="set +ex; head -n 3 '${fil}' | fgrep -i 'Copyright'"
    piped_command+=" | fgrep -v '${year}' | awk '{print \"${fil}: \" \$0}'"
    piped_command+=" >> 'copyright_year.log'"
    wrong_strings="$(bash -c "${piped_command}" || true)" || die
done
lines="$(< "copyright_year.log" wc -l)"
if [ "${lines}" != "0" ]; then
    # TODO: Decide which text goes to stdout and which to stderr.
    warn "Copyright lines with wrong year detected: ${lines}"
    # TODO: Disable when output size does more harm than good.
    pwd
    cat "copyright_year.log" >&2
    warn
    warn "Copyright year checker: FAIL"
    exit 1
fi

warn
warn "Copyright year checker: PASS"
