#!/usr/bin/env bash

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

function download_artifacts () {
    # Get and/or install VPP artifacts from packagecloud.io.
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
        download_ubuntu_artifacts || die
    elif [ "${os_id}" == "centos" ]; then
        download_centos_artifacts || die
    elif [ "${os_id}" == "opensuse" ]; then
        download_opensuse_artifacts || die
    else
        die "${os_id} is not yet supported."
    fi
}

function download_ubuntu_artifacts () {
    # Get and/or install Ubuntu VPP artifacts from packagecloud.io.
    #
    # Variables read:
    # - REPO_URL - FD.io Packagecloud repository.
    # - VPP_VERSION - VPP version.
    # - INSTALL - If install packages or download only. Default: download

    set -exuo pipefail

    curl -s "${REPO_URL}"/script.deb.sh | sudo bash || {
        die "Packagecloud FD.io repo fetch failed."
    }
    # If version is set we will add suffix.
    artifacts=()
    vpp=(vpp vpp-dbg vpp-dev vpp-api-python libvppinfra libvppinfra-dev
         vpp-plugin-core vpp-plugin-dpdk)
    if [ -z "${VPP_VERSION-}" ]; then
        artifacts+=(${vpp[@]})
    else
        artifacts+=(${vpp[@]/%/=${VPP_VERSION-}})
    fi

    if [ "${INSTALL:-false}" = true ]; then
        sudo apt-get -y install "${artifacts[@]}" || {
            die "Install VPP artifacts failed."
        }
    else
       echo "Not downloading packages, expecting packages in download_dir"
       # apt-get -y download "${artifacts[@]}" || {
       #     die "Download VPP artifacts failed."
       # }
#wget --content-disposition https://packagecloud.io/fdio/master/packages/ubuntu/bionic/vpp_${VPP_VERSION-}_arm64.deb/download.deb
#wget --content-disposition https://packagecloud.io/fdio/master/packages/ubuntu/bionic/vpp-api-python_${VPP_VERSION-}_arm64.deb/download.deb
#wget --content-disposition https://packagecloud.io/fdio/master/packages/ubuntu/bionic/vpp-dbg_${VPP_VERSION-}_arm64.deb/download.deb
#wget --content-disposition https://packagecloud.io/fdio/master/packages/ubuntu/bionic/vpp-dev_${VPP_VERSION-}_arm64.deb/download.deb
#wget --content-disposition https://packagecloud.io/fdio/master/packages/ubuntu/bionic/libvppinfra_${VPP_VERSION-}_arm64.deb/download.deb
#wget --content-disposition https://packagecloud.io/fdio/master/packages/ubuntu/bionic/libvppinfra-dev_${VPP_VERSION-}_arm64.deb/download.deb
#wget --content-disposition https://packagecloud.io/fdio/master/packages/ubuntu/bionic/vpp-plugin-dpdk_${VPP_VERSION-}_arm64.deb/download.deb
#wget --content-disposition https://packagecloud.io/fdio/master/packages/ubuntu/bionic/vpp-plugin-core_${VPP_VERSION-}_arm64.deb/download.deb
    fi
}

function download_centos_artifacts () {
    # Get and/or install CentOS VPP artifacts from packagecloud.io.
    #
    # Variables read:
    # - REPO_URL - FD.io Packagecloud repository.
    # - VPP_VERSION - VPP version.
    # - INSTALL - If install packages or download only. Default: download

    set -exuo pipefail

    curl -s "${REPO_URL}"/script.rpm.sh | sudo bash || {
        die "Packagecloud FD.io repo fetch failed."
    }
    # If version is set we will add suffix.
    artifacts=()
    vpp=(vpp vpp-selinux-policy vpp-devel vpp-lib vpp-plugins vpp-api-python)
    if [ -z "${VPP_VERSION-}" ]; then
        artifacts+=(${vpp[@]})
    else
        artifacts+=(${vpp[@]/%/-${VPP_VERSION-}})
    fi

    if [ "${INSTALL:-false}" = true ]; then
        sudo yum -y install "${artifacts[@]}" || {
            die "Install VPP artifact failed."
        }
    else
        sudo yum -y install --downloadonly --downloaddir=. "${artifacts[@]}" || {
            die "Download VPP artifacts failed."
        }
    fi
}

function download_opensuse_artifacts () {
    # Get and/or install OpenSuSE VPP artifacts from packagecloud.io.
    #
    # Variables read:
    # - REPO_URL - FD.io Packagecloud repository.
    # - VPP_VERSION - VPP version.
    # - INSTALL - If install packages or download only. Default: download

    set -exuo pipefail

    curl -s "${REPO_URL}"/script.rpm.sh | sudo bash || {
        die "Packagecloud FD.io repo fetch failed."
    }
    # If version is set we will add suffix.
    artifacts=()
    vpp=(vpp vpp-devel vpp-lib vpp-plugins libvpp0)
    if [ -z "${VPP_VERSION-}" ]; then
        artifacts+=(${vpp[@]})
    else
        artifacts+=(${vpp[@]/%/-${VPP_VERSION-}})
    fi

    if [ "${INSTALL:-false}" = true ]; then
        sudo yum -y install "${artifacts[@]}" || {
            die "Install VPP artifact failed."
        }
    else
        sudo yum -y install --downloadonly --downloaddir=. "${artifacts[@]}" || {
            die "Download VPP artifacts failed."
        }
    fi
}

