#!/bin/bash

set -x

# Setting variables
ROOTDIR=/tmp/openvpp-testing
PWDDIR=$(pwd)
cd ${ROOTDIR}/dpdk-17.02/

modprobe uio
echo "  RC = $?"

lsmod | grep igb_uio
if [ $? -eq 1 ];
then
    insmod ./x86_64-native-linuxapp-gcc/kmod/igb_uio.ko || exit 1
    echo "  RC = $?"
else
    rmmod igb_uio
    echo "  RC = $?"
    insmod ./x86_64-native-linuxapp-gcc/kmod/igb_uio.ko || exit 1
    echo "  RC = $?"
fi

# Binding
./usertools/dpdk-devbind.py -b igb_uio $1 $2

cd ${PWDDIR}
