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


function dpdk_kill () {

    # Kill testpmd and/or l3fwd if running.

    # Function will be noisy and requires custom error handling.
    set -x
    set +eu

    # Try to kill the testpmd.
    sudo pgrep testpmd
    if [ $? -eq "0" ]; then
        success=false
        sudo pkill testpmd
        echo "RC = $?"
        for attempt in {1..60}; do
            echo "Checking if testpmd is still alive, attempt nr ${attempt}"
            sudo pgrep testpmd
            if [ $? -eq "1" ]; then
                echo "testpmd is dead"
                success=true
                break
            fi
            echo "testpmd is still alive, waiting 1 second"
            sleep 1
        done
        if [ "$success" = false ]; then
            echo "The command sudo pkill testpmd failed"
            sudo pkill -9 testpmd
            echo "RC = $?"
            exit 1
        fi
    else
        echo "testpmd is not running"
    fi

    # Try o kill the l3fwd.
    sudo pgrep l3fwd
    if [ $? -eq "0" ]; then
        success=false
        sudo pkill l3fwd
        echo "RC = $?"
        for attempt in {1..60}; do
            echo "Checking if l3fwd is still alive, attempt nr ${attempt}"
            sudo pgrep l3fwd
            if [ $? -eq "1" ]; then
                echo "l3fwd is dead"
                success=true
                break
            fi
            echo "l3fwd is still alive, waiting 1 second"
            sleep 1
        done
        if [ "$success" = false ]; then
            echo "The command sudo pkill l3fwd failed"
            sudo pkill -9 l3fwd
            echo "RC = $?"
            exit 1
        fi
    else
        echo "l3fwd is not running"
    fi

    # Remove hugepages
    sudo rm -f /dev/hugepages/*
}


function dpdk_rebind () {

    # Rebind interfaces back to native driver.
    #
    # Variables read:
    # - DPDK_DIR - Path to DPDK framework.
    # - @ - Script cli arguments.
    # Functions called:
    # - die - Print to stderr and exit.

    pushd "${DPDK_DIR}/" || die "Pushd failed"

    sudo ./usertools/dpdk-devbind.py -b "${@}" || {
        die "Bind ${@} failed"
    }

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
dpdk_kill || die
dpdk_rebind "${@}" || die
