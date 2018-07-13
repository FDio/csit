#!/bin/bash
# Copyright (c) 2018 Cisco and/or its affiliates.
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

set -xo pipefail

# TOPOLOGY
# Space separated list of available testbeds, described by topology files
TOPOLOGIES_3N_HSW="topologies/available/lf_3n_hsw_testbed1.yaml \
                   topologies/available/lf_3n_hsw_testbed2.yaml \
                   topologies/available/lf_3n_hsw_testbed3.yaml"
TOPOLOGIES_2N_SKX="topologies/available/lf_2n_skx_testbed21.yaml \
                   topologies/available/lf_2n_skx_testbed22.yaml \
                   topologies/available/lf_2n_skx_testbed23.yaml \
                   topologies/available/lf_2n_skx_testbed24.yaml"
TOPOLOGIES_3N_SKX="topologies/available/lf_2n_skx_testbed31.yaml \
                   topologies/available/lf_2n_skx_testbed32.yaml"

# SYSTEM
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
export PYTHONPATH=${SCRIPT_DIR}
export DEBIAN_FRONTEND=noninteractive

# RESERVATION
RESERVATION_DIR="/tmp/reservation_dir"

# ARCHIVE
JOB_ARCHIVE_ARTIFACTS=(log.html output.xml report.html)
LOG_ARCHIVE_ARTIFACTS=(log.html output.xml report.html)
JOB_ARCHIVE_DIR="archive"
LOG_ARCHIVE_DIR="$WORKSPACE/archives"
mkdir -p ${JOB_ARCHIVE_DIR}
mkdir -p ${LOG_ARCHIVE_DIR}

# JOB SETTING
case ${JOB_NAME} in
    *2n-skx*)
        TOPOLOGIES=$TOPOLOGIES_2N_SKX
        TOPOLOGIES_TAGS="2_node_*_link_topo"
        ;;
    *3n-skx*)
        TOPOLOGIES=$TOPOLOGIES_3N_SKX
        TOPOLOGIES_TAGS="3_node_*_link_topo"
        ;;
    *)
        TOPOLOGIES=$TOPOLOGIES_3N_HSW
        TOPOLOGIES_TAGS="3_node_*_link_topo"
        ;;
esac
case ${JOB_NAME} in
    *hc2vpp*)
        DUT="hc2vpp"
        ;;
    *vpp*)
        DUT="vpp"
        ;;
    *ligato*)
        DUT="kubernetes"
        ;;
    *dpdk*)
        DUT="dpdk"

        # If we run this script from CSIT jobs we want to use stable version
        DPDK_REPO='https://fast.dpdk.org/rel/'
        if [[ ${TEST_TAG} == *DAILY ]] || \
           [[ ${TEST_TAG} == *WEEKLY ]];
        then
            echo Downloading latest DPDK packages from repo...
            DPDK_STABLE_VER=$(wget --no-check-certificate --quiet -O - ${DPDK_REPO} | \
                grep -v '2015' | grep -Eo 'dpdk-[^\"]+xz' | tail -1)
        else
            echo Downloading DPDK packages of specific version from repo...
            DPDK_STABLE_VER='dpdk-18.05.tar.xz'
        fi
        wget --no-check-certificate --quiet ${DPDK_REPO}${DPDK_STABLE_VER}
        ;;
    *)
        echo "Unable to identify dut type based on JOB_NAME variable: ${JOB_NAME}"
        exit 1
        ;;
esac


# ENVIRONMENT PREPARATION
virtualenv --system-site-packages env
. env/bin/activate
pip install -r requirements.txt

# We iterate over available topologies and wait until we reserve topology
while :; do
    for TOPOLOGY in ${TOPOLOGIES};
    do
        python ${SCRIPT_DIR}/resources/tools/scripts/topo_reservation.py -t ${TOPOLOGY}
        if [ $? -eq 0 ]; then
            WORKING_TOPOLOGY=${TOPOLOGY}
            echo "Reserved: ${WORKING_TOPOLOGY}"
            break
        fi
    done

    if [ ! -z "${WORKING_TOPOLOGY}" ]; then
        # Exit the infinite while loop if we made a reservation
        break
    fi

    # Wait ~3minutes before next try
    SLEEP_TIME=$[ ( $RANDOM % 20 ) + 180 ]s
    echo "Sleeping ${SLEEP_TIME}"
    sleep ${SLEEP_TIME}
done

#for DPDK test, we don't need to install the VPP deb
function cancel_all {
    python ${SCRIPT_DIR}/resources/tools/scripts/topo_reservation.py -c -t $1
}

# On script exit we cancel the reservation
trap "cancel_all ${WORKING_TOPOLOGY}" EXIT

# CSIT EXECUTION
PYBOT_ARGS="--consolewidth 100 \
            --loglevel TRACE \
            --variable TOPOLOGY_PATH:${WORKING_TOPOLOGY} \
            --suite tests.${DUT}.perf"

case "$TEST_TAG" in
    # select specific performance tests based on jenkins job type variable
    PERFTEST_MRR_DAILY )
       TAGS=('mrrAND64bAND1c'
             'mrrAND64bAND2c'
             'mrrAND64bAND4c'
             'mrrAND78bAND1c'
             'mrrAND78bAND2c'
             'mrrAND78bAND4c'
             'mrrANDimixAND1c'
             'mrrANDimixAND2c'
             'mrrANDimixAND4c')
        ;;
    VERIFY-PERF-PATCH )
        if [[ -z "$TEST_TAG_STRING" ]]; then
            # If nothing is specified, we will run pre-selected tests by
            # following tags. Items of array will be concatenated by OR in Robot
            # Framework.
            TEST_TAG_ARRAY=('mrrANDnic_intel-x710AND1cAND64b')
        else
            # If trigger contains tags, split them into array.
            TEST_TAG_ARRAY=(${TEST_TAG_STRING//:/ })
        fi

        TAGS=()

        for TAG in "${TEST_TAG_ARRAY[@]}"; do
            if [[ ${TAG} == "!"* ]]; then
                # Exclude tags are not prefixed.
                TAGS+=("${TAG}")
            else
                # We will prefix with perftest to prevent running other tests
                # (e.g. Functional).
                prefix="perftestAND"
                if [[ ${JOB_NAME} == vpp-* ]] ; then
                    # Automatic prefixing for VPP jobs to limit the NIC used and
                    # traffic evaluation to MRR.
                    prefix="${prefix}mrrANDnic_intel-x710AND"
                fi
                TAGS+=("$prefix${TAG}")
            fi
        done
        ;;
    * )
        TAGS=('perftest')
esac

# Catenate TAG selections
EXPANDED_TAGS=()
for TAG in "${TAGS[@]}"; do
    if [[ ${TAG} == "!"* ]]; then
        EXPANDED_TAGS+=(" --exclude ${TAG#$"!"} ")
    else
        EXPANDED_TAGS+=(" --include ${TOPOLOGIES_TAGS}AND${TAG} ")
    fi
done

# Execute the test
pybot ${PYBOT_ARGS}${EXPANDED_TAGS[@]} tests/
RETURN_STATUS=$(echo $?)

# Archive JOB artifacts in jenkins
for i in ${JOB_ARCHIVE_ARTIFACTS[@]}; do
    cp $( readlink -f ${i} | tr '\n' ' ' ) ${JOB_ARCHIVE_DIR}/
done
# Archive JOB artifacts to logs.fd.io
for i in ${LOG_ARCHIVE_ARTIFACTS[@]}; do
    cp $( readlink -f ${i} | tr '\n' ' ' ) ${LOG_ARCHIVE_DIR}/
done

exit ${RETURN_STATUS}
