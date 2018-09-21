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

# This script uses robot.tidy to overwite all robot files
# with their "canonic" form, and then runs "git diff".
# Proper virtualenv is assumed to be active.
# This script passes only if no line has changed.
# The diff output stored to tidy.log (overwriting).
# The logic is inspired by OpenDaylight Integration/Test: tools/robot_check/.

# "set -eu" handles failures from the following two lines.
BASH_CHECKS_DIR="$(dirname $(readlink -e "${BASH_SOURCE[0]}"))"
BASH_FUNCTION_DIR="$(readlink -e "${BASH_CHECKS_DIR}/../../function")"
source "${BASH_FUNCTION_DIR}/common.sh" || {
    echo "Source failed." >&2
    exit 1
}

# Tidy escapes empty cell as '  ', making empty columns too wide for us.
# We are going to patch in our desired behavior.
py_to_patch=".tox/tidy/lib/python2.7/site-packages/robot/writer/formatters.py"
diff_to_patch_with="resources/tools/checkers/tidy_formatters.diff"
patch --forward "$py_to_patch" < "$diff_to_patch_with" || die
py_to_patch=".tox/tidy/lib/python2.7/site-packages/robot/writer/filewriters.py"
diff_to_patch_with="resources/tools/checkers/tidy_filewriters.diff"
patch --forward "$py_to_patch" < "$diff_to_patch_with" || die

# We need multiple more patches for this to work like we want:
# - Tolerate Copyright as a comment (or move to some suite setting).
# - Respect \ before endline as a command to go to next line.
# - Line length handling in general.

python -m robot.tidy --usepipes --recursive ./ || die

lines=$(git diff | tee tidy.log | wc -l) || die
if [ "${lines}" != "0" ]; then
    # TODO: Decide which text goes to stdout and which to stderr.
    warn "Tidy conflict diff nonzero: ${lines}"
    ## TODO: Enable when output size does more good than harm.
    # cat tidy.log >&2
    warn
    warn "Tidy checker: FAIL"
    exit 1
fi

warn
warn "Tidy checker: PASS"
