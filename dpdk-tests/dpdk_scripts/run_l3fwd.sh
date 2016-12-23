#!/bin/bash

ROOTDIR=/tmp/openvpp-testing
PWDDIR=$(pwd)

DPDK_VERSION=16.07
DPDK_DIR=dpdk-${DPDK_VERSION}

cpu_coremask=$1
port_config=$2
adj_mac0=$3
adj_mac1=$4
jumbo_frames=$5

#kill the l3fwd
sudo pkill l3fwd

sleep 2

pid=`pgrep l3fwd`
if [ "$pid" != "" ]; then
    echo "terminate the l3fwd failed!"
    exit 1
fi

#run the l3fwd
cd ${ROOTDIR}/${DPDK_DIR}
if [ "$jumbo_frames" = "yes" ]; then
sudo sh -c "screen -dmS DPDK-test ./examples/l3fwd/build/app/l3fwd -c ${cpu_coremask} \
    -n 4 -- -P -L -p 0x3 --config='${port_config}' --enable-jumbo \
    --max-pkt-len=9000 --eth-dest=0,${adj_mac0} --eth-dest=1,${adj_mac1}"
else
sudo sh -c "screen -dmS DPDK-test ./examples/l3fwd/build/app/l3fwd -c ${cpu_coremask} \
    -n 4 -- -P -L -p 0x3 --config='${port_config}' --eth-dest=0,${adj_mac0} \
    --eth-dest=1,${adj_mac1}"
fi

cd ${PWDDIR}
