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
# - TEST_CODE - The test selection string from environment or argument.
# - DOWNLOAD_DIR - Path to directory where pybot takes the build to test from.
# - CSIT_DIR - Path to existing directory with root of local CSIT git repository.
# Files read:
# - ${CSIT_DIR}/DPDK_STABLE_VER - DPDK version to use by csit-vpp not-timed jobs.
# - ${CSIT_DIR}/VPP_STABLE_VER_UBUNTU - VPP version to use by those.
# - ../vpp*.deb - Relative to ${DOWNLOAD_DIR}, copied there for vpp-csit jobs.
# Directories updated:
# - ${DOWNLOAD_DIR}, vpp-*.deb files are copied here for vpp-csit jobs.
# - ./ - Assumed ${DOWNLOAD_DIR}, vpp-*.deb files are downloaded here for csit-vpp.
# Functions called:
# - die - Print to stderr and exit, defined in common_functions.sh
# Bash scripts executed:
# - ${CSIT_DIR}/resources/tools/scripts/download_install_vpp_pkgs.sh
#   - Should download and extract requested files to ./.

case "$TEST_CODE" in
    csit-*)
        # Use downloaded packages with specific version
        if [[ "$TEST_CODE" == *daily* ]] || \
           [[ "$TEST_CODE" == *weekly* ]] || \
           [[ "$TEST_CODE" == *timed* ]];
        then
            echo "Downloading latest VPP packages from NEXUS..."
            # TODO: Can we source?
            bash "${CSIT_DIR}/resources/tools/scripts/download_install_vpp_pkgs.sh" \
                --skip-install || {
                die 1 "Failed to get VPP packages!"
            }
        else
            echo "Downloading VPP packages of specific version from NEXUS..."
            dpdk_stable_ver=$(cat ${CSIT_DIR}/DPDK_STABLE_VER)
            vpp_stable_ver=$(cat ${CSIT_DIR}/VPP_STABLE_VER_UBUNTU)
            bash "${CSIT_DIR}/resources/tools/scripts/download_install_vpp_pkgs.sh" \
                --skip-install --vpp ${vpp_stable_ver} --dkms ${dpdk_stable_ver} || {
                die 1 "Failed to get VPP packages!"
            }
        fi
        ;;
    vpp-csit-*)
        # Use local built packages.
        mv "${DOWNLOAD_DIR}"/../"vpp"*".deb" "${DOWNLOAD_DIR}"/
        ;;
    *)
        die 1 "Unable to identify job type from: ${TEST_CODE}!"
        ;;
esac
