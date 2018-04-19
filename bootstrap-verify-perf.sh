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

# Space separated list of available testbeds, described by topology files
TOPOLOGIES="topologies/available/lf_testbed1.yaml \
            topologies/available/lf_testbed2.yaml \
            topologies/available/lf_testbed3.yaml"

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
export PYTHONPATH=${SCRIPT_DIR}
export DEBIAN_FRONTEND=noninteractive

# Reservation dir
RESERVATION_DIR="/tmp/reservation_dir"
INSTALLATION_DIR="/tmp/install_dir"

JOB_ARCHIVE_ARTIFACTS=(log.html output.xml report.html)
LOG_ARCHIVE_ARTIFACTS=(log.html output.xml report.html)
JOB_ARCHIVE_DIR="archive"
LOG_ARCHIVE_DIR="$WORKSPACE/archives"
mkdir -p ${JOB_ARCHIVE_DIR}
mkdir -p ${LOG_ARCHIVE_DIR}

# If we run this script from CSIT jobs we want to use stable vpp version
if [[ ${JOB_NAME} == csit-* ]] ;
then
    if [[ ${TEST_TAG} == *DAILY ]] || \
       [[ ${TEST_TAG} == *WEEKLY ]];
    then
        echo Downloading latest VPP packages from NEXUS...
        bash ${SCRIPT_DIR}/resources/tools/scripts/download_install_vpp_pkgs.sh --skip-install
    else
        echo Downloading VPP packages of specific version from NEXUS...
        DPDK_STABLE_VER=$(cat ${SCRIPT_DIR}/DPDK_STABLE_VER)
        VPP_STABLE_VER=$(cat ${SCRIPT_DIR}/VPP_STABLE_VER_UBUNTU)
        bash ${SCRIPT_DIR}/resources/tools/scripts/download_install_vpp_pkgs.sh --skip-install --vpp ${VPP_STABLE_VER} --dkms ${DPDK_STABLE_VER}
    fi
    # Jenkins VPP deb paths (convert to full path)
    VPP_DEBS="$( readlink -f *.deb | tr '\n' ' ' )"
    # Take vpp package and get the vpp version
    VPP_STABLE_VER="$( expr match $(ls *.deb | head -n 1) 'vpp_\(.*\)_amd64.deb' )"

# If we run this script from vpp project we want to use local build
elif [[ ${JOB_NAME} == vpp-* ]] ;
then
    # Use local packages provided as argument list
    # Jenkins VPP deb paths (convert to full path)
    VPP_DEBS="$( readlink -f $@ | tr '\n' ' ' )"
    # Take vpp package and get the vpp version
    VPP_STABLE_VER="$( expr match $1 'vpp-\(.*\)-deb.deb' )"
else
    echo "Unable to identify job type based on JOB_NAME variable: ${JOB_NAME}"
    exit 1
fi

WORKING_TOPOLOGY=""

sudo apt-get -y update
sudo apt-get -y install libpython2.7-dev python-virtualenv

virtualenv --system-site-packages env
. env/bin/activate

echo pip install
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

function cancel_all {
    python ${SCRIPT_DIR}/resources/tools/scripts/topo_installation.py -c -d ${INSTALLATION_DIR} -t $1
    python ${SCRIPT_DIR}/resources/tools/scripts/topo_reservation.py -c -t $1
}

# On script exit we cancel the reservation and installation and delete all vpp
# packages
trap "cancel_all ${WORKING_TOPOLOGY}" EXIT

python ${SCRIPT_DIR}/resources/tools/scripts/topo_installation.py \
    -t ${WORKING_TOPOLOGY} -d ${INSTALLATION_DIR} -p ${VPP_DEBS}
if [ $? -eq 0 ]; then
    echo "VPP Installed on hosts from: ${WORKING_TOPOLOGY}"
    rm vpp*
else
    echo "Failed to copy vpp deb files to DUTs"
    exit 1
fi

# Based on job we will identify DUT
if [[ ${JOB_NAME} == *hc2vpp* ]] ;
then
    DUT="hc2vpp"
elif [[ ${JOB_NAME} == *vpp* ]] ;
then
    DUT="vpp"
elif [[ ${JOB_NAME} == *ligato* ]] ;
then
    DUT="kubernetes"
elif [[ ${JOB_NAME} == *dpdk* ]] ;
then
    DUT="dpdk"
else
    echo "Unable to identify dut type based on JOB_NAME variable: ${JOB_NAME}"
    exit 1
fi

PYBOT_ARGS="--consolewidth 150 --loglevel TRACE --variable TOPOLOGY_PATH:${WORKING_TOPOLOGY} --suite tests.${DUT}.perf"

case "$TEST_TAG" in
    # select specific performance tests based on jenkins job type variable
    PERFTEST_DAILY )
        TAGS=('ndrdiscANDnic_intel-x520-da2AND1t1c'
              'ndrdiscANDnic_intel-x520-da2AND2t2c'
              'ndrdiscAND1t1cANDipsec'
              'ndrdiscAND2t2cANDipsec')
        ;;
    PERFTEST_SEMI_WEEKLY )
        TAGS=('ndrdiscANDnic_intel-x710AND1t1c'
              'ndrdiscANDnic_intel-x710AND2t2c'
              'ndrdiscANDnic_intel-xl710AND1t1c'
              'ndrdiscANDnic_intel-xl710AND2t2c')
        ;;
    PERFTEST_MRR_DAILY )
       TAGS=('mrrAND64bAND1t1c'
             'mrrAND64bAND2t2c'
             'mrrAND64bAND4t4c'
             'mrrAND78bAND1t1c'
             'mrrAND78bAND2t2c'
             'mrrAND78bAND4t4c'
             'mrrANDimixAND1t1cANDvhost'
             'mrrANDimixAND2t2cANDvhost'
             'mrrANDimixAND4t4cANDvhost'
             'mrrANDimixAND1t1cANDmemif'
             'mrrANDimixAND2t2cANDmemif'
             'mrrANDimixAND4t4cANDmemif')
        ;;
    VERIFY-PERF-NDRDISC )
        TAGS=('ndrdiscAND1t1c'
              'ndrdiscAND2t2c')
        ;;
    VERIFY-PERF-PDRDISC )
        TAGS=('pdrdiscAND1t1c'
              'pdrdiscAND2t2c')
        ;;
    VERIFY-PERF-MRR )
        TAGS=('mrrAND1t1c'
              'mrrAND2t2c')
        ;;
    VERIFY-PERF-IP4 )
        TAGS=('mrrANDnic_intel-x520-da2AND1t1cANDip4base'
              'mrrANDnic_intel-x520-da2AND1t1cANDip4fwdANDfib_2m')
        ;;
    VERIFY-PERF-IP6 )
        TAGS=('mrrANDnic_intel-x520-da2AND1t1cANDip6base'
              'mrrANDnic_intel-x520-da2AND1t1cANDip6fwdANDfib_2m')
        ;;
    VERIFY-PERF-L2 )
        TAGS=('mrrANDnic_intel-x520-da2AND1t1cANDl2xcbase'
              'mrrANDnic_intel-x520-da2AND1t1cANDl2bdbase')
        ;;
    VERIFY-PERF-LISP )
        TAGS=('pdrchkANDnic_intel-x520-da2AND1t1cANDlisp')
        ;;
    VERIFY-PERF-VXLAN )
        TAGS=('pdrchkANDnic_intel-x520-da2AND1t1cANDvxlan')
        ;;
    VERIFY-PERF-VHOST )
        TAGS=('pdrdiscANDnic_intel-x520-da2AND1t1cANDvhost')
        ;;
    VERIFY-PERF-MEMIF )
        TAGS=('pdrdiscANDnic_intel-x520-da2AND1t1cANDmemif'
              'pdrdiscANDnic_intel-x520-da2AND2t2cANDmemif'
              'mrrANDnic_intel-x520-da2AND1t1cANDmemif'
              'mrrANDnic_intel-x520-da2AND2t2cANDmemif')
        ;;
    VERIFY-PERF-IPSECHW )
        TAGS=('pdrdiscANDnic_intel-xl710AND1t1cANDipsechw'
              'pdrdiscANDnic_intel-xl710AND2t2cANDipsechw'
              'mrrANDnic_intel-xl710AND1t1cANDipsechw'
              'mrrANDnic_intel-xl710AND2t2cANDipsechw')
        ;;
    VPP-VERIFY-PERF-IP4 )
        TAGS=('mrrANDnic_intel-x520-da2AND1t1cANDip4base'
              'mrrANDnic_intel-x520-da2AND1t1cANDip4fwdANDfib_2m')
        ;;
    VPP-VERIFY-PERF-IP6 )
        TAGS=('mrrANDnic_intel-x520-da2AND1t1cANDip6base'
              'mrrANDnic_intel-x520-da2AND1t1cANDip6fwdANDfib_2m')
        ;;
    VPP-VERIFY-PERF-L2 )
        TAGS=('mrrANDnic_intel-x520-da2AND1t1cANDl2xcbase'
              'mrrANDnic_intel-x520-da2AND1t1cANDl2bdbase')
        ;;
    VPP-VERIFY-PERF-LISP )
        TAGS=('pdrchkANDnic_intel-x520-da2AND1t1cANDlisp')
        ;;
    VPP-VERIFY-PERF-VXLAN )
        TAGS=('pdrchkANDnic_intel-x520-da2AND1t1cANDvxlan')
        ;;
    VPP-VERIFY-PERF-VHOST )
        TAGS=('pdrdiscANDnic_intel-x520-da2AND1t1cANDvhost')
        ;;
    VPP-VERIFY-PERF-MEMIF )
        TAGS=('pdrdiscANDnic_intel-x520-da2AND1t1cANDmemif'
              'pdrdiscANDnic_intel-x520-da2AND2t2cANDmemif'
              'mrrANDnic_intel-x520-da2AND1t1cANDmemif'
              'mrrANDnic_intel-x520-da2AND2t2cANDmemif')
        ;;
    VPP-VERIFY-PERF-ACL )
        TAGS=('pdrdiscANDnic_intel-x520-da2AND1t1cANDacl'
              'pdrdiscANDnic_intel-x520-da2AND2t2cANDacl')
        ;;
    VPP-VERIFY-PERF-IPSECHW )
        TAGS=('pdrdiscANDnic_intel-xl710AND1t1cANDipsechw'
              'pdrdiscANDnic_intel-xl710AND2t2cANDipsechw'
              'mrrANDnic_intel-xl710AND1t1cANDipsechw'
              'mrrANDnic_intel-xl710AND2t2cANDipsechw')
        ;;
    * )
        TAGS=('perftest')
esac

# Catenate TAG selections by 'OR'
printf -v INCLUDES " --include %s " "${TAGS[@]}"

# Execute the test
pybot ${PYBOT_ARGS}${INCLUDES} tests/
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
