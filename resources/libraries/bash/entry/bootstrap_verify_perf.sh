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
source "${BASH_FUNCTION_DIR}/gather.sh" || die "Source failed."
source "${BASH_FUNCTION_DIR}/ansible.sh" || die "Source failed."
common_dirs || die
check_prerequisites || die
get_test_code "${1-}" || die
get_test_tag_string || die
select_topology || die
select_arch_os || die
gather_build || die
check_download_dir || die
activate_virtualenv || die
generate_tests || die
archive_tests || die
reserve_and_cleanup_testbed || die
select_tags || die
run_pybot || die
untrap_and_unreserve_testbed || die
move_archives || die
die_on_pybot_error || die
