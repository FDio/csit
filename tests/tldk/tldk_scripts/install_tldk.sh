#!/bin/bash

set -x

# set arch, default to x86_64 if none given
ARCH=${1:-"x86_64"}

# dpdk prefers "arm64" to "aarch64" and does not allow arm64 native target
if [ $ARCH == "aarch64" ]; then
    ARCH="arm64"
    MACHINE="armv8a"
else
    MACHINE="native"
fi

DPDK_VERSION=16.11.1

ROOTDIR=/tmp/TLDK-testing
PWDDIR=$(pwd)
DPDK_DIR=dpdk
DPDK_PACKAGE=${DPDK_DIR}"-"${DPDK_VERSION}.tar.xz

# compile and install the DPDK
cd ${ROOTDIR}
sudo tar xvf ${DPDK_PACKAGE}
sudo mv dpdk-stable-${DPDK_VERSION} dpdk
echo $PWD
echo ${DPDK_PACKAGE}
cd ./${DPDK_DIR}
sudo sed -i 's/^CONFIG_RTE_LIBRTE_PMD_PCAP=n/CONFIG_RTE_LIBRTE_PMD_PCAP=y/g' ./config/common_base
sudo make install T=${ARCH}-${MACHINE}-linuxapp-gcc
cd ${PWDDIR}

# compile the TLDK
export RTE_SDK=${ROOTDIR}/${DPDK_DIR}/
export RTE_TARGET=${ARCH}-${MACHINE}-linuxapp-gcc
cd ${ROOTDIR}/tldk
make all
cd ${PWDDIR}

sudo killall -9 l4fwd 2>/dev/null

sleep 5

pid=`pgrep l4fwd`
if [ "$pid" != "" ]; then
    echo "terminate the l4fwd failed!"
    exit 1
fi

# check and setup the hugepages
SYS_HUGEPAGE=$(cat /sys/kernel/mm/hugepages/hugepages-2048kB/nr_hugepages)
if [ ${SYS_HUGEPAGE} -lt 1024 ]; then
    MOUNT=$(mount | grep /mnt/huge)
    while [ "${MOUNT}" != "" ]
    do
        sudo umount /mnt/huge
        sleep 1
        MOUNT=$(mount | grep /mnt/huge)
    done

    echo 1024 | sudo tee /sys/devices/system/node/node0/hugepages/hugepages-2048kB/nr_hugepages
    echo 1024 | sudo tee /sys/devices/system/node/node1/hugepages/hugepages-2048kB/nr_hugepages

    sudo mkdir -p /mnt/huge
    sudo mount -t hugetlbfs nodev /mnt/huge/
    test $? -eq 0 || exit 1
fi
