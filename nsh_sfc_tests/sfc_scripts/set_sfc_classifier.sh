#!/bin/bash

sudo service vpp restart

vppctl set int state $1 up
vppctl set int ip table $1 0
vppctl set int ip address $1 192.168.50.76/24

vppctl classify table mask l3 ip4 proto
vppctl classify session l2-input-hit-next input-node nsh-classifier table-index 0 match l3 ip4 proto 6 opaque-index 47615
vppctl set int l2 bridge $1 1 1
vppctl set interface l2 input classify intfc $1 ip4-table 0

vppctl create vxlan-gpe tunnel local 192.168.50.76 remote 192.168.50.71 vni 9 next-nsh encap-vrf-id 0 decap-vrf-id 0
vppctl set int l2 bridge vxlan_gpe_tunnel0 1 1
vppctl create nsh entry nsp 185 nsi 255 md-type 1 c1 3232248395 c2 9 c3 3232248392 c4 50336437 next-ethernet
vppctl create nsh map nsp 185 nsi 255 mapped-nsp 185 mapped-nsi 255 nsh_action push encap-vxlan-gpe-intf 2

vppctl ip route add 192.168.50.71/24 via 192.168.50.76
vppctl set ip arp $1 192.168.50.71 $2
vppctl ip route add 10.10.12.00/24 via 192.168.50.76

