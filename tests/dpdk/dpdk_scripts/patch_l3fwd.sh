#!/usr/bin/env bash

# Copyright (c) 2020 Cisco and/or its affiliates.
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


function common_dirs () {

    # Set global variables, create some directories (without touching content).

    # Variables set:
    # - BASH_FUNCTION_DIR - Path to existing directory this file is located in.
    # - DPDK_DIR - Path to DPDK framework.
    # - CSIT_DIR - Path to CSIT framework.
    # Directories created if not present:
    # - DPDK_DIR.
    # Functions called:
    # - die - Print to stderr and exit.

    set -exuo pipefail

    this_file=$(readlink -e "${BASH_SOURCE[0]}") || {
        die "Some error during locating of this source file."
    }
    BASH_FUNCTION_DIR=$(dirname "${this_file}") || {
        die "Some error during dirname call."
    }
    CSIT_DIR=$(readlink -e "/tmp/openvpp-testing") || {
        die "Readlink failed."
    }
    DPDK_DIR=$(readlink -e "${CSIT_DIR}/dpdk") || {
        die "Readlink failed."
    }
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


function dpdk_l3fwd_compile () {

    # Compile DPDK l3fwd sample app.
    #
    # Variables read:
    # - DPDK_DIR - Path to DPDK framework.
    # - CSIT_DIR - Path to CSIT framework.
    # Functions called:
    # - die - Print to stderr and exit.

    set -exuo pipefail

    arch=$(uname -m) || {
        die "Get CPU architecture failed."
    }

    # DPDK prefers "arm64" to "aarch64" and does not allow arm64 native target.
    if [ ${arch} == "aarch64" ]; then
        arch="arm64"
        machine="armv8a"
    else
        machine="native"
    fi

    # Patch settings.

    # Compile the l3fwd.
    export RTE_SDK="${DPDK_DIR}/"
    export RTE_TARGET="${arch}-${machine}-linuxapp-gcc"
    # Patch settings.
    sed_rxd="s/^#define RTE_TEST_RX_DESC_DEFAULT 128/#define RTE_TEST_RX_DESC_DEFAULT 2048/g"
    sed_txd="s/^#define RTE_TEST_TX_DESC_DEFAULT 512/#define RTE_TEST_TX_DESC_DEFAULT 2048/g"
    sed_file="./main.c"
    pushd "${RTE_SDK}"/examples/l3fwd || die "Pushd failed"
    sed -i "${sed_rxd}" "${sed_file}" || die "Patch failed"
    sed -i "${sed_txd}" "${sed_file}" || die "Patch failed"
    chmod +x ${1} && source ${1} || die "Patch failed"
    make clean || die "Failed to compile l3fwd"
    make -j || die "Failed to compile l3fwd"
    popd || die "Popd failed"
}


function warn () {

    # Print the message to standard error.
    #
    # Arguments:
    # - ${@} - The text of the message.

    set -exuo pipefail

    echo "$@" >&2
}


common_dirs || die
dpdk_l3fwd_compile "${@}" || die
