#!/bin/bash

ROOTDIR=/tmp/openvpp-testing
PWDDIR=$(pwd)

cd ${ROOTDIR}/nsh_sfc_tests/sfc_scripts/
sudo rm -f temp_packet.pcap

sudo /usr/sbin/tcpdump -i $1 -c 1 -w temp_packet.pcap &

if [ ! $? -eq 0 ]; then
    echo "Start the tcpdump failed!!!"
    exit 1
fi

cd ${PWDDIR}
