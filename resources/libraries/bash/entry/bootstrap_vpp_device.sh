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

BASH_ENTRY_DIR="$(dirname $(readlink -e "${BASH_SOURCE[0]}"))"
BASH_FUNCTION_DIR="$(readlink -e "${BASH_ENTRY_DIR}/../function")"
source "${BASH_FUNCTION_DIR}/common.sh" || {
    echo "Source failed." >&2
    exit 1
}

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

    # Docker Container UUIDs
    declare -A DCR_UUIDS
    # Docker Container SSH TCP ports.
    declare -A DCR_PORTS
    # Docker Container PIDs (namespaces).
    declare -A DCR_CPIDS

    dcr_image="pmikus/csit-vpp-device-test:latest"
    dcr_params="--privileged --shm-size 512M -d -P"

    # Run TG and SUT1. As initial version we do support only 2-node.
    DCR_UUIDS+=([tg]="$(docker run ${dcr_params} ${dcr_image})")
    DCR_UUIDS+=([sut1]="$(docker run ${dcr_params} ${dcr_image})")

    trap 'docker rm "${DCR_UUIDS[@]}" --force || die "Cleanup docker failed."' \
        EXIT SIGHUP SIGINT SIGQUIT SIGTERM || {
        die "Trap attempt failed, kill Docker containers manually. Aborting."
    }

    # Get Container TCP port.
    DCR_PORTS+=([tg]="$(docker port ${DCR_UUIDS[tg]})")
    DCR_PORTS+=([sut1]="$(docker port ${DCR_UUIDS[sut1]})")

    # Get Container PIDs.
    DCR_CPIDS+=([tg]="$(docker inspect --format='{{ .State.Pid }}' ${DCR_UUIDS[tg]})")
    DCR_CPIDS+=([sut1]="$(docker inspect --format='{{ .State.Pid }}' ${DCR_UUIDS[sut1]})")
}

function reserve_sriov_vf () {
    # TODO
    #
    # Arguments:
    # - ${1} - Timeout value for acquiring mutex. Optional
    # - ${2} - Mutex directory that acts as mutex. Optional

    set -exuo pipefail

    # Check if we have any VFs available.
    pci_path="/sys/bus/pci/devices/*/device"
    pci_whitelist=()
    # Add Intel Corporation XL710/X710 Virtual Function to the whitelist.
    # See http://pci-ids.ucw.cz/v2.2/pci.ids for more info.
    pci_whitelist+=($(fgrep -l "0x154c" ${pci_path} | xargs -r dirname)) || {
        die "Failed to get whitelist of PCI addresses."
    }

    if [[ -z ${pci_whitelist[@]} ]]; then
        die "List of PCI addresses of VFs is empty."
    fi

    mutex_timeout=${1:-3600} || {
        die "Reading optional argument failed, somehow."
    }

    mutex_file=${2:-/tmp/mutex_file} || {
        die "Reading optional argument failed, somehow."
    }

    exec {lock_fd}>${mutex_file} || {
        die "Mutex enter failed."
    }
    flock --timeout "${mutex_timeout}" "${lock_fd}" || {
        die "Calling flock() failed."
    }
    # ----------------------
    # Enter mutex succeeded.
    warn "Mutex enter succeeded for PID $$."

    # East side of connection.
    east_netdevs=()
    # West side of connection.
    west_netdevs=()

    for netdev in $(ls /sys/bus/pci/devices/*/net); do
        # We will filter only VFs
        if [[ -d /sys/class/net/${netdev}/device/physfn ]]; then
            # We will filter to east/west side of connection (this can be in
            # future overriden by more advanced conditions for mapping)
            if [[ "${netdev}" == enp24* ]]; then
                east_netdevs+=(${netdev})
            elif [[ "${netdev}" == enp59* ]]; then
                west_netdevs+=(${netdev})
            fi
        fi
    done

    # We need at least two interfaces from east/west for building topology.
    if [ "${#east_netdevs[@]}" -ge 2 ] || [ "${#west_netdevs[@]}" -ge 2 ]; then
        die "Not enough network interfaces found."
    fi

    echo "${east_netdevs[@]:0:2}"
    echo "${west_netdevs[@]:0:2}"

    ip link set ${east_netdevs[0]} netns ${DCR_UUIDS[tg]} || {
        die "Moving interface to ${DCR_CPIDS[tg]} namepsace failed."
    }
    ip link set ${east_netdevs[1]} netns ${DCR_UUIDS[tg]} || {
        die "Moving interface to ${DCR_CPIDS[tg]} namepsace failed."
    }
    ip link set ${west_netdevs[0]} netns ${DCR_UUIDS[sut1]} || {
        die "Moving interface to ${DCR_CPIDS[sut1]} namepsace failed."
    }
    ip link set ${west_netdevs[1]} netns ${DCR_UUIDS[sut1]} || {
        die "Moving interface to ${DCR_CPIDS[sut1]} namepsace failed."
    }
    # ---------------------
    # Remove lock so we are not blocking others anymore.
    flock -u "${lock_fd}" || {
        die "Mutex destroy failed."
    }
    warn "Mutex leave succeeded for PID $$."
}

common_dirs || die
start-csit-sut-dcr || die
reserve_sriov_vf || die

# Continue with topology file creation and rest of virtualenv/pybot/archive
