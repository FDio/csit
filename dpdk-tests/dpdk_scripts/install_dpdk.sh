#!/bin/bash

echo "###" $0 "###"

echo "Setting variables ..."
DPDK_VERSION=17.02
DPDK_DIR=dpdk-${DPDK_VERSION}
DPDK_PACKAGE=${DPDK_DIR}.tar.xz

echo "  DPDK_VERSION = ${DPDK_VERSION}"
echo "  DPDK_DIR = ${DPDK_DIR}"
echo "  DPDK_PACKAGE = ${DPDK_PACKAGE}"

ROOTDIR=/tmp/openvpp-testing
PWDDIR=$(pwd)

echo "  ROOTDIR = ${ROOTDIR}"
echo "  PWDDIR = ${PWDDIR}"

echo "Download the DPDK package ..."
cd ${ROOTDIR}
echo "  Download from fast.dpdk.org/rel/${DPDK_PACKAGE}"
wget "fast.dpdk.org/rel/${DPDK_PACKAGE}" || exit 1
echo "  Unzip ${DPDK_PACKAGE}"
tar xJvf ${DPDK_PACKAGE}

echo "Compile and install the DPDK ..."
cd ./${DPDK_DIR}
make install T=x86_64-native-linuxapp-gcc -j || exit 1
cd ${PWDDIR}

echo "Compile the l3fwd ..."
export RTE_SDK=${ROOTDIR}/${DPDK_DIR}/
export RTE_TARGET=x86_64-native-linuxapp-gcc
echo "  RTE_SDK = ${ROOTDIR}/${DPDK_DIR}/"
echo "  RTE_TARGET = x86_64-native-linuxapp-gcc"
cd ${RTE_SDK}/examples/l3fwd
make -j || exit 1
cd ${PWDDIR}

echo "Check and setup the hugepages ..."
SYS_HUGEPAGE=$(cat /sys/kernel/mm/hugepages/hugepages-2048kB/nr_hugepages)
echo "  SYS_HUGEPAGE = ${SYS_HUGEPAGE}"
if [ ${SYS_HUGEPAGE} -lt 4096 ]; then
    echo "  It is not enough, should be at least 4096"
    MOUNT=$(mount | grep /mnt/huge)
    while [ "${MOUNT}" != "" ]
    do
        sudo umount /mnt/huge
        sleep 1
        MOUNT=$(mount | grep /mnt/huge)
    done

    echo 2048 | sudo tee /sys/devices/system/node/node0/hugepages/hugepages-2048kB/nr_hugepages
    echo 2048 | sudo tee /sys/devices/system/node/node1/hugepages/hugepages-2048kB/nr_hugepages

    echo "  Mounting hugepages"
    sudo mkdir -p /mnt/huge
    sudo mount -t hugetlbfs nodev /mnt/huge/
    test $? -eq 0 || exit 1
fi

echo "Check and set the max map count ..."
SYS_MAP=$(cat /proc/sys/vm/max_map_count)
echo "  /proc/sys/vm/max_map_count: ${SYS_MAP}"

if [ ${SYS_MAP} -lt 200000 ]; then
    echo 200000 | sudo tee /proc/sys/vm/max_map_count
    echo "  /proc/sys/vm/max_map_count set to 200000"
fi
