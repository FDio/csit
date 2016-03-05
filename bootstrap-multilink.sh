#!/bin/bash

set -x

ls -laR /etc/nodepool/

cat /etc/nodepool/*


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
