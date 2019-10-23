#!/usr/bin/env bash

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

# FIXME: Update.
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

# TODO: "git bisect skip" if test fails during the search?

# "set -eu" handles failures from the following two lines.
BASH_ENTRY_DIR="$(dirname $(readlink -e "${BASH_SOURCE[0]}"))"
BASH_FUNCTION_DIR="$(readlink -e "${BASH_ENTRY_DIR}/../function")"
source "${BASH_FUNCTION_DIR}/common.sh" || {
    echo "Source failed." >&2
    exit 1
}
source "${BASH_FUNCTION_DIR}/per_patch.sh" || die "Source failed."
common_dirs || die
check_prerequisites || die
set_perpatch_vpp_dir || die
# Unfortunately, git bisect only works at the to of repo.
cd "${VPP_DIR}" || die
git bisect start || die
trap "git bisect reset" EXIT RETURN

# Important commits affecting behavior.
# v19.04          3d18a191aaf31ef8b1524ab80fed22a304adf75d:
#  - Release build.
# v19.08-rc0-225  19542299d3f4095acda802b73b8a71a2f208cdf2:
#  - VPPApiClient was called VPP before.
#  - Also, apidir is not a class field, not read from os.environ[].
# v19.08-rc0-667  7b8a30d08bffcb8c6fe7faa8d7f7dc557e175770:
#  - "make pkg-verify" does not work before.
# v19.08          1c586de48cc76fc6eac50f5d87003e2a80aa43e7:
#  - Release build.
# v20.01-rc0-68   053204ab039d34a990ff0e14c32ce3b294fcce0e:
#  - Interface API, *_up_down => flags.

git checkout "d83c4a8d70cfd9dc8c5af3d7391d2ea6a67aa480" || die
git describe
git bisect new || die
build_vpp_ubuntu_amd64 "NEW" || die
set_aside_current_build_artifacts "3d18a191aaf31ef8b1524ab80fed22a304adf75d" || die
git describe
build_vpp_ubuntu_amd64 "OLD" || die
set_aside_parent_build_artifacts || die
initialize_csit_dirs || die
get_test_code "${1-}" || die
get_test_tag_string || die
set_perpatch_dut || die
select_topology || die
select_arch_os || die
activate_virtualenv "${VPP_DIR}" || die
pip install -r "${PYTHON_SCRIPTS_DIR}/perpatch_requirements.txt" || {
    die "Perpatch Python requirements installation failed."
}
generate_tests || die
archive_tests || die
reserve_and_cleanup_testbed || die
select_tags || die
compose_pybot_arguments || die
# Testing current first. Good for early failures or for API changes.
select_build "build_current" || die
check_download_dir || die
run_pybot || die
copy_archives || die
archive_parse_test_results "csit_current/0" || die
cp "csit_current/0/results.txt" "csit_current/results.txt" || die
#target="${VPP_DIR}/csit_current"
#mkdir -p "${target}" || die
#echo "[1100000, 1110000]" > "${target}/results.txt"
#die_on_pybot_error || die
# TODO: Use less heavy way to avoid apt remove failures.
cleanup_topo
select_build "build_parent" || die
check_download_dir || die
run_pybot || die
untrap_and_unreserve_testbed || die
copy_archives || die
archive_parse_test_results "csit_parent/0" || die
#target="${VPP_DIR}/csit_parent"
#mkdir -p "${target}" || die
#echo "[1190000, 1200000]" > "${target}/results.txt"
cp "csit_parent/0/results.txt" "csit_parent/results.txt" || die
#die_on_pybot_error || die
git bisect old | tee "git.log" || die
git describe
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
    git clean -dffx "build"/ "build-root"/
    build_vpp_ubuntu_amd64 "MIDDLE" || die
    reserve_and_cleanup_testbed || die
    select_tags || die
    compose_pybot_arguments || die
    select_build "build-root" || die
    check_download_dir || die
    run_pybot || die
    untrap_and_unreserve_testbed || die
    copy_archives || die
    archive_parse_test_results "csit_parent/${iteration}" || die
    cp -f "csit_parent/${iteration}/results.txt" "csit_new/results.txt" || die
#    target="${VPP_DIR}/csit_new"
#    mkdir -p "${target}"
#    echo | awk ' { srand('"${iteration}"'); print "[1" 100000 + 100000 * rand() ", 1" 100000 + 100000 * rand() "]" } ' | tee "${target}/results.txt"
#    die_on_pybot_error || die
    set +e
    python "${TOOLS_DIR}/integrated/compare_bisect.py"
    bisect_rc="${?}"
    set -e
    if [[ "${bisect_rc}" == "3" ]]; then
        adjective="new"
        cat "csit_new/results.txt" > "csit_current/results.txt"
    elif [[ "${bisect_rc}" == "0" ]]; then
        adjective="old"
        cat "csit_new/results.txt" > "csit_parent/results.txt"
    else
        die "Unexpected return code ${bisect_rc}"
    fi
    git bisect "${adjective}" | tee "git.log" || die
    git describe
done
echo "Bisection finished."
git status
