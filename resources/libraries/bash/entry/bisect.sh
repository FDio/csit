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

# This entry script does not change which CSIT branch is used,
# use "with_oper_for_vpp.sh" wrapper for that.
#
# This script is to be used for locating performance regressions
# (or breakages, or progressions, or fixes).
# It uses "git bisect" commands on the VPP repository,
# between the triggered VPP patch and a commit specified in the first argument
# of the gerrit comment text.
# The other arguments are used as tag expressions for selecting tests as usual.
# Currently only MRR test type is supported.
#
# Logs are present in the archive directory, bu usually the main output
# is the offending commit as identified by "git bisect", visible in console.
#
# While selecting just one testcase is the intended use,
# this script should be able to deal with multiple testcases as well,
# grouping all the values together. This usually inflates
# the standard deviation, but it is not clear how that affects the bisection.
#
# For the bisection decision, jumpavg library is used,
# deciding whether shorter description is achieved by forcefully grouping
# the middle results with the old, or with the new ones.
#
# If any test failure happens, one retry is attempted.
# If all tries fail, an artificial result is used to distinguish
# from normal results. Currently, the value 2.0, with the same multiplicity
# is used for fail results.
#
# Note that if there was a VPP API change that affects tests in the interval,
# there usually is not good way for single CSIT commit to work there.
# You can try manually reverting the CSIT changes to make tests pass,
# possibly needing to search over multiple subintervals.
#
# If a regression happens during a subinterval where the test fails
# due to bug in VPP, you may try to create a new commit chain
# with the fix cherry-picked to the start of the interval.
# Do not do that on Gerrit, as that would open multiple fake changes.
#
# Assumptions:
# + There is a directory holding VPP repo with patch under test checked out.
# + It contains csit subdirectory with CSIT code to use (this script is there).
# + Everything needed to build VPP is already installed locally.
# Consequences:
# + Working directory is switched to the VPP repo root.
# + At the end, VPP repo has checked out and built some commit,
#   used last in "git bisect".
# + Directories build_root, build and csit are reset during the run.
# + The following directories (relative to VPP repo) are (re)created:
# ++ csit_current, csit_parent, build_current, build_parent,
# ++ archive, csit/archive, csit/download_dir.
# Arguments:
# - ${1} - If present, override JOB_NAME to simplify manual usage.

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
get_test_code "${1-}" || die
get_test_tag_string || die
# Unfortunately, git bisect only works at the top of the repo.
cd "${VPP_DIR}" || die
git bisect start || die
# TODO: Can we add a trap for "git bisect reset" or even "deactivate",
# without affecting the inner trap for unreserve and cleanup?

# Important commits affecting behavior.
# 2019-08-20:
# v20.01-rc0-68   053204ab039d34a990ff0e14c32ce3b294fcce0e
#  - Interface API, *_up_down => flags.
# 2019-08-21:
# v20.01-rc0-78   b6103105f99e0c7f210a9596f205a1efd21b626f
#  - DPDK version bump to 19.08.
#  - Mostly a progression, but can be a regression is some testcases.
# 2019-09-10:
# v20.01-rc0-163  546f955b3dad6c0866a8ba778d0cfe1ef43d81d4
#  - Memif API change.
# 2019-10-15:
# v20.01-rc0-396  6df2c7954126a316f86908526c3bb4d649f06597
#  - .sendall broke socket papi https://gerrit.fd.io/r/c/vpp/+/22672
# 2019-10-16:
# v20.01-rc0-403  8921dc675458b238fc03c5aed53d3462bcdbdb3c
#  - fixed .sendall https://gerrit.fd.io/r/c/vpp/+/22699
# 2019-10-31:
# v20.01-rc0-524  67a6dcbc4490582abd0b1fc2a6cac822520b6a3c
#  - DPDK patch introduced, breaks multiple jobs, memif breaks DUT.
# 2019-11-06:
# v20.01-rc0-593  4d11b6cecaa9c1be20aa149bc8779f197f6393ed
#  - fixed dpdk patch memif issue

git describe || die
git bisect new || die
# Building HEAD first, good for avoiding DPDK rebuilds.
build_vpp_ubuntu "NEW" || die
set_aside_current_build_artifacts "${GIT_BISECT_FROM}" || die
git describe || die
build_vpp_ubuntu "OLD" || die
set_aside_parent_build_artifacts || die
initialize_csit_dirs || die
set_perpatch_dut || die
select_topology || die
select_arch_os || die
activate_virtualenv "${VPP_DIR}" || die
generate_tests || die
archive_tests || die
reserve_and_cleanup_testbed || die
select_tags || die
compose_pybot_arguments || die
select_build "build_current" || die
check_download_dir || die
run_and_parse "csit_current/0" || die
cp "csit_current/0/results.txt" "csit_current/results.txt" || die
# TODO: Use less heavy way to avoid apt remove failures.
ansible_playbook "cleanup" || die
select_build "build_parent" || die
check_download_dir || die
run_and_parse "csit_parent/0" || die
untrap_and_unreserve_testbed || die
cp "csit_parent/0/results.txt" "csit_parent/results.txt" || die
git bisect old | tee "git.log" || die
git describe || die
mkdir -p "csit_new" || die
iteration=0
while true
do
    if head -n 1 "git.log" | cut -b -11 | fgrep -q "Bisecting:"; then
        echo "Still bisecting..."
    else
        echo "Bisecting done."
        break
    fi
    let iteration+=1
    git clean -dffx "build"/ "build-root"/ || die
    build_vpp_ubuntu "MIDDLE" || die
    reserve_and_cleanup_testbed || die
    select_build "build-root" || die
    check_download_dir || die
    run_and_parse "csit_parent/${iteration}" || die
    untrap_and_unreserve_testbed || die
    cp -f "csit_parent/${iteration}/results.txt" "csit_new/results.txt" || die
    set +e
    python3 "${TOOLS_DIR}/integrated/compare_bisect.py"
    bisect_rc="${?}"
    set -e
    if [[ "${bisect_rc}" == "3" ]]; then
        adjective="new"
        cp -f "csit_new/results.txt" "csit_current/results.txt" || die
    elif [[ "${bisect_rc}" == "0" ]]; then
        adjective="old"
        cp -f "csit_new/results.txt" "csit_parent/results.txt" || die
    else
        die "Unexpected return code ${bisect_rc}"
    fi
    git bisect "${adjective}" | tee "git.log" || die
    git describe || die
done
git status || die
