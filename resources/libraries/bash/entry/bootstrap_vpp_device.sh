#!/usr/bin/env bash

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

set -exuo pipefail

# Assumptions:
# + There is a directory holding CSIT code to use (this script is there).
# + At least one of the following is true:
# ++ JOB_NAME environment variable is set,
# ++ or this entry script has access to arguments.
# Consequences (and specific assumptions) are multiple,
# examine tree of functions for current description.

# "set -eu" handles failures from the following two lines.
BASH_ENTRY_DIR="$(dirname $(readlink -e "${BASH_SOURCE[0]}"))"
BASH_FUNCTION_DIR="$(readlink -e "${BASH_ENTRY_DIR}/../function")"
source "${BASH_FUNCTION_DIR}/common.sh" || {
    echo "Source failed." >&2
    exit 1
}
source "${BASH_FUNCTION_DIR}/gather.sh" || die "Source failed."

function get_pci_addr () {
    # TODO
    #
    # Arguments:
    # - ${1} - PCI address or linux network device name. Optional
    # Variables set:
    # - PCI_ADDR - PCI address of network device.

    set -exuo pipefail

    if [ -d /sys/class/net/${1-}/device ]; then
        PCI_ADDR=$(basename $(readlink /sys/class/net/${1}/device))
    else
        PCI_ADDR=${1-}
    fi
    if [ ! -d /sys/bus/pci/devices/${PCI_ADDR} ]; then
        die "PCI device ${1-} doesn't exist"
    fi
}

function start-csit-sut-dcr () {
    # TODO
    #
    # Arguments:

    set -exuo pipefail

    if ! installed docker; then
        die "Docker not present. Please install before continue."
    fi

    local dcr_image="pmikus/csit-vpp-device-test:latest"
    local dcr_params="--privileged --shm-size 512M -d -P"

    # Docker Container UUIDs
    declare -gA DCR_UUIDS
    # Docker Container SSH TCP ports.
    declare -gA DCR_PORTS
    # Docker Container PIDs (namespaces).
    declare -gA DCR_CPIDS


    # Run TG and DUT1. As initial version we do support only 2-node.
    DCR_UUIDS+=([tg]="$(docker run ${dcr_params} ${dcr_image})")
    DCR_UUIDS+=([dut1]="$(docker run ${dcr_params} ${dcr_image})")

    trap 'docker rm "${DCR_UUIDS[@]}" --force || die "Cleanup docker failed."' \
        EXIT SIGHUP SIGINT SIGQUIT SIGTERM || {
        die "Trap attempt failed, kill Docker containers manually. Aborting."
    }

    # Get Container TCP port.
    DCR_PORTS+=([tg]="$(docker port ${DCR_UUIDS[tg]})")
    DCR_PORTS+=([dut1]="$(docker port ${DCR_UUIDS[dut1]})")

    # Get Container PIDs.
    DCR_CPIDS+=([tg]="$(docker inspect --format='{{ .State.Pid }}' ${DCR_UUIDS[tg]})")
    DCR_CPIDS+=([dut1]="$(docker inspect --format='{{ .State.Pid }}' ${DCR_UUIDS[dut1]})")
}

function reserve_sriov_vf () {
    # TODO
    #
    # Arguments:
    # - ${1} - Timeout value for acquiring mutex. Optional
    # - ${2} - Mutex directory that acts as mutex. Optional

    set -exuo pipefail

    # Following code is specifing VFs ID based on nodeness and flavor.
    # As there is great variability in hardware configuration outside LF,
    # from bootstrap architecure point of view these are considered as flavors.
    # Anyone can override flavor of its own machine and add condition there.
    # See http://pci-ids.ucw.cz/v2.2/pci.ids for more info.
    pci_path="/sys/bus/pci/devices/*/device"
    net_path="/sys/bus/pci/devices/*/net/*"

    case_text="${NODENESS}_${FLAVOR}"
    case "${case_text}" in
        "1n_skx")
            # Add Intel Corporation XL710/X710 Virtual Function to the
            # whitelist.
            pci_id="0x154c"
            tg_netdev="enp24*"
            dut1_netdev="enp59*"
            ;;
        *)
            die "Unknown specification: ${case_text}"
    esac

    # Not needed?
    #pci_vfs=()
    #pci_vfs+=($(fgrep -l "${pci_id}" ${pci_path} | xargs -r dirname)) || {
    #    die "Failed to find VFs PCI device with ID "${pci_id}"."
    #}

    #if [[ -z ${pci_vfs[@]} ]]; then
    #    die "List of PCI addresses of VFs PCI ID "${pci_id}" is empty."
    #fi

    mutex_timeout=${1:-3600} || {
        die "Reading optional argument failed, somehow."
    }

    mutex_file=${2:-/tmp/mutex_file} || {
        die "Reading optional argument failed, somehow."
    }

    # Create mutex.
    exec {lock_fd}>${mutex_file} || {
        die "Mutex enter failed."
    }
    flock --timeout "${mutex_timeout}" "${lock_fd}" || {
        die "Calling flock() failed."
    }
    # ----------------------
    # Enter mutex succeeded.
    warn "Mutex enter succeeded for PID $$."

    # East side of connections.
    tg_netdevs=()
    # West side of connections.
    dut1_netdevs=()

    # Following code is filtering available VFs represented by network device
    # name. Only allowed VFs PCI IDs are used.
    for netdev in \
        $(find ${net_path} -type d -name . -o -prune -exec basename '{}' ';');
    do
        if grep -q "${pci_id}" "/sys/class/net/${netdev}/device/device"; then
            # We will filter to east/west side of connection (this can be in
            # future overriden by more advanced conditions for mapping).
            if [[ "${netdev}" == ${tg_netdev} ]]; then
                tg_netdevs+=(${netdev})
            elif [[ "${netdev}" == ${dut1_netdev} ]]; then
                dut1_netdevs+=(${netdev})
            fi
        fi
    done

    # We need at least two interfaces from east/west for building topology.
    if [ "${#tg_netdevs[@]}" -ge 2 ] || [ "${#dut1_netdevs[@]}" -ge 2 ]; then
        die "Not enough linux network interfaces found."
    fi

    echo "${tg_netdevs[@]::2}"
    echo "${dut1_netdevs[@]::2}"

    start-csit-sut-dcr || die

    for netdev in "${tg_netdevs[@]::2}"; do
        ip link set ${netdev} netns ${DCR_UUIDS[tg]} || {
            die "Moving interface to ${DCR_CPIDS[tg]} namepsace failed."
        }
    done
    for netdev in "${dut1_netdevs[@]::2}"; do
        ip link set ${netdev} netns ${DCR_UUIDS[dut1]} || {
            die "Moving interface to ${DCR_CPIDS[dut1]} namepsace failed."
        }
    done

    # ---------------------
    # Remove lock so we are not blocking others anymore.
    flock -u "${lock_fd}" || {
        die "Mutex destroy failed."
    }
    warn "Mutex leave succeeded for PID $$."
}

common_dirs || die
get_test_tag_string || die
get_test_code "${1-}" || die
select_topology || die
#gather_build || die
#check_download_dir || die
#activate_virtualenv "${CSIT_DIR}" || die
reserve_sriov_vf || die
# <------- Testing up to here now
#make_topology || die
#select_tags || die
#compose_pybot_arguments || die
#run_pybot || die
#copy_archives || die
#die_on_pybot_error || die
