#!/bin/bash
# Copyright (c) 2017 Cisco and/or its affiliates.
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

function wrk_utils.install {
    # Install wrk

    # Directory for wrk:
    dir=${1}
    # Force the installation:
    force=${2:-false}

    # Check if wrk is installed:
    if [ "${force}" = true ]; then
        wrk_utils.destroy ${dir}
    else
        which wrk
        if [ $? -eq 0 ]; then
            exit 0
        fi
    fi

    # Install pre-requisites:
    sudo apt-get install build-essential libssl-dev git -y

    # Change the directory:
    cd ${dir}

    # Clone the wrk from git repo:
    git clone https://github.com/wg/wrk.git

    # Build the wrk:
    cd wrk
    make

    # Move the executable to somewhere in the PATH, e.q:
    sudo cp wrk /usr/local/bin
}

function wrk_utils.destroy {
    # Remove wrk

    # Directory for wrk:
    dir=${1}

    sudo rm /usr/local/bin/wrk || true
    sudo rm -rf ${dir}/wrk || true
}

function wrk_utils.traffic_1_url_n_cores {
    # Send traffic
    # - to one URL (NIC)
    # - using n instances of wrk, each on separate core.

    # The first CPU used for wrk
    first_cpu=${1}
    # The last CPU used for wrk
    last_cpu=${2}
    # Total number of threads to use by one instance of wrk to send traffic.
    threads=${3}
    # Total number of HTTP connections to keep open with each thread handling
    # N = connections / threads.
    connections=${4}
    # Duration of the test.
    duration=${5}
    # HTTP header to add to request.
    header=${6:-""}
    # Record a timeout if a response is not received within this amount of time.
    timeout=${7:-""}
    # Path to LuaJIT script.
    script=${8:-""}
    # Print detailed latency statistics.
    latency=${9}
    # URL to send the traffic to.
    url=${10}

    if [ "${timeout}" != "" ]; then
        timeout="--timeout ${timeout}"
    fi

    if [ "${latency}" = true ]; then
        latency="--latency"
    else
        latency=""
    fi

    if [ "${script}" != "" ]; then
        script="--script '${script}'"
    fi

    for i in `seq ${first_cpu} ${last_cpu}`; do
        taskset --cpu-list ${i} \
            wrk --threads ${threads} \
                --connections ${connections} \
                --duration ${duration} \
                --header '${header}' \
                ${timeout} \
                ${script} \
                ${latency} \
                ${url} &
    done
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
    header=${5:-""}
    # Record a timeout if a response is not received within this amount of time.
    timeout=${6:-""}
    # Path to LuaJIT script.
    script=${7:-""}
    # Print detailed latency statistics.
    latency=${8}
    # URL to send the traffic to.
    urls=${9}

    if [ "${timeout}" != "" ]; then
        timeout="--timeout ${timeout}"
    fi

    if [ "${latency}" = true ]; then
        latency="--latency"
    else
        latency=""
    fi

    if [ "${script}" != "" ]; then
        script="--script '${script}'"
    fi

    urls=$(echo ${urls} | tr ";" "\n")
    cpu=${first_cpu}
    for url in ${urls}; do
        taskset --cpu-list ${cpu} \
            wrk --threads ${threads} \
                --connections ${connections} \
                --duration ${duration} \
                --header '${header}' \
                ${timeout} \
                ${script} \
                ${latency} \
                ${url} &
        cpu=`echo $((${cpu}+${1}))`
    done
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
    header=${6:-""}
    # Record a timeout if a response is not received within this amount of time.
    timeout=${7:-""}
    # Path to LuaJIT script.
    script=${8:-""}
    # Print detailed latency statistics.
    latency=${9}
    # URL to send the traffic to.
    urls=${10}

    if [ "${timeout}" != "" ]; then
        timeout="--timeout ${timeout}"
    fi

    if [ "${latency}" = true ]; then
        latency="--latency"
    else
        latency=""
    fi

    if [ "${script}" != "" ]; then
        script="--script '${script}'"
    fi

    urls=$(echo ${urls} | tr ";" "\n")
    cpu=${first_cpu}
    for i in `seq 1 ${cpus_per_url}`; do
        for url in ${urls}; do
            taskset --cpu-list ${cpu} \
                wrk --threads ${threads} \
                    --connections ${connections} \
                    --duration ${duration} \
                    --header '${header}' \
                    ${timeout} \
                    ${script} \
                    ${latency} \
                    ${url} &
            cpu=`echo $((${cpu}+${1}))`
        done
        echo
    done
}
