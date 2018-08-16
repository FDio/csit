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
# + There is a directory holding CSIT code to use (this script is there).
# + At least one of the following is true:
# ++ JOB_NAME environment variable is set,
# ++ or this entry script has access to arguments.
# Consequences (and specific assumptions) are multiple,
# examine tree of fragments for current description.

# FIXME: Define API contract (as opposed to just help) for bootstrap.

BASH_ENTRY_DIR=$(dirname $(readlink -e "${BASH_SOURCE[0]}"))
BASH_FRAGMENT_DIR=$(readlink -e "${BASH_ENTRY_DIR}/../fragment")
source "${BASH_FRAGMENT_DIR}/common_dirs.sh"
source "${BASH_FRAGMENT_DIR}/common_functions.sh"
# Each fragment should pass or die, so no need to "|| die" when sourcing.
source "${BASH_FRAGMENT_DIR}/verify/bootstrap_help.sh"
source "${BASH_FRAGMENT_DIR}/get_test_tag_string.sh"
source "${BASH_FRAGMENT_DIR}/verify/get_test_code.sh"
source "${BASH_FRAGMENT_DIR}/select_topology.sh" "${NODENESS}" "${FLAVOR}"
source "${BASH_FRAGMENT_DIR}/verify/gather_build.sh"
source "${BASH_FRAGMENT_DIR}/check_download_dir.sh"
source "${BASH_FRAGMENT_DIR}/activate_virtualenv.sh" "${CSIT_DIR}"
source "${BASH_FRAGMENT_DIR}/reserve_testbed.sh"
source "${BASH_FRAGMENT_DIR}/cleanup_testbed.sh"
source "${BASH_FRAGMENT_DIR}/verify/select_verify_tags.sh"
source "${BASH_FRAGMENT_DIR}/compose_pybot_arguments.sh"
source "${BASH_FRAGMENT_DIR}/run_pybot.sh"
source "${BASH_FRAGMENT_DIR}/unreserve_testbed.sh"
source "${BASH_FRAGMENT_DIR}/cp_archives.sh"
source "${BASH_FRAGMENT_DIR}/fail_fast.sh"
