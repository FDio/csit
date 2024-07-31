# Copyright (c) 2024 Cisco and/or its affiliates.
# Copyright (c) 2024 PANTHEON.tech and/or its affiliates.
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

# This library defines functions used mainly by "bootstrap" entry scripts.
# Generally, the functions assume "common.sh" library has been sourced already.

# Keep functions ordered alphabetically, please.

function gather_build () {

    # Variables read:
    # - TEST_CODE - String affecting test selection, usually jenkins job name.
    # - DOWNLOAD_DIR - Path to directory robot takes the build to test from.
    # - BASH_FUNCTION_DIR = Path to Bash script directory.
    # Variables set:
    # - DUT - CSIT test/ subdirectory containing suites to execute.
    # Directories updated:
    # - ${DOWNLOAD_DIR} - Files needed by tests are gathered here.
    # Functions called:
    # - die - Print to stderr and exit, defined in common.sh
    # - gather_os - Parse os parameter for OS/distro name.
    # - gather_dpdk, gather_vpp - See their definitions.
    # Multiple other side effects are possible,
    # see functions called from here for their current description.

    set -exuo pipefail

    pushd "${DOWNLOAD_DIR}" || die "Pushd failed."
    case "${TEST_CODE}" in
        *"vpp"*)
            DUT="vpp"
            source "${BASH_FUNCTION_DIR}/gather_${DUT}.sh" || die "Source fail."
            gather_vpp || die "The function should have died on error."
            ;;
        *"dpdk"*)
            DUT="dpdk"
            source "${BASH_FUNCTION_DIR}/gather_${DUT}.sh" || die "Source fail."
            gather_dpdk || die "The function should have died on error."
            ;;
        *"trex"*)
            DUT="trex"
            source "${BASH_FUNCTION_DIR}/gather_${DUT}.sh" || die "Source fail."
            gather_trex || die "The function should have died on error."
            ;;
        *)
            die "Unable to identify DUT type from: ${TEST_CODE}"
            ;;
    esac
    popd || die "Popd failed."
}
