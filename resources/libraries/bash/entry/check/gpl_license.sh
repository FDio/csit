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
# if it detects any file edited or added since HEAD~
# containing a copyright notice in first 3 lines,
# but not GPL-based license.
# The offending files are stored to gpl_license.log (overwriting).

# "set -eu" handles failures from the following two lines.
BASH_CHECKS_DIR="$(dirname $(readlink -e "${BASH_SOURCE[0]}"))"
BASH_FUNCTION_DIR="$(readlink -e "${BASH_CHECKS_DIR}/../../function")"
source "${BASH_FUNCTION_DIR}/common.sh" || {
    echo "Source failed." >&2
    exit 1
}

IFS=$'\n'
gpl_files=($(git diff --name-only HEAD~ | grep '^GPL/' || true))
unset IFS
logfile="gpl_license.log"
truncate -s 0 "${logfile}" || die
# A change can have thousands of files, supress console output in the cycle.
set +x
for fil in "${gpl_files[@]}"; do
    if head -n 3 "${fil}" | fgrep -iq 'Copyright'; then
        # Copyrighted file, processed below.
        true
    else
        # Uncopyrighted files are allowed.
        # TODO: Should we have list of extesions that require Copyright?
        continue
    fi
    if fgrep -q 'GNU General Public License v2.0 or later' "${fil}"; then
        # This can be GPL only or the OR license, we accept both.
        # TODO: Should we require "Apache-2.0 OR GPL-2.0-or-later"?
        continue
    else
        echo "GPL license not detected: ${fil}" >> "${logfile}"
    fi
done
set -x
lines="$(< "${logfile}" wc -l)"
if [ "${lines}" != "0" ]; then
    # TODO: Decide which text goes to stdout and which to stderr.
    warn "Wrong licensed files in GPL directory detected: ${lines}"
    # TODO: Disable when output size does more harm than good.
    pwd
    cat "${logfile}" >&2
    warn
    warn "GPL license checker: FAIL"
    exit 1
fi

warn
warn "GPL license checker: PASS"
