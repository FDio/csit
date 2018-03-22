#!/bin/bash

set -x

OS_ID=$(grep '^ID=' /etc/os-release | cut -f2- -d= | sed -e 's/\"//g')
ROOTDIR=/tmp/DMM-testing
PWDDIR=$(pwd)
APP_DIR=${ROOTDIR}/dmm/release/bin/
LIB_PATH=${APP_DIR}/../lib64
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

cat /proc/meminfo

cd ${LIB_PATH}
chmod 777 *
ls -l

cd ${APP_DIR}
cp -r ${LIB_PATH}/libnStackAPI.so .
cp -r ../configure/* .
chmod 777 *

if [ "$OS_ID" == "ubuntu" ]; then
	ifaddress1=$(ifconfig eth1 | grep 'inet addr' | cut -d: -f2 | awk '{print $1}')
	echo $ifaddress1
	ifaddress2=$(ifconfig eth2 | grep 'inet addr' | cut -d: -f2 | awk '{print $1}')
	echo $ifaddress2
elif [ "$OS_ID" == "centos" ]; then
	ifaddress1=$(ifconfig enp0s8 | grep 'inet' | cut -d: -f2 | awk '{print $2}')
	echo $ifaddress1
	ifaddress2=$(ifconfig enp0s9 | grep 'inet' | cut -d: -f2 | awk '{print $2}')
	echo $ifaddress2
fi

echo '{
        "default_stack_name": "kernel",
        "module_list": [
        {
                "stack_name": "kernel",
                "function_name": "kernel_stack_register",
                "libname": "./",
                "loadtype": "static",
                "deploytype": "1",
                "maxfd": "1024",
                "minfd": "0",
                "priorty": "1",
                "stackid": "0",
    },
  ]
}' | tee module_config.json

echo '{
        "ip_route": [
        {
                "subnet": "'$ifaddress1'/24",
                "type": "nstack-kernel",
        },
        {
                "subnet": "'$ifaddress2'/24",
                "type": "nstack-kernel",
        },
        ],
        "prot_route": [
        {
                "proto_type": "1",
                "type": "nstack-kernel",
        },
        {
                "proto_type": "2",
                "type": "nstack-kernel",
        }
        ],
}' | tee rd_config.json

ls -l

#only for kernal stack
if [ ${proc_name} -eq 0 ]; then
sudo LD_PRELOAD=${LIB_PATH}/libnStackAPI.so ./vs_epoll -p 20000 -d ${dut2_ip} -a 10000 -s ${dut1_ip} -l 200 -t 50000 -i 0 -f 1 -r 20000 -n 1 -w 10 -u 10000 -e 10 -x 1
else
sudo LD_PRELOAD=${LIB_PATH}/libnStackAPI.so ./vc_common -p 20000 -d ${dut1_ip} -a 10000 -s ${dut2_ip} -l 200 -t 50000 -i 0 -f 1 -r 20000 -n 1 -w 10 -u 10000 -e 10 -x 1
fi

cd ${PWDDIR}

ps -elf | grep vs_epoll

sleep 10
