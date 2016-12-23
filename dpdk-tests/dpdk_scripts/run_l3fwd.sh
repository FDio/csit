#!/bin/bash

ROOTDIR=/tmp/openvpp-testing
PWDDIR=$(pwd)

DPDK_VERSION=17.02
DPDK_DIR=dpdk-${DPDK_VERSION}

L3FWD_LOG=/tmp/l3fwd.log
L3FWD_PID=/tmp/l3fwd.pid

cpu_corelist=$1
port_config=$2
adj_mac0=$3
adj_mac1=$4
jumbo_frames=$5

#kill the l3fwd
sudo pgrep l3fwd
if [ $? -eq "0" ]; then
    success=false
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
fi

sudo rm -f ${L3FWD_LOG}
sudo rm -f ${L3FWD_PID}
sudo rm -f /dev/hugepages/*

#run the l3fwd
cd ${ROOTDIR}/${DPDK_DIR}
if [ "$jumbo_frames" = "yes" ]; then
tail -f /dev/null | nohup ./examples/l3fwd/build/app/l3fwd -l ${cpu_corelist} \
    -n 4 -- -P -L -p 0x3 --config='${port_config}' --enable-jumbo \
    --max-pkt-len=9000 --eth-dest=0,${adj_mac0} --eth-dest=1,${adj_mac1} \
    > ${L3FWD_LOG} 2>&1 &
echo $! > ${L3FWD_PID}
else
tail -f /dev/null | nohup ./examples/l3fwd/build/app/l3fwd -l ${cpu_corelist} \
    -n 4 -- -P -L -p 0x3 --config='${port_config}' --eth-dest=0,${adj_mac0} \
    --eth-dest=1,${adj_mac1} > ${L3FWD_LOG} 2>&1 &
echo $! > ${L3FWD_PID}
fi

cd ${PWDDIR}
