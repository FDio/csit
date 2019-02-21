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

VERSION=`../vpp-version`
JVPP_VERSION=`../jvpp-version`
# Figure out what system we are running on
if [[ -f /etc/lsb-release ]];then
    . /etc/lsb-release
elif [[ -f /etc/redhat-release ]];then
    sudo yum install -y redhat-lsb
    DISTRIB_ID=`lsb_release -si`
    DISTRIB_RELEASE=`lsb_release -sr`
    DISTRIB_CODENAME=`lsb_release -sc`
    DISTRIB_DESCRIPTION=`lsb_release -sd`
fi
echo "----- OS INFO -----"
echo DISTRIB_ID: ${DISTRIB_ID}
echo DISTRIB_RELEASE: ${DISTRIB_RELEASE}
echo DISTRIB_CODENAME: ${DISTRIB_CODENAME}
echo DISTRIB_DESCRIPTION: ${DISTRIB_DESCRIPTION}

VPP_DEB_NEW_ARTIFACTS="vpp libvppinfra vpp-plugin-core vpp-api-java"
VPP_DEB_ARTIFACTS="vpp vpp-lib vpp-plugins vpp-api-java"
VPP_RPM_ARTIFACTS="vpp vpp-lib vpp-plugins vpp-api-java"
# Check OS and stream to set correct packages
if [[ "$DISTRIB_ID" == "CentOS" ]]; then
    VPP_ARTIFACTS=${VPP_RPM_ARTIFACTS}
elif [[ "$DISTRIB_ID" == "Ubuntu" ]]; then
    if [[ "$STREAM" == "1807 1810 1901" ]]; then
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
        if [[ "$ART" == "vpp-api-java" ]]; then
            VPP_DEB_PACKAGES="$VPP_DEB_PACKAGES $ART=$JVPP_VERSION"
            VPP_RPM_PACKAGES="$VPP_RPM_PACKAGES $ART-$JVPP_VERSION"
        else
            VPP_DEB_PACKAGES="$VPP_DEB_PACKAGES $ART=$VERSION"
            VPP_RPM_PACKAGES="$VPP_RPM_PACKAGES $ART-$VERSION"
        fi
    else
        VPP_DEB_PACKAGES="$VPP_DEB_PACKAGES $ART"
        VPP_RPM_PACKAGES="$VPP_RPM_PACKAGES $ART"
    fi
done

echo "----- DOWNLOADING PACKAGES -----"
REPO_URL="https://packagecloud.io/fdio/${STREAM}"
echo "REPO_URL: ${REPO_URL}"
if [[ "$DISTRIB_ID" == "Ubuntu" ]]; then
    if [[ -f /etc/apt/sources.list.d/99fd.io.list ]];then
        echo "Deleting: /etc/apt/sources.list.d/99fd.io.list"
        sudo rm /etc/apt/sources.list.d/99fd.io.list
    fi
    if [[ "$DISTRIB_CODENAME" == "bionic" ]]; then
        sudo add-apt-repository universe
        sudo apt-get update
        sudo apt-get install -y libmbedcrypto1 libmbedtls10 libmbedx509-0
    elif [[ "$DISTRIB_CODENAME" == "xenial" ]]; then
        sudo apt-get install -y libmbedcrypto0 libmbedtls10 libmbedx509-0
    fi
    curl -s https://packagecloud.io/install/repositories/fdio/${STREAM}/script.deb.sh | sudo bash
    apt-get download ${VPP_DEB_PACKAGES} || true
elif [[ "$DISTRIB_ID" == "CentOS" ]]; then
    if [[ -f /etc/yum.repos.d/fdio-master.repo ]]; then
        echo "Deleting: /etc/yum.repos.d/fdio-master.repo"
        sudo rm /etc/yum.repos.d/fdio-master.repo
    fi
    curl -s https://packagecloud.io/install/repositories/fdio/${STREAM}/script.rpm.sh | sudo bash
    sudo yum -y install --downloadonly --downloaddir=./ ${VPP_RPM_PACKAGES} || true
fi
# TODO(CSIT-994): reenable NSH
# NSH_GROUP="io.fd.nsh_sfc"
# NSH_ARTIFACTS="vpp-nsh-plugin"

# install vpp-api-java, this extracts jvpp .jar files into usr/share/java
if [[ "${OS}" == "centos7" ]]; then
    sudo rpm --install ${INSTALL_PACKAGES}
else
    sudo dpkg --install ${INSTALL_PACKAGES}
fi

# install jvpp jars into maven repo, so that maven picks them up when building hc2vpp
version=`../jvpp/version`

current_dir=`pwd`
cd /usr/share/java

for item in jvpp*.jar; do
    # Example filename: jvpp-registry-17.01-20161206.125556-1.jar
    # ArtifactId = jvpp-registry
    # Version = 17.01
    basefile=$(basename -s .jar "$item")
    artifactId=$(echo "$basefile" | cut -d '-' -f 1-2)
    mvn install:install-file -Dfile=${item} -DgroupId=io.fd.vpp -DartifactId=${artifactId} -Dversion=${version} -Dpackaging=jar -Dmaven.repo.local=/tmp/r -Dorg.ops4j.pax.url.mvn.localRepository=/tmp/r
done

cd ${current_dir}