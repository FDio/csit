#!/bin/bash

ROOTDIR=/tmp/openvpp-testing
PWDDIR=$(pwd)

cd ${ROOTDIR}/dpdk-16.07/
modprobe uio
insmod ./x86_64-native-linuxapp-gcc/kmod/igb_uio.ko
./tools/dpdk-devbind.py -b igb_uio $1 $2
cd ${PWDDIR}
