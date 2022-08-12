# Copyright (c) 2022 Cisco and/or its affiliates.
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

# This script call a Python script to make sure
# the yaml and json formats of UTI model schemas are in sync.
# The check is skipped if no edits in schema directory are detected.

# "set -eu" handles failures from the following two lines.
BASH_CHECKS_DIR="$(dirname $(readlink -e "${BASH_SOURCE[0]}"))"
BASH_FUNCTION_DIR="$(readlink -e "${BASH_CHECKS_DIR}/../../function")"
source "${BASH_FUNCTION_DIR}/common.sh" || {
    echo "Source failed." >&2
    exit 1
}
common_dirs || die

impl_log="edited_files.log"
git diff --name-only HEAD~ > "${impl_log}"
if ! grep -q '^docs/model/schema/' "${impl_log}"; then
    # Failing grep means no model edits.
    warn "No model schema edits detected."
    warn
    warn "CSIT model yaml checker: PASS"
    exit 0
fi

pushd "${CSIT_DIR}/docs/model/schema"
if ! python3 "check_yaml2json.py"; then
    warn
    warn "CSIT model yaml checker: FAIL"
    popd
    exit 1
fi
popd

warn "Model schema edited, json in sync with yaml."
warn
warn "CSIT model yaml checker: PASS"
exit 0
