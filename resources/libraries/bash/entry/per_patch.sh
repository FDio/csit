#!/usr/bin/env bash

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

# Assumptions:
# + There is a directory holding VPP repo with patch under test checked out.
# + It contains csit subdirectory with CSIT code to use (this script is there).
# + Everything needed to build VPP is already installed locally.
# Consequences:
# + At the end, VPP repo has parent commit checked out and built.
# + Directories build_root, dpdk and csit are reset during the run.
# + The following directories (relative to VPP repo) are (re)created:
# ++ csit_new, csit_parent, build_new, build_parent,
# ++ archive, csit/archive, csit_download_dir.
# This entry script currently does not need any environment variable set.

# TODO: Support tag selection by parsing gerrit comment.
# TODO: Implement some kind of VPP build caching.

# "set -eu" handles failures from the following five lines.
BASH_ENTRY_DIR=$(dirname $(readlink -e "${BASH_SOURCE[0]}"))
BASH_FRAGMENT_DIR=$(readlink -e "${BASH_ENTRY_DIR}/../fragment")
source "${BASH_FRAGMENT_DIR}/common_dirs.sh"
common_dirs
source "${BASH_FRAGMENT_DIR}/common_functions.sh"
# Function "die" is now available.
source "${BASH_FRAGMENT_DIR}/activate_virtualenv.sh" || die 1 "Source failed."
source "${BASH_FRAGMENT_DIR}/check_download_dir.sh" || die 1 "Source failed."
source "${BASH_FRAGMENT_DIR}/cleanup_testbed.sh" || die 1 "Source failed."
source "${BASH_FRAGMENT_DIR}/compose_pybot_arguments.sh" || {
    die 1 "Source failed."
}
source "${BASH_FRAGMENT_DIR}/copy_archives.sh" || die 1 "Source failed."
source "${BASH_FRAGMENT_DIR}/fail_fast.sh" || die 1 "Source failed."
source "${BASH_FRAGMENT_DIR}/perpatch/build_vpp_ubuntu_amd64.sh" || {
    die 1 "Source failed."
}
source "${BASH_FRAGMENT_DIR}/perpatch/compare_test_results.sh" || {
    die 1 "Source failed."
}
source "${BASH_FRAGMENT_DIR}/perpatch/download_builds.sh" || {
    die 1 "Source failed."
}
source "${BASH_FRAGMENT_DIR}/perpatch/prepare_build_parent.sh" || {
    die 1 "Source failed."
}
source "${BASH_FRAGMENT_DIR}/perpatch/prepare_test_parent.sh" || {
    die 1 "Source failed."
}
source "${BASH_FRAGMENT_DIR}/perpatch/prepare_test_new.sh" || {
    die 1 "Source failed."
}
source "${BASH_FRAGMENT_DIR}/perpatch/select_perpatch_tags.sh" || {
    die 1 "Source failed."
}
source "${BASH_FRAGMENT_DIR}/perpatch/set_perpatch_vpp_dir.sh" || {
    die 1 "Source failed."
}
source "${BASH_FRAGMENT_DIR}/reserve_testbed.sh" || die 1 "Source failed."
source "${BASH_FRAGMENT_DIR}/run_pybot.sh" || die 1 "Source failed."
source "${BASH_FRAGMENT_DIR}/select_topology.sh" || die 1 "Source failed."
source "${BASH_FRAGMENT_DIR}/unreserve_testbed.sh" || die 1 "Source failed."

set_perpatch_vpp_dir || die 1 "Function call failed."
build_vpp_ubuntu_amd64 "NEW" || die 1 "Function call failed."
prepare_build_parent || die 1 "Function call failed."
build_vpp_ubuntu_amd64 "PARENT" || die 1 "Function call failed."
prepare_test_new || die 1 "Function call failed."
## Replace previous 4 lines with this to speed up testing.
#download_builds "REPLACE_WITH_URL" || die 1 "Function call failed."
select_topology "2n" "skx" || die 1 "Function call failed."
select_perpatch_tags || die 1 "Function call failed."
activate_virtualenv "${VPP_DIR}" || die 1 "Function call failed."
reserve_testbed || die 1 "Function call failed."
compose_pybot_arguments || die 1 "Function call failed."
cleanup_testbed || die 1 "Function call failed."
check_download_dir || die 1 "Function call failed."
run_pybot "10" || die 1 "Function call failed."
copy_archives || die 1 "Function call failed."
fail_fast || die 1 "Function call failed."
prepare_test_parent || die 1 "Function call failed."
check_download_dir || die 1 "Function call failed."
run_pybot "10" || die 1 "Function call failed."
copy_archives || die 1 "Function call failed."
fail_fast || die 1 "Function call failed."
unreserve_testbed || die 1 "Function call failed."
compare_test_results || die 1 "Function call failed."
# TODO: Make sure archiving works as expected.
