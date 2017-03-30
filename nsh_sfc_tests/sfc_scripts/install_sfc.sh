#!/bin/bash

ROOTDIR=/tmp/openvpp-testing
PWDDIR=$(pwd)

VPP_VERSION=17.01-rc2~4-gbf2fcad
NSH_PLUGIN_VERSION=17.01-rc2

#at first, we need to stop the vpp service if have
sudo service vpp stop

#check the vpp installed or not
#if yes, will check the vpp version
vpp_need_install=0
sudo dpkg -l vpp >/dev/null 2>&1
if [ $? -eq 0 ]; then
    vpp_version=`dpkg -s vpp | grep Version | awk -F' ' '{print $2}'`
    if [ "${vpp_version}" != "${VPP_VERSION}" ]; then
        vpp_need_install=1
    fi
else
    vpp_need_install=1
fi

if [ ${vpp_need_install} -eq 1 ]; then
    cd ${ROOTDIR}/vpp-debs/
    sudo dpkg -i vpp*.deb >/dev/null 2>&1
    test $? -eq 0 || exit 1
    cd ${PWDDIR}
fi

#check the vpp NSH SFC Plugin installed or not
#if yes, will check the version
nsh_need_install=0
sudo dpkg -l vpp-nsh-plugin >/dev/null 2>&1
if [ $? -eq 0 ]; then
    nsh_plugin_version=`dpkg -s vpp-nsh-plugin | grep Version | awk -F' ' '{print $2}'`
    if [ "${nsh_plugin_version}" != "${NSH_PLUGIN_VERSION}" ]; then
        nsh_need_install=1
    fi
else
    nsh_need_install=1
fi

if [ ${nsh_need_install} -eq 1 ]; then
    cd ${ROOTDIR}/nsh-plugin-debs/
    sudo dpkg -i vpp-nsh-plugin*.deb >/dev/null 2>&1
    test $? -eq 0 || exit 1
    cd ${PWDDIR}
fi

#check and setup the hugepages
SYS_HUGEPAGE=$(cat /sys/kernel/mm/hugepages/hugepages-2048kB/nr_hugepages)
if [ ${SYS_HUGEPAGE} -lt 4096 ]; then
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
