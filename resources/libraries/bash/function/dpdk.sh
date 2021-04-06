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


function common_dirs () {

    # Set global variables, create some directories (without touching content).
    # This function assumes running in remote testbed. It might override other
    # functions if included from common.sh.

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
    mkdir -p "${CSIT_DIR}/dpdk" || die "Mkdir failed."
    DPDK_DIR=$(readlink -e "${CSIT_DIR}/dpdk") || {
        die "Readlink failed."
    }
}


function dpdk_bind () {

    # Bind interfaces to driver.
    #
    # Variables read:
    # - DPDK_DIR - Path to DPDK framework.
    # - @ - Script cli arguments.
    # Functions called:
    # - die - Print to stderr and exit.

    set -exuo pipefail

    pushd "${DPDK_DIR}/" || die "Pushd failed"

    sudo ./usertools/dpdk-devbind.py -b "${@}" || {
        die "Bind ${@} failed"
    }

    popd || die "Popd failed"
}


function dpdk_compile () {

    # Compile DPDK archive.
    #
    # Variables read:
    # - DPDK_DIR - Path to DPDK framework.
    # - CSIT_DIR - Path to CSIT framework.
    # Variables exported:
    # - RTE_SDK - DPDK directory.
    # - RTE_TARGET - Make targed of DPDK framework.
    # Functions called:
    # - die - Print to stderr and exit.

    set -exuo pipefail

    pushd "${DPDK_DIR}" || die "Pushd failed"

    # Patch ARM.
    sed_file="config/arm/meson.build"
    sed_cmd="s/'RTE_MAX_LCORE', [0-9]*/'RTE_MAX_LCORE', $(nproc --all)/"
    sed -i "${sed_cmd}" "${sed_file}" || die "RTE_MAX_LCORE Patch failed"
    sed_cmd="s/'RTE_MAX_NUMA_NODES', [0-9]*/'RTE_MAX_NUMA_NODES', "
    sed_cmd+="$(echo /sys/devices/system/node/node* | wc -w)/"
    sed -i "${sed_cmd}" "${sed_file}" || die "RTE_MAX_NUMA_NODES Patch failed"

    # Patch L3FWD.
    sed_rxd="s/^#define RTE_TEST_RX_DESC_DEFAULT 128/#define RTE_TEST_RX_DESC_DEFAULT 1024/g"
    sed_txd="s/^#define RTE_TEST_TX_DESC_DEFAULT 512/#define RTE_TEST_TX_DESC_DEFAULT 1024/g"
    sed_file="./main.c"
    pushd examples/l3fwd || die "Pushd failed"
    sed -i "${sed_rxd}" "${sed_file}" || die "Patch failed"
    sed -i "${sed_txd}" "${sed_file}" || die "Patch failed"
    popd || die "Popd failed"

    # Compile using Meson and Ninja.
    export CFLAGS=""
    CFLAGS+="-DRTE_LIBRTE_I40E_16BYTE_RX_DESC=y"
    meson -Dexamples=l3fwd build || {
        die "Failed to compile DPDK!"
    }
    ninja -C build || die "Failed to compile DPDK!"
}


function dpdk_extract () {

    # Extract DPDK framework.
    #
    # Variables read:
    # - DPDK_DIR - Path to DPDK framework.
    # - CSIT_DIR - Path to CSIT framework.
    # Functions called:
    # - die - Print to stderr and exit.

    set -exuo pipefail

    pushd "${CSIT_DIR}" || die "Pushd failed"
    tar -xvf download_dir/dpdk*.tar.xz --strip=1 --directory "${DPDK_DIR}" || {
        die "Failed to extract DPDK!"
    }
}


function dpdk_kill () {

    # Kill testpmd and/or l3fwd if running.

    # Function will be noisy and requires custom error handling.
    set -x
    set +e

    # Try to kill the testpmd.
    sudo pgrep testpmd
    if [ $? -eq "0" ]; then
        success=false
        sudo pkill testpmd
        for attempt in {1..60}; do
            echo "Checking if testpmd is still alive, attempt nr ${attempt}"
            sudo pgrep testpmd
            if [ $? -eq "1" ]; then
                success=true
                break
            fi
            echo "testpmd is still alive, waiting 1 second"
            sleep 1
        done
        if [ "$success" = false ]; then
            echo "The command sudo pkill testpmd failed"
            sudo pkill -9 testpmd
            exit 1
        fi
    else
        echo "testpmd is not running"
    fi

    # Try to kill the l3fwd.
    l3fwd_pid="$(pgrep l3fwd)"
    if [ ! -z "${l3fwd_pid}" ]; then
        success=false
        sudo kill -15 "${l3fwd_pid}"
        for attempt in {1..60}; do
            echo "Checking if l3fwd is still alive, attempt nr ${attempt}"
            l3fwd_pid="$(pgrep l3fwd)"
            if [ -z "${l3fwd_pid}" ]; then
                success=true
                break
            fi
            echo "l3fwd is still alive, waiting 1 second"
            sleep 1
        done
        if [ "${success}" = false ]; then
            echo "The command sudo kill -15 l3fwd failed"
            sudo kill -9 "${l3fwd_pid}"
            exit 1
        fi
    else
        echo "l3fwd is not running"
    fi

    # Remove hugepages
    sudo rm -rf /dev/hugepages/* || die "Removing hugepages failed!"
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

    pushd "${DPDK_DIR}" || die "Pushd failed"
    # Patch L3FWD.
    sed_rxd="s/^#define RTE_TEST_RX_DESC_DEFAULT 128/#define RTE_TEST_RX_DESC_DEFAULT 2048/g"
    sed_txd="s/^#define RTE_TEST_TX_DESC_DEFAULT 512/#define RTE_TEST_TX_DESC_DEFAULT 2048/g"
    sed_file="./main.c"
    pushd examples/l3fwd || die "Pushd failed"
    sed -i "${sed_rxd}" "${sed_file}" || die "Patch failed"
    sed -i "${sed_txd}" "${sed_file}" || die "Patch failed"
    chmod +x ${1} && source ${1} || die "Patch failed"
    popd || die "Popd failed"

    ninja -C build || die "Failed to compile DPDK!"
}


function dpdk_l3fwd () {

    # Run DPDK l3fwd.
    #
    # Variables read:
    # - DPDK_DIR - Path to DPDK framework.
    # Functions called:
    # - die - Print to stderr and exit.

    set -exuo pipefail

    rm -f screenlog.0 || true
    binary="${DPDK_DIR}/build/examples/dpdk-l3fwd"

    sudo sh -c "screen -dmSL DPDK-test ${binary} ${@}" || {
        die "Failed to start l3fwd"
    }

    for attempt in {1..60}; do
        echo "Checking if l3fwd is alive, attempt nr ${attempt}"
        if fgrep "L3FWD: entering main loop on lcore" screenlog.0; then
            exit 0
        fi
        sleep 1
    done
    cat screenlog.0

    exit 1
}


function dpdk_precheck () {

    # Precheck system settings (nr_hugepages, max_map_count).
    #
    # Functions called:
    # - die - Print to stderr and exit.

    set -exuo pipefail

    sys_hugepage="$(< /sys/kernel/mm/hugepages/hugepages-2048kB/nr_hugepages)"
    node0="/sys/devices/system/node/node0/hugepages/hugepages-2048kB/"
    node1="/sys/devices/system/node/node1/hugepages/hugepages-2048kB/"
    if [ ${sys_hugepage} -lt 4096 ]; then
        echo 2048 | sudo tee "${node0}"/nr_hugepages || die
        echo 2048 | sudo tee "${node1}"/nr_hugepages || die
    fi

    sys_map="$(< /proc/sys/vm/max_map_count)"
    if [ ${sys_map} -lt 200000 ]; then
        echo 200000 | sudo tee /proc/sys/vm/max_map_count || die
    fi
}


function dpdk_testpmd () {

    # Run DPDK testpmd.
    #
    # Variables read:
    # - DPDK_DIR - Path to DPDK framework.
    # Functions called:
    # - die - Print to stderr and exit.

    set -exuo pipefail

    rm -f screenlog.0 || true
    binary="${DPDK_DIR}/build/app/dpdk-testpmd"

    sudo sh -c "screen -dmSL DPDK-test ${binary} ${@}" || {
        die "Failed to start testpmd"
    }

    for attempt in {1..60}; do
        echo "Checking if testpmd is alive, attempt nr ${attempt}"
         if fgrep "Press enter to exit" screenlog.0; then
             cat screenlog.0
             exit 0
        fi
        sleep 1
    done
    cat screenlog.0

    exit 1
}
