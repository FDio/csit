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

set -xeu -o pipefail

# FUNCTIONS
function warn () {
    # Error messages should go to standard error.
    echo "$@" >&2
}
function die () {
    status="$1"
    shift
    warn "$@"
    exit "$status"
}

# Trap function
function cancel_all() {
    python ${SCRIPT_DIR}/resources/tools/scripts/topo_cancel.py -t $1
    python ${SCRIPT_DIR}/resources/tools/scripts/topo_reservation.py -c -t $1
}

function help() {
    die 1 "$1 usage: "															# TODO: Help function
}

# TOPOLOGY
# Space separated list of available testbeds, described by topology files
TOPOLOGIES_3N_HSW=(topologies/available/lf_3n_hsw_testbed1.yaml
                   topologies/available/lf_3n_hsw_testbed2.yaml
                   topologies/available/lf_3n_hsw_testbed3.yaml)
TOPOLOGIES_2N_SKX=(topologies/available/lf_2n_skx_testbed21.yaml
                   topologies/available/lf_2n_skx_testbed24.yaml)
TOPOLOGIES_3N_SKX=(topologies/available/lf_3n_skx_testbed31.yaml
                   topologies/available/lf_3n_skx_testbed32.yaml)

# SYSTEM
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
export PYTHONPATH=${SCRIPT_DIR}
export DEBIAN_FRONTEND=noninteractive

# RESERVATION
RESERVATION_DIR="/tmp/reservation_dir"
INSTALLATION_DIR="/tmp/install_dir"

# ARCHIVE
JOB_ARCHIVE_ARTIFACTS=(log.html output.xml report.html)
LOG_ARCHIVE_ARTIFACTS=(log.html output.xml report.html)
JOB_ARCHIVE_DIR="archive"
LOG_ARCHIVE_DIR="$WORKSPACE/archives"
mkdir -p ${JOB_ARCHIVE_DIR}
mkdir -p ${LOG_ARCHIVE_DIR}

# Explicit read-only and exportable
declare -xr $TOPOLOGIES_3N_HSW
declare -xr $TOPOLOGIES_2N_SKX
declare -xr $TOPOLOGIES_3N_SKX
declare -xr $SCRIPT_DIR
declare -xr $RESERVATION_DIR
declare -xr $INSTALLATION_DIR

# JOB SETTING																	#TODO: parametrize script + Add NIC processing
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
        # Fallback to 3-node Haswell by default
        TOPOLOGIES=$TOPOLOGIES_3N_HSW
        TOPOLOGIES_TAGS="3_node_*_link_topo"
        ;;
esac

if [ -z "${TOPOLOGIES}" ]; then
    die 1 "No applicable topology found!"
fi

case ${JOB_NAME} in																#TODO: Parametrize script
    *hc2vpp*)
        DUT="hc2vpp"
        ;;
    *vpp*)
        DUT="vpp"

        case ${JOB_NAME} in
            csit-vpp-*)
                # Use downloaded packages with specific version
                if [[ ${TEST_TAG} == *DAILY ]] || \
                   [[ ${TEST_TAG} == *WEEKLY ]];
                then
                    echo Downloading latest VPP packages from NEXUS...
                    bash ${SCRIPT_DIR}/resources/tools/scripts/download_install_vpp_pkgs.sh \
                        --skip-install
                else
                    echo Downloading VPP packages of specific version from NEXUS...
                    DPDK_STABLE_VER=$(cat ${SCRIPT_DIR}/DPDK_STABLE_VER)
                    VPP_STABLE_VER=$(cat ${SCRIPT_DIR}/VPP_STABLE_VER_UBUNTU)
                    bash ${SCRIPT_DIR}/resources/tools/scripts/download_install_vpp_pkgs.sh \
                        --skip-install --vpp ${VPP_STABLE_VER} --dkms ${DPDK_STABLE_VER}
                fi
                # Jenkins VPP deb paths (convert to full path)
                DUT_PKGS="$( readlink -f ${DUT}*.deb | tr '\n' ' ' )"
                ;;
            vpp-csit-*)
                # Use local packages provided as argument list
                # Jenkins VPP deb paths (convert to full path)
                DUT_PKGS="$( readlink -f $@ | tr '\n' ' ' )"
                ;;
            *)
                die 1 "Unable to identify job type from: ${JOB_NAME}!"
                ;;
        esac
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
            echo "Downloading latest DPDK packages from repo..."
            DPDK_STABLE_VER=$(wget --no-check-certificate --quiet -O - ${DPDK_REPO} | \
                grep -v '2015' | grep -Eo 'dpdk-[^\"]+xz' | tail -1)
        else
            echo "Downloading DPDK packages of specific version from repo..."
            DPDK_STABLE_VER='dpdk-18.05.tar.xz'
        fi
        wget --no-check-certificate ${DPDK_REPO}${DPDK_STABLE_VER}
        ;;
    *)
        die 1 "Unable to identify DUT type from: ${JOB_NAME}!"
        ;;
esac

# ENVIRONMENT PREPARATION
virtualenv --system-site-packages env || {
    die 1 "Failed to create virtual env!"
}
. env/bin/activate || {
    die 1 "Failed to activate virtual env!"
}
pip install -r requirements.txt || {
    die 1 "Failed to install requirements to virtual env!"
}

# We iterate over available topologies and wait until we reserve topology
while :; do
    for TOPOLOGY in ${TOPOLOGIES};
    do
        python ${SCRIPT_DIR}/resources/tools/scripts/topo_reservation.py -t ${TOPOLOGY}
        if [ $? -eq 0 ]; then
            WORKING_TOPOLOGY=${TOPOLOGY}
            echo "Reserved: ${WORKING_TOPOLOGY}"
            # On script exit we clean testbed.
            trap "cancel_all ${WORKING_TOPOLOGY}" EXIT
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

python ${SCRIPT_DIR}/resources/tools/scripts/topo_transfer_items.py \
    -t ${WORKING_TOPOLOGY} -d ${INSTALLATION_DIR}
if [ $? -ne 0 ]; then
    die 1 "Failed to copy DUT packages files to hosts from: ${WORKING_TOPOLOGY}!"
fi

# CSIT EXECUTION
PYBOT_ARGS="--consolewidth 100 --variable TOPOLOGY_PATH:${WORKING_TOPOLOGY} --suite tests.${DUT}.perf"

case "$TEST_TAG" in
    # Select specific performance tests based on jenkins job type variable
    PERFTEST_DAILY )
        TAGS=(ndrpdrANDnic_intel-x520-da2AND1c
              ndrpdrANDnic_intel-x520-da2AND2c
              ndrpdrAND1cANDipsec
              ndrpdrAND2cANDipsec)
        ;;
    PERFTEST_SEMI_WEEKLY )
        TAGS=(ndrpdrANDnic_intel-x710AND1c
              ndrpdrANDnic_intel-x710AND2c
              ndrpdrANDnic_intel-xl710AND1c
              ndrpdrANDnic_intel-xl710AND2c)
        ;;
    PERFTEST_MRR_DAILY )
       TAGS=(mrrAND64bAND1c
             mrrAND64bAND2c
             mrrAND64bAND4c
             mrrAND78bAND1c
             mrrAND78bAND2c
             mrrAND78bAND4c
             mrrANDimixAND1cANDvhost
             mrrANDimixAND2cANDvhost
             mrrANDimixAND4cANDvhost
             mrrANDimixAND1cANDmemif
             mrrANDimixAND2cANDmemif
             mrrANDimixAND4cANDmemif)
        ;;
    VERIFY-PERF-PATCH )
        if [[ -z "$TEST_TAG_STRING" ]]; then
            # If nothing is specified, we will run pre-selected tests by
            # following tags. Items of array will be concatenated by OR in Robot
            # Framework.
            TEST_TAG_ARRAY=(mrrANDnic_intel-x710AND1cAND64bANDip4base
                            mrrANDnic_intel-x710AND1cAND78bANDip6base
                            mrrANDnic_intel-x710AND1cAND64bANDl2bdbase)
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
        TAGS=(perftest)
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
for item in ${JOB_ARCHIVE_ARTIFACTS[@]}; do
    cp $( readlink -f ${item} | tr '\n' ' ' ) ${JOB_ARCHIVE_DIR}/
done
# Archive JOB artifacts to logs.fd.io
for item in ${LOG_ARCHIVE_ARTIFACTS[@]}; do
    cp $( readlink -f ${item} | tr '\n' ' ' ) ${LOG_ARCHIVE_DIR}/
done

exit ${RETURN_STATUS}
