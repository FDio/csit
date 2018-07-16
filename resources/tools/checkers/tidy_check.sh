# Copyright (c) 2018 Cisco and/or its affiliates.
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

# This file does not have executable flag nor shebang.
# This file should be executed from tox, as the assumend working directory
# is different from where this file is located.

# The logic is inspired by OpenDaylight Integration/Test: tools/robot_check/.

set -exu

# Tidy escapes empty cell as '  ', making empty columns too wide for us.
# Ee are going to patch in our desired behavior.
py_to_patch=".tox/tidy/lib/python2.7/site-packages/robot/writer/formatters.py"
diff_to_patch_withpatch_file="resources/tools/checkers/tidy_formatters.diff"
patch --forward "$py_to_patch" < "$diff_to_patch_withpatch_file"
py_to_patch=".tox/tidy/lib/python2.7/site-packages/robot/writer/filewriters.py"
diff_to_patch_withpatch_file="resources/tools/checkers/tidy_filewriters.diff"
patch --forward "$py_to_patch" < "$diff_to_patch_withpatch_file"

# We need multiple more patches for this to work like we want:
# - Tolerate Copyright as a comment (or move to some suite setting).
# - Respect \ before endline as a command to go to next line.
# - Line length handling in general.

python -m robot.tidy --usepipes --recursive ./

lines=`git diff | tee tidy.log | wc -l`
if [ "$lines" != "0" ]; then
    echo "Tidy conflict diff nonzero: $lines"
    ## TODO: Enable when output size does more good than harm.
    # cat tidy.log
    echo
    echo "Tidy checker: FAIL"
    exit 1
fi

echo
echo "Tidy checker: PASS"
