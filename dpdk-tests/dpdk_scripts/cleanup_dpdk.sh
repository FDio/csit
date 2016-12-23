#!/bin/bash

ROOTDIR=/tmp/openvpp-testing
PWDDIR=$(pwd)

TESTPMD_LOG=/tmp/testpmd.log
TESTPMD_PID=/tmp/testpmd.pid
L3FWD_LOG=/tmp/l3fwd.log
L3FWD_PID=/tmp/l3fwd.pid
DPDK_VERSION=17.02
DPDK_DIR=dpdk-${DPDK_VERSION}

port1_driver=$1
port1_pci=$2
port2_driver=$3
port2_pci=$4

#kill the dpdk application
sudo pgrep testpmd
if [ $? -eq "0" ]; then
    success=false
    sudo pkill tail
    sudo pkill testpmd
    for attempt in {1..5}; do
        sudo pgrep testpmd
        if [ $? -eq "1" ]; then
            success=true
            break
        fi
        sleep 1
    done
    if [ "$success" = false ]; then
        echo "The command sudo pkill testpmd failed"
        exit 1
    fi
    cat ${TESTPMD_LOG}
fi

#also kill the l3fwd
sudo pgrep l3fwd
if [ $? -eq "0" ]; then
    success=false
    sudo pkill tail
    sudo pkill l3fwd
    for attempt in {1..5}; do
        sudo pgrep l3fwd
        if [ $? -eq "1" ]; then
            success=true
            break
        fi
        sleep 1
    done
    if [ "$success" = false ]; then
        echo "The command sudo pkill l3fwd failed"
        exit 1
    fi
    cat ${L3FWD_LOG}
fi

sudo rm -f ${TESTPMD_LOG}
sudo rm -f ${TESTPMD_PID}
sudo rm -f ${L3FWD_LOG}
sudo rm -f ${L3FWD_PID}
sudo rm -f /dev/hugepages/*

cd ${ROOTDIR}/${DPDK_DIR}/
./usertools/dpdk-devbind.py -b ${port1_driver} ${port1_pci}
./usertools/dpdk-devbind.py -b ${port2_driver} ${port2_pci}

sleep 2

if1_name=`./usertools/dpdk-devbind.py --s | grep "${port1_pci}" | sed -n 's/.*if=\(\S\)/\1/p' | awk -F' ' '{print $1}'`
if2_name=`./usertools/dpdk-devbind.py --s | grep "${port2_pci}" | sed -n 's/.*if=\(\S\)/\1/p' | awk -F' ' '{print $1}'`

ifconfig ${if1_name} up
ifconfig ${if2_name} up

rmmod igb_uio
rmmod uio

cd ${PWDDIR}
