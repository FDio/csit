# Copyright (c) 2023 Cisco and/or its affiliates.
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

# This is a fixer script, so be careful before starting it.
# It is recommended to always commit your recent edits before running this,
# and use "git diff" after running this to confirm the edits are correct.
# Otherwise you can lose your edits and introduce bad edits.

# This script runs a variant of "git diff" command
# to get the list of edited files, and few sed commands to edit the year
# if "20.." pattern matches in first 3 lines.
# No detection of "copyright", so edits can apply at surprising places.

# 3 lines were chosen, because first two lines could be shebang and empty line.

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
# A change can have thousands of files, supress console output for the cycle.
set +x
for fil in "${files[@]}"; do
    if [[ -f "${fil}" ]]; then
        sed -i "1 s/20../${year}/g" "${fil}"
        sed -i "2 s/20../${year}/g" "${fil}"
        sed -i "3 s/20../${year}/g" "${fil}"
    # Else the file was actually deleted and sed would fail.
    fi
done
set -x
