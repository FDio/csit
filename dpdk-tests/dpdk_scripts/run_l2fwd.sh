#!/bin/bash

ROOTDIR=/tmp/openvpp-testing
PWDDIR=$(pwd)

TESTPMD_LOG=/tmp/testpmd.log
TESTPMD_PID=/tmp/testpmd.pid

cpu_corelist=$1
nb_cores=$2
queue_nums=$3
jumbo_frames=$4

#kill the testpmd
sudo pgrep testpmd
if [ $? -eq "0" ]; then
    success=false
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
fi

sudo rm -f ${TESTPMD_PID}
sudo rm -f /dev/hugepages/*
sudo rm -f ${TESTPMD_LOG}

#run the testpmd
cd ${ROOTDIR}
if [ "$jumbo_frames" = "yes" ]; then
tail -f /dev/null | nohup ./dpdk-16.07/x86_64-native-linuxapp-gcc/app/testpmd -l ${cpu_corelist} \
    -n 4 -- --nb-ports=2 --portmask=0x3 --nb-cores=${nb_cores} \
    --max-pkt-len=9000 --txqflags=0 --forward-mode=io --rxq=${queue_nums} \
    --txq=${queue_nums} --auto-start > ${TESTPMD_LOG} 2>&1 &
echo $! > ${TESTPMD_PID}
else
tail -f /dev/null | nohup ./dpdk-16.07/x86_64-native-linuxapp-gcc/app/testpmd -l ${cpu_corelist} \
    -n 4 -- --nb-ports=2 --portmask=0x3 --nb-cores=${nb_cores} \
    --forward-mode=io --rxq=${queue_nums} --txq=${queue_nums} --auto-start > ${TESTPMD_LOG} 2>&1 &
echo $! > ${TESTPMD_PID}
fi

cd ${PWDDIR}
