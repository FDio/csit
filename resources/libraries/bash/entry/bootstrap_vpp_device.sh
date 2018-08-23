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
    # - ${1} - PCI address or linux network device name.
    # Variables set:
    # - PCI_ADDR - PCI address of network device.

    set -exuo pipefail

    if [ -d /sys/class/net/${1}/device ]; then
        PCI_ADDR=$(basename $(readlink /sys/class/net/${1}/device))
    fi
    if [ ! -d /sys/bus/pci/devices/${PCI_ADDR} ]; then
        die "PCI device ${1} doesn't exist"
    fi
}

function get_available_net_devs () {
    # TODO
    #
    # Arguments:

    set -exuo pipefail

    case_text="${NODENESS}_${FLAVOR}"
    case "${case_text}" in
        "1n_skx")
            # Add Intel Corporation XL710/X710 Virtual Function to the
            # whitelist.
            pci_dev="0x154c"
            tg_netdev="enp24*"
            dut1_netdev="enp59*"
            ;;
        "1n_vbox")
            # Add Intel Corporation 82545EM Gigabit Ethernet Controller to the
            # whitelist.
            pci_dev="0x100f"
            tg_netdev="eth1*"
            dut1_netdev="eth2*"
            ;;
        *)
            die "Unknown specification: ${case_text}"
    esac

    net_path="/sys/bus/pci/devices/*/net/*"

    # TG side of connections.
    TG_NETDEVS=()
    # DUT1 side of connections.
    DUT1_NETDEVS=()

    # Following code is filtering available VFs represented by network device
    # name. Only allowed VFs PCI IDs are used.
    for netdev in \
        $(find ${net_path} -type d -name . -o -prune -exec basename '{}' ';');
    do
        if grep -q "${pci_dev}" "/sys/class/net/${netdev}/device/device"; then
            # We will filter to TG/DUT1 side of connection (this can be in
            # future overriden by more advanced conditions for mapping).
            if [[ "${netdev}" == ${tg_netdev} ]]; then
                TG_NETDEVS+=(${netdev})
            elif [[ "${netdev}" == ${dut1_netdev} ]]; then
                DUT1_NETDEVS+=(${netdev})
            fi
        fi
    done

    # We need at least two interfaces for TG/DUT1 for building topology.
    if [ "${#TG_NETDEVS[@]}" -lt 2 ] || [ "${#DUT1_NETDEVS[@]}" -lt 2 ]; then
        die "Not enough linux network interfaces found."
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
    # Anyone can override flavor for its own machine and add condition here.
    # See http://pci-ids.ucw.cz/v2.2/pci.ids for more info.

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

    get_available_net_devs || die
    start-csit-sut-dcr || die

    for netdev in "${TG_NETDEVS[@]::2}"; do
        ip link set ${netdev} netns ${DCR_CPIDS[tg]} || {
            die "Moving interface to ${DCR_CPIDS[tg]} namespace failed."
        }
    done
    for netdev in "${DUT1_NETDEVS[@]::2}"; do
        ip link set ${netdev} netns ${DCR_CPIDS[dut1]} || {
            die "Moving interface to ${DCR_CPIDS[dut1]} namespace failed."
        }
    done

    # ---------------------
    # Remove mutex so we are not blocking others anymore.
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
