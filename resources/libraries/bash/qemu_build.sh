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
QEMU_INSTALL_DIR="/opt/qemu"
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

if test "$(id -u)" -ne 0
then
    echo "Please use root or sudo to be able to install into: ${QEMU_INSTALL_DIR}"
    exit 1
fi

WORKING_DIR=$(mktemp -d) || exit 1
trap "rm -r ${WORKING_DIR}" EXIT

if [[ "$@" == "--force" ]]; then
    rm -rf ${QEMU_INSTALL_DIR}
else
    test -d ${QEMU_INSTALL_DIR} && echo "Qemu already installed: ${QEMU_INSTALL_DIR}" && exit 0
fi

wget -P ${WORKING_DIR} -q ${QEMU_PACKAGE_URL} || \
    echo "Failed to download ${QEMU_VERSION}" || exit 1
tar --strip-components 1 -xjf ${WORKING_DIR}/${QEMU_DOWNLOAD_PACKAGE} -C ${WORKING_DIR} || \
    echo "Failed to exctract ${QEMU_VERSION}.tar.xz" || exit 1

cd ${WORKING_DIR}
rm -r ${QEMU_INSTALL_DIR}; mkdir ${QEMU_INSTALL_DIR} || \
    echo "Failed to create ${qemu_install_dir}" || exit 1

if [[ "$@" == "--patch" ]]; then
    run-parts -v  ${SCRIPT_DIR}/qemu_patches/${QEMU_VERSION}
fi
./configure --target-list=x86_64-softmmu --prefix=${QEMU_INSTALL_DIR} || \
    echo "Failed to configure ${QEMU_VERSION}" || exit 1
make -j`nproc` || \
    echo "Failed to compile ${QEMU_VERSION}" || exit 1
make install || \
    echo "Failed to install ${QEMU_VERSION}" || exit 1

echo QEMU ${QEMU_VERSION} ready

