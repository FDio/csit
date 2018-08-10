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
# examine tree of functions for current description.

# FIXME: Define API contract (as opposed to just help) for bootstrap.

# "set -eu" handles failures from the following two lines.
BASH_ENTRY_DIR=$(dirname $(readlink -e "${BASH_SOURCE[0]}"))
BASH_FUNCTION_DIR=$(readlink -e "${BASH_ENTRY_DIR}/../function")
# TODO: "die" is not well-defined if source fails. How to improve?
source "${BASH_FUNCTION_DIR}/common.sh" || die 1 "Source failed."
source "${BASH_FUNCTION_DIR}/bootstrap.sh" || die 1 "Source failed."
# TODO: Vary die messages, or move a default one into die definition.
common_dirs || die 1 "Function call failed."
get_test_tag_string || die 1 "Function call failed."
get_test_code "${1-}" || die 1 "Function call failed."
select_topology "${NODENESS}" "${FLAVOR}" || die 1 "Function call failed."
gather_build || die 1 "Function call failed."
check_download_dir || die 1 "Function call failed."
activate_virtualenv "${CSIT_DIR}" || die 1 "Function call failed."
reserve_testbed || die 1 "Function call failed."
cleanup_testbed || die 1 "Function call failed."
select_tags || die 1 "Function call failed."
compose_pybot_arguments || die 1 "Function call failed."
run_pybot || die 1 "Function call failed."
unreserve_testbed || die 1 "Function call failed."
copy_archives || die 1 "Function call failed."
fail_fast || die 1 "Function call failed."
