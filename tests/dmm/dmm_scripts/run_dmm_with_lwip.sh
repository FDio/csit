#!/bin/bash

set -x
OS_ID=$(grep '^ID=' /etc/os-release | cut -f2- -d= | sed -e 's/\"//g')
ROOTDIR=/tmp/DMM-testing
PWDDIR=$(pwd)
APP_DIR=${ROOTDIR}/dmm/stacks/lwip_stack/app_test/
LIB_PATH=${APP_DIR}/../release/lib64/
dut1_ip=$1
dut2_ip=$2
proc_name=$3
#proc_name => 0 = server, 1= client

set ifname ""
set ifaddress ""
set ifmac ""

for i in $(ls -1 /sys/class/net); do
  ifaddress_i=$(ifconfig $i | grep 'inet' | head -n 1 | cut -d: -f2 | awk '{print $1}')
  if [ $ifaddress_i ] && [ ${ifaddress_i%%.*} != "10" ] && [ ${ifaddress_i%%.*} != "127" ] ; then
	ifname=$i
        ifaddress=$ifaddress_i
	ifmac=$(ifconfig $i | grep 'HWaddr' | awk -F " " '{print $5}')
 	break
  fi
done

if [ -z $ifname ] || [ -z $ifaddress ] || [ -z $ifmac ]; then
echo "No suitable interface found"
    exit
fi

## use $ifname $ifaddress $ifmac
echo "ifname : " $ifname " address: "  $ifaddress " Mac :" $ifmac

#DPDK download path
DPDK_FOLDER=/tmp/dpdk/dpdk-18.02

mkdir -p ${APP_DIR}
export LD_LIBRARY_PATH=${LIB_PATH}

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
chmod 777 *
ls -l

if [ "$OS_ID" == "centos" ]; then
    ifaddress1=$(ifconfig $ifname | grep 'inet' | cut -d: -f2 | awk '{print $2}')
    echo $ifaddress1
    ifaddresscut=$(ifconfig $ifname | grep 'inet' | head -n 1 | awk -F " " '{print $2}' | awk -F "." '{print $1"."$2"."$3}')
    echo $ifaddresscut
    ifmac=$(ifconfig $ifname | grep 'ether' | awk -F " " '{print $2}')
    echo $ifmac
elif [ "$OS_ID" == "ubuntu" ]; then
    ifaddress1=$(ifconfig $ifname | grep 'inet' | head -n 1 | cut -d: -f2 | awk '{print $1}')
    echo $ifaddress1
    ifaddresscut=$(ifconfig $ifname | grep 'inet' | head -n 1 | cut -d: -f2 | awk '{print $1}' | awk -F "." '{print $1"."$2"."$3}')
    echo $ifaddresscut
    ifmac=$(ifconfig $ifname | grep 'HWaddr' | awk -F " " '{print $5}')
    echo $ifmac
fi

chmod 775 ${APP_DIR}/../release_tar.sh
cd ${APP_DIR}/../
ls -l
./release_tar.sh
chmod 775 ${APP_DIR}/../nStackServer/
chmod 775 ${APP_DIR}/../nStackServer/*
ls -l
chmod 775 ${APP_DIR}/../nStackServer/script/*
chmod 775 ${APP_DIR}/../nStackServer/bin/*
chmod 775 ${APP_DIR}/../nStackServer/configure/*

cd ${APP_DIR}/../nStackServer/script
sed -i 's!/root/dpdk/dpdk-18.02!'$DPDK_FOLDER'!1' nstack_var.sh

cd ../
cp ./configure/*.json bin/
cd bin

if [ "$OS_ID" == "centos" ]; then
    sed -i 's!eth7!'$ifname'!1' ip_data.json
elif [ "$OS_ID" == "ubuntu" ]; then
    sed -i 's!eth7!'$ifname'!1' ip_data.json
fi

sed -i 's!00:54:32:19:3d:19!'$ifmac'!1' ip_data.json
sed -i 's!192.168.1.207!'$ifaddress1'!1' ip_data.json

sed -i 's!192.168.1.1!'$ifaddresscut'.0!1' network_data_tonStack.json
sed -i 's!192.168.1.254!'$ifaddresscut'.1!1' network_data_tonStack.json
sed -i 's!192.168.1.098!'$ifaddresscut'.5!1' network_data_tonStack.json
sed -i 's!192.168.1.209!'$ifaddresscut'.254!1' network_data_tonStack.json
sed -i 's!192.168.1.0!'$ifaddresscut'.0!1' network_data_tonStack.json
sed -i 's!192.168.1.254!'$ifaddresscut'.1!1' network_data_tonStack.json

if [ "$OS_ID" == "centos" ]; then
    sed -i 's!eth7!'$ifname'!1' network_data_tonStack.json
elif [ "$OS_ID" == "ubuntu" ]; then
    sed -i 's!eth7!'$ifname'!1' network_data_tonStack.json
fi
sed -i 's!eth7!'$ifname'!1' network_data_tonStack.json

cd $ROOTDIR/dmm/release/bin
cp -r v* ../../stacks/lwip_stack/app_test
cd $ROOTDIR/dmm/stacks/lwip_stack/app_test
cp -r ../app_conf/*.json .

sed -i 's!192.168.1.1!'$ifaddresscut'.0!1' rd_config.json

cd $APP_DIR/../nStackServer
bash -x ./stop_nstack.sh
cat /proc/meminfo | grep Huge
bash -x ./start_nstack.sh
cat /proc/meminfo | grep Huge
check_result=$(pgrep nStackMain)
if [ -z "$check_result"  ]; then
    echo "nStackMain execute failed"
    exit 1
else
    echo "nStackMain execute successful"
fi

cd ${APP_DIR}

if [ ${proc_name} -eq 0 ]; then
sudo LD_LIBRARY_PATH=${LIB_PATH} ./vs_epoll -p 20000 -d ${dut2_ip} -a 10000 -s ${dut1_ip} -l 200 -t 50000 -i 0 -f 1 -r 20000 -n 1 -w 10 -u 10000 -e 10 -x 1
else
sudo LD_LIBRARY_PATH=${LIB_PATH} ./vc_common -p 20000 -d ${dut1_ip} -a 10000 -s ${dut2_ip} -l 200 -t 50 -i 0 -f 1 -r 20000 -n 1 -w 10 -u 10000 -e 10 -x 1
fi

cd ${PWDDIR}

ps -elf | grep vs_epoll

sleep 10
