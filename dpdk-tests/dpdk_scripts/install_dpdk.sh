#!/bin/bash

ROOTDIR=/tmp/openvpp-testing
PWDDIR=$(pwd)

#compile and install the DPDK
cd ${ROOTDIR}
tar xJf dpdk-16.07.tar.xz
cd ./dpdk-16.07
make install T=x86_64-native-linuxapp-gcc -j
cd ${PWDDIR}

#compile the l3fwd
export RTE_SDK=${ROOTDIR}/dpdk-16.07/
export RTE_TARGET=x86_64-native-linuxapp-gcc
cd ${RTE_SDK}/examples/l3fwd
make -j
cd ${PWDDIR}

#setup the hugepages
MOUNT=$(mount | grep /mnt/huge)
while [ "${MOUNT}" != "" ]
do
    sudo umount /mnt/huge
    sleep 1
    MOUNT=$(mount | grep /mnt/huge)
done

echo 2048 > /sys/devices/system/node/node0/hugepages/hugepages-2048kB/nr_hugepages
echo 2048 > /sys/devices/system/node/node1/hugepages/hugepages-2048kB/nr_hugepages

sudo mkdir -p /mnt/huge
sudo mount -t hugetlbfs nodev /mnt/huge/
test $? -eq 0 || exit 1

echo 200000 > /proc/sys/vm/max_map_count

#modprobe uio
#insmod ${RTE_SDK}/${RTE_TARGET}/kmod/igb_uio.ko
