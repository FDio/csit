#!/bin/bash

set -x

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
DPDK_VERSION=16.04
DPDK_DIR=dpdk
DPDK_PACKAGE=${DPDK_DIR}"-"${DPDK_VERSION}.tar.xz
DPDK_INSTALL_PATH=/usr
ROOTDIR=${SCRIPT_DIR}/../../../

# compile and install the DPDK
echo "DPDK build started....."
cd ${ROOTDIR}

tar xvf ${DPDK_PACKAGE}
cd dpdk-16.04
sed -i 's!CONFIG_RTE_EXEC_ENV=.*!CONFIG_RTE_EXEC_ENV=y!1' config/common_base
sed -i 's!CONFIG_RTE_BUILD_SHARED_LIB=.*!CONFIG_RTE_BUILD_SHARED_LIB=y!1' config/common_base
sed -i 's!CONFIG_RTE_LIBRTE_EAL=.*!CONFIG_RTE_LIBRTE_EAL=y!1' config/common_base

sudo make install  T=x86_64-native-linuxapp-gcc DESTDIR=${DPDK_INSTALL_PATH} -j 4
if [ $? -eq 0 ]
then
  echo "DPDK build is SUCCESS"
else
  echo "DPDK build has FAILED"
  exit 1
fi

#===========build DMM=================
echo "DMM build started....."
cd ${ROOTDIR}/dmm/thirdparty/glog/glog-0.3.4/
autoreconf -ivf

cd ${ROOTDIR}/dmm/build/
cmake ..
make -j 8
if [ $? -eq 0 ]
then
  echo "DMM build is SUCCESS"
else
  echo "DMM build has FAILED"
  exit 1
fi
