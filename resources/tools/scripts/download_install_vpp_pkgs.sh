#!/bin/bash

# Copyright (c) 2016 Cisco and/or its affiliates.
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

set -x -e -o pipefail

OS_ID=$(grep '^ID=' /etc/os-release | cut -f2- -d= | sed -e 's/\"//g')
OS_VERSION_ID=$(grep '^VERSION_ID=' /etc/os-release | cut -f2- -d= | sed -e 's/\"//g')

NEXUSPROXY="https://nexus.fd.io"

function artifacts {
    local install=$1

    if [ "$OS_ID" == "ubuntu" ]; then
        VPP_REPO_URL_PATH="./VPP_REPO_URL_UBUNTU"
        if [ -e "$VPP_REPO_URL_PATH" ]; then
            VPP_REPO_URL=$(cat $VPP_REPO_URL_PATH)
            REPO_NAME=$(echo ${VPP_REPO_URL#https://nexus.fd.io/content/repositories/})
            REPO_NAME=$(echo ${REPO_NAME%io/fd/vpp/})
        else
            OS_VERSION_CODENAME=$(grep '^VERSION_CODENAME=' /etc/os-release | cut -f2- -d= | sed -e 's/\"//g')
            REPO_NAME="fd.io.master.ubuntu.${OS_VERSION_CODENAME}.main"
        fi
        REPO_URL="${NEXUSPROXY}/content/repositories/${REPO_NAME}"

        echo "deb ${REPO_URL} ./" | sudo tee /etc/apt/sources.list.d/99fd.io.list
        sudo apt-get -y update \
            -o Dir::Etc::sourcelist="sources.list.d/99fd.io.list" \
            -o Acquire::AllowInsecureRepositories=true \
            -o Dir::Etc::sourceparts="-" \
            -o APT::Get::AllowUnauthenticated=true \
            -o APT::Get::List-Cleanup="0"

        ARTIFACTS="vpp vpp-dbg vpp-dev vpp-dpdk-dkms vpp-lib vpp-plugins"

        if [ "$install" = true ]; then
            echo Installing VPP
            sudo apt-get -y install ${ARTIFACTS} \
                -o Acquire::AllowInsecureRepositories=true \
                -o APT::Get::AllowUnauthenticated=true
        else
            echo Downloading VPP
            apt-get -y download ${ARTIFACTS} \
                -o Acquire::AllowInsecureRepositories=true \
                -o APT::Get::AllowUnauthenticated=true
        fi

    elif [ "$OS_ID" == "centos" ]; then
        VPP_REPO_URL_PATH="./VPP_REPO_URL_CENTOS"
        if [ -e "$VPP_REPO_URL_PATH" ]; then
            VPP_REPO_URL=$(cat $VPP_REPO_URL_PATH)
            REPO_NAME=$(echo ${VPP_REPO_URL#https://nexus.fd.io/content/repositories/})
            REPO_NAME=$(echo ${REPO_NAME%/io/fd/vpp/})
        else
            REPO_NAME="fd.io.master.centos7"
        fi
        REPO_URL="${NEXUSPROXY}/content/repositories/${REPO_NAME}"

        sudo cat << EOF > fdio-master.repo
[fdio-master]
name=fd.io master branch latest merge
baseurl=${REPO_URL}
enabled=1
gpgcheck=0
EOF
        sudo mv fdio-master.repo /etc/yum.repos.d/fdio-master.repo

        ARTIFACTS="vpp vpp-selinux-policy vpp-devel vpp-lib vpp-plugins"

        if [ "$install" = true ]; then
            echo Installing VPP
            sudo yum -y install ${ARTIFACTS}
        else
            echo Downloading VPP
            sudo yum -y install --downloadonly --downloaddir=. ${ARTIFACTS}
        fi
    elif [ "$OS_ID" == "opensuse" ]; then
        VPP_REPO_URL_PATH="./VPP_REPO_URL_OPENSUSE"
        if [ -e "$VPP_REPO_URL_PATH" ]; then
            VPP_REPO_URL=$(cat $VPP_REPO_URL_PATH)
            REPO_NAME=$(echo ${VPP_REPO_URL#https://nexus.fd.io/content/repositories/})
            REPO_NAME=$(echo ${REPO_NAME%/io/fd/vpp/})
        else
            REPO_NAME='fd.io.master.opensuse'
        fi
        REPO_URL="${NEXUSPROXY}/content/repositories/${REPO_NAME}"

        sudo cat << EOF > fdio-master.repo
[fdio-master]
name=fd.io master branch latest merge
baseurl=${REPO_URL}
enabled=1
gpgcheck=0
EOF
        sudo mv fdio-master.repo /etc/yum/repos.d/fdio-master.repo

        ARTIFACTS="vpp vpp-devel vpp-lib vpp-plugins libvpp0"

        if [ "$install" = true ]; then
            echo Installing VPP
            sudo yum -y install ${ARTIFACTS}
        else
            echo Downloading VPP
            sudo yum -y install --downloadonly --downloaddir=. ${ARTIFACTS}
        fi
    else
        echo "$OS_ID is not yet supported."
        exit 1
    fi

}

function display_help () {
    echo "Usage: $0 [--install]"
}

INSTALL=true

while :
do
    case "$1" in
        -h | --help)
            display_help
            exit 0
            ;;
        -s | --skip-install)
            INSTALL=false
            shift 1
            ;;
        -*)
            echo "Error: Unknown option: $1" >&2
            display_help
            exit 1
            ;;
        *)
            break
            ;;
     esac
done

artifacts ${INSTALL}
