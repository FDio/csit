#!/bin/bash

echo "###" $0 "###"

echo "Setting variables ..."
ROOTDIR=/tmp/openvpp-testing
PWDDIR=$(pwd)

echo "  ROOTDIR = ${ROOTDIR}"
echo "  PWDDIR = ${PWDDIR}"

cd ${ROOTDIR}/dpdk-17.02/

echo "modprobe uio"
modprobe uio
echo "  RC = $?"

echo "lsmod | grep igb_uio"
lsmod | grep igb_uio
echo "  RC = $?"

if [ $? -eq 1 ];
then
    echo "insmod ./x86_64-native-linuxapp-gcc/kmod/igb_uio.ko || exit 1"
    insmod ./x86_64-native-linuxapp-gcc/kmod/igb_uio.ko || exit 1
    echo "  RC = $?"
else
    echo "rmmod igb_uio"
    rmmod igb_uio
    echo "  RC = $?"
    echo "insmod ./x86_64-native-linuxapp-gcc/kmod/igb_uio.ko || exit 1"
    insmod ./x86_64-native-linuxapp-gcc/kmod/igb_uio.ko || exit 1
    echo "  RC = $?"
fi

echo "Binding ..."
echo "  ./usertools/dpdk-devbind.py -b igb_uio $1 $2"
./usertools/dpdk-devbind.py -b igb_uio $1 $2

cd ${PWDDIR}
