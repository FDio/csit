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

OS_ID=$(grep '^ID=' /etc/os-release | cut -f2- -d= | sed -e 's/\"//g')
OS_VERSION_ID=$(grep '^VERSION_ID=' /etc/os-release | cut -f2- -d= | sed -e 's/\"//g')

# TODO: Convert to new bash coding style
# TODO: Add die()

function artifacts {
    # TODO: Docstring

    set -exuo pipefail

    REPO_URL_PATH="./VPP_REPO_URL"
    if [ -e "${REPO_URL_PATH}" ]; then
        REPO_URL="$(<${REPO_URL_PATH})"
    else
        REPO_URL="https://packagecloud.io/install/repositories/fdio/master"
    fi
    if [ "${OS_ID}" == "ubuntu" ]; then
        curl -s "${REPO_URL}"/script.deb.sh | sudo bash

        # If version is set we will add suffix
        VPP=(vpp vpp-dbg vpp-dev vpp-lib vpp-plugins)
        DKMS=(vpp-dpdk-dkms)
        if [ -z "${VPP_VERSION}" ]; then
            ARTIFACTS+=(${VPP[@]/%/${VPP_VERSION}})
            ARTIFACTS+=(${DKMS[@]/%/${DKMS_VERSION}})
        else
            ARTIFACTS+=(${VPP[@]/%/=${VPP_VERSION}})
            ARTIFACTS+=(${DKMS[@]/%/=${DKMS_VERSION}})
        fi

        if [ "${INSTALL}" = true ]; then
            echo Installing VPP
            sudo apt-get -y install "${ARTIFACTS[@]}"
        else
            echo Downloading VPP
            apt-get -y download "${ARTIFACTS[@]}"
        fi

    elif [ "${OS_ID}" == "centos" ]; then
        curl -s "${REPO_URL}"/script.rpm.sh | sudo bash

        # If version is set we will add suffix
        VPP=(vpp vpp-selinux-policy vpp-devel vpp-lib vpp-plugins)
        if [ -z "${VPP_VERSION}" ]; then
            ARTIFACTS+=(${VPP[@]/%/${VPP_VERSION}})
        else
            ARTIFACTS+=(${VPP[@]/%/-${VPP_VERSION}})
        fi

        if [ "${INSTALL}" = true ]; then
            echo Installing VPP
            sudo yum -y install "${ARTIFACTS[@]}"
        else
            echo Downloading VPP
            sudo yum -y install --downloadonly --downloaddir=. "${ARTIFACTS[@]}"
        fi
    elif [ "${OS_ID}" == "opensuse" ]; then
        curl -s "${REPO_URL}"/script.rpm.sh | sudo bash

        # If version is set we will add suffix
        VPP=(vpp vpp-devel vpp-lib vpp-plugins libvpp0)
        if [ -z "${VPP_VERSION}" ]; then
            ARTIFACTS+=(${VPP[@]/%/${VPP_VERSION}})
        else
            ARTIFACTS+=(${VPP[@]/%/-${VPP_VERSION}})
        fi

        if [ "${INSTALL}" = true ]; then
            echo Installing VPP
            sudo yum -y install "${ARTIFACTS[@]}"
        else
            echo Downloading VPP
            sudo yum -y install --downloadonly --downloaddir=. "${ARTIFACTS[@]}"
        fi
    else
        echo "${OS_ID} is not yet supported."
        exit 1
    fi
}

# Whether to install artifacts or not
INSTALL=true
# VPP version (default empty = latest)
VPP_VERSION=""
# DKMS version (default empty = latest)
DKMS_VERSION=""

while :
do
    case "$1" in
        -s | --skip-install)
            INSTALL=false
            shift 1
            ;;
        -v | --vpp)
            VPP_VERSION="$2"
            shift 2
            ;;
        -d | --dkms)
            DKMS_VERSION="$2"
            shift 2
            ;;
        *)
            break
            ;;
     esac
done

artifacts "${INSTALL}" "${VPP_VERSION}" "${DKMS_VERSION}"
