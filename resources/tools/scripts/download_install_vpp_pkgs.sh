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

set -ex

URL="https://nexus.fd.io/service/local/artifact/maven/content"
VER="RELEASE"
GROUP="io.fd.vpp"

if [ -f "/etc/redhat-release" ]; then
    trap 'rm -f *.rpm.md5; exit' EXIT
    trap 'rm -f *.rpm.md5;rm -f *.rpm; exit' ERR

    VPP_REPO_URL_PATH="./VPP_REPO_URL_CENTOS"
    if [ -e "$VPP_REPO_URL_PATH" ]; then
        VPP_REPO_URL=$(cat $VPP_REPO_URL_PATH)
        REPO=$(echo ${VPP_REPO_URL#https://nexus.fd.io/content/repositories/})
        REPO=$(echo ${REPO%/io/fd/vpp/})
    else
        REPO='fd.io.master.centos7'
    FILES=*.rpm
    MD5FILES=*.rpm.md5
    fi

    ARTIFACTS="vpp vpp-selinux-policy vpp-devel vpp-lib vpp-plugins"
    PACKAGE="rpm rpm.md5"
    CLASS=""
    VPP_INSTALL_COMMAND="rpm -ivh *.rpm"
else
    trap 'rm -f *.deb.md5; exit' EXIT
    trap 'rm -f *.deb.md5;rm -f *.deb; exit' ERR

    VPP_REPO_URL_PATH="./VPP_REPO_URL_UBUNTU"
    if [ -e "$VPP_REPO_URL_PATH" ]; then
        VPP_REPO_URL=$(cat $VPP_REPO_URL_PATH)
        REPO=$(echo ${VPP_REPO_URL#https://nexus.fd.io/content/repositories/})
        REPO=$(echo ${REPO%/io/fd/vpp/})
    else
        REPO='fd.io.master.ubuntu.xenial.main'
    FILES=*.deb
    MD5FILES=*.deb.md5
    fi

    ARTIFACTS="vpp vpp-dbg vpp-dev vpp-dpdk-dkms vpp-lib vpp-plugins"
    PACKAGE="deb deb.md5"
    CLASS="deb"
    VPP_INSTALL_COMMAND="dpkg -i *.deb"
fi

for ART in ${ARTIFACTS}; do
    for PAC in $PACKAGE; do
        curl "${URL}?r=${REPO}&g=${GROUP}&a=${ART}&p=${PAC}&v=${VER}&c=${CLASS}" -O -J || exit
    done
done

for FILE in ${FILES}; do
    echo " "${FILE} >> ${FILE}.md5
done

for MD5FILE in ${MD5FILES}; do
    md5sum -c ${MD5FILE} || exit
done

if [ "$1" != "--skip-install" ]; then
    echo Installing VPP
    sudo ${VPP_INSTALL_COMMAND}
else
    echo VPP Installation skipped
fi
