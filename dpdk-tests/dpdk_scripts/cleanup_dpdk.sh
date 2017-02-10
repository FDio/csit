#!/bin/bash

set -x

# Setting variables
ROOTDIR=/tmp/openvpp-testing
PWDDIR=$(pwd)
#TESTPMD_LOG=/tmp/testpmd.log
#TESTPMD_PID=/tmp/testpmd.pid

# Setting command line arguments
port1_driver=$1
port1_pci=$2
port2_driver=$3
port2_pci=$4

# Try to kill the testpmd
sudo pgrep testpmd
if [ $? -eq "0" ]; then
    success=false
    #sudo pkill tail
    sudo pkill testpmd
    echo "  RC = $?"
    for attempt in {1..5}; do
        echo "    Checking if testpmd is still alive, attempt nr ${attempt}"
        sudo pgrep testpmd
        if [ $? -eq "1" ]; then
            echo "    testpmd is dead"
            success=true
            break
        fi
        echo "    testpmd is still alive, waiting 1 second"
        sleep 1
    done
    if [ "$success" = false ]; then
        echo "  The command sudo pkill testpmd failed"
        echo "  Kill it with SIGKILL"
        sudo pkill -9 testpmd
        echo "RC = $?"
        exit 1
    fi
    #cat ${TESTPMD_LOG}
else
    echo "testpmd is not running"
fi

# echo "Remove ${TESTPMD_LOG}, ${TESTPMD_PID} and /dev/hugepages/*"
#sudo rm -f ${TESTPMD_LOG}
#sudo rm -f ${TESTPMD_PID}
sudo rm -f /dev/hugepages/*

sleep 2

cd ${ROOTDIR}/dpdk-17.02/
echo "./usertools/dpdk-devbind.py -b ${port1_driver} ${port1_pci}"
./usertools/dpdk-devbind.py -b ${port1_driver} ${port1_pci}
echo "  RC = $?"
echo "./usertools/dpdk-devbind.py -b ${port2_driver} ${port2_pci}"
./usertools/dpdk-devbind.py -b ${port2_driver} ${port2_pci}
echo "  RC = $?"

sleep 2

if1_name=`./usertools/dpdk-devbind.py --s | grep "${port1_pci}" | sed -n 's/.*if=\(\S\)/\1/p' | awk -F' ' '{print $1}'`
if2_name=`./usertools/dpdk-devbind.py --s | grep "${port2_pci}" | sed -n 's/.*if=\(\S\)/\1/p' | awk -F' ' '{print $1}'`

echo "rmmod igb_uio"
rmmod igb_uio
echo "  RC = $?"

#echo "rmmod uio"
#rmmod uio
#echo "  RC = $?"

cd ${PWDDIR}
