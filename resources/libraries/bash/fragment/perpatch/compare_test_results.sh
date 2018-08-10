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

set -exuo pipefail

# Variables read:
# - BASH_FRAGMENT_DIR - Path to directory holding parser fragment.

source "${BASH_FRAGMENT_DIR}/perpatch/parse_bmrr_results.sh"

function compare_test_results () {

    set -exuo pipefail

    # Variables read:
    # - VPP_DIR - Path to directory with VPP git repo (at least built parts).
    # - ARCHIVE_DIR - Path to where robot result files are created in.
    # - PYTHON_SCRIPTS_DIR - Path to directory holding comparison utility.
    # Directories recreated:
    # - csit_parent - Sibling to csit directory, for holding results
    #   of parent build.
    # Functions called:
    # - die - Print to stderr and exit, defined in common_functions.sh
    # - parse_bmrr_results - See eponymous fragment file.
    # Exit code:
    # - 0 - If the comparison utility sees no regression (nor data error).
    # - 1 - If the comparison utility sees a regression (or data error).

    cd "${VPP_DIR}" || die 1 "Change directory operation failed."
    rm -rf "csit_parent" || die 1 "Remove operation failed."
    mkdir -p "csit_parent" || die 1 "Directory creation failed."
    for filename in "output.xml" "log.html" "report.html"; do
        mv "${ARCHIVE_DIR}/${filename}" "csit_parent/${filename}" || {
            die 1 "Attempt to move '${filename}' failed."
        }
    done
    parse_bmrr_results "csit_parent" || {
        die 1 "The function should have died on error."
    }

    # Reusing CSIT main virtualenv.
    pip install -r "${PYTHON_SCRIPTS_DIR}/perpatch_requirements.txt" || {
        die 1 "Perpatch Python requirements installation failed."
    }
    python "${PYTHON_SCRIPTS_DIR}/compare_perpatch.py"
    # The exit code determines the vote result.
}
