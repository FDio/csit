#!/bin/bash

set -x

# Setting variables
DPDK_VERSION=dpdk-17.02
ROOTDIR=/tmp/openvpp-testing
TESTPMDLOG=screenlog.0
PWDDIR=$(pwd)

# Setting command line arguments
cpu_corelist=$1
nb_cores=$2
queue_nums=$3
jumbo_frames=$4

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

# Remove hugepages
sudo rm -f /dev/hugepages/*

sleep 2

cd ${ROOTDIR}/${DPDK_VERSION}/
rm -f ${TESTPMDLOG}
if [ "$jumbo_frames" = "yes" ]; then
    sudo sh -c "screen -dmSL DPDK-test ./x86_64-native-linuxapp-gcc/app/testpmd -l ${cpu_corelist} \
        -n 4 -- --numa --nb-ports=2 --portmask=0x3 --nb-cores=${nb_cores} \
        --max-pkt-len=9000 --txqflags=0 --forward-mode=io --rxq=${queue_nums} \
        --txq=${queue_nums} --auto-start"
    sleep 10
    cat ${TESTPMDLOG}
else
    sudo sh -c "screen -dmSL DPDK-test ./x86_64-native-linuxapp-gcc/app/testpmd -l ${cpu_corelist} \
        -n 4 -- --numa --nb-ports=2 --portmask=0x3 --nb-cores=${nb_cores} \
        --forward-mode=io --rxq=${queue_nums} --txq=${queue_nums} --auto-start"
    sleep 10
    cat ${TESTPMDLOG}
fi

cd ${PWDDIR}
