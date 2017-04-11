#!/bin/bash

set -x

sudo service vpp restart
sleep 5

sudo vppctl set int state $1 up
sleep 10
sudo vppctl set int ip table $1 7
sudo vppctl set int ip address $1 192.168.50.76/24

sudo vppctl create vxlan-gpe tunnel local 192.168.50.76 remote 192.168.50.71 vni 9 next-nsh encap-vrf-id 7 decap-vrf-id 7
sudo vppctl set int l2 bridge vxlan_gpe_tunnel0 1 1

sudo vppctl create vxlan-gpe tunnel local 192.168.50.76 remote 192.168.50.72 vni 10 next-nsh encap-vrf-id 7 decap-vrf-id 7
sudo vppctl set int l2 bridge vxlan_gpe_tunnel1 1 1

sudo vppctl create nsh entry nsp 185 nsi 255 md-type 1 c1 3232248395 c2 9 c3 3232248392 c4 50336437 next-ethernet
sudo vppctl create nsh entry nsp 185 nsi 254 md-type 1 c1 3232248395 c2 9 c3 3232248392 c4 50336437 next-ethernet

sleep 2
vxlan_gpe_index0=`sudo vppctl sh interfaces | grep "vxlan_gpe_tunnel0" | awk '{print $2}'`
vxlan_gpe_index1=`sudo vppctl sh interfaces | grep "vxlan_gpe_tunnel1" | awk '{print $2}'`
sudo vppctl create nsh map nsp 185 nsi 255 mapped-nsp 185 mapped-nsi 254 nsh_action swap encap-vxlan-gpe-intf ${vxlan_gpe_index0}

sudo vppctl ip route add 192.168.50.71/32 via 192.168.50.76 $1
sudo vppctl ip route add 192.168.50.72/32 via 192.168.50.76 $1
sudo vppctl set ip arp fib-id 7 $1 192.168.50.71 $2
sudo vppctl set ip arp fib-id 7 $1 192.168.50.72 $2

sudo vppctl trace add dpdk-input 100
