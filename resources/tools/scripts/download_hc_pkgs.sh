#!/bin/bash

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

set -x

STREAM=$1
OS=$2

# TODO(CSIT-994): reenable NSH
# NSH_GROUP="io.fd.nsh_sfc"
# NSH_ARTIFACTS="vpp-nsh-plugin"
# Figure out what system we are running on
if [[ -f /etc/os-release ]];then
    source /etc/os-release
else
    echo "Cannot determine OS version"
    exit 1
fi
echo "----- OS INFO -----"
echo DISTRIB_ID: ${ID}
echo DISTRIB_RELEASE: ${VERSION_ID}
echo DISTRIB_CODENAME: ${VERSION_CODENAME}
echo DISTRIB_DESCRIPTION: ${PRETTY_NAME}

VERSION="RELEASE"
echo "----- DOWNLOADING HONEYCOMB AND JVPP PACKAGES -----"
REPO_URL="https://packagecloud.io/fdio/${STREAM}"
echo "REPO_URL: ${REPO_URL}"
if [[ "$ID" == "ubuntu" ]]; then
    if [[ -f /etc/apt/sources.list.d/99fd.io.list ]];then
        echo "Deleting: /etc/apt/sources.list.d/99fd.io.list"
        sudo rm /etc/apt/sources.list.d/99fd.io.list
    fi
    curl -s https://packagecloud.io/install/repositories/fdio/${STREAM}/script.deb.sh | sudo bash
    apt-get download honeycomb vpp-api-java || true
elif [[ "$ID" == "centos" ]]; then
    if [[ -f /etc/yum.repos.d/fdio-master.repo ]]; then
        echo "Deleting: /etc/yum.repos.d/fdio-master.repo"
        sudo rm /etc/yum.repos.d/fdio-master.repo
    fi
    curl -s https://packagecloud.io/install/repositories/fdio/${STREAM}/script.rpm.sh | sudo bash
    sudo yum -y install --downloadonly --downloaddir=./ honeycomb vpp-api-java || true
fi

# TODO(CSIT-994): reenable NSH
# for ART in ${NSH_ARTIFACTS}; do
#     for PAC in ${PACKAGE}; do
#         curl "${URL}?r=${REPO}&g=${NSH_GROUP}&a=${ART}&p=${PAC}&v=${VER}&c=${CLASS}" -O -J || exit
#     done
# done

# determine VPP dependency
# use latest if honeycomb package does not depend on single VPP version, e.g. stable branches since HC2VPP-285
VERSION="RELEASE"
if [[ "${OS}" == "centos7" ]]; then
    HC_VPP_VER=`rpm -qpR honeycomb*.rpm | grep -oP 'vpp = \K.+'`
    if [[ "${HC_VPP_VER}" != "" ]]; then
        VERSION=${HC_VPP_VER}.x86_64
    fi
else
    HC_VPP_VER=`dpkg -I honeycomb*.deb | grep -oP 'vpp \(= \K[^\)]+'`
    if [[ "${HC_VPP_VER}" != "" ]]; then
        VERSION=${HC_VPP_VER}
    fi
fi

VPP_DEB_NEW_ARTIFACTS="vpp libvppinfra vpp-plugin-core vpp-plugin-dpdk vpp-api-python"
VPP_DEB_ARTIFACTS="vpp vpp-lib vpp-plugins vpp-api-python"
VPP_RPM_ARTIFACTS="vpp vpp-lib vpp-plugins vpp-api-python"
# Check OS and stream to set correct packages
if [[ "$ID" == "centos" ]]; then
    VPP_ARTIFACTS=${VPP_RPM_ARTIFACTS}
elif [[ "$ID" == "ubuntu" ]]; then
    if [[ "1807 1810 1901" =~ .*$STREAM.* ]]; then
        VPP_ARTIFACTS=${VPP_DEB_ARTIFACTS}
    else
        VPP_ARTIFACTS=${VPP_DEB_NEW_ARTIFACTS}
    fi
fi
VPP_DEB_PACKAGES=""
VPP_RPM_PACKAGES=""
INSTALL_PACKAGES=""
for ART in ${VPP_ARTIFACTS}; do
    INSTALL_PACKAGES="$INSTALL_PACKAGES $ART*"
    if [[ "${VERSION}" != 'RELEASE' ]]; then
            VPP_DEB_PACKAGES="$VPP_DEB_PACKAGES $ART=$VERSION"
            VPP_RPM_PACKAGES="$VPP_RPM_PACKAGES $ART-$VERSION"
    else
        VPP_DEB_PACKAGES="$VPP_DEB_PACKAGES $ART"
        VPP_RPM_PACKAGES="$VPP_RPM_PACKAGES $ART"
    fi
done

echo "----- DOWNLOADING VPP PACKAGES -----"
REPO_URL="https://packagecloud.io/fdio/${STREAM}"
echo "REPO_URL: ${REPO_URL}"
if [[ "$ID" == "ubuntu" ]]; then
    apt-get download ${VPP_DEB_PACKAGES} || true
elif [[ "$ID" == "centos" ]]; then
    sudo yum -y install --downloadonly --downloaddir=./ ${VPP_RPM_PACKAGES} || true
fi
