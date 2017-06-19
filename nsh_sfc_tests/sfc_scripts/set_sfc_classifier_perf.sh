#!/bin/bash

set -x

vpp_interface1=$1
vpp_interface2=$2
if1_adj_mac=$3
if2_adj_mac=$4
DUTTYPE=$5

#if setup on DUT1, config the router and classifier
if [ "${DUTTYPE}" == "DUT1" ]; then
    sudo service vpp restart
    sleep 5

    sudo vppctl set int state ${vpp_interface1} up
    sleep 10
    sudo vppctl set int ip table ${vpp_interface1} 0
    sudo vppctl set int ip address ${vpp_interface1} 192.168.50.76/24

    sudo vppctl classify table mask l3 ip4 proto
    sudo vppctl classify session l2-input-hit-next input-node nsh-classifier table-index 0 match l3 ip4 proto 61 opaque-index 47615
    sudo vppctl set int l2 bridge ${vpp_interface1} 1 1
    sudo vppctl set interface l2 input classify intfc ${vpp_interface1} ip4-table 0

    sudo vppctl create vxlan-gpe tunnel local 192.168.60.76 remote 192.168.60.71 vni 9 next-nsh encap-vrf-id 0 decap-vrf-id 0
    sudo vppctl set int l2 bridge vxlan_gpe_tunnel0 1 1

    sleep 2
    vxlan_gpe_index=`sudo vppctl sh int | grep "vxlan_gpe_tunnel0" | awk '{print $2}'`
    sudo vppctl create nsh entry nsp 185 nsi 255 md-type 1 c1 3232248395 c2 9 c3 3232248392 c4 50336437 next-ethernet
    sudo vppctl create nsh map nsp 185 nsi 255 mapped-nsp 185 mapped-nsi 255 nsh_action push encap-vxlan-gpe-intf ${vxlan_gpe_index}

    sudo vppctl set int state ${vpp_interface2} up
    sleep 10
    sudo vppctl set int ip table ${vpp_interface2} 0
    sudo vppctl set int ip address ${vpp_interface2} 192.168.60.76/24

    sudo vppctl set interface l2 xconnect ${vpp_interface2} ${vpp_interface1}
    sudo vppctl set ip arp ${vpp_interface1} 192.168.50.71 ${if1_adj_mac}

    sudo vppctl ip route add 192.168.60.71/24 via 192.168.60.76
    sudo vppctl set ip arp ${vpp_interface2} 192.168.60.71 ${if2_adj_mac}
    sudo vppctl ip route add 20.20.20.00/24 via 192.168.50.76

    sudo vppctl trace add dpdk-input 100

elif [ "${DUTTYPE}" == "DUT2" ]; then
    sudo service vpp restart
    sleep 5

    sudo vppctl set int state ${vpp_interface2} up
    sleep 10
    sudo vppctl set int ip table ${vpp_interface2} 0
    sudo vppctl set int ip address ${vpp_interface2} 192.168.60.76/24

    sudo vppctl classify table mask l3 ip4 proto
    sudo vppctl classify session l2-input-hit-next input-node nsh-classifier table-index 0 match l3 ip4 proto 61 opaque-index 47615
    sudo vppctl set int l2 bridge ${vpp_interface2} 1 1
    sudo vppctl set interface l2 input classify intfc ${vpp_interface2} ip4-table 0

    sudo vppctl create vxlan-gpe tunnel local 192.168.50.76 remote 192.168.50.71 vni 9 next-nsh encap-vrf-id 0 decap-vrf-id 0
    sudo vppctl set int l2 bridge vxlan_gpe_tunnel0 1 1

    sleep 2
    vxlan_gpe_index=`sudo vppctl sh int | grep "vxlan_gpe_tunnel0" | awk '{print $2}'`
    sudo vppctl create nsh entry nsp 185 nsi 255 md-type 1 c1 3232248395 c2 9 c3 3232248392 c4 50336437 next-ethernet
    sudo vppctl create nsh map nsp 185 nsi 255 mapped-nsp 185 mapped-nsi 255 nsh_action push encap-vxlan-gpe-intf ${vxlan_gpe_index}

    sudo vppctl set int state ${vpp_interface1} up
    sleep 10
    sudo vppctl set int ip table ${vpp_interface1} 0
    sudo vppctl set int ip address ${vpp_interface1} 192.168.50.76/24

    sudo vppctl set interface l2 xconnect ${vpp_interface1} ${vpp_interface2}
    sudo vppctl set ip arp ${vpp_interface2} 192.168.60.71 ${if2_adj_mac}

    sudo vppctl ip route add 192.168.50.71/24 via 192.168.50.76
    sudo vppctl set ip arp ${vpp_interface1} 192.168.50.71 ${if1_adj_mac}
    sudo vppctl ip route add 10.10.10.00/24 via 192.168.60.76

    sudo vppctl trace add dpdk-input 100

else
    echo "Not support the DUT type!!!"
    exit 1
fi
