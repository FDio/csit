#!/bin/bash

set -x

# set arch, default to x86_64 if none given
ARCH=${1:-"x86_64"}

# dpdk prefers "arm64" to "aarch64" and does not allow arm64 native target
if [ $ARCH == "aarch64" ]; then
    ARCH="arm64"
    MACHINE="armv8a"
else
    MACHINE="native"
fi

ROOTDIR=/tmp/TLDK-testing
PWDDIR=$(pwd)

rx_file=$1
tx_file=$2
nic_pci=$3
fe_cfg=$4
be_cfg=$5
IPv4_addr=$6
IPv6_addr=$7

echo $IPv4_addr

# Try to kill the l4fwd
sudo pgrep l4fwd
if [ $? -eq "0" ]; then
    success=false
    sudo pkill l4fwd
    echo "RC = $?"
    for attempt in {1..5}; do
        echo "Checking if l4fwd is still alive, attempt nr ${attempt}"
        sudo pgrep l4fwd
        if [ $? -eq "1" ]; then
            echo "l4fwd is dead"
            success=true
            break
        fi
        echo "l4fwd is still alive, waiting 1 second"
        sleep 1
    done
    if [ "$success" = false ]; then
        echo "The command sudo pkill l4fwd failed"
        sudo pkill -9 l4fwd
        echo "RC = $?"
        exit 1
    fi
else
    echo "l4fwd is not running"
fi

#mount the hugepages again
sudo umount /mnt/huge
sudo mount -t hugetlbfs nodev /mnt/huge/
test $? -eq 0 || exit 1

sleep 2

#run the l4fwd with tag U
# need to install libpcap, libpcap-dev to use --vdev
cd ${ROOTDIR}
if [ "$IPv6_addr" == "NONE" ]; then
sudo sh -c "nohup ./tldk/${ARCH}-${MACHINE}-linuxapp-gcc/app/l4fwd --lcore='0' \
    -n 2 --vdev 'eth_pcap1,rx_pcap=${rx_file},tx_pcap=${tx_file}' \
    -b ${nic_pci} -- -P -U -R 0x1000 -S 0x1000 -s 0x20 -f ${fe_cfg} -b ${be_cfg} \
    port=0,lcore=0,rx_offload=0,tx_offload=0,ipv4=${IPv4_addr} &"
elif [ "$IPv4_addr" == "NONE" ]; then
sudo sh -c "nohup ./tldk/${ARCH}-${MACHINE}-linuxapp-gcc/app/l4fwd --lcore='0' \
    -n 2 --vdev 'eth_pcap1,rx_pcap=${rx_file},tx_pcap=${tx_file}' \
    -b ${nic_pci} -- -P -U -R 0x1000 -S 0x1000 -s 0x20 -f ${fe_cfg} -b ${be_cfg} \
    port=0,lcore=0,rx_offload=0,tx_offload=0,ipv6=${IPv6_addr} &"
fi

cd ${PWDDIR}

ps -elf | grep l4fwd

sleep 10
