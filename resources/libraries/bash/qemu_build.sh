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

echo
echo Downloading QEMU source
echo
sudo rm -rf /tmp/qemu-2.2.1
cd /tmp
wget http://wiki.qemu-project.org/download/qemu-2.2.1.tar.bz2

echo
echo Extracting QEMU
echo
tar xjf qemu-2.2.1.tar.bz2
rm qemu-2.2.1.tar.bz2

echo
echo Building QEMU
echo
cd qemu-2.2.1
mkdir build
cd build
../configure --target-list=x86_64-softmmu
make -j`nproc`

echo
echo QEMU ready
echo
