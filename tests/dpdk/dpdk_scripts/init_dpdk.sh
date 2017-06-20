#!/bin/bash

set -x

# Setting variables
DPDK_VERSION=dpdk-17.05
ROOTDIR=/tmp/openvpp-testing
PWDDIR=$(pwd)
cd ${ROOTDIR}/${DPDK_VERSION}/

modprobe uio
echo "RC = $?"

lsmod | grep igb_uio
if [ $? -ne 1 ];
then
    rmmod igb_uio || \
        { echo "Failed to remove igb_uio module"; exit 1; }
fi

lsmod | grep uio_pci_generic
if [ $? -ne 1 ];
then
    rmmod uio_pci_generic || \
        { echo "Failed to remove uio_pci_generic module"; exit 1; }
fi

insmod ./x86_64-native-linuxapp-gcc/kmod/igb_uio.ko || \
    { echo "Failed to insert igb_uio module"; exit 1; }

# Binding
./usertools/dpdk-devbind.py -b igb_uio $1 $2 || \
    { echo "Failed to bind interface $1 and $2 to igb_uio"; exit 1; }

cd ${PWDDIR}
