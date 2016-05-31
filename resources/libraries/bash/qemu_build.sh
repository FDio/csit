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

QEMU_VERSION="qemu-2.2.1"

QEMU_DOWNLOAD_REPO="http://wiki.qemu-project.org/download/"
QEMU_DOWNLOAD_PACKAGE="${QEMU_VERSION}.tar.bz2"
QEMU_PACKAGE_URL="${QEMU_DOWNLOAD_REPO}${QEMU_DOWNLOAD_PACKAGE}"
QEMU_INSTALL_DIR="/opt/qemu"

if test "$(id -u)" -ne 0
then
    echo "Please use root or sudo to be able to access target installation directory: ${TARGET_DIR}"
    exit 1
fi

WORKING_DIR=$(mktemp -d)
test $? -eq 0 || exit 1

cleanup () {
    rm -r ${WORKING_DIR}
}

trap cleanup EXIT

test -d ${QEMU_INSTALL_DIR} && echo "Qemu aleready installed: ${QEMU_INSTALL_DIR}" && exit 0

echo
echo Downloading QEMU source
echo
wget -P ${WORKING_DIR} -q ${QEMU_PACKAGE_URL} || exit
test $? -eq 0 || exit 1

echo
echo Extracting QEMU
echo
tar --strip-components 1 -xjf ${QEMU_DOWNLOAD_PACKAGE} -C ${WORKING_DIR} || exit
test $? -eq 0 || exit 1

echo
echo Building QEMU
echo
cd ${WORKING_DIR}
mkdir ${QEMU_INSTALL_DIR}
mkdir build
cd build
../configure --target-list=x86_64-softmmu --prefix=${QEMU_INSTALL_DIR} || exit
make -j`nproc` || exit 1
make install || exit 1

echo
echo QEMU ready
echo
