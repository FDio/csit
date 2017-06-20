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

SCRIPT_NAME=$(basename $0)

# define a function to get the l3fwd PID
function get_l3fwd_pid()
{
    pid_l3fwd=`sudo ps -elf | grep l3fwd | grep -v grep | grep -v SCREEN | grep -v ${SCRIPT_NAME} | awk '{print $4}'`
    echo ${pid_l3fwd}
}

# Try to kill the l3fwd
# Don't use the pgrep and pkill
l3fwd_pid=`get_l3fwd_pid`
echo ${l3fwd_pid}
if [ ! -z ${l3fwd_pid} ]; then
    success=false
    sudo kill -15 ${l3fwd_pid}
    echo "RC = $?"
    for attempt in {1..5}; do
        echo "Checking if l3fwd is still alive, attempt nr ${attempt}"
        l3fwd_pid=`get_l3fwd_pid`
        if [ -z ${l3fwd_pid} ]; then
            echo "l3fwd is dead"
            success=true
            break
        fi
        echo "l3fwd is still alive, waiting 1 second"
        sleep 1
    done
    if [ "$success" = false ]; then
        echo "The command sudo kill -15 l3fwd failed"
        sudo kill -9 ${l3fwd_pid}
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
    --eth-dest=1,${adj_mac1} --parse-ptype"
else
    sudo sh -c "screen -dmSL DPDK-test ./examples/l3fwd/build/app/l3fwd \
    -l ${cpu_corelist} -n 4 -- -P -L -p 0x3 --config='${port_config}' \
    --eth-dest=0,${adj_mac0} --eth-dest=1,${adj_mac1} --parse-ptype"
fi

sleep 10
less -r ${L3FWDLOG}

cd ${PWDDIR}

