#!/bin/bash

set -x

TIMESTAMP=$(date +%Y-%m-%d_%H-%M-%S)
OS_ID=$(grep '^ID=' /etc/os-release | cut -f2- -d= | sed -e 's/\"//g')
ROOTDIR=/tmp/DMM-testing

DMM_DIR=${ROOTDIR}/dmm/

#DPDK download path
DPDK_DOWNLOAD_PATH=/tmp/dpdk

#dpdk installation path
DPDK_INSTALL_PATH=/usr

# compile and install the DPDK
echo "DPDK build started....."
cd ${ROOTDIR}

#DPDK will be having dependancy on linux headers
if [ "$OS_ID" == "ubuntu" ]; then
    sudo apt-get -y install git build-essential linux-headers-`uname -r`
    sudo apt-get install libnuma-dev
elif [ "$OS_ID" == "debian" ]; then
    sudo apt-get -y install git build-essential linux-headers-`uname -r`
elif [ "$OS_ID" == "centos" ]; then
    sudo yum groupinstall -y "Development Tools"
    sudo yum install -y kernel-headers
elif [ "$OS_ID" == "opensuse" ]; then
    sudo yum groupinstall -y "Development Tools"
    sudo yum install -y kernel-headers
fi

#===========build DPDK================
mkdir -p $DPDK_DOWNLOAD_PATH

DPDK_FOLDER=$DPDK_DOWNLOAD_PATH/dpdk-18.02-$TIMESTAMP
cd $DPDK_DOWNLOAD_PATH
mkdir $DPDK_FOLDER
tar xvf /tmp/DMM-testing/dpdk-18.02.tar.xz -C $DPDK_FOLDER
cd $DPDK_FOLDER/dpdk-18.02

sed -i 's!CONFIG_RTE_EXEC_ENV=.*!CONFIG_RTE_EXEC_ENV=y!1' config/common_base
sed -i 's!CONFIG_RTE_BUILD_SHARED_LIB=.*!CONFIG_RTE_BUILD_SHARED_LIB=y!1' config/common_base
sed -i 's!CONFIG_RTE_LIBRTE_EAL=.*!CONFIG_RTE_LIBRTE_EAL=y!1' config/common_base
sed -i 's!CONFIG_RTE_EAL_PMD_PATH=.*!CONFIG_RTE_EAL_PMD_PATH="/tmp/dpdk/drivers/"!1' config/common_base

sudo make install  T=x86_64-native-linuxapp-gcc DESTDIR=${DPDK_INSTALL_PATH} -j 4
if [ $? -eq 0 ]
then
  echo "DPDK build is SUCCESS"
else
  echo "DPDK build has FAILED"
  exit 1
fi

mkdir -p /tmp/dpdk/drivers/
cp -f /usr/lib/librte_mempool_ring.so /tmp/dpdk/drivers/

export NSTACK_LOG_ON=DBG

# Try to kill the vs_epoll
sudo killall vs_epoll

sudo pgrep vs_epoll
if [ $? -eq "0" ]; then
    success=false
    sudo pkill vs_epoll
    echo "RC = $?"
    for attempt in {1..5}; do
        echo "Checking if vs_epoll is still alive, attempt nr ${attempt}"
        sudo pgrep vs_epoll
        if [ $? -eq "1" ]; then
            echo "vs_epoll is dead"
            success=true
            break
        fi
        echo "vs_epoll is still alive, waiting 1 second"
        sleep 1
    done
    if [ "$success" = false ]; then
        echo "The command sudo pkill vs_epoll failed"
        sudo pkill -9 vs_epoll
        echo "RC = $?"
        exit 1
    fi
else
    echo "vs_epoll is not running"
fi

# check and setup the hugepages
SYS_HUGEPAGE=$(cat /sys/kernel/mm/hugepages/hugepages-2048kB/nr_hugepages)
hugepageFree=$(cat /sys/kernel/mm/hugepages/hugepages-2048kB/free_hugepages)

if [ ${SYS_HUGEPAGE} -lt 1024 ] || [ $hugepageFree -eq 0 ]; then
    MOUNT=$(mount | grep /mnt/nstackhuge)
    count=$(mount | grep /mnt/nstackhuge | wc -l)

    while [ "${MOUNT}" != "" ] || [ "${count}" -ne 0 ]
    do
        sudo umount /mnt/nstackhuge
        sleep 1
        MOUNT=$(mount | grep /mnt/nstackhuge)
        count=$[$count -1]
    done

    sock_count=$(lscpu | grep 'Socket(s):' | head -1 | awk '{print $2}')
    ls -l /sys/devices/system/node/

    while [ "${sock_count}" -ne 0 ]
    do
        sock_count=$[$sock_count - 1]
        echo 1024 | sudo tee /sys/devices/system/node/node"$sock_count"/hugepages/hugepages-2048kB/nr_hugepages
    done

    sudo mkdir -p /mnt/nstackhuge
    sudo mount -t hugetlbfs -o pagesize=2M none /mnt/nstackhuge/
    test $? -eq 0 || exit 1
else
    sudo mkdir -p /mnt/nstackhuge
    sudo mount -t hugetlbfs -o pagesize=2M none /mnt/nstackhuge/
fi

sudo mkdir -p /var/run/ip_module/
