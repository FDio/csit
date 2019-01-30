# Copyright (c) 2019 Cisco and/or its affiliates.
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
    start_topology_containers "${3}" || die
    bind_interfaces_to_containers || die
    set_env_variables || die
    print_env_variables || die
    exit_mutex || die
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

    set -exuo pipefail

    for NETDEV in "${TG_NETDEVS[@]}"; do
        get_pci_addr || die
        link_target=$(readlink -f /sys/bus/pci/devices/"${PCI_ADDR}") || {
            die "Reading symlink for PCI address failed!"
        }
        cmd="ln -s ${link_target} /sys/bus/pci/devices/${PCI_ADDR}"

        sudo ip link set ${NETDEV} netns ${DCR_CPIDS[tg]} || {
            die "Moving interface to ${DCR_CPIDS[tg]} namespace failed!"
        }
        docker exec "${DCR_UUIDS[tg]}" ${cmd} || {
            die "Linking PCI address in container failed!"
        }
    done
    for NETDEV in "${DUT1_NETDEVS[@]}"; do
        get_pci_addr || die
        link_target=$(readlink -f /sys/bus/pci/devices/"${PCI_ADDR}") || {
            die "Reading symlink for PCI address failed!"
        }
        cmd="ln -s ${link_target} /sys/bus/pci/devices/${PCI_ADDR}"

        sudo ip link set ${NETDEV} netns ${DCR_CPIDS[dut1]} || {
            die "Moving interface to ${DCR_CPIDS[dut1]} namespace failed!"
        }
        docker exec "${DCR_UUIDS[dut1]}" ${cmd} ||  {
            die "Linking PCI address in container failed!"
        }
    done
}


function bind_interfaces_to_driver () {
    # Bind network interface specified by parameter to driver specified by
    # parameter.
    #
    # Variables read:
    # - ADDR - PCI address of network interface.
    # - DRIVER - Kernel driver.

    pci_path="/sys/bus/pci/devices/${ADDR}"
    drv_path="/sys/bus/pci/drivers/${DRIVER}"
    vd="$(cat ${pci_path}/vendor ${pci_path}/device)" || {
        die "Failed to retrieve interface details!"
    }
    set +e
    echo ${vd} | sudo tee ${drv_path}/new_id
    set -e
    echo ${ADDR} | sudo tee ${pci_path}/driver/unbind || {
        die "Failed to unbind interface ${ADDR}!"
    }
    echo ${ADDR} | sudo tee ${drv_path}/bind || {
        die "Failed to bind interface ${ADDR}!"
    }
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

    # Check if some container is using volume and remove all the hanged
    # containers before removing volume. Command will not fail in case there
    # are no containers to remove.
    docker rm --force $(docker ps -q --filter volume=${DCR_VOLUMES[dut1]}) || {
        warn "Failed to remove hanged containers or nothing to remove!"
    }

    # Remove DUT1 volume.
    docker volume rm --force "${DCR_VOLUMES[dut1]}" || {
        die "Failed to remove DUT1 volume!"
    }

    # Rebind interfaces back to kernel drivers.
    for ADDR in ${TG_PCIDEVS[@]}; do
        DRIVER="${TG_DRIVERS[0]}"
        bind_interfaces_to_driver || die
    done
    for ADDR in ${DUT1_PCIDEVS[@]}; do
        DRIVER="${DUT1_DRIVERS[0]}"
        bind_interfaces_to_driver || die
    done
}


function clean_environment_on_exit () {
    # Cleanup environment by removing topology containers and binding
    # interfaces back to original driver only if exit code is not 0.
    # This function acts as workaround as 'set -eu' does not trigger ERR trap.

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
    # - ${1} - Node flavor string, usually describing the processor and node
    # multiplicity of desired testbed, separated by underscore.
    # Variables set:
    # - DUT1_NETDEVS - List of network devices allocated to DUT1 container.
    # - DUT1_PCIDEVS - List of PCI addresses allocated to DUT1 container.
    # - DUT1_NETMACS - List of MAC addresses allocated to DUT1 container.
    # - DUT1_DRIVERS - List of interface drivers to DUT1 container.
    # - TG_NETDEVS - List of network devices allocated to TG container.
    # - TG_PCIDEVS - List of PCI addresses allocated to TG container.
    # - TG_NETMACS - List of MAC addresses allocated to TG container.
    # - TG_DRIVERS - List of interface drivers to TG container.

    set -exuo pipefail

    # Following code is specifing VFs ID based on nodeness and flavor.
    # As there is great variability in hardware configuration outside LF,
    # from bootstrap architecure point of view these are considered as flavors.
    # Anyone can override flavor for its own machine and add condition here.
    # See http://pci-ids.ucw.cz/v2.2/pci.ids for more info.
    case_text="${1}_${2}"
    case "${case_text}" in
        "1n_skx")
            # Add Intel Corporation XL710/X710 Virtual Function to the
            # whitelist.
            pci_id="0x154c"
            tg_netdev=(enp24)
            dut1_netdev=(enp59)
            ;;
        "1n_vbox")
            # Add Intel Corporation 82545EM Gigabit Ethernet Controller to the
            # whitelist.
            pci_id="0x100f"
            tg_netdev=(eth1 eth2)
            dut1_netdev=(eth3 eth4)
            ;;
        *)
            die "Unknown specification: ${case_text}!"
    esac

    net_path="/sys/bus/pci/devices/*/net/*"

    # TG side of connections.
    TG_NETDEVS=()
    TG_PCIDEVS=()
    TG_NETMACS=()
    TG_DRIVERS=()
    # DUT1 side of connections.
    DUT1_NETDEVS=()
    DUT1_PCIDEVS=()
    DUT1_NETMACS=()
    DUT1_DRIVERS=()

    # Following code is filtering available VFs represented by network device
    # name. Only allowed VFs PCI IDs are used.
    for netdev in \
        $(find ${net_path} -type d -name . -o -prune -exec basename '{}' ';');
    do
        if grep -q "${pci_id}" "/sys/class/net/${netdev}/device/device"; then
            # We will filter to TG/DUT1 side of connection (this can be in
            # future overriden by more advanced conditions for mapping).
            for sub in ${tg_netdev[@]}; do
                if [[ "${netdev#*$sub}" != "${netdev}" ]]; then
                    tg_side+=(${netdev})
                fi
            done
            for sub in ${dut1_netdev[@]}; do
                if [[ "${netdev#*$sub}" != "${netdev}" ]]; then
                    dut1_side+=(${netdev})
                fi
            done
        fi
    done

    for netdev in "${tg_side[@]::2}"; do
        TG_NETDEVS+=(${netdev})
    done
    for netdev in "${dut1_side[@]::2}"; do
        DUT1_NETDEVS+=(${netdev})
    done

    for NETDEV in "${TG_NETDEVS[@]}"; do
        get_pci_addr
        get_mac_addr
        get_krn_driver
        TG_PCIDEVS+=(${PCI_ADDR})
        TG_NETMACS+=(${MAC_ADDR})
        TG_DRIVERS+=(${KRN_DRIVER})
    done
    for NETDEV in "${DUT1_NETDEVS[@]}"; do
        get_pci_addr
        get_mac_addr
        get_krn_driver
        DUT1_PCIDEVS+=(${PCI_ADDR})
        DUT1_NETMACS+=(${MAC_ADDR})
        DUT1_DRIVERS+=(${KRN_DRIVER})
    done

    # We need at least two interfaces for TG/DUT1 for building topology.
    if [ "${#TG_NETDEVS[@]}" -ne 2 ] || [ "${#DUT1_NETDEVS[@]}" -ne 2 ]; then
        die "Not enough linux network interfaces found!"
    fi
    if [ "${#TG_PCIDEVS[@]}" -ne 2 ] || [ "${#DUT1_PCIDEVS[@]}" -ne 2 ]; then
        die "Not enough pci interfaces found!"
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
    fi
    if [ ! -d /sys/bus/pci/devices/${PCI_ADDR} ]; then
        die "PCI device ${NETDEV} doesn't exist!"
    fi
}


function installed () {

    set -exuo pipefail

    # Check if the given utility is installed. Fail if not installed.
    #
    # Arguments:
    # - ${1} - Utility to check.
    # Returns:
    # - 0 - If command is installed.
    # - 1 - If command is not installed.

    command -v "${1}"
}


function print_env_variables () {
    # Get environment variables prefixed by CSIT_.

    set -exuo pipefail

    env | grep CSIT_
}


function read_env_variables () {
    # Read environment variables from parameters.
    #
    # Arguments:
    # - ${@} - Variables passed as an argument.

    set -exuo pipefail

    for param in "$@"; do
        export "${param}"
    done
    declare -gA DCR_UUIDS
    declare -gA DCR_VOLUMES
    DCR_UUIDS+=([tg]="${CSIT_TG_UUID}")
    DCR_UUIDS+=([dut1]="${CSIT_DUT1_UUID}")
    DCR_VOLUMES+=([dut1]="${CSIT_DUT1_VOL}")
    TG_PCIDEVS=("${CSIT_TG_INTERFACES_PORT1_PCI}")
    TG_DRIVERS=("${CSIT_TG_INTERFACES_PORT1_DRV}")
    TG_PCIDEVS+=("${CSIT_TG_INTERFACES_PORT2_PCI}")
    TG_DRIVERS+=("${CSIT_TG_INTERFACES_PORT2_DRV}")
    DUT1_PCIDEVS=("${CSIT_DUT1_INTERFACES_PORT1_PCI}")
    DUT1_DRIVERS=("${CSIT_DUT1_INTERFACES_PORT1_DRV}")
    DUT1_PCIDEVS+=("${CSIT_DUT1_INTERFACES_PORT2_PCI}")
    DUT1_DRIVERS+=("${CSIT_DUT1_INTERFACES_PORT2_DRV}")
}


function set_env_variables () {
    # Set environment variables.
    #
    # Variables read:
    # - DCR_UUIDS - Docker Container UUIDs.
    # - DCR_PORTS - Docker Container's SSH ports.
    # - DUT1_NETMACS - List of network devices MAC addresses of DUT1 container.
    # - DUT1_PCIDEVS - List of PCI addresses of devices of DUT1 container.
    # - DUT1_DRIVERS - List of interface drivers to DUT1 container.
    # - TG_NETMACS - List of network devices MAC addresses of TG container.
    # - TG_PCIDEVS - List of PCI addresses of devices of TG container.
    # - TG_DRIVERS - List of interface drivers to TG container.

    set -exuo pipefail

    set -a
    CSIT_TG_HOST="$(hostname --all-ip-addresses | awk '{print $1}')" || {
        die "Reading hostname IP address failed!"
    }
    CSIT_TG_PORT="${DCR_PORTS[tg]#*:}"
    CSIT_TG_UUID="${DCR_UUIDS[tg]}"
    CSIT_TG_ARCH="$(uname -i)" || {
        die "Reading machine architecture failed!"
    }
    CSIT_DUT1_HOST="$(hostname --all-ip-addresses | awk '{print $1}')" || {
        die "Reading hostname IP address failed!"
    }
    CSIT_DUT1_PORT="${DCR_PORTS[dut1]#*:}"
    CSIT_DUT1_UUID="${DCR_UUIDS[dut1]}"
    CSIT_DUT1_ARCH="$(uname -i)" || {
        die "Reading machine architecture failed!"
    }
    CSIT_DUT1_VOL="${DCR_VOLUMES[dut1]}"
    CSIT_TG_INTERFACES_PORT1_MAC="${TG_NETMACS[0]}"
    CSIT_TG_INTERFACES_PORT1_PCI="${TG_PCIDEVS[0]}"
    CSIT_TG_INTERFACES_PORT1_DRV="${TG_DRIVERS[0]}"
    CSIT_TG_INTERFACES_PORT2_MAC="${TG_NETMACS[1]}"
    CSIT_TG_INTERFACES_PORT2_PCI="${TG_PCIDEVS[1]}"
    CSIT_TG_INTERFACES_PORT2_DRV="${TG_DRIVERS[1]}"
    CSIT_DUT1_INTERFACES_PORT1_MAC="${DUT1_NETMACS[0]}"
    CSIT_DUT1_INTERFACES_PORT1_PCI="${DUT1_PCIDEVS[0]}"
    CSIT_DUT1_INTERFACES_PORT1_DRV="${DUT1_DRIVERS[0]}"
    CSIT_DUT1_INTERFACES_PORT2_MAC="${DUT1_NETMACS[1]}"
    CSIT_DUT1_INTERFACES_PORT2_PCI="${DUT1_PCIDEVS[1]}"
    CSIT_DUT1_INTERFACES_PORT2_DRV="${DUT1_DRIVERS[1]}"
    set +a
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
    dcr_stc_params+="--shm-size 512M "
    # Override access to PCI bus by attaching a filesystem mount to the
    # container.
    dcr_stc_params+="--mount type=tmpfs,destination=/sys/bus/pci/devices "
    # Mount vfio to be able to bind to see binded interfaces. We cannot use
    # --device=/dev/vfio as this does not see newly binded interfaces.
    dcr_stc_params+="--volume /dev/vfio:/dev/vfio "
    # Mount nested_vm image to be able to run VM tests.
    dcr_stc_params+="--volume /var/lib/vm/vhost-nested.img:/var/lib/vm/vhost-nested.img "
    # Mount docker.sock to be able to use docker deamon of the host.
    dcr_stc_params+="--volume /var/run/docker.sock:/var/run/docker.sock "

    # Docker Container UUIDs.
    declare -gA DCR_UUIDS
    # Docker Container SSH TCP ports.
    declare -gA DCR_PORTS
    # Docker Container PIDs (namespaces).
    declare -gA DCR_CPIDS
    # Docker Container volumes with no relationship to the host.
    declare -gA DCR_VOLUMES

    # Create DUT1 /tmp volume to be able to install VPP in "nested" container.
    params=(--name DUT1_VOL_$(uuidgen))
    DCR_VOLUMES+=([dut1]="$(docker volume create "${params[@]}")") || {
        die "Failed to create DUT1 /tmp volume!"
    }

    # Mount DUT1_VOL as /tmp directory on DUT1 container
    dcr_stc_params_dut1="--volume ${DCR_VOLUMES[dut1]}:/tmp "

    # Run TG and DUT1. As initial version we do support only 2-node.
    params=(${dcr_stc_params} --name csit-tg-$(uuidgen) ${dcr_image})
    DCR_UUIDS+=([tg]="$(docker run "${params[@]}")") || {
        die "Failed to start TG docker container!"
    }
    params=(${dcr_stc_params} ${dcr_stc_params_dut1}
            --name csit-dut1-$(uuidgen) ${dcr_image})
    DCR_UUIDS+=([dut1]="$(docker run "${params[@]}")") || {
        die "Failed to start DUT1 docker container!"
    }

    trap 'clean_environment_on_exit' EXIT || {
        die "Trap attempt failed, please cleanup manually. Aborting!"
    }

    # Get Containers TCP ports.
    params=(${DCR_UUIDS[tg]})
    DCR_PORTS+=([tg]="$(docker port "${params[@]}")") || {
        die "Failed to get port of TG docker container!"
    }
    params=(${DCR_UUIDS[dut1]})
    DCR_PORTS+=([dut1]="$(docker port "${params[@]}")") || {
        die "Failed to get port of DUT1 docker container!"
    }

    # Get Containers PIDs.
    params=(--format="{{ .State.Pid }}" ${DCR_UUIDS[tg]})
    DCR_CPIDS+=([tg]="$(docker inspect "${params[@]}")") || {
        die "Failed to get PID of TG docker container!"
    }
    params=(--format="{{ .State.Pid }}" ${DCR_UUIDS[dut1]})
    DCR_CPIDS+=([dut1]="$(docker inspect "${params[@]}")") || {
        die "Failed to get PID of DUT1 docker container!"
    }
}

function warn () {
    # Print the message to standard error.
    #
    # Arguments:
    # - ${@} - The text of the message.

    echo "$@" >&2
}
