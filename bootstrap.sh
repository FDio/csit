#!/bin/bash
#set -euf -o pipefail

#git clone ssh://rotterdam-jobbuilder@gerrit.fd.io:29418/vpp
#
#cd vpp/build-root
#./bootstrap.sh
#make PLATFORM=vpp TAG=vpp_debug install-deb
#
#ls -la

#set -x
#
#ping 10.30.51.17 -w 3 || true
#ping 10.30.51.18 -w 3 || true
#ping 10.30.51.16 -w 3 || true
#ping 10.30.51.21 -w 3 || true
#ping 10.30.51.22 -w 3 || true
#ping 10.30.51.20 -w 3 || true
#ping 10.30.51.25 -w 3 || true
#ping 10.30.51.26 -w 3 || true
#ping 10.30.51.24 -w 3 || true

#IFS=',' read -ra ADDR <<< "${JCLOUDS_IPS}"
#
#function ssh_do() {
#    echo
#    echo "### "  ssh $@
#    ssh $@
#}
#
#
#set
#
#for addr in "${ADDR[@]}"; do
#    echo
#    echo ${addr}
#    echo
#
#    ssh_do localadmin@${addr} hostname || true
#    ssh_do localadmin@${addr} ifconfig -a || true
#    ssh_do localadmin@${addr} lspci -Dnn || true
#    ssh_do localadmin@${addr} "lspci -Dnn | grep 0200" || true
#    ssh_do localadmin@${addr} free -m || true
#    ssh_do localadmin@${addr} cat /proc/meminfo || true
#done


virtualenv env
. env/bin/activate

echo pip install
pip install -r requirements.txt

PYTHONPATH=`pwd` pybot -L TRACE -v TOPOLOGY_PATH:topologies/available/lf_testbed2.yaml tests

