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

# This script examines any file edited since HEAD~ (filtered by extension),
# and fails if no line with "Copyright" and the current year is found.
# The list of offending files is written to copyright.log (overwriting).
# The log also specifies whether the copyright is missing or outdated.

# "set -eu" handles failures from the following two lines.
BASH_CHECKS_DIR="$(dirname $(readlink -e "${BASH_SOURCE[0]}"))"
BASH_FUNCTION_DIR="$(readlink -e "${BASH_CHECKS_DIR}/../../function")"
source "${BASH_FUNCTION_DIR}/common.sh" || {
    echo "Source failed." >&2
    exit 1
}

fulldate=$(date)
year="${fulldate##* }"
# Regexp allowing only files we expect to need copyright.
# Start from an array, each item is to be prepended by ., appended by $,
# and joined by |.
extensions_array=("gitgnore" "ini" "md" "py" "robot" "rst" "sh" "txt" "yaml")
pattern=""
for extension in "${extensions_array[@]}"; do
    pattern+="\.${extension}"'$'"\|"
done
# One more "extension" just to avoid trailing pipe.
pattern+="/Dockerfile"'$'
# Get array of edited files.
# Commands to expand, pipe has to be left out.
cmd1="git diff --name-only HEAD~"
cmd2="grep \"${pattern}\""
# When calling, commands has to be without quotes.
readarray -t file_array <<<$(${cmd1} | ${cmd2}) || {
    # We need to tolerate changes that only edit other files.
    errors=$(${cmd1} | ${cmd2} 2>&1 || true)
    if [[ "${errors}" ]]; then
        # TODO: do we need to echo errors?
        die "Failure at getting list of files to check copyright in."
    fi
    # Empty file array is accepted.
    # Accidentally, if "git diff" fails, we still proceed with empty array.
}
logfile="copyright.log"
truncate --size 0 "${logfile}" || die "truncate failed"
# Temporary +x so big changes do not spam.
set +x
for filename in "${file_array[@]}"; do
    if ! fgrep -q "Copyright" "${filename}"; then
        echo "No copyright found in file: ${filename}" >> "${logfile}"
    elif ! fgrep "Copyright" "${filename}" | fgrep -q "${year}"; then
        echo "No year ${year} copyright found in: ${filename}" >> "${logfile}"
    fi
done
set -x
if [ -s "${logfile}" ]; then
    warn "Copyright violations detected."
    # TODO: Disable when output size does more harm than good.
    cat "${logfile}" >&2
    warn
    warn "Copyright checker: FAIL"
    exit 1
fi
warn
warn "Copyright checker: PASS"
