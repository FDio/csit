#!/bin/bash
set -euf -o pipefail

#git clone ssh://rotterdam-jobbuilder@gerrit.fd.io:29418/vpp
#
#cd vpp/build-root
#./bootstrap.sh
#make PLATFORM=vpp TAG=vpp_debug install-deb
#
#ls -la

IFS=',' read -ra ADDR <<< "${JCLOUDS_IPS}"

function ssh_do() {
    echo
    echo "### "  ssh $@
    ssh $@
}


set

for addr in "${ADDR[@]}"; do
    echo
    echo ${addr}
    echo

    ssh_do localadmin@${addr} hostname || true
    ssh_do localadmin@${addr} ifconfig -a || true
    ssh_do localadmin@${addr} lspci -Dnn || true
    ssh_do localadmin@${addr} "lspci -Dnn | grep 0200" || true
    ssh_do localadmin@${addr} free -m || true
    ssh_do localadmin@${addr} cat /proc/meminfo || true
done




