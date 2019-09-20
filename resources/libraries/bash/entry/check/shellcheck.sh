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

# This script runs shellcheck and propagates its exit code.
# The output is stored in checkstyle format to shellcheck.xml (overwriting).

# "set -eu" handles failures from the following two lines.
BASH_CHECKS_DIR="$(dirname "$(readlink -e "${BASH_SOURCE[0]}")")"
BASH_FUNCTION_DIR="$(readlink -e "${BASH_CHECKS_DIR}/../../function")"
source "${BASH_FUNCTION_DIR}/common.sh" || {
    echo "Source failed." >&2
    exit 1
}
shellcheck_args=("--shell=bash" "--format=checkstyle")
find_args=("." "-name" "*.sh" "!" "-path" "*/.*" "-print0")
if find "${find_args[@]}" | \
        xargs -0r shellcheck "${shellcheck_args[@]}" > "shellcheck.xml"; then
    warn
    warn "Shellcheck checker: PASS"
else
    # TODO: Decide which text goes to stdout and which to stderr.
    warn "Shellcheck exited with nonzero status."
    ## TODO: Enable when output size does more good than harm.
    # cat "shellcheck.log" >&2
    warn
    warn "Shellcheck checker: FAIL"
    exit 1
fi
