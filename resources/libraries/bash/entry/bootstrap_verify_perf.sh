# Copyright (c) 2021 Cisco and/or its affiliates.
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

# Assumptions:
# + There is a directory holding CSIT code to use (this script is there).
# + At least one of the following is true:
# ++ JOB_NAME environment variable is set,
# ++ or this entry script has access to arguments.
# Consequences (and specific assumptions) are multiple,
# examine tree of functions for current description.

# FIXME: Define API contract (as opposed to just help) for bootstrap.

# "set -eu" handles failures from the following two lines.
BASH_ENTRY_DIR="$(dirname $(readlink -e "${BASH_SOURCE[0]}"))"
BASH_FUNCTION_DIR="$(readlink -e "${BASH_ENTRY_DIR}/../function")"
source "${BASH_FUNCTION_DIR}/common.sh" || {
    echo "Source failed." >&2
    exit 1
}
source "${BASH_FUNCTION_DIR}/per_patch.sh" || die "Source failed."
source "${BASH_FUNCTION_DIR}/ansible.sh" || die "Source failed."
source "${BASH_FUNCTION_DIR}/terraform.sh" || die "Source failed."
common_dirs || die
check_prerequisites || die
get_test_code "${1-}" || die
get_test_tag_string || die
select_arch_os || die
git clone "${GIT_URL}/vpp" --branch "stable/2206" --single-branch --no-checkout || die
git tag || die
git checkout "v22.06" || die
git cherry-pick fecb2524ab71b105422a9a4377429c1871220234 || die
git cherry-pick 738eaa6f4965956a592392834bd1b6fcd0a20633 || die
git tag -a "v22.06-backport" || die
VPP_DIR="${CSIT_DIR}/vpp"
set_perpatch_dut || die
build_vpp_ubuntu_amd64 "BACKPORT" || die
set_aside_commit_build_artifacts || die
select_build "build_current" || die
check_download_dir || die
activate_virtualenv || die
generate_tests || die
archive_tests || die
prepare_topology || die
select_topology || die
reserve_and_cleanup_testbed || die
select_tags || die
compose_pybot_arguments || die
set_environment_variables || die
run_pybot || die
untrap_and_unreserve_testbed || die
move_archives || die
die_on_pybot_error || die
