#!/bin/bash

#sudo apt-get -y install libpython2.7-dev

#VIRL_VMS="10.30.51.53,10.30.51.51,10.30.51.52"
#IFS=',' read -ra ADDR <<< "${VIRL_VMS}"
#
#function ssh_do() {
#    echo
#    echo "### "  ssh $@
#    ssh -i priv_key -o StrictHostKeyChecking=no $@
#}

#for addr in "${ADDR[@]}"; do
#    echo
#    echo ${addr}
#    echo
#
#    ssh_do cisco@${addr} hostname || true
#    ssh_do cisco@${addr} "ifconfig -a" || true
#    ssh_do cisco@${addr} "lspci -Dnn | grep 0200" || true
#    ssh_do cisco@${addr} "free -m" || true
#    ssh_do cisco@${addr} "cat /proc/meminfo" || true
#    ssh_do cisco@${addr} "dpkg -l vpp\*" || true
#    ssh_do cisco@${addr} "lshw -c network" || true
#    ssh_do cisco@${addr} "sudo -S sh -c 'echo exec show  hardware | vpp_api_test '"
#done

virtualenv env
. env/bin/activate

echo pip install
pip install -r requirements.txt

#PYTHONPATH=`pwd` pybot -L TRACE -v TOPOLOGY_PATH:topologies/available/virl.yaml --exclude PERFTEST tests || true
PYTHONPATH=`pwd` pybot -L TRACE -v TOPOLOGY_PATH:topologies/available/lf_testbed2.yaml -s performance tests || true
PYTHONPATH=`pwd` pybot -L TRACE -v TOPOLOGY_PATH:topologies/available/lf_testbed2-710-520.yaml -s performance tests || true

