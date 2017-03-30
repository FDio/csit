#!/bin/bash

vppctl set int state TenGigabitEthernet7/0/0 up
vppctl set int ip table TenGigabitEthernet7/0/0 0
vppctl set int ip address TenGigabitEthernet7/0/0 192.168.50.76/24

vppctl create vxlan-gpe tunnel local 192.168.50.76 remote 192.168.50.71 vni 9 next-nsh encap-vrf-id 0 decap-vrf-id 0
vppctl set int l2 bridge vxlan_gpe_tunnel0 1 1

vppctl create vxlan tunnel src 192.168.50.76 dst 192.168.50.72 vni 1 encap-vrf-id 0 decap-next node nsh-proxy
vppctl set int l2 bridge vxlan_tunnel0 1 1

vppctl create nsh entry nsp 185 nsi 255 md-type 1 c1 3232248395 c2 9 c3 3232248392 c4 50336437 next-ethernet
vppctl create nsh entry nsp 185 nsi 254 md-type 1 c1 3232248395 c2 9 c3 3232248392 c4 50336437 next-ethernet

vppctl create nsh map nsp 185 nsi 255 mapped-nsp 185 mapped-nsi 255 nsh_action pop encap-vxlan4-intf 3
vppctl create nsh map nsp 185 nsi 254 mapped-nsp 185 mapped-nsi 254 nsh_action push encap-vxlan-gpe-intf 2

vppctl ip route add 192.168.50.71/24 via 192.168.50.76
vppctl set ip arp TenGigabitEthernet7/0/0 192.168.50.71 90e2.ba48.7a91
vppctl set ip arp TenGigabitEthernet7/0/0 192.168.50.72 0800.2761.0705

