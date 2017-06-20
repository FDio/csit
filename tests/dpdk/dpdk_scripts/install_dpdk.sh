#!/bin/bash

set -x

# Setting variables
DPDK_VERSION=dpdk-17.05
DPDK_DIR=${DPDK_VERSION}
DPDK_PACKAGE=${DPDK_DIR}.tar.xz
ROOTDIR=/tmp/openvpp-testing
PWDDIR=$(pwd)

# Download the DPDK package
cd ${ROOTDIR}
wget "fast.dpdk.org/rel/${DPDK_PACKAGE}" || \
    { echo "Failed to download $DPDK_PACKAGE"; exit 1; }
tar xJvf ${DPDK_PACKAGE} || \
    { echo "Failed to extract $DPDK_PACKAGE"; exit 1; }

# Compile the DPDK
cd ./${DPDK_DIR}
sudo sed -i 's/^CONFIG_RTE_LIBRTE_I40E_16BYTE_RX_DESC=n/CONFIG_RTE_LIBRTE_I40E_16BYTE_RX_DESC=y/g' ./config/common_base
make install T=x86_64-native-linuxapp-gcc -j || \
    { echo "Failed to compile $DPDK_VERSION"; exit 1; }
cd ${PWDDIR}

# Compile the l3fwd
export RTE_SDK=${ROOTDIR}/${DPDK_DIR}/
export RTE_TARGET=x86_64-native-linuxapp-gcc
cd ${RTE_SDK}/examples/l3fwd
sudo sed -i 's/^#define RTE_TEST_RX_DESC_DEFAULT 128/#define RTE_TEST_RX_DESC_DEFAULT 2048/g' ./main.c
sudo sed -i 's/^#define RTE_TEST_TX_DESC_DEFAULT 512/#define RTE_TEST_TX_DESC_DEFAULT 2048/g' ./main.c
make -j || \
    { echo "Failed to compile l3fwd"; exit 1; }
cd ${PWDDIR}

# Check and setup the hugepages
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
    sudo mount -t hugetlbfs nodev /mnt/huge/ || \
        { echo "Failed to mount hugepages"; exit 1; }
fi

# Check and set the max map count
SYS_MAP=$(cat /proc/sys/vm/max_map_count)

if [ ${SYS_MAP} -lt 200000 ]; then
    echo 200000 | sudo tee /proc/sys/vm/max_map_count
fi
