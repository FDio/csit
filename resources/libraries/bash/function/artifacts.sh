#!/usr/bin/env bash

# Copyright (c) 2019 Cisco and/or its affiliates.
# Copyright (c) 2019 PANTHEON.tech and/or its affiliates.
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
    BOTH_QUOTES='"'"'"
    MATCH="[^${BOTH_QUOTES}]*"
    QMATCH="[${BOTH_QUOTES}]\?"
    SED_COMMAND="s#.*apt_source_path=${QMATCH}\(${MATCH}\)${QMATCH}#\1#p"
    APT_FDIO_REPO_FILE=$(curl -s "${REPO_URL}"/script.deb.sh | \
                         sed -n ${SED_COMMAND}) || {
                             die "Local fdio repo file path fetch failed."
                         }

    if [ ! -f ${APT_FDIO_REPO_FILE} ]; then
        die "${APT_FDIO_REPO_FILE} not found, \
            repository installation was not successful."
    fi

    packages=$(apt-cache -o Dir::Etc::SourceList=${APT_FDIO_REPO_FILE} \
               -o Dir::Etc::SourceParts=${APT_FDIO_REPO_FILE} dumpavail \
               | grep Package: | cut -d " " -f 2) || {
                   die "Retrieval of available VPP packages failed."
               }
    if [ -z "${VPP_VERSION-}" ]; then
        # If version is not specified, find out the most recent version
        VPP_VERSION=$(apt-cache --no-all-versions show vpp | grep Version: | \
                      cut -d " " -f 2) || {
                          die "Retrieval of most recent VPP version failed."
                      }
    fi

    set +x
    for package in ${packages}; do
        # Filter packages with given version
        pkg_info=$(apt-cache show ${package}) || {
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

    if [ "${INSTALL:-false}" = true ]; then
        sudo apt-get -y install "${artifacts[@]}" || {
            die "Install VPP artifacts failed."
        }
    else
        apt-get -y download "${artifacts[@]}" || {
            die "Download VPP artifacts failed."
        }
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
    packages=(vpp vpp-selinux-policy vpp-devel vpp-lib vpp-plugins vpp-api-python)
    if [ -z "${VPP_VERSION-}" ]; then
        artifacts+=(${packages[@]})
    else
        artifacts+=(${packages[@]/%/-${VPP_VERSION-}})
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
    packages=(vpp vpp-devel vpp-lib vpp-plugins libvpp0)
    if [ -z "${VPP_VERSION-}" ]; then
        artifacts+=(${packages[@]})
    else
        artifacts+=(${packages[@]/%/-${VPP_VERSION-}})
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
