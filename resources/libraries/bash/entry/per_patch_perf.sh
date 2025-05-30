#!/usr/bin/env bash

# Copyright (c) 2025 Cisco and/or its affiliates.
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
# ++ archives, csit/archives, csit_download_dir.

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
get_test_code "${1-}" || die
get_test_tag_string || die
set_perpatch_vpp_dir || die
git status || die
git describe || die
build_vpp_ubuntu "CURRENT" || die
set_aside_build_artifacts "current" || die
git checkout "HEAD~" || die "Failed to checkout parent commit."
git status || die
git describe || die
build_vpp_ubuntu "PARENT" || die
set_aside_build_artifacts "parent" || die
initialize_csit_dirs "parent" "current" || die
set_perpatch_dut || die
select_topology || die
select_arch_os || die
activate_virtualenv "${VPP_DIR}" || die
generate_tests || die
archive_tests || die
reserve_and_cleanup_testbed || die
# Support for interleaved measurements is kept for future.
iterations=1 # 8
for ((iter=0; iter<iterations; iter++)); do
    if ((iter)); then
        # Function reserve_and_cleanup_testbed has already cleaned it once,
        # but we need to clean it explicitly on subsequent iterations.
        ansible_playbook "cleanup" || die
    fi
    # Testing current first. Good for early failures or for API changes.
    select_build "build_current" || die
    check_download_dir || die
    run_robot || die
    move_test_results "csit_current/${iter}" || die
    # TODO: Use less heavy way to avoid apt remove failures.
    ansible_playbook "cleanup" || die
    select_build "build_parent" || die
    check_download_dir || die
    run_robot || die
    move_test_results "csit_parent/${iter}" || die
done
untrap_and_unreserve_testbed || die
compare_test_results  # The error code becomes this script's error code.
