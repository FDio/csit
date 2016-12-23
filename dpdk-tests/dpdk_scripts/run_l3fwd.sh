#!/bin/bash

set -x

# Setting variables
DPDK_VERSION=dpdk-17.05
ROOTDIR=/tmp/openvpp-testing
L3FWDLOG=screenlog.0
PWDDIR=$(pwd)

cpu_corelist=$1
port_config=$2
adj_mac0=$3
adj_mac1=$4
jumbo_frames=$5

# Try to kill the l3fwd
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

sudo rm -f /dev/hugepages/*

sleep 2

#run the l3fwd
cd ${ROOTDIR}/${DPDK_VERSION}/
rm -f ${L3FWDLOG}
if [ "$jumbo_frames" = "yes" ]; then
    sudo sh -c "screen -dmSL DPDK-test ./examples/l3fwd/build/app/l3fwd \
    -l ${cpu_corelist} -n 4 -- -P -L -p 0x3 --config='${port_config}' \
    --enable-jumbo --max-pkt-len=9000 --eth-dest=0,${adj_mac0} \
    --eth-dest=1,${adj_mac1}"
else
    sudo sh -c "screen -dmSL DPDK-test ./examples/l3fwd/build/app/l3fwd \
    -l ${cpu_corelist} -n 4 -- -P -L -p 0x3 --config='${port_config}' \
    --eth-dest=0,${adj_mac0} --eth-dest=1,${adj_mac1}"
fi

sleep 10
less -r ${L3FWDLOG}

cd ${PWDDIR}
