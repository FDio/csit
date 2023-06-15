#!/usr/bin/env bash

# Copyright (c) 2023 Cisco and/or its affiliates.
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

    # enable l3fwd
    meson_options="-Dexamples=l3fwd "

    # i40e specific options
    meson_options="${meson_options} \
        -Dc_args=-DRTE_LIBRTE_I40E_16BYTE_RX_DESC=y"

    # Configure generic build - the same used by VPP
    meson_options="${meson_options} -Dplatform=generic"

    # Compile using Meson and Ninja.
    meson setup ${meson_options} build || {
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
    # Functions called:
    # - die - Print to stderr and exit.

    set -exuo pipefail

    pushd "${DPDK_DIR}" || die "Pushd failed"
    # Patch L3FWD.
    pushd examples/l3fwd || die "Pushd failed"
    chmod +x ${1} && source ${1} || die "Patch failed"
    popd || die "Popd failed"

    ninja -C build || die "Failed to compile DPDK!"
}


function dpdk_l3fwd () {

    # Run DPDK l3fwd.
    #
    # No check for "entering main loop" is done here,
    # as the later check in dpdk_l3fwd_check is more important.
    # This way l3fwd can be starting on multiple DUTs at once,
    # so dut-dut link can go up within default wait time 9s.
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
}


function dpdk_l3fwd_pid () {
    l3fwd_pid="$(pidof dpdk-l3fwd)"
    if [ ! -z "${l3fwd_pid}" ]; then
        echo "L3fwd process ID: ${l3fwd_pid}"
    else
        echo "L3fwd not running!"
    fi
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
    # No check for "Press enter to exit" is done here,
    # as the later check in dpdk_testpmd_check is more important.
    # This way testpmd can be starting on multiple DUTs at once,
    # so dut-dut link can go up within default wait time 9s.
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
}


function dpdk_app_check () {

    # Return with error code 1 if a dpdk app is not ready in time.
    #
    # This function holds logic common to testpmd and l3fwd,
    # as the only difference between them is the "done string"
    # emitted when link checking is done. At that time, both links
    # should be reported as up.
    # This function looks for the "done string" each second up to 30 times,
    # and when the link checking is done, it verifies that the links are up.
    #
    # L3fwd can only be started with its own link checking
    # (waits up to 9 seconds) and without LSC (Link State Change) interrupts.
    # So it is either fully ready when it prints its "done string",
    # or it does not signal when (if ever) the missing link goes up.
    # While testpmd can be started without link checking and with interrupts,
    # that would only make detection logic here more complicated.
    #
    # Currently, all testbeds are fairly quick at bringing links up,
    # assuming apps on both DUTs are starting at the same time.
    # Occasional timeout will probably be fixed by few app restarts.
    #
    # If links become too slow at getting up (as they did in CSIT-1848),
    # (so that in-app 9s wait is no longer enough and check will fail)
    # it would be better to keep tests failing (so fixing infra gets priority).
    #
    # Arguments:
    # - ${1} - App name, currently either "testpmd" or "l3fwd".

    set -exuo pipefail

    if [[ "${1}" == "testpmd" ]]; then
        # Link state is reported sooner than this,
        # but it is safer to require the last consistent string.
        pattern="Press enter to exit"
    elif [[ "${1}" == "l3fwd" ]]; then
        pattern="L3FWD: entering main loop on lcore"
    else
        echo "Unsupported dpdk app: ${1}"
        return 1
    fi
    set +x
    for attempt in $(seq 30); do
        sleep 1
        if ! grep -q "${pattern}" "screenlog.0"; then
            echo "Attempt ${attempt} does not see Done yet."
            continue
        fi
        if ! fgrep -q "Port 0 Link up" "screenlog.0"; then
            echo "Dpdk app startup done but link 0 is not up."
            set -x
            return 1
        fi
        if ! fgrep -q "Port 1 Link up" "screenlog.0"; then
            echo "Dpdk app startup done but link 1 is not up."
            set -x
            return 1
        fi
        echo "Dpdk app is ready."
        set -x
        return 0
    done
    echo "Dpdk app is still not ready after ${attempt} checks."
    set -x
    return 1
}


function dpdk_testpmd_pid () {
    testpmd_pid="$(pidof dpdk-testpmd)"
    if [ ! -z "${testpmd_pid}" ]; then
        echo "Testpmd process ID: ${testpmd_pid}"
    else
        echo "Testpmd not running!"
    fi
}
