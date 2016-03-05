#!/bin/bash
# Copyright (c) 2016 Cisco and/or its affiliates.
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at:
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

set -x

cat /etc/nodepool/*

id

function ssh_do() {
    echo
    echo "### "  ssh $@
    ssh -i /etc/nodepool/id_rsa -o StrictHostKeyChecking=no $@
}

ssh -vv jenkins@`cat /etc/nodepool/primary_node` ifconfig -a

#for addr in `cat /etc/nodepool/sub_nodes`; do
#    echo
#    echo ${addr}
#    echo
#
#    if [[ ! "10.30.4.4" =~ 10\.30\.4.* ]]; then
#        echo "Weird address: ${addr}, skipping"
#        continue
#    fi
#
#    ssh_do jenkins@${addr} hostname || true
#    ssh_do jenkins@${addr} "ifconfig -a" || true
#    ssh_do jenkins@${addr} "lspci -Dnn | grep 0200" || true
#    ssh_do jenkins@${addr} "free -m" || true
#    ssh_do jenkins@${addr} "cat /proc/meminfo" || true
#    ssh_do jenkins@${addr} "dpkg -l vpp\*" || true
#    ssh_do jenkins@${addr} "sudo lshw -c network" || true
#    ssh_do jenkins@${addr} "sudo cat /proc/cpuinfo" || true
#done

echo ##################

subnodes=(`cat /etc/nodepool/sub_nodes`)
#ssh_do jenkins@${subnodes[0]} "sudo ifconfig eth1 172.16.1.1/24 up"
#ssh_do jenkins@${subnodes[0]} "sudo ifconfig eth2 172.16.2.1/24 up"
#ssh_do jenkins@${subnodes[0]} "sudo ifconfig eth3 down"
#ssh_do jenkins@${subnodes[0]} "sudo ifconfig eth4 down"
#ssh_do jenkins@${subnodes[0]} "sudo ifconfig eth5 172.16.5.1/24 up"
#ssh_do jenkins@${subnodes[0]} "sudo ifconfig eth6 172.16.6.1/24 up"
#ssh_do jenkins@${subnodes[0]} "sudo ifconfig -a"
#
#
#ssh_do jenkins@${subnodes[1]} "sudo ifconfig eth1 172.16.1.2/24 up"
#ssh_do jenkins@${subnodes[1]} "sudo ifconfig eth2 172.16.2.2/24 up"
#ssh_do jenkins@${subnodes[1]} "sudo ifconfig eth3 172.16.3.2/24 up"
#ssh_do jenkins@${subnodes[1]} "sudo ifconfig eth4 172.16.4.2/24 up"
#ssh_do jenkins@${subnodes[1]} "sudo ifconfig eth5 down"
#ssh_do jenkins@${subnodes[1]} "sudo ifconfig eth6 down"
#ssh_do jenkins@${subnodes[1]} "sudo ifconfig -a"
#
#ssh_do jenkins@${subnodes[2]} "sudo ifconfig eth1 down"
#ssh_do jenkins@${subnodes[2]} "sudo ifconfig eth2 down"
#ssh_do jenkins@${subnodes[2]} "sudo ifconfig eth3 172.16.3.3/24 up"
#ssh_do jenkins@${subnodes[2]} "sudo ifconfig eth4 172.16.4.3/24 up"
#ssh_do jenkins@${subnodes[2]} "sudo ifconfig eth5 172.16.5.3/24 up"
#ssh_do jenkins@${subnodes[2]} "sudo ifconfig eth6 172.16.6.3/24 up"
#ssh_do jenkins@${subnodes[2]} "sudo ifconfig -a"

for addr in `cat /etc/nodepool/sub_nodes`; do
    echo
    echo ${addr}
    echo

    if [[ ! "10.30.4.4" =~ 10\.30\.4.* ]]; then
        echo "Weird address: ${addr}, skipping"
        continue
    fi

    ssh_do jenkins@${addr} "sudo apt-get -y install arping"

    ssh_do jenkins@${addr} "sudo ifconfig eth1 up"
    ssh_do jenkins@${addr} "sudo ifconfig eth2 up"
    ssh_do jenkins@${addr} "sudo ifconfig eth3 up"
    ssh_do jenkins@${addr} "sudo ifconfig eth4 up"
    ssh_do jenkins@${addr} "sudo ifconfig eth5 up"
    ssh_do jenkins@${addr} "sudo ifconfig eth6 up"
    #ssh_do jenkins@${addr} "sudo ifconfig -a"
    #ssh_do jenkins@${addr} "sudo arp -a"
    ssh_do jenkins@${addr} -- "nohup sudo tcpdump -n -i any -vv arp > tcpdumpout 2>&1 & "
done


ssh_do jenkins@${subnodes[0]} "sudo arping -c 1 -I eth1 -b 1.1.1.1"
ssh_do jenkins@${subnodes[0]} "sudo arping -c 1 -I eth2 -b 1.1.1.1"
ssh_do jenkins@${subnodes[0]} "sudo arping -c 1 -I eth3 -b 1.1.1.1"
ssh_do jenkins@${subnodes[0]} "sudo arping -c 1 -I eth4 -b 1.1.1.1"
ssh_do jenkins@${subnodes[0]} "sudo arping -c 1 -I eth5 -b 1.1.1.1"
ssh_do jenkins@${subnodes[0]} "sudo arping -c 1 -I eth6 -b 1.1.1.1"


echo "XXXXXXXXXXXXXXX"

jobs
ssh_do jenkins@${subnodes[0]} "ps aux"
ssh_do jenkins@${subnodes[0]} "sudo killall tcpdump"
ssh_do jenkins@${subnodes[0]} "cat tcpdumpout"
echo "XXXXXXXXXXXXXXX"
ssh_do jenkins@${subnodes[1]} "ps aux"
ssh_do jenkins@${subnodes[1]} "sudo killall tcpdump"
ssh_do jenkins@${subnodes[1]} "cat tcpdumpout"
echo "XXXXXXXXXXXXXXX"
ssh_do jenkins@${subnodes[2]} "ps aux"
ssh_do jenkins@${subnodes[2]} "sudo killall tcpdump"
ssh_do jenkins@${subnodes[2]} "cat tcpdumpout"

#echo "XXXXXXXXXXXXXXXX HERE BE PINGS NOW"
#
#ssh_do jenkins@${subnodes[0]} "ping 172.16.1.2 -c 1"
#ssh_do jenkins@${subnodes[0]} "ping 172.16.2.2 -c 1"
#ssh_do jenkins@${subnodes[0]} "ping 172.16.5.3 -c 1"
#ssh_do jenkins@${subnodes[0]} "ping 172.16.6.3 -c 1"
#
#ssh_do jenkins@${subnodes[1]} "ping 172.16.3.3 -c 1"
#ssh_do jenkins@${subnodes[1]} "ping 172.16.4.3 -c 1"


#virtualenv env
#. env/bin/activate
#
#echo pip install
#pip install -r requirements.txt
#
#PYTHONPATH=`pwd` pybot -L TRACE \
#    -v TOPOLOGY_PATH:topologies/enabled/topology.yaml \
#    --include vm_env \
#    --include 3_NODE_SINGLE_LINK_TOPO \
#    --exclude 3_node_double_link_topoNOT3_node_single_link_topo \
#    --exclude PERFTEST \
#    --noncritical EXPECTED_FAILING \
#    tests/
