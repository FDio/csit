#!/bin/bash

# Copyright (c) 2017 Cisco and/or its affiliates.
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

STREAM=$1
OS=$2

URL="https://nexus.fd.io/service/local/artifact/maven/content"
VER="RELEASE"
GROUP="io.fd.vpp"
NSH_GROUP="io.fd.nsh_sfc"
NSH_ARTIFACTS="vpp-nsh-plugin"

if [ "${OS}" == "ubuntu1604" ]; then
    trap 'rm -f *.deb.md5; exit' EXIT
    trap 'rm -f *.deb.md5;rm -f *.deb; exit' ERR
        REPO_OS="ubuntu.xenial.main"
    VPP_ARTIFACTS="vpp vpp-selinux-policy vpp-devel vpp-lib vpp-plugins vpp-api-java vpp-api-python vpp-api-lua"
    PACKAGE="deb deb.md5"
    CLASS="deb"
    FILES="*.deb"
    MD5FILES="*.deb.md5"
elif [ "${OS}" == "centos7" ]; then
    trap 'rm -f *.rpm.md5; exit' EXIT
    trap 'rm -f *.rpm.md5;rm -f *.rpm; exit' ERR
    REPO_OS="centos7"
    VPP_ARTIFACTS="vpp vpp-dbg vpp-dev vpp-dpdk-dkms vpp-lib vpp-plugins vpp-api-java vpp-api-python vpp-api-lua"
    PACKAGE="rpm rpm.md5"
    CLASS="rpm"
    FILES="*.rpm"
    MD5FILES="*.rpm.md5"
fi

REPO="fd.io.${STREAM}.${REPO_OS}"

for ART in ${VPP_ARTIFACTS}; do
    for PAC in $PACKAGE; do
        curl "${URL}?r=${REPO}&g=${GROUP}&a=${ART}&p=${PAC}&v=${VER}&c=${CLASS}" -O -J || exit
    done
done

for ART in ${NSH_ARTIFACTS}; do
    for PAC in $PACKAGE; do
        curl "${URL}?r=${REPO}&g=${NSH_GROUP}&a=${ART}&p=${PAC}&v=${VER}&c=${CLASS}" -O -J || exit
    done
done

VPP_PKGS=($(echo ${FILES}))
for FILE in "${!VPP_PKGS[@]}"; do
    echo " "${FILE} >> ${FILE}.md5
done

MD5_PKGS=($(echo ${MD5FILES}))
for MD5FILE in "${!MD5_PKGS[@]}"; do
    md5sum -c ${MD5FILE} || exit
done
