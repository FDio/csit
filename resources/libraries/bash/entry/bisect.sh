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
# Many different test types are supported.
#
# Logs are present in the archive directory, but usually the main output
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
# If the shortest description is achieved with 3 separate groups,
# bisect interval focuses on biggest relative change
# (with respect to pairwise maximum).
#
# If any test failure happens, few retries are attempted.
# If all tries fail, an artificial result is used to distinguish
# from normal results. Currently, the value 2.0, with the same multiplicity
# is used for fail results.
#
# Note that if there was a VPP API change that affects tests in the interval,
# there frequently is no good way for single CSIT commit to work there.
# You can try manually reverting the CSIT changes to make tests pass,
# possibly needing to search over multiple subintervals.
# Using and older CSIT commit (possibly cherry-picking the bisect Change
# if it was not present in CSIT compatible with old enough VPP builds)
# is the fastest solution; but beware of CSIT-induced performance effects
# (e.g. TRex settings).
#
# If a regression happens during a subinterval where the test fails
# due to a bug in VPP, you may try to create a new commit chain
# with the fix cherry-picked to the start of the interval.
# Do not do that as a chain in Gerrit, it would be long and Gerrit will refuse
# edits of already merged Changes.
# Instead, add a block of bash code to do the manipulation
# on local git history between checkout and bisect.
#
# At the start, the script executes first bisect iteration in an attempt
# to avoid work if the search interval has only one commit (or is invalid).
# Only when the work is needed, earliest and latest commits are built
# and tested. Branches "earliest", "middle" and "latest" are temporarily created
# as a way to remember which commits to check out.
#
# Assumptions:
# + There is a directory holding VPP repo with patch under test checked out.
# + It contains csit subdirectory with CSIT code to use (this script is there).
# + Everything needed to build VPP is already installed locally.
# Consequences:
# + Working directory is switched to the VPP repo root.
# + At the end, VPP repo has checked out and built some commit,
#   as chosen by "git bisect".
# + Directories build_root, build and csit are reset during the run.
# + The following directories (relative to VPP repo) are (re)created:
# ++ csit_{earliest,early,middle,late,latest}, build_{earliest,latest},
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

# Save the current commit.
git checkout -b "latest"
# Save the lower bound commit.
git checkout -b "earliest"
git reset --hard "${GIT_BISECT_FROM}"

# This is the place for custom code manipulating local git history.

#git checkout -b "alter"
#...
#git checkout "latest"
#git rebase "alter" || git rebase --skip
#git branch -D "alter"

git bisect start || die
# TODO: Can we add a trap for "git bisect reset" or even "deactivate",
# without affecting the inner trap for unreserve and cleanup?
git checkout "latest"
git status || die
git describe || die
git bisect new || die
# Performing first iteration early to avoid testing or even building.
git checkout "earliest" || die "Failed to checkout earliest commit."
git status || die
git describe || die
# The first iteration.
git bisect old | tee "git.log" || die "Invalid bisect interval?"
git checkout -b "middle" || die "Failed to create branch: middle"
git status || die
git describe || die
if head -n 1 "git.log" | cut -b -11 | fgrep -q "Bisecting:"; then
    echo "Building and testing initial bounds."
else
    echo "Single commit, no work needed."
    exit 0
fi
# Building latest first, good for avoiding DPDK rebuilds.
git checkout "latest" || die "Failed to checkout latest commit."
build_vpp_ubuntu "LATEST" || die
set_aside_build_artifacts "latest" || die
git checkout "earliest" || die "Failed to checkout earliest commit."
git status || die
git describe || die
build_vpp_ubuntu "EARLIEST" || die
set_aside_build_artifacts "earliest" || die
git checkout "middle" || die "Failed to checkout middle commit."
git branch -D "earliest" "latest" || die "Failed to remove branches."
# Done with repo manipulation for now, testing commences.
initialize_csit_dirs "earliest" "early" "middle" "late" "latest" || die
set_perpatch_dut || die
select_topology || die
select_arch_os || die
activate_virtualenv "${VPP_DIR}" || die
generate_tests || die
archive_tests || die
reserve_and_cleanup_testbed || die
select_tags || die
# TODO: Does it matter which build is tested first?
select_build "build_latest" || die
check_download_dir || die
run_and_parse "csit_latest" || die
cp "csit_latest/results.txt" "csit_late/results.txt" || die
select_build "build_earliest" || die
check_download_dir || die
run_and_parse "csit_earliest" || die
untrap_and_unreserve_testbed || die
cp "csit_earliest/results.txt" "csit_early/results.txt" || die
# See function documentation for the logic in the loop.
main_bisect_loop || die
# In worst case, the middle branch is still checked out.
# TODO: Is there a way to ensure "middle" branch is always deleted?
git branch -D "middle" || true
