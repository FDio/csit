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

# This script runs a few grep-based commands and fails
# if it detects any VPP perf suite not using perfmon plugin
# (before autogeneration).
# The offending files are stored to perfmon.log (overwriting).

# "set -eu" handles failures from the following two lines.
BASH_CHECKS_DIR="$(dirname $(readlink -e "${BASH_SOURCE[0]}"))"
BASH_FUNCTION_DIR="$(readlink -e "${BASH_CHECKS_DIR}/../../function")"
source "${BASH_FUNCTION_DIR}/common.sh" || {
    echo "Source failed." >&2
    exit 1
}

log="perfmon.log"
truncate -s 0 "${log}" || die
plugin="@{plugins_to_enable}"
where="tests/vpp/perf/"
needs="perfmon_plugin.so"
# The second grep fails in good case of no wrong suite.
set +e
fgrep -rn "${plugin}" "${where}" | fgrep -v "${needs}" >> "${log}"
set -e
lines=$(wc -l "${log}" | cut -d ' ' -f 1)
if [ "${lines}" != "0" ]; then
    warn "Suites without perfmon plugin detected: ${lines}"
    cat "${log}" >&2
    warn
    warn "Perfmon checker: FAIL"
    exit 1
fi

warn
warn "Perfmon checker: PASS"
