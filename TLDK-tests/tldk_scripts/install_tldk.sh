#!/bin/bash

DPDK_VERSION=16.07
DPDK_DIR=dpdk-${DPDK_VERSION}
DPDK_PACKAGE=${DPDK_DIR}.tar.xz

ROOTDIR=/tmp/TLDK-testing
PWDDIR=$(pwd)

# check whether install libpcap and libpcap-dev
#output=`dpkg -l libpcap*`
#if [[ $result != *"no packages"* ]]
# then
#    echo "no libpcap candidate!"
#    exit 1
# fi
# output=`dpkg -l libpcap-dev`
# if [[ $result != *"no ppackages"* ]]
# then
#     echo "no libpcap-dev candidate"
#    exit 1
# fi


#compile and install the DPDK
cd ${ROOTDIR}
tar xJf ${DPDK_PACKAGE}
echo $PWD
echo ${DPDK_PACKAGE}
cd ./${DPDK_DIR}
sed -i 's/^CONFIG_RTE_LIBRTE_PMD_PCAP=n/CONFIG_RTE_LIBRTE_PMD_PCAP=y/g' ./config/common_base
make install T=x86_64-native-linuxapp-gcc
cd ${PWDDIR}

#compile the TLDK
export RTE_SDK=${ROOTDIR}/${DPDK_DIR}/
export RTE_TARGET=x86_64-native-linuxapp-gcc
cd ${ROOTDIR}/tldk
make all
cd ${PWDDIR}

#setup the hugepages

sudo killall -9 udpfwd 2>/dev/null

pid=`pgrep udpfwd`
if [ "$pid" != "" ]; then
    echo "terminate the udpfwd failed!"
    exit 1
fi

#check and setup the hugepages
SYS_HUGEPAGE=$(cat /sys/kernel/mm/hugepages/hugepages-2048kB/nr_hugepages)
if [ ${SYS_HUGEPAGE} -lt 1024 ]; then
    MOUNT=$(mount | grep /mnt/huge)
    while [ "${MOUNT}" != "" ]
    do
        sudo umount /mnt/huge
        sleep 1
        MOUNT=$(mount | grep /mnt/huge)
    done

    echo 1024 > /sys/devices/system/node/node0/hugepages/hugepages-2048kB/nr_hugepages
    echo 1024 > /sys/devices/system/node/node1/hugepages/hugepages-2048kB/nr_hugepages

    sudo mkdir -p /mnt/huge
    sudo mount -t hugetlbfs nodev /mnt/huge/
    test $? -eq 0 || exit 1
fi
