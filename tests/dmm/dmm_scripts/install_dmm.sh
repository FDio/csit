#!/bin/bash

set -x

OS_ID=$(grep '^ID=' /etc/os-release | cut -f2- -d= | sed -e 's/\"//g')
DPDK_VERSION=16.04
ROOTDIR=/tmp/DMM-testing
DPDK_DIR=dpdk
DPDK_PACKAGE=${DPDK_DIR}"-"${DPDK_VERSION}.tar.xz
DPDK_INSTALL_PATH=/usr
DMM_DIR=${ROOTDIR}/dmm/

# compile and install the DPDK
echo "DPDK build started....."
cd ${ROOTDIR}

#DPDK will be having dependancy on linux headers
if [ "$OS_ID" == "ubuntu" ]; then
    sudo apt-get -y install git build-essential linux-headers-`uname -r`
elif [ "$OS_ID" == "debian" ]; then
    sudo apt-get -y install git build-essential linux-headers-`uname -r`
elif [ "$OS_ID" == "centos" ]; then
    uname -r
    sudo yum install kernel-devel
elif [ "$OS_ID" == "opensuse" ]; then
    sudo yum groupinstall -y "Development Tools"
    sudo yum install -y kernel-headers
fi

tar xvf ${DPDK_PACKAGE}

cd dpdk-16.04
sed -i 's!CONFIG_RTE_EXEC_ENV=.*!CONFIG_RTE_EXEC_ENV=y!1' config/common_base
sed -i 's!CONFIG_RTE_BUILD_SHARED_LIB=.*!CONFIG_RTE_BUILD_SHARED_LIB=y!1' config/common_base
sed -i 's!CONFIG_RTE_LIBRTE_EAL=.*!CONFIG_RTE_LIBRTE_EAL=y!1' config/common_base

if [ "$OS_ID" == "centos" ]; then
sed -i 's!CONFIG_RTE_LIBRTE_KNI=.*!CONFIG_RTE_LIBRTE_KNI=y!1' config/common_base
sed -i 's!CONFIG_RTE_KNI_KMOD=.*!CONFIG_RTE_KNI_KMOD=y!1' config/common_base
fi

sudo make install  T=x86_64-native-linuxapp-gcc DESTDIR=${DPDK_INSTALL_PATH} -j 4
if [ $? -eq 0 ]
then
  echo "DPDK build is SUCCESS"
else
  echo "DPDK build has FAILED"
  exit 1
fi

export NSTACK_LOG_ON=DBG

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

    ls -l /sys/devices/system/node/
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
