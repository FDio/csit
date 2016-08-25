#!/bin/bash

ROOTDIR=/tmp/TLDK-testing
PWDDIR=$(pwd)

rx_file=$1
tx_file=$2
nic_pci=$3
fe_cfg=$4
be_cfg=$5
IPv4_addr=$6
IPv6_addr=$7

#kill the udpfwd
sudo killall -9 udpfwd 2>/dev/null

sleep 2

pid=`pgrep udpfwd`
if [ "$pid" != "" ]; then
    echo "terminate the udpfwd failed!"
    exit 1
fi

#mount the hugepages again
sudo umount /mnt/huge
sudo mount -t hugetlbfs nodev /mnt/huge/
test $? -eq 0 || exit 1

sleep 2

#run the udpfwd
cd ${ROOTDIR}
if [ "$IPv6_addr" == "NONE" ]; then
sudo sh -c "nohup ./tldk/x86_64-native-linuxapp-gcc/app/udpfwd --lcore='0' \
    -n 2 --vdev 'eth_pcap1,rx_pcap=${rx_file},tx_pcap=${tx_file}' \
    -b ${nic_pci} -- -P -R 0x1000 -S 0x1000 -s 0x20 -f ${fe_cfg} -b ${be_cfg} \
    port=0,lcore=0,rx_offload=0,tx_offload=0,ipv4=${IPv4_addr} &"
elif [ "$IPv4_addr" == "NONE" ]; then
sudo sh -c "nohup ./tldk/x86_64-native-linuxapp-gcc/app/udpfwd --lcore='0' \
    -n 2 --vdev 'eth_pcap1,rx_pcap=${rx_file},tx_pcap=${tx_file}' \
    -b ${nic_pci} -- -P -R 0x1000 -S 0x1000 -s 0x20 -f ${fe_cfg} -b ${be_cfg} \
    port=0,lcore=0,rx_offload=0,tx_offload=0,ipv6=${IPv6_addr} &"
fi

cd ${PWDDIR}

sleep 10
