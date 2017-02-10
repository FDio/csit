#!/bin/bash

set -x

# Setting variables
ROOTDIR=/tmp/openvpp-testing
PWDDIR=$(pwd)
#TESTPMD_LOG=/tmp/testpmd.log
#TESTPMD_PID=/tmp/testpmd.pid

# Setting command line arguments
cpu_corelist=$1
nb_cores=$2
queue_nums=$3
jumbo_frames=$4

# Try to kill the testpmd
sudo pgrep testpmd
if [ $? -eq "0" ]; then
    success=false
    #sudo pkill tail
    sudo pkill testpmd
    echo "RC = $?"
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
else
    echo "testpmd is not running"
fi

# Remove ${TESTPMD_LOG}, ${TESTPMD_PID} and /dev/hugepages/*
#sudo rm -f ${TESTPMD_LOG}
#sudo rm -f ${TESTPMD_PID}
sudo rm -f /dev/hugepages/*

sleep 2

echo "Run the testpmd ..."
cd ${ROOTDIR}
if [ "$jumbo_frames" = "yes" ]; then
    sudo sh -c "screen -dmS DPDK-test ./dpdk-17.02/x86_64-native-linuxapp-gcc/app/testpmd -l ${cpu_corelist} \
        -n 4 -- --numa --nb-ports=2 --portmask=0x3 --nb-cores=${nb_cores} \
        --max-pkt-len=9000 --txqflags=0 --forward-mode=io --rxq=${queue_nums} \
        --txq=${queue_nums} --auto-start"
    #tail -f /dev/null | nohup ./dpdk-17.02/x86_64-native-linuxapp-gcc/app/testpmd -l ${cpu_corelist} \
    #    -n 4 -- --numa --nb-ports=2 --portmask=0x3 --nb-cores=${nb_cores} \
    #    --max-pkt-len=9000 --txqflags=0 --forward-mode=io --rxq=${queue_nums} \
    #    --txq=${queue_nums} --auto-start > ${TESTPMD_LOG} 2>&1 &
    #echo $! > ${TESTPMD_PID}
else
echo "  Jumbo frames are not supported"
    sudo sh -c "screen -dmS DPDK-test ./dpdk-17.02/x86_64-native-linuxapp-gcc/app/testpmd -l ${cpu_corelist} \
        -n 4 -- --numa --nb-ports=2 --portmask=0x3 --nb-cores=${nb_cores} \
        --forward-mode=io --rxq=${queue_nums} --txq=${queue_nums} --auto-start"
    #tail -f /dev/null | nohup ./dpdk-17.02/x86_64-native-linuxapp-gcc/app/testpmd -l ${cpu_corelist} \
    #    -n 4 -- --numa --nb-ports=2 --portmask=0x3 --nb-cores=${nb_cores} \
    #    --forward-mode=io --rxq=${queue_nums} --txq=${queue_nums} --auto-start > ${TESTPMD_LOG} 2>&1 &
    #echo $! > ${TESTPMD_PID}
fi

cd ${PWDDIR}
