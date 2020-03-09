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

set -xuo pipefail

# Setting variables.
DPDK_DIR="dpdk"
ROOTDIR="/tmp/openvpp-testing"
TESTPMDLOG="screenlog.0"
PWDDIR="$(pwd)"

# Setting command line arguments.
cpu_corelist="${1}"
nb_cores="${2}"
queue_nums="${3}"
jumbo_frames="${4}"
rxd="${5:-128}"
txd="${6:-512}"
arch="$(uname -m)"

# DPDK prefers "arm64" to "aarch64" and does not allow arm64 native target.
if [ "${arch}" == "aarch64" ]; then
    arch="arm64"
    machine="armv8a"
else
    machine="native"
fi

# Try to kill the testpmd.
sudo pgrep testpmd
if [ ${?} -eq "0" ]; then
    success=false
    sudo pkill testpmd
    echo "RC = ${?}"
    for attempt in {1..60}; do
        echo "Checking if testpmd is still alive, attempt nr ${attempt}"
        sudo pgrep testpmd
        if [ ${?} -eq "1" ]; then
            echo "testpmd is dead"
            success=true
            break
        fi
        echo "testpmd is still alive, waiting 1 second"
        sleep 1
    done
    if [ "${success}" = false ]; then
        echo "The command sudo pkill testpmd failed"
        sudo pkill -9 testpmd
        echo "RC = ${?}"
        exit 1
    fi
else
    echo "testpmd is not running"
fi

# Try to kill the l3fwd.
sudo pgrep l3fwd
if [ ${?} -eq "0" ]; then
    success=false
    sudo pkill l3fwd
    echo "RC = ${?}"
    for attempt in {1..60}; do
        echo "Checking if l3fwd is still alive, attempt nr ${attempt}"
        sudo pgrep l3fwd
        if [ ${?} -eq "1" ]; then
            echo "l3fwd is dead"
            success=true
            break
        fi
        echo "l3fwd is still alive, waiting 1 second"
        sleep 1
    done
    if [ "${success}" = false ]; then
        echo "The command sudo pkill l3fwd failed"
        sudo pkill -9 l3fwd
        echo "RC = ${?}"
        exit 1
    fi
else
    echo "l3fwd is not running"
fi

# Remove hugepages.
sudo rm -f /dev/hugepages/*

sleep 2

cd "${ROOTDIR}/${DPDK_DIR}/"
rm -f "${TESTPMDLOG}"
TESTPMD_BIN="./${arch}-${machine}-linuxapp-gcc/app/testpmd"

if [ "${jumbo_frames}" = "yes" ]; then
    sudo sh -c "screen -dmSL DPDK-test ${TESTPMD_BIN} \
        -l ${cpu_corelist} -n 4 --log-level 8 -v -- \
        --numa \
        --nb-ports=2 \
        --portmask=0x3 \
        --nb-cores=${nb_cores} \
        --max-pkt-len=9000 \
        --tx-offloads=0x7FFFFFFF \
        --forward-mode=io \
        --rxq=${queue_nums} \
        --txq=$((${nb_cores} + 1)) \
        --burst=64 \
        --rxd=${rxd} \
        --txd=${txd} \
        --disable-link-check \
        --auto-start"
else
    sudo sh -c "screen -dmSL DPDK-test ${TESTPMD_BIN} \
        -l ${cpu_corelist} -n 4 --log-level 8 -v -- \
        --numa \
        --nb-ports=2 \
        --portmask=0x3 \
        --nb-cores=${nb_cores} \
        --forward-mode=io \
        --rxq=${queue_nums} \
        --txq=$((${nb_cores} + 1)) \
        --burst=64 \
        --rxd=${rxd} \
        --txd=${txd} \
        --disable-link-check \
        --auto-start"
fi

for attempt in {1..60}; do
    echo "Checking if testpmd is alive, attempt nr ${attempt}"
    fgrep "Press enter to exit" "${TESTPMDLOG}"
    if [ "${?}" -eq "0" ]; then
        exit 0
    fi
    sleep 1
done
cat "${TESTPMDLOG}"

exit 1
