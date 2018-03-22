#!/bin/bash

set -x

ROOTDIR=/tmp/DMM-testing
PWDDIR=$(pwd)
APP_DIR=${ROOTDIR}/dmm/release/bin/
dut1_ip=$1
dut2_ip=$2
proc_name=$3
#proc_name => 0 = server, 1= client

# Try to kill the vs_epoll
sudo killall vs_epoll

sudo pgrep vs_epoll
if [ $? -eq "0" ]; then
    success=false
    sudo pkill vs_epoll
    echo "RC = $?"
    for attempt in {1..5}; do
        echo "Checking if vs_epoll is still alive, attempt nr ${attempt}"
        sudo pgrep vs_epoll
        if [ $? -eq "1" ]; then
            echo "vs_epoll is dead"
            success=true
            break
        fi
        echo "vs_epoll is still alive, waiting 1 second"
        sleep 1
    done
    if [ "$success" = false ]; then
        echo "The command sudo pkill vs_epoll failed"
        sudo pkill -9 vs_epoll
        echo "RC = $?"
        exit 1
    fi
else
    echo "vs_epoll is not running"
fi

sleep 2

cd ${APP_DIR}

sudo cp -r ../configure/* .

#only for kernal stack
sudo sed -i '15,25d' module_config.json

if [ ${proc_name} -eq 0 ]; then
sudo ./vs_epoll -p 20000 -d ${dut2_ip} -a 10000 -s ${dut1_ip} -l 200 -t 50000 -i 0 -f 1 -r 20000 -n 1 -w 10 -u 10000 -e 10 -x 1
else
sudo ./vc_epoll -p 20000 -d ${dut1_ip} -a 10000 -s ${dut2_ip} -l 200 -t 50000 -i 0 -f 1 -r 20000 -n 1 -w 10 -u 10000 -e 10 -x 1
fi

cd ${PWDDIR}

ps -elf | grep vs_epoll

sleep 10
