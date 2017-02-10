#!/bin/bash

DPDK_VERSION=17.02
DPDK_DIR=dpdk-${DPDK_VERSION}
DPDK_PACKAGE=${DPDK_DIR}.tar.xz

ROOTDIR=/tmp/openvpp-testing
PWDDIR=$(pwd)

#download the DPDK package
#compile and install the DPDK
cd ${ROOTDIR}
wget -q "fast.dpdk.org/rel/${DPDK_PACKAGE}" || exit 1
tar xJf ${DPDK_PACKAGE}
cd ./${DPDK_DIR}
make install T=x86_64-native-linuxapp-gcc -j || exit 1
cd ${PWDDIR}

#compile the l3fwd
export RTE_SDK=${ROOTDIR}/${DPDK_DIR}/
export RTE_TARGET=x86_64-native-linuxapp-gcc
cd ${RTE_SDK}/examples/l3fwd
make -j || exit 1
cd ${PWDDIR}

#check and setup the hugepages
SYS_HUGEPAGE=$(cat /sys/kernel/mm/hugepages/hugepages-2048kB/nr_hugepages)
if [ ${SYS_HUGEPAGE} -lt 4096 ]; then
    MOUNT=$(mount | grep /mnt/huge)
    while [ "${MOUNT}" != "" ]
    do
        sudo umount /mnt/huge
        sleep 1
        MOUNT=$(mount | grep /mnt/huge)
    done

    echo 2048 | sudo tee /sys/devices/system/node/node0/hugepages/hugepages-2048kB/nr_hugepages
    echo 2048 | sudo tee /sys/devices/system/node/node1/hugepages/hugepages-2048kB/nr_hugepages

    sudo mkdir -p /mnt/huge
    sudo mount -t hugetlbfs nodev /mnt/huge/
    test $? -eq 0 || exit 1
fi

#check and set the max map count
SYS_MAP=$(cat /proc/sys/vm/max_map_count)
if [ ${SYS_MAP} -lt 200000 ]; then
    echo 200000 | sudo tee /proc/sys/vm/max_map_count
fi
