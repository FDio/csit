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

# TODO: Convert to new bash coding style

function artifacts () {
    # Get and/or install VPP artifacts
    #
    # Arguments:
    # - ${1} - Whether to install packages or not.
    # Variables set:
    # - XX - Desc

    set -exuo pipefail

    os_id=$(grep '^ID=' /etc/os-release | cut -f2- -d= | sed -e 's/\"//g')

    repo_url_path="./VPP_REPO_URL"
    if [ -e "${repo_url_path}" ]; then
        repo_url="$(<${repo_url_path})"
    else
        repo_url="https://packagecloud.io/install/repositories/fdio/master"
    fi

    if [ "${os_id}" == "ubuntu" ]; then
        curl -s "${repo_url}"/script.deb.sh | sudo bash || {
            die "Packagecloud repo fetch failed."
        }
        # If version is set we will add suffix.
        vpp=(vpp vpp-dbg vpp-dev vpp-lib vpp-plugins)
        dkms=(vpp-dpdk-dkms)
        if [ -z "${VPP_VERSION}" ]; then
            ARTIFACTS+=(${vpp[@]/%/${VPP_VERSION}})
            ARTIFACTS+=(${dkms[@]/%/${DKMS_VERSION}})
        else
            ARTIFACTS+=(${vpp[@]/%/=${VPP_VERSION}})
            ARTIFACTS+=(${dkms[@]/%/=${DKMS_VERSION}})
        fi

        if [ "${INSTALL}" = true ]; then
            sudo apt-get -y install "${ARTIFACTS[@]}" || {
               die "Install VPP artifact failed."
            }
        else
            apt-get -y download "${ARTIFACTS[@]}" || {
               die "Download VPP artifact failed."
            }
        fi

    elif [ "${os_id}" == "centos" ]; then
        curl -s "${repo_url}"/script.rpm.sh | sudo bash || {
            die "Packagecloud repo fetch failed."
        }
        # If version is set we will add suffix.
        vpp=(vpp vpp-selinux-policy vpp-devel vpp-lib vpp-plugins)
        if [ -z "${VPP_VERSION}" ]; then
            ARTIFACTS+=(${vpp[@]/%/${VPP_VERSION}})
        else
            ARTIFACTS+=(${vpp[@]/%/-${VPP_VERSION}})
        fi

        if [ "${INSTALL}" = true ]; then
            sudo yum -y install "${ARTIFACTS[@]}" || {
               die "Install VPP artifact failed."
            }
        else
            sudo yum -y install --downloadonly --downloaddir=. "${ARTIFACTS[@]}" || {
               die "Download VPP artifact failed."
            }
        fi
    elif [ "${os_id}" == "opensuse" ]; then
        curl -s "${repo_url}"/script.rpm.sh | sudo bash || {
            die "Packagecloud repo fetch failed."
        }
        # If version is set we will add suffix.
        vpp=(vpp vpp-devel vpp-lib vpp-plugins libvpp0)
        if [ -z "${VPP_VERSION}" ]; then
            ARTIFACTS+=(${vpp[@]/%/${VPP_VERSION}})
        else
            ARTIFACTS+=(${vpp[@]/%/-${VPP_VERSION}})
        fi

        if [ "${INSTALL}" = true ]; then
            sudo yum -y install "${ARTIFACTS[@]}" || {
               die "Install VPP artifact failed."
            }
        else
            sudo yum -y install --downloadonly --downloaddir=. "${ARTIFACTS[@]}" || {
               die "Download VPP artifact failed."
            }
        fi
    else
        die "${os_id} is not yet supported."
    fi
}

function die () {
    # Print the message to standard error end exit with error code specified
    # by the second argument.
    #
    # Hardcoded values:
    # - The default error message.
    # Arguments:
    # - ${1} - The whole error message, be sure to quote. Optional
    # - ${2} - the code to exit with, default: 1.

    set -x
    set +eu
    warn "${1:-Unspecified run-time error occurred!}"
    exit "${2:-1}"
}

function warn () {
    # Print the message to standard error.
    #
    # Arguments:
    # - ${@} - The text of the message.

    echo "$@" >&2
}

# Whether to install artifacts or not
INSTALL=true
# VPP version (default empty = latest)
VPP_VERSION=""
# DKMS version (default empty = latest)
DKMS_VERSION=""

while :
do
    case "${1-}" in
        -s | --skip-install)
            INSTALL=false
            shift 1
            ;;
        -v | --vpp)
            VPP_VERSION="${2}"
            shift 2
            ;;
        -d | --dkms)
            DKMS_VERSION="${2}"
            shift 2
            ;;
        *)
            break
            ;;
     esac
done

artifacts
