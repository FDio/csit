#!/bin/bash

ROOTDIR=/tmp/openvpp-testing
PWDDIR=$(pwd)

cpu_coremask=$1
nb_cores=$2
queue_nums=$3
jumbo_frames=$4

#kill the testpmd
sudo pkill testpmd

sleep 2

pid=`pgrep testpmd`
if [ "$pid" != "" ]; then
    echo "terminate the testpmd failed!"
    exit 1
fi

#run the testpmd
cd ${ROOTDIR}
if [ "$jumbo_frames" == "yes" ]; then
sudo sh -c "screen -dmS DPDK-test ./dpdk-16.07/x86_64-native-linuxapp-gcc/app/testpmd -c ${cpu_coremask} \
    -n 4 --master-lcore 0 -- --nb-ports=2 --portmask=0x3 --nb-cores=${nb_cores} \
    --max-pkt-len=9000 --txqflags=0 --forward-mode=io --rxq=${queue_nums} \
    --txq=${queue_nums} --auto-start"
else
sudo sh -c "screen -dmS DPDK-test ./dpdk-16.07/x86_64-native-linuxapp-gcc/app/testpmd -c ${cpu_coremask} \
    -n 4 --master-lcore 0 -- --nb-ports=2 --portmask=0x3 --nb-cores=${nb_cores} \
    --forward-mode=io --rxq=${queue_nums} --txq=${queue_nums} --auto-start"
fi

cd ${PWDDIR}
