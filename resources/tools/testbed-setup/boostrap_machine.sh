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


function installed () {
    # Check if the given utility is installed. Fail if not installed.
    #
    # Arguments:
    # - ${1} - Utility to check.
    # Returns:
    # - 0 - If command is installed.
    # - 1 - If command is not installed.

    set -exuo pipefail

    command -v "${1}"
}


function pxe_cimc () {
    # Reboot server with next boot set to PXE, disables PXE after server is UP
    # to prevent endless loop.
    #
    # Variable read:
    # - ${HOST} - Server production IP address (Linux).
    # - ${MGMT} - Server management IP address (IPMI/CIMC).
    # - ${USER} - CIMC user.
    # - ${PASS} - CIMC pass.

    set -exuo pipefail

    cimc/cimc.py -u "${USER}" -p "${PASS}" "${MGMT}" --debug -pxe || {
        die "Failed to send the PXE reboot command!"
    }
    for i in $(seq 1 500); do
        warn "Waiting for server to become reachable ... " || die
        if reachable "${HOST}"; then
            cimc/cimc.py -u "${USER}" -p "${PASS}" "${MGMT}" --debug -hdd || {
                die "Failed to send the HDD command!"
            }
            ssh-keygen -f "/home/testuser/.ssh/known_hosts" -R "${HOST}" || {
                die "Failed to remove obsolete SSH key!"
            }
            warn "Server reachable, PXE running!" || die
            break
        fi
    done
}


function pxe_host () {
    # Reboot host into PXE mode and detect once it is up.
    #
    # Variable read:
    # - @ - All script arguments from command line.
    # Variable set:
    # - ${HOST} - Server production IP address (Linux).
    # - ${MGMT} - Server management IP address (IPMI/CIMC).
    # - ${USER} - User.
    # - ${PASS} - Pass.

    set -exuo pipefail

    if ! installed ipmitool; then
        die "ipmitool not present. Please install before continue!"
    fi

    HOST=${1}
    MGMT=${2}
    USER=${3}
    PASS=${4}

    ipmi="ipmitool -I lanplus -H ${MGMT} -U ${USER} -P ${PASS} chassis status"
    cimc="cimc/cimc.py -u ${USER} -p ${PASS} ${MGMT} --mac-table"
    if ${ipmi}; then
        warn "This is IMPI managed server!"
        pxe_supermicro || die
    elif ${cimc}; then
        warn "This is CIMC managed server!"
        pxe_cimc || die
    fi
}


function pxe_supermicro () {
    # Reboot server with next boot set to PXE.
    #
    # Variable read:
    # - ${HOST} - Server production IP address (Linux).
    # - ${MGMT} - Server management IP address (IPMI/CIMC).
    # - ${USER} - IPMI user.
    # - ${PASS} - IPMI pass.

    set -exuo pipefail

    if ! installed ipmitool; then
        die "ipmitool not present. Please install before continue!"
    fi

    cmd="chassis bootdev pxe"
    ipmitool -I lanplus -H "${MGMT}" -U "${USER}" -P "${PASS}" "${cmd}" || {
        die "Failed to send the ${cmd} command!"
    }
    cmd="power reset"
    ipmitool -I lanplus -H "${MGMT}" -U "${USER}" -P "${PASS}" "${cmd}" || {
        die "Failed to send the ${cmd} command!"
    }
    for i in $(seq 1 500); do
        warn "Waiting for server to become reachable ... " || die
        if reachable "${HOST}"; then
            ssh-keygen -f "/home/testuser/.ssh/known_hosts" -R "${HOST}" || {
                die "Failed to remove obsolete SSH key!"
            }
            warn "Server reachable, PXE running!" || die
            break
        fi
    done
}


function reachable () {
    # Check if the host is reachable. Fail if not reachable.
    #
    # Arguments:
    # - ${1} - Host to check.
    # Returns:
    # - 0 - If host is reachable.
    # - 1 - If host is not reachable.

    set -exuo pipefail

    ping -q -c 1 "${1}" 2>&1 > /dev/null
}


function warn () {
    # Print the message to standard error.
    #
    # Arguments:
    # - ${@} - The text of the message.

    echo "$@" >&2
}

pxe_host "${@}" || die
