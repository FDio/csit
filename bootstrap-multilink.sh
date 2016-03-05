#!/bin/bash
set -x

cat /etc/nodepool/*

id

function ssh_do() {
    echo
    echo "### "  ssh $@
    ssh -i /etc/nodepool/id_rsa -o StrictHostKeyChecking=no $@
}

for addr in `cat /etc/nodepool/sub_nodes_private`; do
    echo
    echo ${addr}
    echo

    ssh_do ${addr} hostname || true
    ssh_do ${addr} "ifconfig -a" || true
    ssh_do ${addr} "lspci -Dnn | grep 0200" || true
    ssh_do ${addr} "free -m" || true
    ssh_do ${addr} "cat /proc/meminfo" || true
    ssh_do ${addr} "dpkg -l vpp\*" || true
    ssh_do ${addr} "sudo lshw -c network" || true
done




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
