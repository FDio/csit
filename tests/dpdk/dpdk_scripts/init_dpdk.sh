#!/bin/bash

set -x

# Setting variables
DPDK_VERSION=dpdk-18.02
ROOTDIR=/tmp/openvpp-testing
PWDDIR=$(pwd)

# set arch, default to x86_64 if none given
ARCH=${3:-"x86_64"}

# dpdk prefers "arm64" to "aarch64" and does not allow arm64 native target
if [ $ARCH == "aarch64" ]; then
    ARCH="arm64"
    MACHINE="armv8a"
else
    MACHINE="native"
fi

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

insmod ./${ARCH}-${MACHINE}-linuxapp-gcc/kmod/igb_uio.ko || \
    { echo "Failed to insert igb_uio module"; exit 1; }

# Binding
./usertools/dpdk-devbind.py -b igb_uio $1 $2 || \
    { echo "Failed to bind interface $1 and $2 to igb_uio"; exit 1; }

cd ${PWDDIR}
