#!/usr/bin/env bash

# Copyright (c) 2021 Cisco and/or its affiliates.
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


function terraform_apply () {

    # Run terraform apply command to prepare topology.
    #
    # Variable read:
    # - ${CSIT_DIR} - CSIT main directory, where terraform modules are located.
    # - ${NODENESS} - Node multiplicity of desired testbed.
    # - ${FLAVOR} - Node flavor string, see common.sh

    set -exuo pipefail

    if ! installed terraform; then
        die "Please install terraform!"
    fi

    pushd "${CSIT_DIR}"/fdio.infra.terraform || die "Pushd failed!"
    pushd "${NODENESS}_${FLAVOR}_c5n" || die "Pushd failed!"
    export TF_LOG=INFO
    terraform apply -auto-approve  || die "Failed to run terraform apply!"
    popd || die "Popd failed!"
    popd || die "Popd failed!"
}

function terraform_destroy () {

    # Run terraform destroy command to prepare module.
    #
    # Variable read:
    # - ${CSIT_DIR} - CSIT main directory, where terraform modules are located.
    # - ${NODENESS} - Node multiplicity of desired testbed.
    # - ${FLAVOR} - Node flavor string, see common.sh

    set -exuo pipefail

    if ! installed terraform; then
        die "Please install terraform!"
    fi

    pushd "${CSIT_DIR}"/fdio.infra.terraform || die "Pushd failed!"
    pushd "${NODENESS}_${FLAVOR}_c5n" || die "Pushd failed!"
    export TF_LOG=INFO
    terraform destroy -auto-approve || die "Failed to run terraform destroy!"
    popd || die "Popd failed!"
    popd || die "Popd failed!"
}


function terraform_init () {

    # Run terraform init command to prepare module.
    #
    # Variable read:
    # - ${CSIT_DIR} - CSIT main directory, where terraform modules are located.
    # - ${NODENESS} - Node multiplicity of desired testbed.
    # - ${FLAVOR} - Node flavor string, see common.sh

    set -exuo pipefail

    if ! installed terraform; then
        die "Please install terraform!"
    fi

    pushd "${CSIT_DIR}"/fdio.infra.terraform || die "Pushd failed!"
    pushd "${NODENESS}_${FLAVOR}_c5n" || die "Pushd failed!"
    export TF_LOG=INFO
    terraform init || die "Failed to run terraform init!"
    popd || die "Popd failed!"
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
