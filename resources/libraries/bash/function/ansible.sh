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
    # While unexpected failures result in "die",
    # failure of the ansible command itself leads to "return 1",
    # so the caller can decide what to do.
    # Typical example: If one of testbed machines is found unresponsive
    # in the initial cleanup after reservation,
    # we want to write a loud message about needing human intervention,
    # leave the testbed reserved, but continue to reserve another testbed.
    #
    # Variable read:
    # - ${WORKING_TOPOLOGY} - Reserved working topology.
    # - ${TOOLS_DIR} - CSIT tools directory, where testbed-setup is located.
    # Functions called:
    # - die - Print to stderr and exit.

    set -exuo pipefail

    if ! installed sshpass; then
        die "Please install sshpass!"
    fi

    if ! installed ansible-playbook; then
        # TODO: Consider moving to requirements.txt?
        pip install ansible==2.7.8 || die "Install ansible via PIP failed!"
    fi

    hosts=($(fgrep host "${WORKING_TOPOLOGY}" | cut -d ":" -f 2)) || {
        die "Failed to read hosts from working topology!"
    }
    pushd "${TOOLS_DIR}"/testbed-setup/ansible || die "Pushd failed!"
    set +e
    ANSIBLE_STDOUT_CALLBACK=yaml ansible-playbook \
        --vault-password-file=vault_pass \
        --extra-vars '@vault.yml' \
        --inventory inventories/lf_inventory/hosts site.yaml \
        --limit "$(echo ${hosts[@]//\"})" \
        --tags "$(echo $@)"
    status="${?}"
    set -e
    popd || die "Popd failed!"
    if [[ "0" != "${status}" ]]; then
        warn "Failed to run ansible on host!"
        return 1
    fi
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
