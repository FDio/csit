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

URL="https://nexus.fd.io/service/local/artifact/maven/content"
VER="RELEASE"
REPO='fd.io.master.ubuntu.trusty.main'
GROUP="io.fd.vpp"
HC_GROUP="io.fd.honeycomb"
VPP_ARTIFACTS="vpp vpp-dbg vpp-dev vpp-dpdk-dev vpp-dpdk-dkms vpp-lib vpp-plugins"
HC_ARTIFACTS="honeycomb"
PACKAGE="deb deb.md5"
CLASS="deb"

for ART in ${VPP_ARTIFACTS}; do
    for PAC in $PACKAGE; do
        curl "${URL}?r=${REPO}&g=${GROUP}&a=${ART}&p=${PAC}&v=${VER}&c=${CLASS}" -O -J || exit
    done
done

for ART in ${HC_ARTIFACTS}; do
    for PAC in $PACKAGE; do
        curl "${URL}?r=${REPO}&g=${HC_GROUP}&a=${ART}&p=${PAC}&v=${VER}&c=${CLASS}" -O -J || exit
    done
done

for FILE in *.deb; do
    echo " "${FILE} >> ${FILE}.md5
done

for MD5FILE in *.md5; do
    md5sum -c ${MD5FILE} || exit
done
