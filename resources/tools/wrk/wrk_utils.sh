#!/bin/bash
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

set -x

function wrk_utils.installed {

    # Check if the WRK utility is installed. Fail if not installed.

    # Returns:
    # - 0 - If command is installed.
    # - 1 - If command is not installed.

    set -exuo pipefail

    command -v wrk
}


function wrk_utils.traffic_1_url_1_core {
    # Send traffic
    # - to n URL (NIC)
    # - using n instances of wrk, each on separate core.

    # The CPU used for wrk
    cpu=${1}
    # Total number of threads to use by one instance of wrk to send traffic.
    threads=${2}
    # Total number of HTTP connections to keep open with each thread handling
    # N = connections / threads.
    connections=${3}
    # Duration of the test.
    duration=${4}
    # HTTP header to add to request.
    header=${5}
    # Record a timeout if a response is not received within this amount of time.
    timeout=${6}
    # Path to LuaJIT script.
    script=${7}
    # Print detailed latency statistics.
    latency=${8}
    # URL to send the traffic to.
    url=${9}

    if [ "${timeout}" != "None" ]; then
        timeout="--timeout ${timeout}"
    else
        timeout=""
    fi

    if [ "${latency}" = "True" ]; then
        latency="--latency"
    else
        latency=""
    fi

    if [ "${script}" != "None" ]; then
        script="--script '${script}'"
    else
        script=""
    fi

    if [ "${header}" != "None" ]; then
        header="${header}"
    else
        header="''"
    fi

    taskset --cpu-list ${cpu} \
        wrk --threads ${threads} \
            --connections ${connections} \
            --duration ${duration} \
            --header "${header}" \
            ${timeout} \
            ${script} \
            ${latency} \
            ${url}
}

function wrk_utils.traffic_n_urls_n_cores {
    # Send traffic
    # - to n URL (NIC)
    # - using n instances of wrk, each on separate core.

    # The first CPU used for wrk
    first_cpu=${1}
    # Total number of threads to use by one instance of wrk to send traffic.
    threads=${2}
    # Total number of HTTP connections to keep open with each thread handling
    # N = connections / threads.
    connections=${3}
    # Duration of the test.
    duration=${4}
    # HTTP header to add to request.
    header=${5}
    # Record a timeout if a response is not received within this amount of time.
    timeout=${6}
    # Path to LuaJIT script.
    script=${7}
    # Print detailed latency statistics.
    latency=${8}
    # URL to send the traffic to.
    urls=${9}

    if [ "${timeout}" != "None" ]; then
        timeout="--timeout ${timeout}"
    else
        timeout=""
    fi

    if [ "${latency}" = "True" ]; then
        latency="--latency"
    else
        latency=""
    fi

    if [ "${script}" != "None" ]; then
        script="--script '${script}'"
    else
        script=""
    fi

    if [ "${header}" != "None" ]; then
        header="${header}"
    else
        header="''"
    fi

    urls=$(echo ${urls} | tr ";" "\n")
    cpu=${first_cpu}
    for url in ${urls}; do
        taskset --cpu-list ${cpu} \
            wrk --threads ${threads} \
                --connections ${connections} \
                --duration ${duration} \
                --header "${header}" \
                ${timeout} \
                ${script} \
                ${latency} \
                ${url} &
        cpu=$((cpu+1))
    done

    sleep ${duration}
    sleep 2
}

function wrk_utils.traffic_n_urls_m_cores {
    # Send traffic
    # - to n URL (NIC)
    # - using m instances of wrk, each on separate core.

    # The first CPU used for wrk
    first_cpu=${1}
    # The last CPU used for wrk
    cpus_per_url=${2}
    # Total number of threads to use by one instance of wrk to send traffic.
    threads=${3}
    # Total number of HTTP connections to keep open with each thread handling
    # N = connections / threads.
    connections=${4}
    # Duration of the test.
    duration=${5}
    # HTTP header to add to request.
    header=${6}
    # Record a timeout if a response is not received within this amount of time.
    timeout=${7}
    # Path to LuaJIT script.
    script=${8}
    # Print detailed latency statistics.
    latency=${9}
    # URL to send the traffic to.
    urls=${10}

    if [ "${timeout}" != "None" ]; then
        timeout="--timeout ${timeout}"
    else
        timeout=""
    fi

    if [ "${latency}" = "True" ]; then
        latency="--latency"
    else
        latency=""
    fi

    if [ "${script}" != "None" ]; then
        script="--script '${script}'"
    else
        script=""
    fi

    if [ "${header}" != "None" ]; then
        header="${header}"
    else
        header="''"
    fi

    urls=$(echo ${urls} | tr ";" "\n")

    cpu=${first_cpu}
    for i in `seq 1 ${cpus_per_url}`; do
        for url in ${urls}; do
            taskset --cpu-list ${cpu} \
                wrk --threads ${threads} \
                    --connections ${connections} \
                    --duration ${duration} \
                    --header "${header}" \
                    ${timeout} \
                    ${script} \
                    ${latency} \
                    ${url} &
            cpu=$((cpu+1))
        done
    done

    sleep ${duration}
    sleep 2
}

args=("$@")
case ${1} in
    installed)
        wrk_utils.installed
        ;;
    traffic_1_url_1_core)
        wrk_utils.traffic_1_url_1_core  "${args[@]:1}"
        ;;
    traffic_n_urls_n_cores)
        wrk_utils.traffic_n_urls_n_cores "${args[@]:1}"
        ;;
    traffic_n_urls_m_cores)
        wrk_utils.traffic_n_urls_m_cores "${args[@]:1}"
        ;;
esac
