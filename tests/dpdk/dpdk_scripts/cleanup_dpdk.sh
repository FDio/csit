#!/bin/bash

set -x

# Setting variables
DPDK_VERSION=dpdk-17.05
ROOTDIR=/tmp/openvpp-testing
TESTPMDLOG=screenlog.0
PWDDIR=$(pwd)

# Setting command line arguments
port1_driver=$1
port1_pci=$2
port2_driver=$3
port2_pci=$4

# Try to kill the testpmd
sudo pgrep testpmd
if [ $? -eq "0" ]; then
    success=false
    sudo pkill testpmd
    echo "RC = $?"
    for attempt in {1..5}; do
        echo "Checking if testpmd is still alive, attempt nr ${attempt}"
        sudo pgrep testpmd
        if [ $? -eq "1" ]; then
            echo "testpmd is dead"
            success=true
            break
        fi
        echo "testpmd is still alive, waiting 1 second"
        sleep 1
    done
    if [ "$success" = false ]; then
        echo "The command sudo pkill testpmd failed"
        sudo pkill -9 testpmd
        echo "RC = $?"
        exit 1
    fi
else
    echo "testpmd is not running"
fi

#also kill the l3fwd
sudo pgrep l3fwd
if [ $? -eq "0" ]; then
    success=false
    sudo pkill l3fwd
    echo "RC = $?"
    for attempt in {1..5}; do
        echo "Checking if l3fwd is still alive, attempt nr ${attempt}"
        sudo pgrep l3fwd
        if [ $? -eq "1" ]; then
            echo "l3fwd is dead"
            success=true
            break
        fi
        echo "l3fwd is still alive, waiting 1 second"
        sleep 1
    done
    if [ "$success" = false ]; then
        echo "The command sudo pkill l3fwd failed"
        sudo pkill -9 l3fwd
        echo "RC = $?"
        exit 1
    fi
else
    echo "l3fwd is not running"
fi

# Remove hugepages
sudo rm -f /dev/hugepages/*

# Unbind interfaces
cd ${ROOTDIR}/${DPDK_VERSION}/
sudo ./usertools/dpdk-devbind.py -b ${port1_driver} ${port1_pci} || \
    { echo "Unbind ${port1_pci} failed"; exit 1; }
sudo ./usertools/dpdk-devbind.py -b ${port2_driver} ${port2_pci} || \
    { echo "Unbind ${port1_pci} failed"; exit 1; }

sleep 2

if1_name=`./usertools/dpdk-devbind.py --s | grep "${port1_pci}" | sed -n 's/.*if=\(\S\)/\1/p' | awk -F' ' '{print $1}'`
if2_name=`./usertools/dpdk-devbind.py --s | grep "${port2_pci}" | sed -n 's/.*if=\(\S\)/\1/p' | awk -F' ' '{print $1}'`

# Remove igb_uio driver
rmmod igb_uio || \
    { echo "Removing igb_uio failed"; exit 1; }

cd ${PWDDIR}
