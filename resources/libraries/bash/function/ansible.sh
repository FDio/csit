#!/usr/bin/env bash

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


function ansible_hosts () {
    # Run ansible playbook on hosts in working topology file. Ansible scope is
    # determined by tags passed as parameters to this function.
    #
    # Variable read:
    # - ${WORKING_TOPOLOGY} - Reserved working topology.
    # - ${TOOLS_DIR} - CSIT tools directory, where testbed-setup is located.

    set -exuo pipefail

    ansible_prepare || die "Preparing Ansible failed!"

    hosts=($(fgrep host "${WORKING_TOPOLOGY}" | cut -d ":" -f 2)) || {
        die "Failed to read hosts from working topology!"
    }
    pushd "${TOOLS_DIR}"/testbed-setup/ansible || die "Pushd failed!"
    ansible-playbook \
        --vault-password-file=vault_pass \
        --extra-vars '@vault.yml' \
        --inventory inventories/lf_inventory/hosts site.yaml \
        --limit "$(echo ${hosts[@]//\"})" \
        --tags "$(echo $@)" || die "Failed to run ansible on host!"
    popd || die "Popd failed!"
}


function ansible_host () {
    # Run ansible playbook on host. Ansible scope is determined by tags passed
    # as parameters to this function.
    #
    # Variable read:
    # - ${HOST} - Host to run Ansible on.
    # - ${TOOLS_DIR} - CSIT tools directory, where testbed-setup is located.

    set -exuo pipefail

    ansible_prepare || die "Preparing Ansible failed!"

    pushd "${TOOLS_DIR}"/testbed-setup/ansible || die "Pushd failed!"
    ansible-playbook \
        --vault-password-file=vault_pass \
        --extra-vars '@vault.yml' \
        --inventory inventories/lf_inventory/hosts site.yaml \
        --limit "${HOST}" \
        --tags "$(echo $@)" || die "Failed to run ansible on host!"
    popd || die "Popd failed!"
}


function ansible_prepare () {
    # Install prerequisites to run Ansible.

    set -exuo pipefail

    if ! installed sshpass; then
        sudo apt-get update -y || die "apt-get update failed!"
        sudo apt-get install -y sshpass || die "Install sshpass failed!"
    fi

    if ! installed ansible-playbook; then
        pip install ansible==2.7.8 || die "Install ansible via PIP failed!"
    fi

    if ! installed python2-pyghmiutil; then
        pip install pyghmi=1.3.0 || die "Install pyghmi via PIP failed!"
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
