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

QEMU_VERSION="qemu-2.5.0"
QEMU_DOWNLOAD_REPO="http://download.qemu-project.org/"
QEMU_DOWNLOAD_PACKAGE="${QEMU_VERSION}.tar.xz"
QEMU_PACKAGE_URL="${QEMU_DOWNLOAD_REPO}${QEMU_DOWNLOAD_PACKAGE}"
QEMU_INSTALL_DIR="/opt/${QEMU_VERSION}"
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

for i in "$@"; do
    case $i in
        --version=*)
            QEMU_VERSION="${i#*=}"
            shift ;;
        --directory=*)
            QEMU_INSTALL_DIR="${i#*=}"
            shift ;;
        --patch)
            PATCH=1
            shift ;;
        --force)
            FORCE=1
            shift ;;
        *)
            ;;
    esac
done

if test "$(id -u)" -ne 0
then
    echo "Please use root or sudo to be able to install into: ${QEMU_INSTALL_DIR}"
    exit 1
fi

WORKING_DIR=$(mktemp -d) || \
    { echo "Failed to create temporary working dir"; exit 1; }
trap "rm -r ${WORKING_DIR}" EXIT

if [ $FORCE ]
then
    rm -rf ${QEMU_INSTALL_DIR}
else
    test -d ${QEMU_INSTALL_DIR} && \
        { echo "Qemu already installed: ${QEMU_INSTALL_DIR}"; exit 0; }
fi

# Download QEMU source code if no local copy exists
if [ ! -f /opt/${QEMU_DOWNLOAD_PACKAGE} ]; then
    wget -P /opt -q ${QEMU_PACKAGE_URL} || \
        { echo "Failed to download ${QEMU_VERSION}"; exit 1; }
fi

# Extract archive into temp directory
tar --strip-components 1 -xf /opt/${QEMU_DOWNLOAD_PACKAGE} -C ${WORKING_DIR} || \
    { echo "Failed to extract ${QEMU_VERSION}.tar.xz"; exit 1; }

cd ${WORKING_DIR}
mkdir ${QEMU_INSTALL_DIR} || \
    { echo "Failed to create ${QEMU_INSTALL_DIR}"; exit 1; }

# Apply additional patches
if [ $PATCH ]
then
    chmod +x ${SCRIPT_DIR}/qemu_patches/${QEMU_VERSION}/*
    run-parts --verbose --report  ${SCRIPT_DIR}/qemu_patches/${QEMU_VERSION}
fi

# Build
./configure --target-list=x86_64-softmmu --prefix=${QEMU_INSTALL_DIR} || \
    { echo "Failed to configure ${QEMU_VERSION}"; exit 1; }
make -j`nproc` || \
    { echo "Failed to compile ${QEMU_VERSION}"; exit 1; }
make install || \
    { echo "Failed to install ${QEMU_VERSION}"; exit 1; }

echo QEMU ${QEMU_VERSION} ready
