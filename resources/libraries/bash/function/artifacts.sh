#!/usr/bin/env bash

# Copyright (c) 2025 Cisco and/or its affiliates.
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

function download_artifacts () {

    # Download or install VPP artifacts from packagecloud.io.
    #
    # Variables read:
    # - CSIT_DIR - Path to existing root of local CSIT git repository.
    # Variables set:
    # - REPO_URL - FD.io Packagecloud repository.
    # Functions conditionally called (see their documentation for side effects):
    # - download_ubuntu_artifacts

    set -exuo pipefail

    os_id=$(grep '^ID=' /etc/os-release | cut -f2- -d= | sed -e 's/\"//g') || {
        die "Get OS release failed."
    }

    repo_url_path="${CSIT_DIR}/VPP_REPO_URL"
    if [ -e "${repo_url_path}" ]; then
        REPO_URL="$(<${repo_url_path})" || {
            die "Read repo URL from ${repo_url_path} failed."
        }
    else
        REPO_URL="https://packagecloud.io/install/repositories/fdio/master"
    fi

    if [ "${os_id}" == "ubuntu" ]; then
        download_ubuntu_artifacts || die
    else
        die "${os_id} is not yet supported."
    fi
}

function download_ubuntu_artifacts () {

    # Download or install Ubuntu VPP artifacts from packagecloud.io.
    #
    # Variables read:
    # - REPO_URL - FD.io Packagecloud repository.
    # - VPP_VERSION - VPP version.
    # - INSTALL - Whether install packages (if set to "true") or download only.
    #             Default: "false".

    set -exuo pipefail

    curl -s "${REPO_URL}"/script.deb.sh | sudo -E bash || {
        die "Packagecloud FD.io repo fetch failed."
    }
    # If version is set we will add suffix.
    artifacts=()
    both_quotes='"'"'"
    match="[^${both_quotes}]*"
    qmatch="[${both_quotes}]\?"
    sed_command="s#.*apt_source_path=${qmatch}\(${match}\)${qmatch}#\1#p"
    apt_fdio_repo_file=$(curl -s "${REPO_URL}"/script.deb.sh | \
                         sed -n ${sed_command}) || {
                             die "Local fdio repo file path fetch failed."
                         }

    if [ ! -f ${apt_fdio_repo_file} ]; then
        die "${apt_fdio_repo_file} not found, \
            repository installation was not successful."
    fi

    pkgs=$(apt-cache -o Dir::Etc::SourceList=${apt_fdio_repo_file} \
               -o Dir::Etc::SourceParts=${apt_fdio_repo_file} dumpavail \
               | grep Package: | cut -d " " -f 2 | grep vpp) || {
                   die "Retrieval of available VPP packages failed."
               }
    if [ -z "${VPP_VERSION-}" ]; then
        # Debug: Confirm the order of displayed versions.
        apt-cache -o Dir::Etc::SourceList=${apt_fdio_repo_file} \
        -o Dir::Etc::SourceParts=${apt_fdio_repo_file} \
        show vpp | grep Version: | cut -d " " -f 2 || true
        # If version is not specified, find out the most recent version.
        # Temporarily, ignore "octeon" versions, as we do not test that yet.
        VPP_VERSION=$(apt-cache -o Dir::Etc::SourceList=${apt_fdio_repo_file} \
                      -o Dir::Etc::SourceParts=${apt_fdio_repo_file} \
                      show vpp | grep Version: | fgrep -v octeon | head -1 | \
                      cut -d " " -f 2) || {
                          die "Retrieval of most recent VPP version failed."
                      }
    fi

    set +x
    for package in ${pkgs}; do
        # Filter packages with given version
        pkg_info=$(apt-cache show -- ${package}) || {
            die "apt-cache show on ${package} failed."
        }
        ver=$(echo ${pkg_info} | grep -o "Version: ${VPP_VERSION-}[^ ]*" | \
              head -1) || true
        if [ -n "${ver-}" ]; then
            echo "Found '${VPP_VERSION-}' among '${package}' versions."
            ver=$(echo "$ver" | cut -d " " -f 2)
            artifacts+=(${package[@]/%/=${ver-}})
        else
            echo "Didn't find '${VPP_VERSION-}' among '${package}' versions."
        fi
    done
    set -x

    if [[ "${INSTALL:-false}" == "true" ]]; then
        sudo apt-get -y install "${artifacts[@]}" || {
            die "Install VPP artifacts failed."
        }
    else
        apt-get -y download "${artifacts[@]}" || {
            die "Download VPP artifacts failed."
        }
    fi
}
