# Copyright (c) 2024 Cisco and/or its affiliates.
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

set -exuo pipefail

# This library defines functions used by multiple entry scripts.
# Deliberately not depending on common.sh to allow standalone usage.
# Keep functions ordered alphabetically, please.

function activate_wrapper () {

    # Acts as wrapper for activate docker topology.
    #
    # Variables read:
    # - ${1} - Node multiplicity of desired testbed.
    # - ${2} - Node flavor string, usually describing the processor.
    # - ${3} - CSIT-SUT-DCR image name and version.

    set -exuo pipefail

    enter_mutex || die
    get_available_interfaces "${1}" "${2}" || die
    bind_dut_interfaces_to_vpp_driver || die
    start_topology_containers "${3}" || die
    bind_interfaces_to_containers || die
    set_env_variables || die
    print_env_variables || die
    exit_mutex || die
}


function bind_dut_interfaces_to_vpp_driver () {

    # Bind DUT network interfaces to the driver that vpp will use
    #
    # Variables read:
    # - DUT1_NETDEVS - List of network devices allocated to DUT1 container.
    # Variables set:
    # - NETDEV - Linux network interface.
    # - DRIVER - Kernel driver to bind the interface to.
    # - KRN_DRIVER - The original kernel driver of the network interface.

    for NETDEV in "${DUT1_NETDEVS[@]}"; do
        get_pci_addr || die
        ethtool -n "${NETDEV}" || echo "ethtool failed"
        get_krn_driver || die
        if [[ ${KRN_DRIVER} == "iavf" ]]; then
            DRIVER="vfio-pci"
            ADDR=${PCI_ADDR}
            bind_interfaces_to_driver || die
        fi
    done
}


function bind_interfaces_to_containers () {

    # Bind linux network interface to container and create symlink for PCI
    # address in container.
    #
    # Variables read:
    # - DCR_UUIDS - Docker Container UUIDs.
    # - DCR_CPIDS - Docker Container PIDs (namespaces).
    # - DUT1_NETDEVS - List of network devices allocated to DUT1 container.
    # - PCI_ADDR - PCI address of network device.
    # - TG_NETDEVS - List of network devices allocated to TG container.
    # Variables set:
    # - NETDEV - Linux network interface.
    # - KRN_DRIVER - Kernel driver of network device.

    set -exuo pipefail

    for PCI_ADDR in "${TG_PCIDEVS[@]}"; do
        get_netdev_name || die
        link_target=$(readlink -f /sys/bus/pci/devices/"${PCI_ADDR}") || {
            die "Reading symlink for PCI address failed!"
        }
        cmd="ln -s ${link_target} /sys/bus/pci/devices/${PCI_ADDR}"

        docker exec "${DCR_UUIDS[tg]}" ${cmd} || {
            die "Linking PCI address in container failed!"
        }

        sudo ip link set ${NETDEV} netns ${DCR_CPIDS[tg]} || {
            die "Moving interface to ${DCR_CPIDS[tg]} namespace failed!"
        }
    done
    for PCI_ADDR in "${DUT1_PCIDEVS[@]}"; do
        link_target=$(readlink -f /sys/bus/pci/devices/"${PCI_ADDR}") || {
            die "Reading symlink for PCI address failed!"
        }
        cmd="ln -s ${link_target} /sys/bus/pci/devices/${PCI_ADDR}"

        docker exec "${DCR_UUIDS[dut1]}" ${cmd} || {
            die "Linking PCI address in container failed!"
        }

        get_krn_driver
        if [[ ${KRN_DRIVER} != "vfio-pci" ]]; then
            get_netdev_name || die
            sudo ip link set ${NETDEV} netns ${DCR_CPIDS[dut1]} || {
                die "Moving interface to ${DCR_CPIDS[dut1]} namespace failed!"
            }
        fi
    done
}


function bind_interfaces_to_driver () {

    # Bind network interface specified by parameter to driver specified by
    # parameter.
    #
    # Variables read:
    # - ADDR - PCI address of network interface.
    # - DRIVER - Kernel driver.

    set -exuo pipefail

    pci_path="/sys/bus/pci/devices/${ADDR}"
    drv_path="/sys/bus/pci/drivers/${DRIVER}"
    if [ -d "${pci_path}/driver" ]; then
        echo ${ADDR} | sudo tee ${pci_path}/driver/unbind > /dev/null || {
            die "Failed to unbind interface ${ADDR}!"
        }
    fi

    echo ${DRIVER} | sudo tee /sys/bus/pci/devices/${ADDR}/driver_override \
        > /dev/null || {
        die "Failed to override driver to ${DRIVER} for ${ADDR}!"
    }

    echo ${ADDR} | sudo tee ${drv_path}/bind > /dev/null || {
        die "Failed to bind interface ${ADDR}!"
    }

    echo | sudo tee /sys/bus/pci/devices/${ADDR}/driver_override > /dev/null \
        || die "Failed to reset driver override for ${ADDR}!"
}


function clean_environment () {

    # Cleanup environment by removing topology containers and shared volumes
    # and binding interfaces back to original driver.
    #
    # Variables read:
    # - DCR_UUIDS - Docker Container UUIDs.
    # - DUT1_PCIDEVS - List of PCI addresses of devices of DUT1 container.
    # - TG_PCIDEVS - List of PCI addresses of devices of TG container.
    # Variables set:
    # - ADDR - PCI address of network interface.
    # - DRIVER - Kernel driver.

    set -exuo pipefail

    # Kill docker containers.
    docker rm --force "${DCR_UUIDS[@]}" || die "Cleanup containers failed!"

    # Check if there are some leftover containers and remove all. Command will
    # not fail in case there are no containers to remove.
    docker rm --force $(docker ps -q --filter name=${DCR_UUIDS[dut1]}) || {
        warn "Failed to remove hanged containers or nothing to remove!"
    }

    # Rebind interfaces back to kernel drivers.
    i=0
    for ADDR in ${TG_PCIDEVS[@]}; do
        DRIVER="${TG_DRIVERS[${i}]}"
        bind_interfaces_to_driver || die
        ((i++))
    done
    i=0
    for ADDR in ${DUT1_PCIDEVS[@]}; do
        DRIVER="${DUT1_DRIVERS[${i}]}"
        bind_interfaces_to_driver || die
        ((i++))
    done
}


function clean_environment_on_exit () {

    # Cleanup environment by removing topology containers and binding
    # interfaces back to original driver only if exit code is not 0.
    # This function acts as workaround as 'set -eu' does not trigger ERR trap.

    set -exuo pipefail

    if [ $? -ne 0 ]; then
        clean_environment || die
    fi
}


function deactivate_wrapper () {

    # Acts as wrapper for deactivate docker topology.
    #
    # Variables read:
    # - ${@} - CSIT environment variables.

    set -exuo pipefail

    enter_mutex || die
    read_env_variables "${@}" || die
    clean_environment || die
    exit_mutex || die
}


function die () {

    # Print the message to standard error end exit with error code specified
    # by the second argument.
    #
    # Duplicate of common.sh function, as this file is also used standalone.
    #
    # Hardcoded values:
    # - The default error message.
    # Arguments:
    # - ${1} - The whole error message, be sure to quote. Optional
    # - ${2} - the code to exit with, default: 1.

    set -x
    set +eu
    warn "${1:-Unspecified run-time error occurred!}"
    exit "${2:-1}"
}


function enter_mutex () {

    # Enter mutual exclusion for protecting execution from starvation and
    # deadlock.

    set -exuo pipefail

    mutex_timeout=3600
    mutex_file="/tmp/mutex_file"

    # Create mutex.
    exec {lock_fd}>${mutex_file} || {
        die "Mutex enter failed!"
    }
    flock --timeout "${mutex_timeout}" "${lock_fd}" || {
        die "Calling flock() failed!"
    }
    # ----------------------
    # Enter mutex succeeded.
    warn "Mutex enter succeeded for PID $$."
}


function exit_mutex () {

    # Exit mutual exclusion.

    set -exuo pipefail

    # ---------------------
    # Remove mutex so we are not blocking others anymore.
    flock -u "${lock_fd}" || {
        die "Mutex destroy failed!"
    }
    warn "Mutex leave succeeded for PID $$."
}


function get_available_interfaces () {

    # Find and get available Virtual functions.
    #
    # Arguments:
    # - ${1} - Nodeness, as set by common.sh get_test_code.
    # - ${2} - Flavor, as set by common.sh get_test_code.
    # Variables set:
    # - DUT1_NETDEVS - List of network devices allocated to DUT1 container.
    # - DUT1_PCIDEVS - List of PCI addresses allocated to DUT1 container.
    # - DUT1_NETMACS - List of MAC addresses allocated to DUT1 container.
    # - DUT1_DRIVERS - List of interface drivers to DUT1 container.
    # - DUT1_VLANS - List of interface vlans to TG container.
    # - DUT1_MODEL - List of interface models to TG container.
    # - TG_NETDEVS - List of network devices allocated to TG container.
    # - TG_PCIDEVS - List of PCI addresses allocated to TG container.
    # - TG_NETMACS - List of MAC addresses allocated to TG container.
    # - TG_DRIVERS - List of interface drivers to TG container.
    # - TG_VLANS - List of interface vlans to TG container.
    # - TG_MODEL - List of interface models to TG container.

    set -exuo pipefail

    # Following code is specifying VFs ID based on nodeness and flavor.
    # As there is great variability in hardware configuration outside LF,
    # from bootstrap architecture point of view these are considered as flavors.
    # Anyone can override flavor for its own machine and add condition here.
    # See http://pci-ids.ucw.cz/v2.2/pci.ids for more info.
    case_text="${1}_${2}"
    case "${case_text}" in
        "1n_skx")
            # Add Intel Corporation XL710/X710 Virtual Function to the
            # whitelist.
            # Add Intel Corporation E810 Virtual Function to the
            # whitelist.
            pci_id="0x154c\|0x1889"
            tg_netdev=(ens1 enp134)
            dut1_netdev=(ens5 enp175)
            ports_per_nic=2
            ;;
       "1n_alt")
            # Add Intel Corporation XL710/X710 Virtual Function to the
            # whitelist.
            # Add MT2892 Family [ConnectX-6 Dx] Virtual Function to the
            # whitelist.
            pci_id="0x154c\|0x101e"
            tg_netdev=(enp1s0f0 enp1s0f1 enP1p1s0f0)
            dut1_netdev=(enP3p2s0f0 enP3p2s0f1 enP1p1s0f1)
            ports_per_nic=2
            ;;
        "1n_spr")
            # Add Intel Corporation XL710/X710 Virtual Function to the
            # whitelist.
            # Add Intel Corporation E810 Virtual Function to the
            # whitelist.
            pci_id="0x154c\|0x1889"
            tg_netdev=(enp42s0 ens5)
            dut1_netdev=(enp61s0 ens7)
            ports_per_nic=2
            ;;
       "1n_vbox")
            # Add Intel Corporation 82545EM Gigabit Ethernet Controller to the
            # whitelist.
            pci_id="0x100f"
            tg_netdev=(enp0s8 enp0s9)
            dut1_netdev=(enp0s16 enp0s17)
            ports_per_nic=1
            ;;
        *)
            die "Unknown specification: ${case_text}!"
    esac

    # TG side of connections.
    TG_NETDEVS=()
    TG_PCIDEVS=()
    TG_NETMACS=()
    TG_DRIVERS=()
    TG_VLANS=()
    TG_MODEL=()
    # DUT1 side of connections.
    DUT1_NETDEVS=()
    DUT1_PCIDEVS=()
    DUT1_NETMACS=()
    DUT1_DRIVERS=()
    DUT1_VLANS=()
    DUT1_MODEL=()

    # Find the first ${device_count} number of available TG Linux network
    # VF device names. Only allowed VF PCI IDs are filtered.
    for netdev in ${tg_netdev[@]}
    do
        ports=0
        for netdev_path in $(grep -l "${pci_id}" \
                             /sys/class/net/${netdev}*/device/device \
                             2> /dev/null)
        do
            if [[ ${ports} -lt ${ports_per_nic} ]]; then
                tg_netdev_name=$(dirname ${netdev_path})
                tg_netdev_name=$(dirname ${tg_netdev_name})
                TG_NETDEVS+=($(basename ${tg_netdev_name}))
                ((ports++))
            else
                break
            fi
        done
        ports_per_device=$((${ports_per_nic}*${#tg_netdev[@]}))
        if [[ ${#TG_NETDEVS[@]} -eq ${ports_per_device} ]]; then
            break
        fi
    done

    i=0
    for netdev in "${TG_NETDEVS[@]}"; do
        # Find the index of selected tg netdev among tg_netdevs
        # e.g. enp8s5f7 is a vf of netdev enp8s5 with index 11
        # and the corresponding dut1 netdev is enp133s13.
        while [[ "${netdev}" != "${tg_netdev[$i]}"* ]]; do
            ((i++))
        done
        # Rename tg netdev to dut1 netdev
        # e.g. enp8s5f7 -> enp133s13f7
        DUT1_NETDEVS+=(${netdev/${tg_netdev[$i]}/${dut1_netdev[$i]}})
        # Don't need to reset i, all netdevs are sorted.
    done

    for NETDEV in "${TG_NETDEVS[@]}"; do
        get_pci_addr
        get_mac_addr
        get_krn_driver
        get_vlan_filter
        get_csit_model
        TG_PCIDEVS+=(${PCI_ADDR})
        TG_NETMACS+=(${MAC_ADDR})
        TG_DRIVERS+=(${KRN_DRIVER})
        TG_VLANS+=(${VLAN_ID})
        TG_MODELS+=(${MODEL})
    done
    for NETDEV in "${DUT1_NETDEVS[@]}"; do
        get_pci_addr
        get_mac_addr
        get_krn_driver
        get_vlan_filter
        get_csit_model
        DUT1_PCIDEVS+=(${PCI_ADDR})
        DUT1_NETMACS+=(${MAC_ADDR})
        DUT1_DRIVERS+=(${KRN_DRIVER})
        DUT1_VLANS+=(${VLAN_ID})
        DUT1_MODELS+=(${MODEL})
    done

    # We need at least two interfaces for TG/DUT1 for building topology.
    if [ "${#TG_NETDEVS[@]}" -lt 2 ] || [ "${#DUT1_NETDEVS[@]}" -lt 2 ]; then
        die "Not enough linux network interfaces found!"
    fi
}


function get_krn_driver () {

    # Get kernel driver from linux network device name.
    #
    # Variables read:
    # - PCI_ADDR - PCI address of network device.
    # Variables set:
    # - KRN_DRIVER - Kernel driver of network device.

    set -exuo pipefail

    pci_path="/sys/bus/pci/devices/${PCI_ADDR}"
    KRN_DRIVER="$(basename $(readlink -f ${pci_path}/driver))" || {
        die "Failed to get kernel driver of PCI interface!"
    }
}


function get_mac_addr () {

    # Get MAC address from linux network device name.
    #
    # Variables read:
    # - NETDEV - Linux network device name.
    # Variables set:
    # - MAC_ADDR - MAC address of network device.

    set -exuo pipefail

    if [ -d /sys/class/net/${NETDEV}/device ]; then
        MAC_ADDR="$(</sys/class/net/${NETDEV}/address)" || {
            die "Failed to get MAC address of linux network interface!"
        }
    fi
}


function get_netdev_name () {

    # Get Linux network device name.
    #
    # Variables read:
    # - PCI_ADDR - PCI address of the device.
    # Variables set:
    # - NETDEV - Linux network device name.

    set -exuo pipefail

    if [ -d /sys/bus/pci/devices/${PCI_ADDR}/net ]; then
        NETDEV="$(basename /sys/bus/pci/devices/${PCI_ADDR}/net/*)" || {
            die "Failed to get Linux interface name of ${PCI_ADDR}"
        }
    fi
}


function get_csit_model () {

    # Get CSIT model name from linux network device name.
    #
    # Variables read:
    # - NETDEV - Linux network device name.
    # Variables set:
    # - MODEL - CSIT model name of network device.

    set -exuo pipefail

    if [ -d /sys/class/net/${NETDEV}/device ]; then
        ID="$(</sys/class/net/${NETDEV}/device/device)" || {
            die "Failed to get device id of linux network interface!"
        }
        case "${ID}" in
            "0x1592"|"0x1889")
                MODEL="Intel-E810CQ"
                ;;
            "0x1572"|"0x154c")
                MODEL="Intel-X710"
                ;;
            "0x101e")
                MODEL="Mellanox-CX6DX"
                ;;
            *)
                MODEL="virtual"
        esac
    fi
}


function get_pci_addr () {

    # Get PCI address in <domain>:<bus:<device>.<func> format from linux network
    # device name.
    #
    # Variables read:
    # - NETDEV - Linux network device name.
    # Variables set:
    # - PCI_ADDR - PCI address of network device.

    set -exuo pipefail

    if [ -d /sys/class/net/${NETDEV}/device ]; then
        PCI_ADDR=$(basename $(readlink /sys/class/net/${NETDEV}/device)) || {
            die "Failed to get PCI address of linux network interface!"
        }
        if [ ! -d /sys/bus/pci/devices/${PCI_ADDR} ]; then
            die "PCI device ${PCI_ADDR} doesn't exist!"
        fi
    else
        die "Can't get device info of interface ${NETDEV}!"
    fi
}


function get_vfio_group () {

    # Get the VFIO group of a pci device.
    #
    # Variables read:
    # - PCI_ADDR - PCI address of a device.
    # Variables set:
    # - VFIO_GROUP - The VFIO group of the PCI device.

    if [[ -d /sys/bus/pci/devices/${PCI_ADDR}/iommu_group ]]; then
        VFIO_GROUP="$(basename\
            $(readlink /sys/bus/pci/devices/${PCI_ADDR}/iommu_group)\
        )" || {
            die "PCI device ${PCI_ADDR} does not have an iommu group!"
        }
    fi
}

function get_vlan_filter () {

    # Get VLAN stripping filter from PF searched by mac adress.
    #
    # Variables read:
    # - MAC_ADDR - MAC address of VF.
    # Variables set:
    # - VLAN_ID - VLAN ids.

    set -exuo pipefail

    # Sed regular expression pattern.
    exp="s/^.*vlan ([[:digit:]]+).*$/\1/"
    VLAN_ID=$(ip link | grep vlan | grep ${MAC_ADDR} | sed -re "${exp}") || true
    VLAN_ID="${VLAN_ID:-0}"
}


function installed () {

    # Check if the given utility is installed. Fail if not installed.
    #
    # Duplicate of common.sh function, as this file is also used standalone.
    #
    # Arguments:
    # - ${1} - Utility to check.
    # Returns:
    # - 0 - If command is installed.
    # - 1 - If command is not installed.

    set -exuo pipefail

    command -v "${1}"
}


function parse_env_variables () {

    # Parse environment variables.
    #
    # Variables read, set or exported: Multiple,
    # see the code for the current list.

    set -exuo pipefail

    IFS=@ read -a TG_NETMACS <<< "${CSIT_TG_INTERFACES_PORT_MAC}"
    IFS=@ read -a TG_PCIDEVS <<< "${CSIT_TG_INTERFACES_PORT_PCI}"
    IFS=@ read -a TG_DRIVERS <<< "${CSIT_TG_INTERFACES_PORT_DRV}"
    IFS=@ read -a TG_VLANS <<< "${CSIT_TG_INTERFACES_PORT_VLAN}"
    IFS=@ read -a TG_MODELS <<< "${CSIT_TG_INTERFACES_PORT_MODEL}"
    IFS=@ read -a DUT1_NETMACS <<< "${CSIT_DUT1_INTERFACES_PORT_MAC}"
    IFS=@ read -a DUT1_PCIDEVS <<< "${CSIT_DUT1_INTERFACES_PORT_PCI}"
    IFS=@ read -a DUT1_DRIVERS <<< "${CSIT_DUT1_INTERFACES_PORT_DRV}"
    IFS=@ read -a DUT1_VLANS <<< "${CSIT_DUT1_INTERFACES_PORT_VLAN}"
    IFS=@ read -a DUT1_MODELS <<< "${CSIT_DUT1_INTERFACES_PORT_MODEL}"

    for port in $(seq "${#TG_NETMACS[*]}"); do
        CSIT_TG_INTERFACES+=$(cat << EOF
        port$((port-1)):
            mac_address: "${TG_NETMACS[$((port-1))]}"
            pci_address: "${TG_PCIDEVS[$((port-1))]}"
            link: "link$((port-1))"
            model: ${TG_MODELS[$((port-1))]}
            driver: "${TG_DRIVERS[$((port-1))]}"
            vlan: ${TG_VLANS[$((port-1))]}
EOF
    )
        CSIT_TG_INTERFACES+=$'\n'
    done
    for port in $(seq "${#DUT1_NETMACS[*]}"); do
        CSIT_DUT1_INTERFACES+=$(cat << EOF
        port$((port-1)):
            mac_address: "${DUT1_NETMACS[$((port-1))]}"
            pci_address: "${DUT1_PCIDEVS[$((port-1))]}"
            link: "link$((port-1))"
            model: ${DUT1_MODELS[$((port-1))]}
            driver: "${DUT1_DRIVERS[$((port-1))]}"
            vlan: ${DUT1_VLANS[$((port-1))]}
EOF
    )
        CSIT_DUT1_INTERFACES+=$'\n'
    done
}


function print_env_variables () {

    # Get environment variables prefixed by CSIT_.

    set -exuo pipefail

    env | grep CSIT_ || true
}


function read_env_variables () {

    # Read environment variables from parameters.
    #
    # Arguments:
    # - ${@} - Variables passed as an argument.
    # Variables read, set or exported: Multiple,
    # see the code for the current list.

    set -exuo pipefail

    for param in "$@"; do
        export "${param}"
    done
    declare -gA DCR_UUIDS
    DCR_UUIDS+=([tg]="${CSIT_TG_UUID}")
    DCR_UUIDS+=([dut1]="${CSIT_DUT1_UUID}")

    IFS=@ read -a TG_NETMACS <<< "${CSIT_TG_INTERFACES_PORT_MAC}"
    IFS=@ read -a TG_PCIDEVS <<< "${CSIT_TG_INTERFACES_PORT_PCI}"
    IFS=@ read -a TG_DRIVERS <<< "${CSIT_TG_INTERFACES_PORT_DRV}"
    IFS=@ read -a TG_VLANS <<< "${CSIT_TG_INTERFACES_PORT_VLAN}"
    IFS=@ read -a TG_MODELS <<< "${CSIT_TG_INTERFACES_PORT_MODEL}"
    IFS=@ read -a DUT1_NETMACS <<< "${CSIT_DUT1_INTERFACES_PORT_MAC}"
    IFS=@ read -a DUT1_PCIDEVS <<< "${CSIT_DUT1_INTERFACES_PORT_PCI}"
    IFS=@ read -a DUT1_DRIVERS <<< "${CSIT_DUT1_INTERFACES_PORT_DRV}"
    IFS=@ read -a DUT1_VLANS <<< "${CSIT_DUT1_INTERFACES_PORT_VLAN}"
    IFS=@ read -a DUT1_MODELS <<< "${CSIT_DUT1_INTERFACES_PORT_MODEL}"
}


function set_env_variables () {

    # Set environment variables.
    #
    # Variables read:
    # - DCR_UUIDS - Docker Container UUIDs.
    # - DCR_PORTS - Docker Container's SSH ports.
    # - DUT1_NETDEVS - List of network devices allocated to DUT1 container.
    # - DUT1_PCIDEVS - List of PCI addresses allocated to DUT1 container.
    # - DUT1_NETMACS - List of MAC addresses allocated to DUT1 container.
    # - DUT1_DRIVERS - List of interface drivers to DUT1 container.
    # - DUT1_VLANS - List of interface vlans to TG container.
    # - DUT1_MODEL - List of interface models to TG container.
    # - TG_NETDEVS - List of network devices allocated to TG container.
    # - TG_PCIDEVS - List of PCI addresses allocated to TG container.
    # - TG_NETMACS - List of MAC addresses allocated to TG container.
    # - TG_DRIVERS - List of interface drivers to TG container.
    # - TG_VLANS - List of interface vlans to TG container.
    # - TG_MODEL - List of interface models to TG container.

    set -exuo pipefail

    set -a
    CSIT_TG_HOST="$(hostname --all-ip-addresses | awk '{print $1}')" || {
        die "Reading hostname IP address failed!"
    }
    CSIT_TG_PORT="${DCR_PORTS[tg]##*:}"
    CSIT_TG_UUID="${DCR_UUIDS[tg]}"
    CSIT_TG_ARCH="$(uname -i)" || {
        die "Reading machine architecture failed!"
    }
    CSIT_DUT1_HOST="$(hostname --all-ip-addresses | awk '{print $1}')" || {
        die "Reading hostname IP address failed!"
    }
    CSIT_DUT1_PORT="${DCR_PORTS[dut1]##*:}"
    CSIT_DUT1_UUID="${DCR_UUIDS[dut1]}"
    CSIT_DUT1_ARCH="$(uname -i)" || {
        die "Reading machine architecture failed!"
    }
    OIFS="$IFS" IFS=@
    set -a
    CSIT_TG_INTERFACES_PORT_MAC="${TG_NETMACS[*]}"
    CSIT_TG_INTERFACES_PORT_PCI="${TG_PCIDEVS[*]}"
    CSIT_TG_INTERFACES_PORT_DRV="${TG_DRIVERS[*]}"
    CSIT_TG_INTERFACES_PORT_VLAN="${TG_VLANS[*]}"
    CSIT_TG_INTERFACES_PORT_MODEL="${TG_MODELS[*]}"
    CSIT_DUT1_INTERFACES_PORT_MAC="${DUT1_NETMACS[*]}"
    CSIT_DUT1_INTERFACES_PORT_PCI="${DUT1_PCIDEVS[*]}"
    CSIT_DUT1_INTERFACES_PORT_DRV="${DUT1_DRIVERS[*]}"
    CSIT_DUT1_INTERFACES_PORT_VLAN="${DUT1_VLANS[*]}"
    CSIT_DUT1_INTERFACES_PORT_MODEL="${DUT1_MODELS[*]}"
    set +a
    IFS="$OIFS"
}


function start_topology_containers () {

    # Starts csit-sut-dcr docker containers for TG/DUT1.
    #
    # Variables read:
    # - CSIT_DIR - Path to existing root of local CSIT git repository.
    # Variables set:
    # - DCR_UUIDS - Docker Container UUIDs.
    # - DCR_PORTS - Docker Container SSH TCP ports.
    # - DCR_CPIDS - Docker Container PIDs (namespaces).

    set -exuo pipefail

    if ! installed docker; then
        die "Docker not present. Please install before continue!"
    fi

    # If the IMAGE is not already loaded then docker run will pull the IMAGE,
    # and all image dependencies, before it starts the container.
    dcr_image="${1}"
    # Run the container in the background and print the new container ID.
    dcr_stc_params="--detach=true "
    # Give extended privileges to this container. A "privileged" container is
    # given access to all devices and able to run nested containers.
    dcr_stc_params+="--privileged "
    # Publish all exposed ports to random ports on the host interfaces.
    dcr_stc_params+="--publish-all "
    # Automatically remove the container when it exits.
    dcr_stc_params+="--rm "
    # Size of /dev/shm.
    dcr_stc_params+="--shm-size 2G "
    # Override access to PCI bus by attaching a filesystem mount to the
    # container.
    dcr_stc_params+="--mount type=tmpfs,destination=/sys/bus/pci/devices "
    # Mount vfio devices to be able to use VFs inside the container.
    vfio_bound="false"
    for PCI_ADDR in ${DUT1_PCIDEVS[@]}; do
        get_krn_driver
        if [[ ${KRN_DRIVER} == "vfio-pci" ]]; then
            get_vfio_group
            dcr_stc_params+="--device /dev/vfio/${VFIO_GROUP} "
            vfio_bound="true"
        fi
    done
    if ! ${vfio_bound}; then
        dcr_stc_params+="--volume /dev/vfio:/dev/vfio "
    fi
    # Disable manipulation with hugepages by VPP.
    dcr_stc_params+="--volume /dev/null:/etc/sysctl.d/80-vpp.conf "
    # Mount docker.sock to be able to use docker deamon of the host.
    dcr_stc_params+="--volume /var/run/docker.sock:/var/run/docker.sock "
    # Mount /opt/boot/ where VM kernel and initrd are located.
    dcr_stc_params+="--volume /opt/boot/:/opt/boot/ "
    # Mount host hugepages for VMs.
    dcr_stc_params+="--volume /dev/hugepages/:/dev/hugepages/ "
    # Disable IPv6.
    dcr_stc_params+="--sysctl net.ipv6.conf.all.disable_ipv6=1 "
    dcr_stc_params+="--sysctl net.ipv6.conf.default.disable_ipv6=1 "

    # Docker Container UUIDs.
    declare -gA DCR_UUIDS
    # Docker Container SSH TCP ports.
    declare -gA DCR_PORTS
    # Docker Container PIDs (namespaces).
    declare -gA DCR_CPIDS

    # Run TG and DUT1. As initial version we do support only 2-node.
    params=(${dcr_stc_params} --name csit-tg-$(uuidgen) ${dcr_image})
    DCR_UUIDS+=([tg]=$(docker run "${params[@]}")) || {
        die "Failed to start TG docker container!"
    }
    params=(${dcr_stc_params} --name csit-dut1-$(uuidgen) ${dcr_image})
    DCR_UUIDS+=([dut1]=$(docker run "${params[@]}")) || {
        die "Failed to start DUT1 docker container!"
    }

    trap 'clean_environment_on_exit' EXIT || {
        die "Trap attempt failed, please cleanup manually. Aborting!"
    }

    # Get Containers TCP ports.
    params=(${DCR_UUIDS[tg]})
    DCR_PORTS+=([tg]=$(docker port "${params[@]}")) || {
        die "Failed to get port of TG docker container!"
    }
    params=(${DCR_UUIDS[dut1]})
    DCR_PORTS+=([dut1]=$(docker port "${params[@]}")) || {
        die "Failed to get port of DUT1 docker container!"
    }

    # Get Containers PIDs.
    params=(--format="{{ .State.Pid }}" ${DCR_UUIDS[tg]})
    DCR_CPIDS+=([tg]=$(docker inspect "${params[@]}")) || {
        die "Failed to get PID of TG docker container!"
    }
    params=(--format="{{ .State.Pid }}" ${DCR_UUIDS[dut1]})
    DCR_CPIDS+=([dut1]=$(docker inspect "${params[@]}")) || {
        die "Failed to get PID of DUT1 docker container!"
    }
}

function warn () {
    # Print the message to standard error.
    #
    # Duplicate of common.sh function, as this file is also used standalone.
    #
    # Arguments:
    # - ${@} - The text of the message.

    set -exuo pipefail

    echo "$@" >&2
}
