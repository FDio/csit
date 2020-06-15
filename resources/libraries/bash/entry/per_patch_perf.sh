#!/usr/bin/env bash

# Copyright (c) 2020 Cisco and/or its affiliates.
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

# This entry script does not change CSIT branch,
# use "with_oper_for_vpp.sh" wrapper for that.
#
# Assumptions:
# + There is a directory holding VPP repo with patch under test checked out.
# + It contains csit subdirectory with CSIT code to use (this script is there).
# + Everything needed to build VPP is already installed locally.
# Consequences:
# + At the end, VPP repo has parent commit checked out and built.
# + Directories build_root, build and csit are reset during the run.
# + The following directories (relative to VPP repo) are (re)created:
# ++ csit_new, csit_parent, build_new, build_parent,
# ++ archive, csit/archive, csit_download_dir.

# TODO: Implement some kind of VPP build caching.

# "set -eu" handles failures from the following two lines.
BASH_ENTRY_DIR="$(dirname $(readlink -e "${BASH_SOURCE[0]}"))"
BASH_FUNCTION_DIR="$(readlink -e "${BASH_ENTRY_DIR}/../function")"
source "${BASH_FUNCTION_DIR}/common.sh" || {
    echo "Source failed." >&2
    exit 1
}
source "${BASH_FUNCTION_DIR}/per_patch.sh" || die "Source failed."
# Cleanup needs ansible.
source "${BASH_FUNCTION_DIR}/ansible.sh" || die "Source failed."
common_dirs || die
check_prerequisites || die
set_perpatch_vpp_dir || die


## git checkout -b old
## # For the upcoming rebase, we need (22531) commit older than bisect lower bound.
## git reset --hard df213385d391f21d99eaeaf066f0130a20f7ccde
## git checkout -b new -t old
## # The following (22878) us first breakage, so its parent
## # is the upper bound (before altering the history).
## git reset --hard 12989b538881f9681f078cf1485c51df1251877a~
## git status
## # We want to remove the following Gerrit changes (by their commit hashes):
## # 22565: 46023762
## # And we want to squash the second into the first:
## # 22982: 67a6dcbc4 (line 194 after 22531)
## # 23288: 4d11b6cec (line 263 after 22531)
## # The offline editing magic, see https://stackoverflow.com/a/12395024
## # For inserting a line see https://fabianlee.org/2018/10/28/linux-using-sed-to-insert-lines-before-or-after-a-match/
## GIT_SEQUENCE_EDITOR='sed -i "/4d11b6cec\|46023762/d" "$1" && sed -i "/^pick 67a6dcbc4.*/a fixup 4d11b6cec" "$1"' git rebase -i old

git status


build_vpp_ubuntu "CURRENT" || die
set_aside_current_build_artifacts || die
initialize_csit_dirs || die
get_test_code "${1-}" || die
get_test_tag_string || die
set_perpatch_dut || die
select_topology || die
select_arch_os || die
activate_virtualenv "${VPP_DIR}" || die
generate_tests || die
archive_tests || die
reserve_and_cleanup_testbed || die
select_tags || die
# Support for interleaved measurements is kept for future.
iterations=1 # 8
for ((iter=0; iter<iterations; iter++)); do
    select_build "build_current" || die
    check_download_dir || die
    run_pybot || die
    copy_archives || die
    archive_parse_test_results "csit_current/${iter}" || die
done
untrap_and_unreserve_testbed || die
