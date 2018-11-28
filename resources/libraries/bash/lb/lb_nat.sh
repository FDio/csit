#!/bin/bash

set -x

vpp_intf1=$1
vpp_intf1_adj_mac=$2
vpp_intf2=$3
vpp_intf2_adj_mac=$4

sudo service vpp restart || exit 1
sleep 10

sudo vppctl set int state ${vpp_intf1} up
sleep 10
sudo vppctl set int ip table ${vpp_intf1} 0
sudo vppctl set int ip address ${vpp_intf1} 192.168.50.73/32

sudo vppctl ip route add 192.168.50.74/24 via ${vpp_intf1}
sudo vppctl set ip arp ${vpp_intf1} 192.168.50.74 ${vpp_intf1_adj_mac}
sudo vppctl set ip arp ${vpp_intf1} 192.168.50.75 ${vpp_intf1_adj_mac}
sudo vppctl set ip arp ${vpp_intf1} 192.168.50.76 ${vpp_intf1_adj_mac}
sudo vppctl set ip arp ${vpp_intf1} 192.168.50.77 ${vpp_intf1_adj_mac}
sudo vppctl set ip arp ${vpp_intf1} 192.168.50.78 ${vpp_intf1_adj_mac}
sudo vppctl set ip arp ${vpp_intf1} 192.168.50.79 ${vpp_intf1_adj_mac}

sudo vppctl set int state ${vpp_intf2} up
sleep 10
sudo vppctl set int ip table ${vpp_intf2} 0
sudo vppctl set int ip address ${vpp_intf2} 192.168.60.73/32

sudo vppctl ip route add 192.168.60.74/24 via ${vpp_intf2}
sudo vppctl set ip arp ${vpp_intf2} 192.168.60.74 ${vpp_intf2_adj_mac}
sudo vppctl set ip arp ${vpp_intf2} 192.168.60.75 ${vpp_intf2_adj_mac}
sudo vppctl set ip arp ${vpp_intf2} 192.168.60.76 ${vpp_intf2_adj_mac}
sudo vppctl set ip arp ${vpp_intf2} 192.168.60.77 ${vpp_intf2_adj_mac}
sudo vppctl set ip arp ${vpp_intf2} 192.168.60.78 ${vpp_intf2_adj_mac}
sudo vppctl set ip arp ${vpp_intf2} 192.168.60.79 ${vpp_intf2_adj_mac}

sudo vppctl lb conf buckets 128
sudo vppctl lb vip 90.1.2.1/32 protocol udp port 20000 encap nat4 \
type clusterip target_port 3307 new_len 1024

sudo vppctl lb as 90.1.2.1/32 protocol udp port 20000 192.168.60.74 \
192.168.60.75 192.168.60.76 192.168.60.77 192.168.60.78 192.168.60.79

sudo vppctl lb set interface nat4 in ${vpp_intf2}
sudo vppctl show lb vip verbose
