#!/bin/bash
# Copyright (c) 2018 Cisco and/or its affiliates.
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

function nic_driver_utils.show_vfs {
    # Prints VFs details on specific PCI.
    # PCI patch
    local path=$1
    # UIN of interface
    local netdev=$2

    printf "\nVirtual Functions:\n%-2s %-12s %-9s %-12s %-17s %s\n" \
      "ID" "PCI Addr" "PCI ID" "Driver" "MAC Addr" "Config"
    for vf_path in ${path}/virtfn*; do
        vf=$(basename $(readlink ${vf_path}))
        vfid=$(basename ${vf_path//virtfn/})
        line=$(ip link show dev ${netdev} | grep "vf ${vfid}")
        driver=$(basename $(readlink ${vf_path}/driver))
        pciid="$(cat ${vf_path}/vendor | cut -dx -f2):$(cat ${vf_path}/device | cut -dx -f2)"
        mac=$(echo $line | sed -n -E -e 's/.*MAC ([0-9a-f:]+),.*/\1/p')
        cfg=$(echo $line | cut -d, -f2-)

        printf "%-2s %-12s %-9s %-12s %-17s%s\n" \
          $vfid $vf $pciid $driver $mac "$cfg"
    done
}

function nic_driver_utils.get_pci_addr {
    # Returns the PCI address of UIN or return back PCI address.
    # Return PCI value
    local addr

    if [ -d /sys/class/net/$2/device ]; then
        addr=$(basename $(readlink /sys/class/net/${2}/device))
    else
        addr=$2
    fi
    if [ ! -d /sys/bus/pci/devices/${pci_addr} ]; then
        echo "PCI device $2 doesn't exist" >&2
        exit 1
    fi
    eval "$1=${addr}"
}

function nic_driver_utils.test_sriov_capability {
    # Test SR-IOV capability of PCI device
    get_pci_addr pci_addr $1
    path="/sys/bus/pci/devices/${pci_addr}"

    if [ ! -f ${path}/sriov_numvfs ]; then
        echo "PCI device $1 is not SR-IOV device" >&2
        exit 1
    fi
}

function nic_driver_utils.show {
    # Prints PCI PF details and includes VFs detail if any
    get_pci_addr pci_addr $1

    nic_driver_utils.test_sriov_capability $1

    printf "%-20s: %s\n" "PCI Address" ${pci_addr}
    printf "%-20s: %s\n" "PCI ID" \
        "$(cat ${path}/vendor | cut -dx -f2):$(cat ${path}/device | cut -dx -f2)"
    printf "%-20s: %s\n" "Driver name" $(basename $(readlink ${path}/driver))
    printf "%-20s: %s\n" "Driver Version" $(cat ${path}/driver/module/version)
    printf "%-20s: %s\n" "PCI Link Speed (max)" "$(cat ${path}/current_link_speed) ($(cat ${path}/max_link_speed))"
    printf "%-20s: %s\n" "PCI Link Width (max)" "$(cat ${path}/current_link_width) ($(cat ${path}/max_link_width))"
    printf "%-20s: %s\n" "NUMA Node" $(cat ${path}/numa_node)
    printf "%-20s: %s\n" "Number of VFs" $(cat ${path}/sriov_numvfs)
    printf "%-20s: %s\n" "Total VFs" $(cat ${path}/sriov_totalvfs)
    if [ -d ${path}/net/* ] ; then
        netdev=$(basename ${path}/net/*)
        netdev_path=${path}/net/${netdev}
        printf "%-20s: %s\n" "Interface" ${netdev}
        printf "%-20s: %s\n" "MAC Address" $(cat ${netdev_path}/address)
        printf "%-20s: %s\n" "State" $(cat ${netdev_path}/operstate)
    fi

    [ $(cat ${path}/sriov_numvfs) -gt 0 ] && show_vfs ${path} ${netdev}
}

function nic_driver_utils.remove_vfs {
    get_pci_addr pci_addr $1
    path="/sys/bus/pci/devices/${pci_addr}"

    [ $(cat ${path}/sriov_numvfs) -gt 0 ] || \
        { echo "No VFs configured on $1" >&2; exit 1; }
    echo 0 | tee ${path}/sriov_numvfs > /dev/null
}

function nic_driver_utils.create_vfs {
    # Creates N VFs on PCI device
    get_pci_addr pci_addr ${1}
    path="/sys/bus/pci/devices/${pci_addr}"

    [ $(cat ${path}/sriov_numvfs) -gt 0 ] && \
        { echo "VFs already configured on $1" >&2; exit 1; }
    [ "0$2" -gt 0 ] || \
        { echo "Please specify number of VFs to create" >&2; exit 1; }

    driver=$(basename $(readlink ${path}/driver))
    if [ "${driver}" != "i40e" ]; then
        echo ${1} | tee ${path}/driver/unbind
        echo ${1} | tee /sys/bus/pci/drivers/i40e/bind
    fi

    echo ${2} | tee ${path}/sriov_numvfs > /dev/null
    [ -d ${path}/net/* ] || \
        { echo "No net device for $1" >&2; exit 1; }
    netdev=$(basename ${path}/net/*)
    netdev_path=${path}/net/${netdev}

    mac_prefix=$(cat ${netdev_path}/address | cut -d: -f1,3,4,5,6 )
    for vf_path in ${path}/virtfn*; do
        vf=$(basename $(readlink ${vf_path}))
        vfid=$(basename ${vf_path//virtfn/})
        mac="${mac_prefix}:$(printf "%02x" ${vfid})"
        sudo ip link set dev ${netdev} vf ${vfid} mac ${mac}
    done

    [ $(cat ${path}/sriov_numvfs) -gt 0 ] && show_vfs ${path} ${netdev}
}

function nic_driver_utils.bind_vfs_vfio_pci {
    # Bind PCI VFs to vfio-pci driver
    get_pci_addr pci_addr ${1}
    path="/sys/bus/pci/devices/${pci_addr}"

    for vf_path in ${path}/virtfn*; do
        vf=$(basename $(readlink ${vf_path}))
        echo ${vf} | tee ${vf_path}/driver/unbind
        echo vfio-pci | tee ${vf_path}/driver_override
        echo ${vf} | tee /sys/bus/pci/drivers/vfio-pci/bind
        echo  | tee ${vf_path}/driver_override
    done
}

case $1 in
    show)
        show $2
        ;;
    create)
        create_vfs $2 $3
        ;;
    remove-all)
        remove_vfs $2
        ;;
    bind)
        bind_vfs_vfio_pci $2
        ;;
    *)
        echo "Please specify command (show, create, remove-all)"
        ;;
esac
