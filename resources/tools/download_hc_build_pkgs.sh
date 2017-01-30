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

trap 'rm -f *.deb.md5; exit' EXIT
trap 'rm -f *.deb.md5;rm -f *.deb; exit' ERR
STREAM=$1

# Download the latest VPP .deb packages, their matching JVPP .jar and VPP plugin .deb packages
URL="https://nexus.fd.io/service/local/artifact/maven/content"
VER="LATEST"
REPO='fd.io.'${STREAM}'.ubuntu.trusty.main'
JVPP_REPO='fd.io.snapshot'
VPP_GROUP="io.fd.vpp"
HC_GROUP="io.fd.hc2vpp"
NSH_GROUP="io.fd.nsh_sfc"
VPP_ARTIFACTS="vpp vpp-dbg vpp-dev vpp-dpdk-dev vpp-dpdk-dkms vpp-lib vpp-plugins"
JVPP_ARTIFACTS="jvpp-core jvpp-registry"
HC_ARTIFACTS="honeycomb"
NSH_ARTIFACTS="vpp-nsh-plugin"
PACKAGE="deb deb.md5"
JVPP_PACKAGE="jar jar.md5"
CLASS="deb"

for ART in ${VPP_ARTIFACTS}; do
    for PAC in $PACKAGE; do
        curl "${URL}?r=${REPO}&g=${VPP_GROUP}&a=${ART}&p=${PAC}&v=${VER}&c=${CLASS}" -O -J || exit
    done
done

for ART in ${JVPP_ARTIFACTS}; do
    for PAC in $JVPP_PACKAGE; do
        curl "${URL}?r=${JVPP_REPO}&g=${VPP_GROUP}&a=${ART}&p=${PAC}&v=${VER}" -O -J || exit
    done
done

for ART in ${HC_ARTIFACTS}; do
    for PAC in $PACKAGE; do
        curl "${URL}?r=${REPO}&g=${HC_GROUP}&a=${ART}&p=${PAC}&v=${VER}&c=${CLASS}" -O -J || exit
    done
done

for ART in ${NSH_ARTIFACTS}; do
    for PAC in $PACKAGE; do
        curl "${URL}?r=${REPO}&g=${NSH_GROUP}&a=${ART}&p=${PAC}&v=${VER}&c=${CLASS}" -O -J || exit
    done
done

for FILE in *.deb; do
    echo " "${FILE} >> ${FILE}.md5
done

for FILE in *.jar; do
    echo " "${FILE} >> ${FILE}.md5
done

for MD5FILE in *.md5; do
    md5sum -c ${MD5FILE} || exit
done

# Install JVPP to maven local repo, to be used in HC2VPP build
JVPP_JARS=$(find . -type f -iname '*.jar')
for item in jvpp*.jar; do
    # Example filename: jvpp-registry-17.01-20161206.125556-1.jar
    # ArtifactId = jvpp-registry
    # Version = 17.01
    basefile=$(basename -s .jar "$item")
    artifactId=$(echo "$basefile" | cut -d '-' -f 1-2)
    version=$(echo "$basefile" | cut -d '-' -f 3)
    mvn install:install-file -Dfile=${item} -DgroupId=io.fd.vpp -DartifactId=${artifactId} -Dversion=${version} -Dpackaging=jar -Dmaven.repo.local=/tmp/r -Dorg.ops4j.pax.url.mvn.localRepository=/tmp/r
done
