#!/bin/bash

vppctl set int state TenGigabitEthernet7/0/0 up
vppctl set int ip table TenGigabitEthernet7/0/0 7
vppctl set int ip address TenGigabitEthernet7/0/0 192.168.50.76/24

vppctl create vxlan-gpe tunnel local 192.168.50.76 remote 192.168.50.71 vni 9 next-nsh encap-vrf-id 7 decap-vrf-id 7
vppctl set int l2 bridge vxlan_gpe_tunnel0 1 1

vppctl create vxlan-gpe tunnel local 192.168.50.76 remote 192.168.50.72 vni 9 next-nsh encap-vrf-id 7 decap-vrf-id 7
vppctl set int l2 bridge vxlan_gpe_tunnel1 1 1

vppctl create nsh entry nsp 185 nsi 255 md-type 1 c1 3232248395 c2 9 c3 3232248392 c4 50336437 next-ethernet
vppctl create nsh entry nsp 185 nsi 254 md-type 1 c1 3232248395 c2 9 c3 3232248392 c4 50336437 next-ethernet
vppctl create nsh map nsp 185 nsi 255 mapped-nsp 185 mapped-nsi 254 nsh_action swap encap-vxlan-gpe-intf 3

vppctl ip route add 192.168.50.71/32 via 192.168.50.76 TenGigabitEthernet7/0/0
vppctl ip route add 192.168.50.72/32 via 192.168.50.76 TenGigabitEthernet7/0/0
vppctl set ip arp fib-id 7 TenGigabitEthernet7/0/0 192.168.50.71 90e2.ba48.7a91
vppctl set ip arp fib-id 7 TenGigabitEthernet7/0/0 192.168.50.72 0800.2761.0705

