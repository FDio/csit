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
                   topologies/available/lf_2n_skx_testbed24.yaml"
TOPOLOGIES_3N_SKX="topologies/available/lf_3n_skx_testbed31.yaml \
                   topologies/available/lf_3n_skx_testbed32.yaml"

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
                echo "Unable to identify job type based on JOB_NAME variable: ${JOB_NAME}"
                exit 1
                ;;
        esac
        ;;
    *ligato*)
        DUT="kubernetes"
        ;;
    *dpdk*)
        DUT="dpdk"
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

if [ -z "${TOPOLOGIES}" ]; then
    echo "No applicable topology found!"
    exit 1
fi
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

function cancel_all {
    python ${SCRIPT_DIR}/resources/tools/scripts/topo_installation.py -c -d ${INSTALLATION_DIR} -t $1
    python ${SCRIPT_DIR}/resources/tools/scripts/topo_reservation.py -c -t $1
}

# On script exit we cancel the reservation and installation and delete all vpp
# packages
trap "cancel_all ${WORKING_TOPOLOGY}" EXIT

python ${SCRIPT_DIR}/resources/tools/scripts/topo_installation.py \
    -t ${WORKING_TOPOLOGY} -d ${INSTALLATION_DIR} -p ${DUT_PKGS}
if [ $? -eq 0 ]; then
    echo "DUT installed on hosts from: ${WORKING_TOPOLOGY}"
else
    echo "Failed to copy DUT packages files to hosts from: ${WORKING_TOPOLOGY}"
    exit 1
fi

# CSIT EXECUTION
PYBOT_ARGS="--consolewidth 100 \
            --loglevel TRACE \
            --variable TOPOLOGY_PATH:${WORKING_TOPOLOGY} \
            --suite tests.${DUT}.perf"

case "$TEST_TAG" in
    # select specific performance tests based on jenkins job type variable
    PERFTEST_DAILY )
        TAGS=('ndrdiscANDnic_intel-x520-da2AND1c'
              'ndrdiscANDnic_intel-x520-da2AND2c'
              'ndrpdrANDnic_intel-x520-da2AND1c'
              'ndrpdrANDnic_intel-x520-da2AND2c'
              'ndrdiscAND1cANDipsec'
              'ndrdiscAND2cANDipsec')
        ;;
    PERFTEST_SEMI_WEEKLY )
        TAGS=('ndrdiscANDnic_intel-x710AND1c'
              'ndrdiscANDnic_intel-x710AND2c'
              'ndrdiscANDnic_intel-xl710AND1c'
              'ndrdiscANDnic_intel-xl710AND2c')
        ;;
    PERFTEST_MRR_DAILY )
       TAGS=('mrrAND64bAND1c'
             'mrrAND64bAND2c'
             'mrrAND64bAND4c'
             'mrrAND78bAND1c'
             'mrrAND78bAND2c'
             'mrrAND78bAND4c'
             'mrrANDimixAND1cANDvhost'
             'mrrANDimixAND2cANDvhost'
             'mrrANDimixAND4cANDvhost'
             'mrrANDimixAND1cANDmemif'
             'mrrANDimixAND2cANDmemif'
             'mrrANDimixAND4cANDmemif')
        ;;
    VERIFY-PERF-PATCH )
        if [[ -z "$TEST_TAG_STRING" ]]; then
            # If nothing is specified, we will run pre-selected tests by
            # following tags. Items of array will be concatenated by OR in Robot
            # Framework.
            TEST_TAG_ARRAY=('ndrpdrAND64B'
                            'ndrpdrAND78B'
                            '!nic_intel-x520-da2'
                            '!nic_intel-xl710'
                            '!nic_cisco-vic-1227'
                            '!nic_cisco-vic-1385'
                            '!acl10'
                            '!100_flows'
                            '!100k_flows'
                            '!lxc'
                            '!single_memif'
                            '!vhost')
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
