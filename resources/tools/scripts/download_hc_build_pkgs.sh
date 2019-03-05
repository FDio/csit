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

set -ex

STREAM=$1
OS=$2

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

VERSION=`../vpp-version`
JVPP_VERSION=`../jvpp-version`
VPP_DEB_NEW_ARTIFACTS="vpp libvppinfra vpp-plugin-core vpp-api-java"
VPP_DEB_ARTIFACTS="vpp vpp-lib vpp-plugins vpp-api-java"
VPP_RPM_ARTIFACTS="vpp vpp-lib vpp-plugins vpp-api-java"
IGNORE_DEPS=""
# Check OS and stream to set correct packages
if [[ "$ID" == "centos" ]]; then
    VPP_ARTIFACTS=${VPP_RPM_ARTIFACTS}
elif [[ "$ID" == "ubuntu" ]]; then
    if [[ "1807 1810 1901" =~ .*$STREAM.* ]]; then
        VPP_ARTIFACTS=${VPP_DEB_ARTIFACTS}
        IGNORE_DEPS="vpp,vpp-lib,vpp-plugins"
    else
        VPP_ARTIFACTS=${VPP_DEB_NEW_ARTIFACTS}
        IGNORE_DEPS="vpp,libvppinfra,vpp-plugin-core"
    fi
fi
VPP_DEB_PACKAGES=""
VPP_RPM_PACKAGES=""
for ART in ${VPP_ARTIFACTS}; do
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
if [[ "$ID" == "ubuntu" ]]; then
    if [[ -f /etc/apt/sources.list.d/99fd.io.list ]];then
        echo "Deleting: /etc/apt/sources.list.d/99fd.io.list"
        sudo rm /etc/apt/sources.list.d/99fd.io.list
    fi
    curl -s https://packagecloud.io/install/repositories/fdio/${STREAM}/script.deb.sh | sudo bash
    apt-get download ${VPP_DEB_PACKAGES} || true
elif [[ "$ID" == "centos" ]]; then
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
    sudo rpm --nodeps --install vpp-api-java*
else
    sudo dpkg --ignore-depends=${IGNORE_DEPS} --install vpp-api-java*
fi

# install jvpp jars into maven repo, so that maven picks them up when building hc2vpp
version=`../jvpp/version`

current_dir=`pwd`
cd /usr/share/java

for item in jvpp*.jar; do
    # Example filename: jvpp-registry-19.04.jar
    # ArtifactId = jvpp-registry
    # Version = 19.04 or 19.04-SNAPSHOT
    basefile=$(basename -s .jar "$item")
    artifactId=$(echo "$basefile" | cut -d '-' -f 1-2)
    mvn install:install-file -Dfile=${item} -DgroupId=io.fd.vpp -DartifactId=${artifactId} -Dversion=${version} -Dpackaging=jar -Dmaven.repo.local=/tmp/r -Dorg.ops4j.pax.url.mvn.localRepository=/tmp/r
done

# vpp-api-package is no longer necessary, breaks the installation of other packages that follow in next steps
if [[ "${OS}" == "centos7" ]]; then
    sudo yum remove "*vpp-api-java*"
else
    sudo apt remove "*vpp-api-java*"
fi

cd ${current_dir}
