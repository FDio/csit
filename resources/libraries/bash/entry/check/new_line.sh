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

# This script runs a grep-based command and fails if it detects any lines
# edited or added since HEAD~ and longer than 80 characters.
# The grep output stored to new_lines.log (overwriting).

# See lines.log to locate where the lines are.

# "set -eu" handles failures from the following two lines.
BASH_CHECKS_DIR="$(dirname $(readlink -e "${BASH_SOURCE[0]}"))"
BASH_FUNCTION_DIR="$(readlink -e "${BASH_CHECKS_DIR}/../../function")"
source "${BASH_FUNCTION_DIR}/common.sh" || {
    echo "Source failed." >&2
    exit 1
}

# Greps do "fail" on zero line output, we need to ignore that in the final grep.
piped_command="set -exuo pipefail && git diff -U0 HEAD~ | grep '^\+' | "
piped_command+="cut -c2- | grep -v '^\+\+ ' | { grep '.\{81\}' || true; } | "
piped_command+="tee 'new_lines.log' | wc -l"
lines="$(bash -c "${piped_command}")" || die
if [ "${lines}" != "0" ]; then
    # TODO: Decide which text goes to stdout and which to stderr.
    warn "Long lines detected: ${lines}"
    # TODO: Disable when output size does more harm than good.
    cat "new_lines.log" >&2
    warn
    warn "New line length checker: FAIL"
    exit 1
fi

warn
warn "New line length checker: PASS"
