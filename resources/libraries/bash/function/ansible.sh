#!/usr/bin/env bash

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


function ansible_adhoc () {

    # Run ansible ad-hoc command module on hosts in working topology file.
    #
    # Variable read:
    # - ${WORKING_TOPOLOGY} - Reserved working topology.
    # - ${CSIT_DIR} - CSIT main directory, where ansible playbooks are located.
    # - ${FLAVOR} - Node flavor string, see common.sh

    set -exuo pipefail

    case "${TEST_CODE}" in
        *"1n-aws" | *"2n-aws" | *"3n-aws")
            INVENTORY_PATH="cloud_inventory"
            ;;
        *"2n-c7gn" | *"3n-c7gn")
            INVENTORY_PATH="cloud_inventory"
            ;;
        *"1n-c6in" | *"2n-c6in" | *"3n-c6in")
            INVENTORY_PATH="cloud_inventory"
            ;;
        *"-x-2n"* | *"-x-3n"*)
            INVENTORY_PATH="external_inventory"
            ;;
        *)
            INVENTORY_PATH="lf_inventory"
            ;;
    esac

    if ! installed sshpass; then
        die "Please install sshpass!"
    fi

    hosts=($(fgrep host "${WORKING_TOPOLOGY}" | cut -d ":" -f 2)) || {
        die "Failed to read hosts from working topology!"
    }
    pushd "${CSIT_DIR}"/fdio.infra.ansible || die "Pushd failed!"
    export ANSIBLE_HOST_KEY_CHECKING=False
    export ANSIBLE_STDOUT_CALLBACK=yaml
    export ANSIBLE_PIPELINING=true
    ansible-playbook \
        --vault-password-file=vault_pass \
        --extra-vars '@vault.yml' \
        --inventory inventories/$INVENTORY_PATH/hosts site.yaml \
        --limit "$(echo ${hosts[@]//\"})" \
        --module-name shell \
        --args \"$(echo $@)\" || die "Failed to run ansible on host!"
    popd || die "Popd failed!"
}

function ansible_playbook () {

    # Run ansible playbook on hosts in working topology file. Ansible scope is
    # determined by tags passed as parameters to this function.
    #
    # Variable read:
    # - ${WORKING_TOPOLOGY} - Reserved working topology.
    # - ${CSIT_DIR} - CSIT main directory, where ansible playbooks are located.
    # - ${FLAVOR} - Node flavor string, see common.sh

    set -exuo pipefail

    case "${TEST_CODE}" in
        *"1n-aws" | *"2n-aws" | *"3n-aws")
            INVENTORY_PATH="cloud_inventory"
            ;;
        *"2n-c7gn" | *"3n-c7gn")
            INVENTORY_PATH="cloud_inventory"
            ;;
        *"1n-c6in" | *"2n-c6in" | *"3n-c6in")
            INVENTORY_PATH="cloud_inventory"
            ;;
        *"-x-2n"* | *"-x-3n"*)
            INVENTORY_PATH="external_inventory"
            ;;
        *)
            INVENTORY_PATH="lf_inventory"
            ;;
    esac

    if ! installed sshpass; then
        die "Please install sshpass!"
    fi

    hosts=($(fgrep host "${WORKING_TOPOLOGY}" | cut -d ":" -f 2)) || {
        die "Failed to read hosts from working topology!"
    }
    pushd "${CSIT_DIR}"/fdio.infra.ansible || die "Pushd failed!"
    export ANSIBLE_HOST_KEY_CHECKING=False
    export ANSIBLE_STDOUT_CALLBACK=yaml
    export ANSIBLE_PIPELINING=true
    ansible-playbook \
        --vault-password-file=vault_pass \
        --extra-vars '@vault.yml' \
        --inventory inventories/$INVENTORY_PATH/hosts site.yaml \
        --limit "$(echo ${hosts[@]//\"})" \
        --tags "$(echo $@)" || die "Failed to run ansible on host!"
    popd || die "Popd failed!"
}


function installed () {

    # Check if the given utility is installed. Fail if not installed.
    #
    # Arguments:
    # - ${1} - Utility to check.
    # Returns (implicitly):
    # - 0 - If command is installed.
    # - 1 - If command is not installed.

    set -exuo pipefail

    command -v "${1}"
}
