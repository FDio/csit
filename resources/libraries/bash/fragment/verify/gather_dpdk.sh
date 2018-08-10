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

function gather_dpdk () {

    set -exuo pipefail

    # Ensure latest DPDK archive is downloaded.
    #
    # Variables read:
    # - TEST_CODE - The test selection string from environment or argument.
    # Hardcoded:
    # - dpdk archive name to download if TEST_CODE is not time based.
    # Directories updated:
    # - ./ - Assumed ${DOWNLOAD_DIR}, dpdk-*.tar.xz is downloaded if not there.
    # Functions called:
    # - die - Print to stderr and exit, defined in common_functions.sh

    dpdk_repo="https://fast.dpdk.org/rel"
    # Use downloaded packages with specific version
    if [[ "${TEST_CODE}" == *daily* ]] || \
       [[ "${TEST_CODE}" == *weekly* ]] || \
       [[ "${TEST_CODE}" == *timed* ]];
    then
        echo "Downloading latest DPDK packages from repo..."
        wget_command="wget --no-check-certificate -nv -O - '${dpdk_repo}'"
        dpdk_stable_ver=$(${wget_command} | grep -v "2015"\
            | grep -Eo 'dpdk-[^\"]+xz' | tail -1) || {
            die 1 "Composite piped command failed."
        }
    else
        echo "Downloading DPDK packages of specific version from repo..."
        # TODO: Can we autodetect this based on what CSIT-stable VPP uses?
        dpdk_stable_ver="dpdk-18.05.tar.xz"
    fi
    # TODO: Use "wget -N" instead checking for file presence?
    if [[ ! -f "${dpdk_stable_ver}" ]]; then
        wget -nv --no-check-certificate "${dpdk_repo}/${dpdk_stable_ver}" || {
            die 1 "Failed to get DPDK package from: ${dpdk_repo}"
        }
    fi
}
