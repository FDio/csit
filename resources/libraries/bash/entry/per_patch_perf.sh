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

# TODO: Implement some kind of VPP build caching.

# "set -eu" handles failures from the following two lines.
BASH_ENTRY_DIR="$(dirname $(readlink -e "${BASH_SOURCE[0]}"))"
BASH_FUNCTION_DIR="$(readlink -e "${BASH_ENTRY_DIR}/../function")"
source "${BASH_FUNCTION_DIR}/common.sh" || {
    echo "Source failed." >&2
    exit 1
}
source "${BASH_FUNCTION_DIR}/per_patch.sh" || die "Source failed."
common_dirs || die
set_perpatch_vpp_dir || die
build_vpp_ubuntu_amd64 "NEW" || die
prepare_build_parent || die
build_vpp_ubuntu_amd64 "PARENT" || die
prepare_test_new || die
## Replace previous 4 lines with this to speed up testing.
#download_builds "REPLACE_WITH_URL" || die
get_test_tag_string || die
get_test_code "${1-}" || die
set_perpatch_dut || die
select_topology || die
activate_virtualenv "${VPP_DIR}" || die
reserve_testbed || die
select_tags || die
compose_pybot_arguments || die
check_download_dir || die
run_pybot "10" || die
copy_archives || die
die_on_pybot_error || die
prepare_test_parent || die
check_download_dir || die
run_pybot "10" || die
untrap_and_unreserve_testbed || die
copy_archives || die
die_on_pybot_error || die
compare_test_results  # The error code becomes this script's error code.
# TODO: After merging, make sure archiving works as expected.
