#!/bin/bash
# Copyright (c) 2018 Cisco and/or its affiliates.
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

function dpdk_utils.dpdk_delete {
    # Deletes the DPDK directory
    # DPDK install directory
    dpdk_install_dir=$1
    # DPDK install version
    dpdk_install_ver=$2

    [ -d ${dpdk_install_dir}/${dpdk_install_ver} ] && \
        sudo rm -r ${dpdk_install_dir}/${dpdk_install_ver} && \
        echo "${dpdk_install_dir}/${dpdk_install_ver} removed"
}

function dpdk_utils.dpdk_install {
    # Downloads and installs DPDK
    # DPDK install directory
    dpdk_install_dir=$1
    # DPDK install version
    dpdk_install_ver=$2
    # DPDK compile target
    dpdk_target=x86_64-native-linuxapp-gcc
    # Force install (if true then remove previous installation; default false)
    force_install=${3:-false}

    if [ "$force_install" = true ]; then
        # Cleanup DPDK DIR
        dpdk_utils.dpdk_delete ${dpdk_install_dir} ${dpdk_install_ver}
    else
        # Test if DPDK was installed previously
        test -d ${dpdk_install_dir}/${dpdk_install_ver} && \
            { echo "DPDK ${dpdk_install_ver} ready"; exit 0; }
    fi

    # Download the DPDK package if no local copy exists
    if [ ! -f ${dpdk_install_dir}/${dpdk_install_ver}.tar.xz ]; then
        sudo wget -e use_proxy=yes -P ${dpdk_install_dir} -q \
            fast.dpdk.org/rel/${dpdk_install_ver}.tar.xz || \
            { echo "Failed to download ${dpdk_install_ver}"; exit 1; }
    fi

    # Create DPDK install dir if not exists and extract
    sudo mkdir -p ${dpdk_install_dir} || \
        { echo "Failed to create ${dpdk_install_dir}"; exit 1; }
    sudo tar -xJf ${dpdk_install_dir}/${dpdk_install_ver}.tar.xz \
        -C ${dpdk_install_dir} || \
        { echo "Failed to extract ${dpdk_install_ver}.tar.xz"; exit 1; }

    cd ${dpdk_install_dir}/${dpdk_install_ver}

    # Compile and install the DPDK
    sudo make install T=${dpdk_target} -j DESTDIR=install || \
        { echo "Installation of ${dpdk_install_ver} failed"; exit 1; }

    echo "DPDK ${dpdk_install_ver} ready"
}

function dpdk_utils.load_modules {
    # Loads kernel modules and bind interfaces to drivers
    # Use igb_uio [true|false]
    use_igb_uio=${1:-false}
    # DPDK install directory
    dpdk_install_dir=$2
    # DPDK install version
    dpdk_install_ver=$3

    sudo modprobe uio
    sudo modprobe uio_pci_generic

    if [ "${use_igb_uio}" = true ]; then
        sudo rmmod igb_uio
        # Try to insert IGB_UIO module
        sudo insmod ${dpdk_install_dir}/${dpdk_install_ver}/x86_64-native-linuxapp-gcc/kmod/igb_uio.ko
        # If failed then download/compile DPDK
        if [ $? -ne 0 ]; then
            dpdk_utils.dpdk_install ${dpdk_install_dir} ${dpdk_install_ver} true
            sudo insmod ${dpdk_install_dir}/${dpdk_install_ver}/x86_64-native-linuxapp-gcc/kmod/igb_uio.ko
        fi
    fi
}
