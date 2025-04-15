# Copyright (c) 2025 Cisco and/or its affiliates.
# Copyright (c) 2025 PANTHEON.tech and/or its affiliates.
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

function build_vpp () {

    # Variables read:
    # - BASH_FUNCTION_DIR - Bash directory with functions.
    # - TEST_CODE - The test selection string from environment or argument.
    # - DOWNLOAD_DIR - Path to directory robot takes the build to test from.
    # - CSIT_DIR - Path to existing root of local CSIT git repository.
    # Variables set:
    # - VPP_VERSION - VPP stable version under test.
    # Files read:
    # - ${CSIT_DIR}/${VPP_COMMIT_FILE} - VPP commit to use.
    # Directories updated:
    # - ${DOWNLOAD_DIR}, vpp-*.deb files are copied here for testing.
    # Functions called:
    # - die - Print to stderr and exit, defined in common.sh

    set -exuo pipefail


    case "${TEST_CODE}" in
        "csit-"*)
            # Use downloaded packages with specific version.
            if [[ "${TEST_CODE}" == *"daily"* ]] || \
               { [[ "${TEST_CODE}" == *"weekly"* ]] && \
                 [[ "${TEST_CODE}" != *"device"* ]]; } || \
               [[ "${TEST_CODE}" == *"semiweekly"* ]] || \
               [[ "${TEST_CODE}" == *"hourly"* ]];
            then
                warn "Cloning latest commit from VPP repository."
            else
                warn "Cloning stable commit from VPP repository."
                VPP_VERSION="$(<"${CSIT_DIR}/${VPP_COMMIT_FILE}")" || {
                    die "Read VPP stable version failed."
                }
            fi
            source "${BASH_FUNCTION_DIR}/per_patch.sh" || die "Source failed."
            set_csit_vpp_dir || die
            clone_vpp_repo || die
            build_vpp_ubuntu "CURRENT" || die
            select_build "build-root" || die
            remove_vpp_repo || die
            ;;
        *)
            die "Unsupported job type from: ${TEST_CODE}"
            ;;
    esac
}
