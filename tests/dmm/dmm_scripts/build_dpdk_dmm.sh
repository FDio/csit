#!/bin/bash

set -x

OS_ID=$(grep '^ID=' /etc/os-release | cut -f2- -d= | sed -e 's/\"//g')
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
ROOTDIR=${SCRIPT_DIR}/../../../
DPDK_VERSION=16.04
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

cd ${DMM_DIR}/thirdparty/glog/glog-0.3.4/ && autoreconf -ivf
cd ${DMM_DIR}/build/
cmake ..
make -j 8

if [ $? -eq 0 ]
then
  echo "DMM build is SUCCESS"
else
  echo "DMM build has FAILED"
  exit 1
fi

chmod -R ../release/ 777 *
