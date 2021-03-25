# Copyright (c) 2021 Cisco and/or its affiliates.
# Copyright (c) 2021 PANTHEON.tech and/or its affiliates.
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

    # Variables read:
    # - TEST_CODE - String affecting test selection, usually jenkins job name.
    # - DOWNLOAD_DIR - Path to directory pybot takes the build to test from.
    # Variables set:
    # - DUT - CSIT test/ subdirectory containing suites to execute.
    # Directories updated:
    # - ${DOWNLOAD_DIR} - Files needed by tests are gathered here.
    # Functions called:
    # - die - Print to stderr and exit, defined in common.sh
    # - gather_os - Parse os parameter for OS/distro name.
    # - gather_dpdk, gather_vpp gather_nginx - See their definitions.
    # Multiple other side effects are possible,
    # see functions called from here for their current description.

    # TODO: Separate DUT-from-TEST_CODE from gather-for-DUT,
    #   when the first one becomes relevant for per_patch.

    set -exuo pipefail

    pushd "${DOWNLOAD_DIR}" || die "Pushd failed."
    case "${TEST_CODE}" in
        *"hc2vpp"*)
            DUT="hc2vpp"
            # FIXME: Avoid failing on empty ${DOWNLOAD_DIR}.
            ;;
        *"nginx"*)
            DUT="vpp"
            gather_vpp || die "The function should have died on error."
            gather_nginx || die "The function should have died on error."
            ;;
        *"vpp"*)
            DUT="vpp"
            gather_vpp || die "The function should have died on error."
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

    set -exuo pipefail

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
        echo "Downloading DPDK package of specific version from repo ..."
        # Downloading DPDK version based on what VPP is using. Currently
        # it is not easy way to detect from VPP version automatically.
        dpdk_stable_ver="$(< "${CSIT_DIR}/DPDK_VPP_VER")".tar.xz || {
            die "Failed to read DPDK VPP version!"
        }
    fi
    # TODO: Use "wget -N" instead checking for file presence?
    if [[ ! -f "${dpdk_stable_ver}" ]]; then
        wget -nv --no-check-certificate "${dpdk_repo}/${dpdk_stable_ver}" || {
            die "Failed to get DPDK package from: ${dpdk_repo}"
        }
    fi
}


function gather_vpp () {

    # Variables read:
    # - BASH_FUNCTION_DIR - Bash directory with functions.
    # - TEST_CODE - The test selection string from environment or argument.
    # - DOWNLOAD_DIR - Path to directory pybot takes the build to test from.
    # - CSIT_DIR - Path to existing root of local CSIT git repository.
    # Variables set:
    # - VPP_VERSION - VPP stable version under test.
    # Files read:
    # - ${CSIT_DIR}/DPDK_STABLE_VER - DPDK version to use
    #   by csit-vpp not-timed jobs.
    # - ${CSIT_DIR}/${VPP_VER_FILE} - Ubuntu VPP version to use.
    # - ../*vpp*.deb|rpm - Relative to ${DOWNLOAD_DIR}, copied for vpp-csit jobs.
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
            # Use locally built packages.
            mv "${DOWNLOAD_DIR}"/../*vpp*."${PKG_SUFFIX}" "${DOWNLOAD_DIR}"/ || {
                die "Move command failed."
            }
            ;;
        *)
            die "Unable to identify job type from: ${TEST_CODE}"
            ;;
    esac
}


function gather_nginx () {

    # Ensure latest NGINX archive is downloaded.
    #
    # Variables read:
    # - TEST_CODE - The test selection string from environment or argument.
    # Hardcoded:
    # - nginx archive name to download if TEST_CODE is not time based.
    # Directories updated:
    # - ./ - Assumed ${DOWNLOAD_DIR}, nginx-*.tar.xz is downloaded if not there.
    # Functions called:
    # - die - Print to stderr and exit, defined in common.sh

    set -exuo pipefail

    nginx_repo="http://nginx.org/download/"
    # Use downloaded packages with specific version
    case "${TEST_CODE}" in
        *"vpp"*)
            if [[ "${TEST_CODE}" == *"daily"* ]] || \
               [[ "${TEST_CODE}" == *"weekly"* ]] || \
               [[ "${TEST_CODE}" == *"timed"* ]];
            then
                echo "Downloading latest NGINX packages from repo..."
                # URL is not in quotes, calling command from variable keeps them.
                wget_command=("wget" "--no-check-certificate" "-nv" "-O" "-")
                wget_command+=("${nginx_repo}")
                nginx_stable_ver="$("${wget_command[@]}" \
                            | grep -Eo 'nginx-[^\"]+gz' | tail -1)" || {
                    die "Composite piped command failed."
                }
            else
                echo "Downloading NGINX package of specific version from repo ..."
                # Downloading NGINX version based on what VPP is using. Currently
                # it is not easy way to detect from VPP version automatically.
                nginx_stable_ver="$(< "${CSIT_DIR}/NGINX_VPP_VER")".tar.gz || {
                    die "Failed to read NGINX VPP version!"
                }
            fi

            if [[ ! -f "${nginx_stable_ver}" ]]; then
                wget -nv --no-check-certificate \
                "${nginx_repo}/${nginx_stable_ver}" || {
                    die "Failed to get NGINX package from: ${nginx_repo}"
                }
            fi
            ;;
        *"vsap"*)
            warn "Downloading latest NGINX packages from Packagecloud."
            # TODO download vcl-nginx from packagecloud.io/fdio/vsap
            ;;
        esac
}