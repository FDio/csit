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

function gather_vpp () {

    # Variables read:
    # - BASH_FUNCTION_DIR - Bash directory with functions.
    # - TEST_CODE - The test selection string from environment or argument.
    # - DOWNLOAD_DIR - Path to directory robot takes the build to test from.
    # - CSIT_DIR - Path to existing root of local CSIT git repository.
    # Variables set:
    # - VPP_VERSION - VPP stable version under test.
    # Files read:
    # - ${CSIT_DIR}/DPDK_STABLE_VER - DPDK version to use
    #   by csit-vpp not-timed jobs.
    # - ${CSIT_DIR}/${VPP_VER_FILE} - Ubuntu VPP version to use.
    # - ../*vpp*.deb|rpm - Relative to ${DOWNLOAD_DIR},
    #   copied for vpp-csit jobs.
    # Directories updated:
    # - ${DOWNLOAD_DIR}, vpp-*.deb files are copied here for vpp-csit jobs.
    # - ./ - Assumed ${DOWNLOAD_DIR}, *vpp*.deb|rpm files
    #   are downloaded here for csit-vpp.
    # Functions called:
    # - die - Print to stderr and exit, defined in common_functions.sh
    # Bash scripts executed:
    # - ${CSIT_DIR}/resources/tools/scripts/download_install_vpp_pkgs.sh
    #   - Should download and extract requested files to ./.

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
                warn "Downloading latest VPP packages from Packagecloud."
            else
                warn "Downloading stable VPP packages from Packagecloud."
                VPP_VERSION="$(<"${CSIT_DIR}/${VPP_VER_FILE}")" || {
                    die "Read VPP stable version failed."
                }
            fi
            source "${BASH_FUNCTION_DIR}/artifacts.sh" || die "Source failed."
            download_artifacts || die
            ;;
        "vpp-csit-"*)
            # Shorten line.
            pkgs="${PKG_SUFFIX}"
            # Use locally built packages.
            mv "${DOWNLOAD_DIR}"/../*vpp*."${pkgs}" "${DOWNLOAD_DIR}"/ || {
                die "Move command failed."
            }
            ;;
        *)
            die "Unable to identify job type from: ${TEST_CODE}"
            ;;
    esac
}
