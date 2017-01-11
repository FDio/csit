#!/bin/bash

ROOTDIR=/tmp/openvpp-testing
PWDDIR=$(pwd)

cd ${ROOTDIR}/dpdk-16.07/
modprobe uio
lsmod | grep igb_uio
if [ $? -eq 1 ];
then
    insmod ./x86_64-native-linuxapp-gcc/kmod/igb_uio.ko || exit 1
else
    rmmod igb_uio
    insmod ./x86_64-native-linuxapp-gcc/kmod/igb_uio.ko || exit 1
fi
./tools/dpdk-devbind.py -b igb_uio $1 $2
cd ${PWDDIR}
