#!/bin/sh

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

# This builds the "listmaker" image. This is essentially a one-time
# action and most likely applicable to CSIT test lab only.

cd $(dirname $0)
BUILD_DIR="$(pwd)/build"
PACKER_DIR="${BUILD_DIR}/packer"
OUT_DIR="${BUILD_DIR}/output/listmaker"

if [ "$1" == "centos-7-1511" ]; then
    RELEASE_NAME="csit-centos-7-1511-listmaker"
    PACKER_TEMPLATE="listmaker/centos-7-1511.json"
else
    echo "Please provide OS as parameter:"
    echo "Options: ${0} [centos-7-1511|?]"
    exit 1
fi

VIRL_IMAGE_SUBTYPE=server
VIRL_IMAGE_NAME="${RELEASE_NAME}"
VIRL_IMAGE_FILE="${OUT_DIR}/packer-${RELEASE_NAME}"

# export PACKER_LOG="1"

# This script requires that the following two environment variables be defined-
#
# $VIRL_USER
# $VIRL_PASSWORD

if [ "$VIRL_USER" = "" ] || [ "$VIRL_PASSWORD" = "" ]
then
  echo '$VIRL_USER and $VIRL_PASSWORD environment variables must be defined'
  exit 1
fi

###
### Download and extract packer, if not already installed
###
os=$(uname -s)
if [ "$os" = "Darwin" ]
then
  packer_url="https://releases.hashicorp.com/packer/0.10.1/packer_0.10.1_darwin_amd64.zip"
elif [ "$os" = "Linux" ]
then
  packer_url="https://releases.hashicorp.com/packer/0.10.1/packer_0.10.1_linux_amd64.zip"
fi

mkdir -p $BUILD_DIR
wget -P ${PACKER_DIR} -N ${packer_url}

unzip -n ${PACKER_DIR}/packer*zip -d ${PACKER_DIR}

###
### Build the actual image as per packer script. Packer post-processor will
### upload it to VIRL.
###
${BUILD_DIR}/packer/packer build -var "release=${RELEASE_NAME}" \
  -var "outputdir=${OUT_DIR}" -force -machine-readable ${PACKER_TEMPLATE}
