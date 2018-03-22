#!/bin/bash

set -x

DPDK_VERSION=16.04

ROOTDIR=/tmp/DMM-testing
PWDDIR=$(pwd)
DPDK_DIR=dpdk
DPDK_PACKAGE=${DPDK_DIR}"-"${DPDK_VERSION}.tar.xz
DPDK_INSTALL_PATH=/tmp/DMM-testing/dpdk_install/tmp

# compile and install the DPDK
cd ${ROOTDIR}

sudo mkdir dpdk_install
sudo tar xvf ${DPDK_PACKAGE}

echo $PWD
echo ${DPDK_PACKAGE}

cd dpdk-16.04
sudo sed -i 's!CONFIG_RTE_EXEC_ENV=.*!CONFIG_RTE_EXEC_ENV=y!1' config/common_base
sudo sed -i 's!CONFIG_RTE_BUILD_SHARED_LIB=.*!CONFIG_RTE_BUILD_SHARED_LIB=y!1' config/common_base
sudo sed -i 's!CONFIG_RTE_LIBRTE_EAL=.*!CONFIG_RTE_LIBRTE_EAL=y!1' config/common_base

sudo make install  T=x86_64-native-linuxapp-gcc DESTDIR=${DPDK_INSTALL_PATH}
cd x86_64-native-linuxapp-gcc
sudo make

sudo mkdir ${DPDK_INSTALL_PATH}/lib64/
sudo cp -r ${DPDK_INSTALL_PATH}/lib/* ${DPDK_INSTALL_PATH}/lib64/

cd ${PWDDIR}

# compile the DMM
cd ${ROOTDIR}/dmm/release/lib64/
sudo rm -rf *.so
sudo rm -rf *.a

cd ${ROOTDIR}/dmm/thirdparty/glog/glog-0.3.4/
sudo autoreconf -ivf

cd ${ROOTDIR}/dmm/build/
sudo cmake -D DMM_DPDK_INSTALL_DIR=$DPDK_INSTALL_PATH ..
sudo make -j 8

export NSTACK_LOG_ON=DBG

cd ${PWDDIR}

sudo killall -9 vs_epoll 2>/dev/null

sleep 5

pid=`pgrep vs_epoll`
if [ "$pid" != "" ]; then
    echo "terminate the vs_epoll failed!"
    exit 1
fi

# check and setup the hugepages
SYS_HUGEPAGE=$(cat /sys/kernel/mm/hugepages/hugepages-2048kB/nr_hugepages)
hugepageFree=$(cat /proc/meminfo | grep -c "HugePages_Free:        0")

if [ ${SYS_HUGEPAGE} -lt 1024 ] || [ $hugepageFree -ne 0 ]; then
    MOUNT=$(mount | grep /mnt/nstackhuge)
    while [ "${MOUNT}" != "" ]
    do
        sudo umount /mnt/nstackhuge
        sleep 1
        MOUNT=$(mount | grep /mnt/nstackhuge)
    done

    echo 1024 | sudo tee /sys/devices/system/node/node0/hugepages/hugepages-2048kB/nr_hugepages
    echo 1024 | sudo tee /sys/devices/system/node/node1/hugepages/hugepages-2048kB/nr_hugepages

    sudo mkdir -p /mnt/nstackhuge
    sudo mount -t hugetlbfs -o pagesize=2M none /mnt/nstackhuge/
    test $? -eq 0 || exit 1
else
    sudo mkdir -p /mnt/nstackhuge
    sudo mount -t hugetlbfs -o pagesize=2M none /mnt/nstackhuge/
fi

sudo mkdir -p /var/run/ip_module/
