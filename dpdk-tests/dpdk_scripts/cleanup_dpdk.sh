#!/bin/bash

ROOTDIR=/tmp/openvpp-testing
PWDDIR=$(pwd)

port1_driver=$1
port1_pci=$2
port2_driver=$3
port2_pci=$4

#kill the dpdk application
sudo pkill testpmd
sudo pkill l3fwd
sleep 1

cd ${ROOTDIR}/dpdk-16.07/
./tools/dpdk-devbind.py -b ${port1_driver} ${port1_pci}
./tools/dpdk-devbind.py -b ${port2_driver} ${port2_pci}
sleep 1

if1_name=`./tools/dpdk-devbind.py --s | grep "${port1_pci}" | sed -n 's/.*if=\(\S\)/\1/p' | awk -F' ' '{print $1}'`
if2_name=`./tools/dpdk-devbind.py --s | grep "${port2_pci}" | sed -n 's/.*if=\(\S\)/\1/p' | awk -F' ' '{print $1}'`

ifconfig ${if1_name} up
ifconfig ${if2_name} up

rmmod igb_uio
rmmod uio

cd ${PWDDIR}
