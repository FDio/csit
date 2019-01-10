#!/usr/bin/env bash

# Copyright (c) 2019 Cisco and/or its affiliates.
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

function download_artifacts_hc () {
    # Get and/or install HC artifacts from packagecloud.io.
    #
    # Variables read:
    # - CSIT_DIR - Path to existing root of local CSIT git repository.
    # Variables set:
    # - REPO_URL - FD.io Packagecloud repository.

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
        download_ubuntu_artifacts_hc || die
    elif [ "${os_id}" == "centos" ]; then
        download_centos_artifacts_hc || die
    else
        die "${os_id} is not yet supported."
    fi
}

function download_ubuntu_artifacts_hc () {
    # Get and/or install Ubuntu HC artifacts from packagecloud.io.
    #
    # Variables read:
    # - REPO_URL - FD.io Packagecloud repository.
    # - HC_VERSION - HC version.
    # - INSTALL - If install packages or download only. Default: download

    set -exuo pipefail

    curl -s "${REPO_URL}"/script.deb.sh | sudo bash || {
        die "Packagecloud FD.io repo fetch failed."
    }
    # If version is set we will add suffix.
    artifacts=()
    hc=(honeycomb)
    if [ -z "${HC_VERSION-}" ]; then
        artifacts+=(${hc[@]})
    else
        artifacts+=(${hc[@]/%/=${HC_VERSION-}})
    fi

    if [ "${INSTALL:-false}" = true ]; then
        sudo apt-get -y install "${artifacts[@]}" || {
            die "Install HC artifacts failed."
        }
    else
        apt-get -y download "${artifacts[@]}" || {
            die "Download HC artifacts failed."
        }
    fi
}

function download_centos_artifacts_hc () {
    # Get and/or install CentOS HC artifacts from packagecloud.io.
    #
    # Variables read:
    # - REPO_URL - FD.io Packagecloud repository.
    # - HC_VERSION - HC version.
    # - INSTALL - If install packages or download only. Default: download

    set -exuo pipefail

    curl -s "${REPO_URL}"/script.rpm.sh | sudo bash || {
        die "Packagecloud FD.io repo fetch failed."
    }
    # If version is set we will add suffix.
    artifacts=()
    hc=(honeycomb)
    if [ -z "${HC_VERSION-}" ]; then
        artifacts+=(${hc[@]})
    else
        artifacts+=(${hc[@]/%/-${HC_VERSION-}})
    fi

    if [ "${INSTALL:-false}" = true ]; then
        sudo yum -y install "${artifacts[@]}" || {
            die "Install HC artifact failed."
        }
    else
        sudo yum -y install --downloadonly --downloaddir=. "${artifacts[@]}" || {
            die "Download HC artifacts failed."
        }
    fi
}

