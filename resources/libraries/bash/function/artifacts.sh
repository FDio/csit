#!/usr/bin/env bash

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

function download_vsap () {

    # Download or install VSAP artifacts from packagecloud.io.
    #
    # Variables set:
    # - REPO_URL - FD.io Packagecloud repository.
    # - PKG_KEY - Keywords to download package.
    # Functions conditionally called (see their documentation for side effects):
    # - download_ubuntu_repo_file
    # - download_ubuntu

    set -exuo pipefail

    mode=$1
    os_id=$(grep '^ID=' /etc/os-release | cut -f2- -d= | sed -e 's/\"//g') || {
        die "Get OS release failed."
    }

    repo_url_path="${CSIT_DIR}/VSAP_REPO_URL"
    if [ -e "${repo_url_path}" ]; then
        REPO_URL="$(<${repo_url_path})" || {
            die "Read repo URL from ${repo_url_path} failed."
        }
    else
        die "Read repo URL failed."
    fi

    if [ "${os_id}" == "ubuntu" ]; then
        download_ubuntu_repo_file || die
        PKG_KEY=vsap-${mode}
        download_ubuntu_packages || die
        PKG_KEY=openssl3
        download_ubuntu_packages || die
    else
        die "${os_id} is not yet supported."
    fi

}

function download_ubuntu_repo_file () {

    # Download fdio repo file from packagecloud.io.
    #
    # Variables read:
    # - APT_FDIO_REPO_FILE - FD.io repo file in packagecloud.io.

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
    APT_FDIO_REPO_FILE=$(curl -s "${REPO_URL}"/script.deb.sh | \
                         sed -n ${sed_command}) || {
                             die "Local fdio repo file path fetch failed."
                         }
    if [ ! -f ${APT_FDIO_REPO_FILE} ]; then
        die "${APT_FDIO_REPO_FILE} not found,
	repository installation was not successful."
    fi
}

function download_ubuntu_packages () {

    # Download or install Ubuntu packages from packagecloud.io.
    #
    # Variables read:
    # - INSTALL - Whether install packages (if set to "true") or download only.
    #             Default: "false".

    packages=$(apt-cache -o Dir::Etc::SourceList=${APT_FDIO_REPO_FILE} \
               -o Dir::Etc::SourceParts=${APT_FDIO_REPO_FILE} dumpavail \
               | grep Package: | cut -d " " -f 2 | grep ${PKG_KEY}) || {
                   die "Retrieval of available ${PKG_KEY} packages failed."
               }

    if [ -z "${pkg_version-}" ]; then
        # If version is not specified, find out the most recent version
        pkg_version=$(apt-cache -o Dir::Etc::SourceList=${APT_FDIO_REPO_FILE} \
                      -o Dir::Etc::SourceParts=${APT_FDIO_REPO_FILE} \
                      --no-all-versions show ${PKG_KEY} | grep Version: | \
                      cut -d " " -f 2) || {
                          die "Retrieval of most recent version failed."
                      }
    fi
    set +x

    for package in ${packages}; do
        # Filter packages with given version
        pkg_info=$(apt-cache show -- ${package}) || {
            die "apt-cache show on ${package} failed."
        }
        ver=$(echo ${pkg_info} | grep -o "Version: ${pkg_version-}[^ ]*" | \
              head -1) || true
        if [ -n "${ver-}" ]; then
            echo "Found '${pkg_version-}' among '${package}' versions."
            ver=$(echo "$ver" | cut -d " " -f 2)
            artifacts+=(${package[@]/%/=${ver-}})
        else
            echo "Didn't find '${pkg_version-}' among '${package}' versions."
        fi
    done
    set -x
    pkg_version=""

    if [[ "${INSTALL:-false}" == "true" ]]; then
        sudo apt-get -y install "${artifacts[@]}" || {
            die "Install ${PKG_KEY} PKG artifacts failed."
        }
    else
        apt-get -y download "${artifacts[@]}" || {
            die "Download ${PKG_KEY} PKG artifacts failed."
        }
    fi


}

function download_artifacts () {

    # Download or install VPP artifacts from packagecloud.io.
    #
    # Variables read:
    # - CSIT_DIR - Path to existing root of local CSIT git repository.
    # Variables set:
    # - REPO_URL - FD.io Packagecloud repository.
    # Functions conditionally called (see their documentation for side effects):
    # - download_ubuntu_artifacts
    # - download_centos_artifacts
    # - download_opensuse_artifacts

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

    # Download or install Ubuntu VPP artifacts from packagecloud.io.
    #
    # Variables set:
    # - PKG_KEY - Keywords to download package.
    # Functions called (see their documentation for side effects):
    # - download_ubuntu_repo_file
    # - download_ubuntu
    download_ubuntu_repo_file || die
    PKG_KEY=vpp
    download_ubuntu_packages || die
}

function download_centos_artifacts () {

    # Download or install CentOS VPP artifacts from packagecloud.io.
    #
    # Variables read:
    # - REPO_URL - FD.io Packagecloud repository.
    # - VPP_VERSION - VPP version.
    # - INSTALL - Whether install packages (if set to "true") or download only.
    #             Default: "false".

    set -exuo pipefail

    curl -s "${REPO_URL}"/script.rpm.sh | sudo -E bash || {
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

    if [[ "${INSTALL:-false}" == "true" ]]; then
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

    # Download or install OpenSuSE VPP artifacts from packagecloud.io.
    #
    # Variables read:
    # - REPO_URL - FD.io Packagecloud repository.
    # - VPP_VERSION - VPP version.
    # - INSTALL - Whether install packages (if set to "true") or download only.
    #             Default: "false".

    set -exuo pipefail

    curl -s "${REPO_URL}"/script.rpm.sh | sudo -E bash || {
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

    if [[ "${INSTALL:-false}" == "true" ]]; then
        sudo yum -y install "${artifacts[@]}" || {
            die "Install VPP artifact failed."
        }
    else
        sudo yum -y install --downloadonly --downloaddir=. "${artifacts[@]}" || {
            die "Download VPP artifacts failed."
        }
    fi
}
