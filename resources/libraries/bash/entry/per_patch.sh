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
BASH_ENTRY_DIR=$(dirname $(readlink -e "${BASH_SOURCE[0]}"))
BASH_FUNCTION_DIR=$(readlink -e "${BASH_ENTRY_DIR}/../function")
# TODO: "die" is not well-defined if source fails. How to improve?
source "${BASH_FUNCTION_DIR}/common.sh" || die 1 "Source failed."
source "${BASH_FUNCTION_DIR}/per_patch.sh" || die 1 "Source failed."
# TODO: Vary die messages, or move a default one into die definition.
common_dirs || die 1 "Function call failed."
set_perpatch_vpp_dir || die 1 "Function call failed."
build_vpp_ubuntu_amd64 "NEW" || die 1 "Function call failed."
prepare_build_parent || die 1 "Function call failed."
build_vpp_ubuntu_amd64 "PARENT" || die 1 "Function call failed."
prepare_test_new || die 1 "Function call failed."
## Replace previous 4 lines with this to speed up testing.
#download_builds "REPLACE_WITH_URL" || die 1 "Function call failed."
get_test_tag_string || die 1 "Function call failed."
get_test_code "${1-}" || die 1 "Function call failed."
select_topology "${NODENESS}" "${FLAVOR}" || die 1 "Function call failed."
activate_virtualenv "${VPP_DIR}" || die 1 "Function call failed."
reserve_testbed || die 1 "Function call failed."
cleanup_testbed || die 1 "Function call failed."
select_tags || die 1 "Function call failed."
compose_pybot_arguments || die 1 "Function call failed."
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
# TODO: After merging, make sure archiving works as expected.
