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

# This library defines functions used mainly by "bootstrap" entry scripts.
# Generally, the functions assume "common.sh" library has been sourced already.

# Keep functions ordered alphabetically, please.

# TODO: Add a link to bash style guide.


function gather_build () {

    set -exuo pipefail

    # Variables read:
    # - TEST_CODE - String affecting test selection, usually jenkins job name.
    # - DOWNLOAD_DIR - Path to directory pybot takes the build to test from.
    # Variables set:
    # - DUT - CSIT test/ subdirectory containing suites to execute.
    # Directories updated:
    # - ${DOWNLOAD_DIR} - Files needed by tests are gathered here.
    # Functions called:
    # - die - Print to stderr and exit, defined in common.sh
    # - gather_dpdk, gather_vpp, gather_ligato - See their definitions.
    # Multiple other side effects are possible,
    # see functions called from here for their current description.

    # TODO: Separate DUT-from-TEST_CODE from gather-for-DUT,
    #   when the first one becomes relevant for per_patch.

    pushd "${DOWNLOAD_DIR}" || die "Pushd failed."
    case "${TEST_CODE}" in
        *"hc2vpp"*)
            DUT="hc2vpp"
            # FIXME: Avoid failing on empty ${DOWNLOAD_DIR}.
            ;;
        *"vpp"*)
            DUT="vpp"
            gather_vpp || die "The function should have died on error."
            ;;
        *"ligato"*)
            DUT="kubernetes"
            gather_ligato || die "The function should have died on error."
            ;;
        *"dpdk"*)
            DUT="dpdk"
            gather_dpdk || die "The function should have died on error."
            ;;
        *)
            die "Unable to identify DUT type from: ${TEST_CODE}"
            ;;
    esac
    popd || die "Popd failed."
}


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
    # - die - Print to stderr and exit, defined in common.sh

    dpdk_repo="https://fast.dpdk.org/rel"
    # Use downloaded packages with specific version
    if [[ "${TEST_CODE}" == *"daily"* ]] || \
       [[ "${TEST_CODE}" == *"weekly"* ]] || \
       [[ "${TEST_CODE}" == *"timed"* ]];
    then
        echo "Downloading latest DPDK packages from repo..."
        # URL is not in quotes, calling command from variable keeps them.
        wget_command=("wget" "--no-check-certificate" "-nv" "-O" "-")
        wget_command+=("${dpdk_repo}")
        dpdk_stable_ver="$("${wget_command[@]}" | grep -v "2015"\
            | grep -Eo 'dpdk-[^\"]+xz' | tail -1)" || {
            die "Composite piped command failed."
        }
    else
        echo "Downloading DPDK packages of specific version from repo..."
        # TODO: Can we autodetect this based on what CSIT-stable VPP uses?
        dpdk_stable_ver="dpdk-18.08.tar.xz"
    fi
    # TODO: Use "wget -N" instead checking for file presence?
    if [[ ! -f "${dpdk_stable_ver}" ]]; then
        wget -nv --no-check-certificate "${dpdk_repo}/${dpdk_stable_ver}" || {
            die "Failed to get DPDK package from: ${dpdk_repo}"
        }
    fi
}


function gather_ligato () {

    set -exuo pipefail

    # Build docker image (with vpp, ligato and vpp-agent),
    # and put it to ${DOWNLOAD_DIR}/.
    #
    # Access rights needed for:
    # - "git clone".
    # - "sudo" without password.
    # - With sudo:
    #   - "docker" commands have everything they needs.
    # Variables read:
    # - DOWNLOAD_DIR - Path to directory pybot takes the build to test from.
    # - CSIT_DIR - Path to existing root of local CSIT git repository.
    # Files read:
    # - ${CSIT_DIR}/VPP_AGENT_STABLE_VER - Vpp agent version to use.
    # Directories updated:
    # - ${DOWNLOAD_DIR} - Docker image stored.
    # - ${CSIT_DIR}/vpp-agent - Created, vpp-agent git repo si cloned there.
    #   - Also, various temporary files are stored there.
    # System consequences:
    # - Docker package is installed.
    # - Presumably dockerd process is started.
    # Other hardcoded values:
    # - Docker .deb file name to download and install.
    # Functions called:
    # - die - Print to stderr and exit, defined in common_functions.sh

    # Install Docker.
    curl -fsSL https://get.docker.com | sudo bash || {
        die "Failed to install Docker package!"
    }

    vpp_agent_stable_branch="$(< "${CSIT_DIR}/VPP_AGENT_STABLE_BRANCH")" || {
        die "Failed to read vpp-agent stable branch!"
    }
    vpp_agent_stable_ver="$(< "${CSIT_DIR}/VPP_AGENT_STABLE_VER")" || {
        die "Failed to read vpp-agent stable VPP version!"
    }

    # Clone & checkout stable vpp-agent.
    cd "${CSIT_DIR}" || die "Change directory failed!"
    git clone -b "${vpp_agent_stable_branch}" --single-branch \
        "https://github.com/ligato/vpp-agent" "vpp-agent" || {
        die "Failed to clone vpp-agent repo!"
    }
    cd "vpp-agent" || die "Change directory failed!"

    # Specify VPP_COMMIT.
    sed -i "s/VPP_COMMIT=.*/VPP_COMMIT=${vpp_agent_stable_ver}/g" ./vpp.env

    # Build dev_vpp_agent docker image.
    pushd "docker/dev" || die "Change directory failed."
    sudo ./build.sh || {
        die "Failed to build dev Docker image!"
    }
    popd || die "Change directory failed."

    # Build prod_vpp_agent docker image.
    pushd "docker/prod" || die "Change directory failed."
    sudo ./build.sh || {
        die "Failed to build prod Docker image!"
    }
    popd || die "Change directory failed."

    # Export Docker image.
    sudo docker save "prod_vpp_agent" | gzip > "prod_vpp_agent.tar.gz" || {
        die "Failed to save Docker image!"
    }
    docker_image="$(readlink -e "prod_vpp_agent.tar.gz")" || {
        die "Failed to get Docker image path!"
    }
    mv "${docker_image}" "${DOWNLOAD_DIR}"/ || die "Failed to move image!"
}


function gather_vpp () {

    set -exuo pipefail

    # Variables read:
    # - BASH_FUNCTION_DIR - Bash directory with functions.
    # - TEST_CODE - The test selection string from environment or argument.
    # - DOWNLOAD_DIR - Path to directory pybot takes the build to test from.
    # - CSIT_DIR - Path to existing root of local CSIT git repository.
    # Files read:
    # - ${CSIT_DIR}/DPDK_STABLE_VER - DPDK version to use
    #   by csit-vpp not-timed jobs.
    # - ${CSIT_DIR}/VPP_STABLE_VER_UBUNTU - VPP version to use by those.
    # - ../vpp*.deb - Relative to ${DOWNLOAD_DIR}, copied for vpp-csit jobs.
    # Directories updated:
    # - ${DOWNLOAD_DIR}, vpp-*.deb files are copied here for vpp-csit jobs.
    # - ./ - Assumed ${DOWNLOAD_DIR}, vpp-*.deb files
    #   are downloaded here for csit-vpp.
    # Functions called:
    # - die - Print to stderr and exit, defined in common_functions.sh
    # Bash scripts executed:
    # - ${CSIT_DIR}/resources/tools/scripts/download_install_vpp_pkgs.sh
    #   - Should download and extract requested files to ./.

    case "${TEST_CODE}" in
        # Not csit-vpp as this code is re-used by ligato gathering.
        "csit-"*)
            # Use downloaded packages with specific version.
            if [[ "${TEST_CODE}" == *"daily"* ]] || \
               ([[ "${TEST_CODE}" == *"weekly"* ]] && \
                [[ "${TEST_CODE}" != *"device"* ]]) || \
               [[ "${TEST_CODE}" == *"semiweekly"* ]];
            then
                warn "Downloading latest VPP packages from Packagecloud."
            else
                warn "Downloading stable VPP packages from Packagecloud."
                if [[ "${TEST_CODE}" == *"device"* ]];
                then
                    VPP_VERSION="$(<"${CSIT_DIR}/VPP_STABLE_VER_UBUNTU_BIONIC")" || {
                        die "Read VPP stable version failed."
                    }
                else
                    VPP_VERSION="$(<"${CSIT_DIR}/VPP_STABLE_VER_UBUNTU")" || {
                        die "Read VPP stable version failed."
                    }
                fi
            fi
            source "${BASH_FUNCTION_DIR}/artifacts.sh" || die "Source failed."
            download_artifacts || die
            ;;
        "vpp-csit-"*)
            # Use locally built packages.
            mv "${DOWNLOAD_DIR}"/../"vpp"*".deb" "${DOWNLOAD_DIR}"/ || {
                die "Move command failed."
            }
            ;;
        *)
            die "Unable to identify job type from: ${TEST_CODE}"
            ;;
    esac
}
