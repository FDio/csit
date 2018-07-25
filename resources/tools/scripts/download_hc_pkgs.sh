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

set -x

STREAM=$1
OS=$2

URL="https://nexus.fd.io/service/local/artifact/maven/content"
VER="RELEASE"
GROUP="io.fd.vpp"
HC_GROUP="io.fd.hc2vpp"
NSH_GROUP="io.fd.nsh_sfc"
HC_ARTIFACTS="honeycomb"
NSH_ARTIFACTS="vpp-nsh-plugin"
VPP_ARTIFACTS="vpp vpp-lib vpp-plugins"

if [ "${OS}" == "ubuntu1604" ]; then
    OS="ubuntu.xenial.main"
    PACKAGE="deb deb.md5"
    CLASS="deb"
elif [ "${OS}" == "centos7" ]; then
    OS="centos7"
    PACKAGE="rpm rpm.md5"
    CLASS=""
fi

REPO="fd.io.${STREAM}.${OS}"

# download latest honeycomb and nsh packages
for ART in ${HC_ARTIFACTS}; do
    for PAC in ${PACKAGE}; do
        curl "${URL}?r=${REPO}&g=${HC_GROUP}&a=${ART}&p=${PAC}&v=${VER}&c=${CLASS}" -O -J || exit
    done
done

for ART in ${NSH_ARTIFACTS}; do
    for PAC in ${PACKAGE}; do
        curl "${URL}?r=${REPO}&g=${NSH_GROUP}&a=${ART}&p=${PAC}&v=${VER}&c=${CLASS}" -O -J || exit
    done
done

# determine VPP dependency
# use latest if honeycomb package does not depend on single VPP version, e.g. stable branches since HC2VPP-285
VER="RELEASE"
if [ "${OS}" == "centos7" ]; then
    HC_VPP_VER=`rpm -qpR honeycomb*.rpm | grep -oP 'vpp = \K.+'`
    if [ "${HC_VPP_VER}" != "" ]; then
        VER=${HC_VPP_VER}.x86_64
    fi
else
    HC_VPP_VER=`dpkg -I honeycomb*.deb | grep -oP 'vpp \(= \K[^\)]+'`
    if [ "${HC_VPP_VER}" != "" ]; then
        VER=${HC_VPP_VER}_amd64
    fi
fi

# download VPP packages
for ART in ${VPP_ARTIFACTS}; do
    for PAC in ${PACKAGE}; do
        curl "${URL}?r=${REPO}&g=${GROUP}&a=${ART}&p=${PAC}&v=${VER}&c=${CLASS}" -O -J || exit
    done
done

# verify downloaded package
if [ "${OS}" == "centos7" ]; then
    FILES=*.rpm
else
    FILES=*.deb
fi

for FILE in ${FILES}; do
    echo " "${FILE} >> ${FILE}.md5
done
for MD5FILE in *.md5; do
    md5sum -c ${MD5FILE} || exit
    rm ${MD5FILE}
done