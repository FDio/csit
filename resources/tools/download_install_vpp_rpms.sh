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

VER="RELEASE"

VPP_REPO_URL_PATH="./VPP_REPO_URL"
if [ -e "$VPP_REPO_URL_PATH" ]; then
    VPP_REPO_URL=$(cat $VPP_REPO_URL_PATH)
    REPO=$(echo ${VPP_REPO_URL#https://nexus.fd.io/content/repositories/})
    REPO=$(echo ${REPO%/fd.io.centos7})
else
    REPO='https://nexus.fd.io/content/repositories/fd.io.centos7'
fi

ARTIFACTS="vpp vpp-lib vpp-debuginfo vpp-devel vpp-python-api vpp-plugins"


yum-config-manager --add-repo $REPO

if [ "$1" != "--skip-install" ]; then
    echo Installing VPP
    sudo yum install -y $ARTIFACTS
else
    echo VPP Installation skipped
fi
