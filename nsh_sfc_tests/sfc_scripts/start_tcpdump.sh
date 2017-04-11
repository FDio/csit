#!/bin/bash

ROOTDIR=/tmp/openvpp-testing
PWDDIR=$(pwd)

cd ${ROOTDIR}/nsh_sfc_tests/sfc_scripts/
sudo rm -f temp_packet.pcap

sudo tcpdump -i $1 -c 1 -w temp_packet.pcap dst host $2 >/dev/null 2>&1 &

cd ${PWDDIR}
