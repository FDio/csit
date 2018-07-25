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

# Download the latest VPP and VPP plugin .deb packages
URL="https://nexus.fd.io/service/local/artifact/maven/content"
VER="RELEASE"
VPP_GROUP="io.fd.vpp"
NSH_GROUP="io.fd.nsh_sfc"
NSH_ARTIFACTS="vpp-nsh-plugin"
VPP_ARTIFACTS="vpp vpp-lib vpp-plugins vpp-api-java"

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

for ART in ${VPP_ARTIFACTS}; do
    for PAC in ${PACKAGE}; do
        curl "${URL}?r=${REPO}&g=${VPP_GROUP}&a=${ART}&p=${PAC}&v=${VER}&c=${CLASS}" -O -J || exit
    done
done

for ART in ${NSH_ARTIFACTS}; do
    for PAC in ${PACKAGE}; do
        curl "${URL}?r=${REPO}&g=${NSH_GROUP}&a=${ART}&p=${PAC}&v=${VER}&c=${CLASS}" -O -J || exit
    done
done

# verify downloaded packages
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

# install vpp-api-java, this extracts jvpp .jar files into usr/share/java
if [ "${OS}" == "centos7" ]; then
    sudo rpm --nodeps --install vpp-api-java*
else
    sudo dpkg --ignore-depends=vpp --install vpp-api-java*
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