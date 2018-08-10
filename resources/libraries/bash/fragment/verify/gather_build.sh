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

# Variables read:
# - BASH_FRAGMENT_DIR - Path to directory holding specialized gather scripts.

source "${BASH_FRAGMENT_DIR}/verify/gather_vpp.sh"
source "${BASH_FRAGMENT_DIR}/verify/gather_ligato.sh"
source "${BASH_FRAGMENT_DIR}/verify/gather_dpdk.sh"

function gather_build () {

    set -exuo pipefail

    # Variables read:
    # - TEST_CODE - String affecting test selection, usually jenkins job name.
    # - DOWNLOAD_DIR - Path to directory where pybot takes the build to test from.
    # Variables set:
    # - DUT - CSIT test/ subdirectory containing suites to execute.
    # Directories updated:
    # - ${DOWNLOAD_DIR} - Files needed by tests are gathered here.
    # Functions called:
    # - die - Print to stderr and exit, defined in common_functions.sh
    # - gather_dpdk, gather_vpp, gather_ligato - See their fragments.
    # Multiple other side effects are possible,
    # see functions called from here for their current description.

    pushd "${DOWNLOAD_DIR}" || die 1 "Pushd failed."
    case "${TEST_CODE}" in
        *hc2vpp*)
            DUT="hc2vpp"
            # FIXME: Avoid failing on empty ${DOWNLOAD_DIR}.
            ;;
        *vpp*)
            DUT="vpp"
            gather_vpp || die 1 "The function should have died on error."
            ;;
        *ligato*)
            DUT="kubernetes"
            gather_ligato || die 1 "The function should have died on error."
            ;;
        *dpdk*)
            DUT="dpdk"
            gather_dpdk || die 1 "The function should have died on error."
            ;;
        *)
            die 1 "Unable to identify DUT type from: ${TEST_CODE}"
            ;;
    esac
    popd || die 1 "Popd failed."
}
