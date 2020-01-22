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
L3FWDLOG="screenlog.0"
PWDDIR="$(pwd)"

# Setting command line arguments.
cpu_corelist="${1}"
port_config="${2}"
adj_mac0="${3}"
adj_mac1="${4}"
jumbo_frames="${5}"

SCRIPT_NAME="$(basename $0)"

# define a function to get the l3fwd PID.
function get_l3fwd_pid()
{
    pid_l3fwd=`sudo ps -elf | grep l3fwd | grep -v grep | grep -v SCREEN | grep -v ${SCRIPT_NAME} | awk '{print $4}'`
    echo "${pid_l3fwd}"
}

# Try to kill the l3fwd.
# Don't use the pgrep and pkill.
l3fwd_pid=`get_l3fwd_pid`
echo "${l3fwd_pid}"
if [ ! -z "${l3fwd_pid}" ]; then
    success=false
    sudo kill -15 "${l3fwd_pid}"
    echo "RC = ${?}"
    for attempt in {1..60}; do
        echo "Checking if l3fwd is still alive, attempt nr ${attempt}"
        l3fwd_pid=`get_l3fwd_pid`
        if [ -z "${l3fwd_pid}" ]; then
            echo "l3fwd is dead"
            success=true
            break
        fi
        echo "l3fwd is still alive, waiting 1 second"
        sleep 1
    done
    if [ "${success}" = false ]; then
        echo "The command sudo kill -15 l3fwd failed"
        sudo kill -9 "${l3fwd_pid}"
        echo "RC = ${?}"
        exit 1
    fi
else
    echo "l3fwd is not running"
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

# Remove hugepages.
sudo rm -f /dev/hugepages/*

sleep 2

cd "${ROOTDIR}/${DPDK_DIR}/"
rm -f "${L3FWDLOG}"
if [ "${jumbo_frames}" = "yes" ]; then
    sudo sh -c "screen -dmSL DPDK-test ./examples/l3fwd/build/app/l3fwd \
    -l ${cpu_corelist} -n 4 --log-level 8 -- \
    -P -L -p 0x3 --config='${port_config}' \
    --enable-jumbo --max-pkt-len=9000 --eth-dest=0,${adj_mac0} \
    --eth-dest=1,${adj_mac1} --parse-ptype"
else
    sudo sh -c "screen -dmSL DPDK-test ./examples/l3fwd/build/app/l3fwd \
    -l ${cpu_corelist} -n 4 --log-level 8 -- \
    -P -L -p 0x3 --config='${port_config}' \
    --eth-dest=0,${adj_mac0} --eth-dest=1,${adj_mac1} --parse-ptype"
fi

for attempt in {1..60}; do
    echo "Checking if l3fwd is alive, attempt nr ${attempt}"
    fgrep "L3FWD: entering main loop on lcore" "${L3FWDLOG}"
    if [ "${?}" -eq "0" ]; then
        cat "${L3FWDLOG}"
        exit 0
    fi
    sleep 1
done

exit 1
