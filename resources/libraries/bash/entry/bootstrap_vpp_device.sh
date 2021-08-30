#!/usr/bin/env bash

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

# Run selection of "device" tests on a VPP build, fail if a test fails.
#
# This is a common bootstrap for csit-vpp and vpp-csit jobs,
# the difference is whether VPP build is downloaded or built from source.
# The two jobs have different directory structure in workspace,
# but the functions hide this fact, so most of the logic is identical.
# That is important, otherwise a CSIT change verified on csit-vpp
# could break vpp-csit, which votes on VPP changes.
#
# This entry script does not change CSIT branch,
# use "with_oper_for_vpp.sh" wrapper for that.
#
# Common assumptions:
# + At least one of the following is true:
# ++ JOB_NAME environment variable is set,
# ++ or this entry script has access to arguments, first one is job name.

# "set -eu" handles failures from the following two lines.
BASH_ENTRY_DIR="$(dirname $(readlink -e "${BASH_SOURCE[0]}"))"
BASH_FUNCTION_DIR="$(readlink -e "${BASH_ENTRY_DIR}/../function")"
source "${BASH_FUNCTION_DIR}/common.sh" || {
    echo "Source failed." >&2
    exit 1
}
common_dirs || die
get_test_code "${1-}" || die
if [[ "${TEST_CODE}" == "csit-vpp"*"device"* ]]; then
    # Download the VPP build to test.
    # Assumptions:
    # + There is a directory holding CSIT code to use (this script is there).
    # Consequences (and specific assumptions) are multiple,
    # examine tree of functions for current description.
    source "${BASH_FUNCTION_DIR}/gather.sh" || die "Source failed."
    select_arch_os || die
    gather_build || die
elif [[ "${TEST_CODE}" == "vpp-csit"*"device"* ]]; then
    # Compile the VPP build to test.
    # Assumptions:
    # + There is a directory holding VPP repo with patch under test checked out.
    # + It contains csit subdir with CSIT code to use (this script is there).
    # + Everything needed to build VPP is already installed locally.
    # Consequences:
    # + The following directories (relative to VPP repo) are (re)created:
    # + csit_current, build_current, archives, csit/archives, csit_download_dir.
    source "${BASH_FUNCTION_DIR}/per_patch.sh" || die "Source failed."
    set_perpatch_vpp_dir || die
    initialize_csit_dirs || die
    build_vpp_ubuntu_amd64 "CURRENT" || die
    set_aside_commit_build_artifacts || die
    select_build "build_current" || die
    set_perpatch_dut || die
else
    die "Devicetest bootstrap supports only csit-vpp and vpp-csit device jobs."
fi
check_download_dir || die
check_prerequisites || die
get_test_tag_string || die
select_arch_os || die
activate_virtualenv || die
generate_tests || die
archive_tests || die
prepare_topology || die
select_topology || die
activate_docker_topology || die
select_tags || die
compose_pybot_arguments || die
set_environment_variables || die
run_pybot || die
move_archives || die
die_on_pybot_error || die
