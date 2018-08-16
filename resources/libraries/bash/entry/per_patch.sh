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

# FIXME: Define API contract for bootstrap, and then
#        either unify bootstarp with this (if the API supports building
#        and testing 2 builds), or reimplement bootstrap as a new entry
#        using common fragments.

BASH_ENTRY_DIR=$(dirname $(readlink -e "${BASH_SOURCE[0]}"))
BASH_FRAGMENT_DIR=$(readlink -e "${BASH_ENTRY_DIR}/../fragment")
source "${BASH_FRAGMENT_DIR}/common_dirs.sh"
source "${BASH_FRAGMENT_DIR}/common_functions.sh"
# Each fragment should pass or die, so no need to "|| die" when sourcing.
source "${BASH_FRAGMENT_DIR}/perpatch/vpp_dir.sh"
source "${BASH_FRAGMENT_DIR}/build_vpp_ubuntu_amd64.sh" "NEW"
source "${BASH_FRAGMENT_DIR}/perpatch/prepare_build_parent.sh"
source "${BASH_FRAGMENT_DIR}/build_vpp_ubuntu_amd64.sh" "PARENT"
source "${BASH_FRAGMENT_DIR}/perpatch/prepare_test_new.sh"
## Replace previous 4 lines with this to speed up testing.
#source "${BASH_FRAGMENT_DIR}/perpatch/download_builds.sh" "REPLACE_WITH_URL"
source "${BASH_FRAGMENT_DIR}/select_topology.sh" "2n" "skx"
source "${BASH_FRAGMENT_DIR}/perpatch/select_perpatch_tags.sh"
source "${BASH_FRAGMENT_DIR}/activate_virtualenv.sh" "${VPP_DIR}"
source "${BASH_FRAGMENT_DIR}/reserve_testbed.sh"
source "${BASH_FRAGMENT_DIR}/compose_pybot_arguments.sh"
source "${BASH_FRAGMENT_DIR}/cleanup_testbed.sh"
source "${BASH_FRAGMENT_DIR}/check_download_dir.sh"
source "${BASH_FRAGMENT_DIR}/run_pybot.sh" 10
source "${BASH_FRAGMENT_DIR}/cp_archives.sh"
source "${BASH_FRAGMENT_DIR}/fail_fast.sh"
source "${BASH_FRAGMENT_DIR}/perpatch/prepare_test_parent.sh"
source "${BASH_FRAGMENT_DIR}/check_download_dir.sh"
source "${BASH_FRAGMENT_DIR}/run_pybot.sh" 10
source "${BASH_FRAGMENT_DIR}/fail_fast.sh"
source "${BASH_FRAGMENT_DIR}/unreserve_testbed.sh"
source "${BASH_FRAGMENT_DIR}/perpatch/compare_test_results.sh"
# TODO: Make sure archiving works as expected.
