#!/bin/bash

set -x
SCRIPT_DIR=`dirname $(readlink -f $0)`
ROOTDIR=$SCRIPT_DIR/../../../

cd ${ROOTDIR}
chmod +x *.deb
sudo dpkg -i libnuma1_2.0.11-1ubuntu1.1_amd64.deb
sudo dpkg -i libnuma-dev_2.0.11-1ubuntu1.1_amd64.deb
sudo dpkg -i ethtool_4.5-1_amd64.deb
sudo dpkg -i lsof_4.89+dfsg-0.1_amd64.deb

DPDK_DOWNLOAD_PATH=$(cat $ROOTDIR/dmm/scripts/build_dpdk.sh | grep DPDK_DOWNLOAD_PATH= | cut -d "=" -f2)
sudo rm /tmp/dpdk
mkdir -p $DPDK_DOWNLOAD_PATH
mv $ROOTDIR/dpdk-18.02.tar.xz $DPDK_DOWNLOAD_PATH
# install DPDK
cp -f $ROOTDIR/dmm/scripts/build_dpdk.sh $ROOTDIR/dmm/scripts/build_dpdk_csit.sh
sed -i 's!wget.*!#comment wget!1' $ROOTDIR/dmm/scripts/build_dpdk_csit.sh
bash -x $ROOTDIR/dmm/scripts/build_dpdk_csit.sh

sudo modprobe uio
sudo modprobe uio_pci_generic
sudo insmod $DPDK_DOWNLOAD_PATH/dpdk-18.02/x86_64-native-linuxapp-gcc/kmod/igb_uio.ko

bash $SCRIPT_DIR/kill_given_proc.sh vs_epoll
bash $SCRIPT_DIR/setup_hugepage.sh
