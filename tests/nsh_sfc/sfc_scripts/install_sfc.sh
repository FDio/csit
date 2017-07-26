#!/bin/bash

set -x

ROOTDIR=/tmp/openvpp-testing
PWDDIR=$(pwd)

#at first, we need to stop the vpp service if have
sudo service vpp stop

#uninstall the vpp and nsh sfc plugin
#and git clone the vpp and nsh sfc plugin source codes
#then compile and install them in the dut nodes.
nsh_need_install=0
sudo dpkg -l vpp-nsh-plugin >/dev/null 2>&1
if [ $? -eq 0 ]; then
    nsh_need_install=0
else
    nsh_need_install=1
fi

vpp_need_install=0
sudo dpkg -l vpp >/dev/null 2>&1
if [ $? -eq 0 ]; then
    vpp_need_install=0
else
    vpp_need_install=1
fi

#if vpp or nsh_sfc plugin not install, we will reinstall them
cd ${ROOTDIR}
VPP_NSH_DEBS=(*.deb)

if [ ${vpp_need_install} -eq 1 ] || [ ${nsh_need_install} -eq 1 ]; then
    sudo dpkg -P vpp-nsh-plugin vpp-nsh-plugin-dbg vpp-nsh-plugin-dev >/dev/null 2>&1
    sudo dpkg -P vpp vpp-dbg vpp-dev vpp-dpdk-dev vpp-dpdk-dkms vpp-lib \
                vpp-plugins vpp-python-api >/dev/null 2>&1

    sudo dpkg -i ${VPP_NSH_DEBS[@]}
    test $? -eq 0 || exit 1
fi
cd ${PWDDIR}

#check and setup the hugepages
SYS_HUGEPAGE=$(cat /sys/kernel/mm/hugepages/hugepages-2048kB/nr_hugepages)
if [ ${SYS_HUGEPAGE} -lt 1024 ]; then
    MOUNT=$(mount | grep /mnt/huge)
    while [ "${MOUNT}" != "" ]
    do
        sudo umount /mnt/huge
        sleep 1
        MOUNT=$(mount | grep /mnt/huge)
    done

    echo 2048 | sudo tee /sys/devices/system/node/node0/hugepages/hugepages-2048kB/nr_hugepages
    echo 2048 | sudo tee /sys/devices/system/node/node1/hugepages/hugepages-2048kB/nr_hugepages

    sudo mkdir -p /mnt/huge
    sudo mount -t hugetlbfs nodev /mnt/huge/
    test $? -eq 0 || exit 1
fi

#check and set the max map count
SYS_MAP=$(cat /proc/sys/vm/max_map_count)
if [ ${SYS_MAP} -lt 200000 ]; then
    echo 200000 | sudo tee /proc/sys/vm/max_map_count
fi

#after all, we can start the vpp service now
sudo service vpp start
