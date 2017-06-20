#!/bin/bash

set -x

ROOTDIR=/tmp/openvpp-testing
PWDDIR=$(pwd)

if_name1=$1
if_name2=$2

VPP_VERSION=`cat ${ROOTDIR}/NSH_SFC_VER | grep VPP | awk -F'= ' '{print $2}'`
NSH_SFC_VERSION=`cat ${ROOTDIR}/NSH_SFC_VER | grep NSH_SFC | awk -F'= ' '{print $2}'`

VPP_CODE_DIR=${ROOTDIR}/vpp_codes
NSH_SFC_CODE_DIR=${ROOTDIR}/nsh_sfc_codes

#at first, we need to stop the vpp service if have
sudo service vpp stop

#uninstall the vpp and nsh sfc plugin
#and git clone the vpp and nsh sfc plugin source codes
#then compile and install them in the dut nodes.
nsh_need_install=0
sudo dpkg -l vpp-nsh-plugin >/dev/null 2>&1
if [ $? -eq 0 ]; then
    nsh_plugin_version=`dpkg -s vpp-nsh-plugin | grep Version | awk -F' ' '{print $2}'`
    if [ "${nsh_plugin_version}" \< "${NSH_SFC_VERSION}" ]; then
        sudo dpkg -P vpp-nsh-plugin vpp-nsh-plugin-dbg vpp-nsh-plugin-dev >/dev/null 2>&1
        test $? -eq 0 || exit 1
        nsh_need_install=1
    fi
else
    nsh_need_install=1
fi

vpp_need_install=0
sudo dpkg -l vpp >/dev/null 2>&1
if [ $? -eq 0 ]; then
    vpp_version=`dpkg -s vpp | grep Version | awk -F' ' '{print $2}'`
    if [ "${vpp_version}" \< "${VPP_VERSION}" ]; then
        sudo dpkg -P vpp vpp-dbg vpp-dev vpp-dpdk-dev vpp-dpdk-dkms vpp-lib \
                     vpp-plugins vpp-python-api >/dev/null 2>&1
        test $? -eq 0 || exit 1
        vpp_need_install=1
    fi
else
    vpp_need_install=1
fi

sleep 5

##begin to clone the vpp source code
if [ ${vpp_need_install} -eq 1 ]; then
    sudo rm -rf ${VPP_CODE_DIR}
    sudo mkdir -p ${VPP_CODE_DIR}
    cd ${VPP_CODE_DIR}
    git clone -b v${VPP_VERSION} https://gerrit.fd.io/r/vpp

    #compile the vpp code
    cd ./vpp/build-root/
    make distclean
    ./bootstrap.sh
    make V=0 PLATFORM=vpp TAG=vpp install-deb

    #after that, install vpp
    sudo dpkg -i *.deb
    cd ${PWDDIR}
fi

##begin to clone the nsh sfc source code
if [ ${nsh_need_install} -eq 1 ]; then
    sudo rm -rf ${NSH_SFC_CODE_DIR}
    sudo mkdir -p ${NSH_SFC_CODE_DIR}
    cd ${NSH_SFC_CODE_DIR}
    git clone -b v${NSH_SFC_VERSION} https://gerrit.fd.io/r/nsh_sfc

    #compile the nsh sfc code
    cd ./nsh_sfc/nsh-plugin/
    sudo rm -rf build
    sudo ./build.sh

    #after that, install the nsh sfc plugin
    cd ./packaging/
    sudo dpkg -i *.deb
    cd ${PWDDIR}
fi

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
