#!/bin/bash

ROOTDIR=/tmp/TLDK-testing
PWDDIR=$(pwd)

#install the libpcap-dev
cd ${ROOTDIR}/TLDK-tests/tldk_deplibs/
sudo dpkg -i libpcap*.deb
cd ${PWDDIR}

#compile and install the DPDK
cd ${ROOTDIR}
tar xJf dpdk-16.07.tar.xz
cd ./dpdk-16.07
sed -i 's/^CONFIG_RTE_LIBRTE_PMD_PCAP=n/CONFIG_RTE_LIBRTE_PMD_PCAP=y/g' ./config/common_base
make install T=x86_64-native-linuxapp-gcc
cd ${PWDDIR}

#compile the TLDK
export RTE_SDK=${ROOTDIR}/dpdk-16.07/
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

MOUNT=$(mount | grep /mnt/huge)
while [ "${MOUNT}" != "" ]
do
    sudo umount /mnt/huge
    sleep 1
    MOUNT=$(mount | grep /mnt/huge)
done
sudo mkdir -p /mnt/huge
sudo mount -t hugetlbfs nodev /mnt/huge/
test $? -eq 0 || exit 1
