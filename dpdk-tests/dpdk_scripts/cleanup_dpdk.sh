#!/bin/bash

echo "###" $0 "###"

echo "Setting variables ..."
ROOTDIR=/tmp/openvpp-testing
PWDDIR=$(pwd)

echo "  ROOTDIR = ${ROOTDIR}"
echo "  PWDDIR = ${PWDDIR}"

TESTPMD_LOG=/tmp/testpmd.log
TESTPMD_PID=/tmp/testpmd.pid

echo "  TESTPMD_LOG = ${TESTPMD_LOG}"
echo "  TESTPMD_PID = ${TESTPMD_PID}"

echo "Command line arguments: "
port1_driver=$1
port1_pci=$2
port2_driver=$3
port2_pci=$4

echo "  port1_driver = ${port1_driver}"
echo "  port1_pci = ${port1_pci}"
echo "  port2_driver = ${port2_driver}"
echo "  port2_pci = ${port2_pci}"

echo "Kill the dpdk application."
echo "  Is testpmd running?"
echo "  sudo pgrep testpmd"
sudo pgrep testpmd
if [ $? -eq "0" ]; then
    success=false
    echo "  testpmd is running, kill it"
    sudo pkill tail
    echo "  sudo pkill tail"
    sudo pkill testpmd
    echo "  RC = $?"
    for attempt in {1..5}; do
        echo "    Checking if testpmd is still alive, attempt nr ${attempt}"
        sudo pgrep testpmd
        if [ $? -eq "1" ]; then
            echo "    testpmd is dead, baby, testpmd's dead"
            success=true
            break
        fi
        echo "    testpmd is still alive, waiting 1 second"
        sleep 1
    done
    if [ "$success" = false ]; then
        echo "The command sudo pkill testpmd failed"
        echo "  Kill it with SIGKILL"
        sudo pkill -9 testpmd
        echo "  RC = $?"
        exit 1
    fi
    cat ${TESTPMD_LOG}
fi

echo "Remove ${TESTPMD_LOG}, ${TESTPMD_PID} and /dev/hugepages/*"
sudo rm -f ${TESTPMD_LOG}
sudo rm -f ${TESTPMD_PID}
sudo rm -f /dev/hugepages/*

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

echo "Set ${if1_name} up"
ifconfig ${if1_name} up
echo "Set ${if2_name} up"
ifconfig ${if2_name} up

echo "rmmod igb_uio"
rmmod igb_uio
echo "  RC = $?"

echo "rmmod uio"
rmmod uio
echo "  RC = $?"

cd ${PWDDIR}
