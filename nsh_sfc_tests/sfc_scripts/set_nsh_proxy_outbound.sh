#!/bin/bash

set -x

vpp_interface1=$1
vpp_interface2=$2
vpp_intf1_adj_mac=$3
vpp_intf2_adj_mac=$4

sudo service vpp restart
sleep 5

sudo vppctl set int state ${vpp_interface1} up
sleep 10
sudo vppctl set int ip table ${vpp_interface1} 0
sudo vppctl set int ip address ${vpp_interface1} 192.168.50.76/24

sudo vppctl create vxlan-gpe tunnel local 192.168.60.76 remote 192.168.60.71 vni 9 next-nsh encap-vrf-id 0 decap-vrf-id 0
sudo vppctl set int l2 bridge vxlan_gpe_tunnel0 1 1

sudo vppctl create vxlan tunnel src 192.168.50.76 dst 192.168.50.72 vni 1 encap-vrf-id 0 decap-next node nsh-proxy
sudo vppctl set int l2 bridge vxlan_tunnel0 1 1

sudo vppctl create nsh entry nsp 185 nsi 255 md-type 1 c1 3232248395 c2 9 c3 3232248392 c4 50336437 next-ethernet
sudo vppctl create nsh entry nsp 185 nsi 254 md-type 1 c1 3232248395 c2 9 c3 3232248392 c4 50336437 next-ethernet

sleep 2
vxlan_gpe_index=`sudo vppctl sh int | grep "vxlan_gpe_tunnel0" | awk '{print $2}'`
vxlan_index=`sudo vppctl sh int | grep "vxlan_tunnel0" | awk '{print $2}'`
sudo vppctl create nsh map nsp 185 nsi 255 mapped-nsp 185 mapped-nsi 255 nsh_action pop encap-vxlan4-intf ${vxlan_index}
sudo vppctl create nsh map nsp 185 nsi 254 mapped-nsp 185 mapped-nsi 254 nsh_action push encap-vxlan-gpe-intf ${vxlan_gpe_index}

sudo vppctl ip route add 192.168.50.72/24 via 192.168.50.76

sudo vppctl set int state ${vpp_interface2} up
sleep 10
sudo vppctl set int ip table ${vpp_interface2} 0
sudo vppctl set int ip address ${vpp_interface2} 192.168.60.76/24

sudo vppctl ip route add 192.168.60.71/24 via 192.168.60.76
sudo vppctl set ip arp ${vpp_interface2} 192.168.60.71 ${vpp_intf2_adj_mac}

sudo vppctl trace add dpdk-input 100
