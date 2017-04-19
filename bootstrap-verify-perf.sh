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

set -x

# Space separated list of available testbeds, described by topology files
TOPOLOGIES="topologies/available/lf_testbed1.yaml \
            topologies/available/lf_testbed2.yaml \
            topologies/available/lf_testbed3.yaml"

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Reservation dir
RESERVATION_DIR="/tmp/reservation_dir"
INSTALLATION_DIR="/tmp/install_dir"

PYBOT_ARGS="-W 150 -L TRACE"

ARCHIVE_ARTIFACTS=(log.html output.xml report.html output_perf_data.xml)

# If we run this script from CSIT jobs we want to use stable vpp version
if [[ ${JOB_NAME} == csit-* ]] ;
then
    mkdir vpp_download
    cd vpp_download

    if [[ ${TEST_TAG} == "PERFTEST_NIGHTLY" ]] ;
    then
        # Download the latest VPP build .deb install packages
        echo Downloading VPP packages...
        bash ${SCRIPT_DIR}/resources/tools/download_install_vpp_pkgs.sh --skip-install

        VPP_DEBS="$( readlink -f *.deb | tr '\n' ' ' )"
        # Take vpp package and get the vpp version
        VPP_STABLE_VER="$( expr match $(ls *.deb | head -n 1) 'vpp-\(.*\)-deb.deb' )"
    else
        DPDK_STABLE_VER=$(cat ${SCRIPT_DIR}/DPDK_STABLE_VER)_amd64
        VPP_REPO_URL=$(cat ${SCRIPT_DIR}/VPP_REPO_URL_UBUNTU)
        VPP_STABLE_VER=$(cat ${SCRIPT_DIR}/VPP_STABLE_VER_UBUNTU)
        VPP_CLASSIFIER="-deb"
        # Download vpp build from nexus and set VPP_DEBS variable
        wget -q "${VPP_REPO_URL}/vpp/${VPP_STABLE_VER}/vpp-${VPP_STABLE_VER}${VPP_CLASSIFIER}.deb" || exit
        wget -q "${VPP_REPO_URL}/vpp-dbg/${VPP_STABLE_VER}/vpp-dbg-${VPP_STABLE_VER}${VPP_CLASSIFIER}.deb" || exit
        wget -q "${VPP_REPO_URL}/vpp-dev/${VPP_STABLE_VER}/vpp-dev-${VPP_STABLE_VER}${VPP_CLASSIFIER}.deb" || exit
        wget -q "${VPP_REPO_URL}/vpp-dpdk-dkms/${DPDK_STABLE_VER}/vpp-dpdk-dkms-${DPDK_STABLE_VER}${VPP_CLASSIFIER}.deb" || exit
        wget -q "${VPP_REPO_URL}/vpp-lib/${VPP_STABLE_VER}/vpp-lib-${VPP_STABLE_VER}${VPP_CLASSIFIER}.deb" || exit
        wget -q "${VPP_REPO_URL}/vpp-plugins/${VPP_STABLE_VER}/vpp-plugins-${VPP_STABLE_VER}${VPP_CLASSIFIER}.deb" || exit
        VPP_DEBS="$( readlink -f *.deb | tr '\n' ' ' )"
    fi

    cd ..

# If we run this script from vpp project we want to use local build
elif [[ ${JOB_NAME} == vpp-* ]] ;
then
    # Use local packages provided as argument list
    # Jenkins VPP deb paths (convert to full path)
    VPP_DEBS="$( readlink -f $@ | tr '\n' ' ' )"
    # Take vpp package and get the vpp version
    VPP_STABLE_VER="$( expr match $1 'vpp-\(.*\)-deb.deb' )"
    # Download DPDK parts not included in dpdk plugin of vpp build
    DPDK_STABLE_VER=$(cat ${SCRIPT_DIR}/DPDK_STABLE_VER)_amd64
    VPP_REPO_URL=$(cat ${SCRIPT_DIR}/VPP_REPO_URL_UBUNTU)
    VPP_CLASSIFIER="-deb"
    wget -q "${VPP_REPO_URL}/vpp-dpdk-dkms/${DPDK_STABLE_VER}/vpp-dpdk-dkms-${DPDK_STABLE_VER}${VPP_CLASSIFIER}.deb" || exit
    VPP_DEBS+=($( readlink -f vpp-dpdk-dkms-${DPDK_STABLE_VER}${VPP_CLASSIFIER}.deb ))
else
    echo "Unable to identify job type based on JOB_NAME variable: ${JOB_NAME}"
    exit 1
fi

WORKING_TOPOLOGY=""
export PYTHONPATH=${SCRIPT_DIR}

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
        python ${SCRIPT_DIR}/resources/tools/topo_reservation.py -t ${TOPOLOGY}
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
    python ${SCRIPT_DIR}/resources/tools/topo_installation.py -c -d ${INSTALLATION_DIR} -t $1
    python ${SCRIPT_DIR}/resources/tools/topo_reservation.py -c -t $1
}

# On script exit we cancel the reservation and installation and delete all vpp
# packages
trap "cancel_all ${WORKING_TOPOLOGY}" EXIT

python ${SCRIPT_DIR}/resources/tools/topo_installation.py -t ${WORKING_TOPOLOGY} \
                                                       -d ${INSTALLATION_DIR} \
                                                       -p ${VPP_DEBS}
if [ $? -eq 0 ]; then
    echo "VPP Installed on hosts from: ${WORKING_TOPOLOGY}"
else
    echo "Failed to copy vpp deb files to DUTs"
    exit 1
fi

case "$TEST_TAG" in
    # run specific performance tests based on jenkins job type variable
    PERFTEST_DAILY )
        pybot ${PYBOT_ARGS} \
              -v TOPOLOGY_PATH:${WORKING_TOPOLOGY} \
              -s "tests.perf" \
              --include ndrdiscANDnic_intel-x520-da2AND1t1cORndrdiscANDnic_intel-x520-da2AND2t2c \
              tests/
        RETURN_STATUS=$(echo $?)
        ;;
    PERFTEST_SEMI_WEEKLY )
        pybot ${PYBOT_ARGS} \
              -v TOPOLOGY_PATH:${WORKING_TOPOLOGY} \
              -s "tests.perf" \
              --include ndrdiscANDnic_intel-x710AND1t1cORndrdiscANDnic_intel-x710AND2t2cORndrdiscANDnic_intel-xl710AND1t1cORndrdiscANDnic_intel-xl710AND2t2c \
              tests/
        RETURN_STATUS=$(echo $?)
        ;;
    VERIFY-PERF-NDRDISC )
        pybot ${PYBOT_ARGS} \
              -v TOPOLOGY_PATH:${WORKING_TOPOLOGY} \
              -s "tests.perf" \
              --include ndrdiscAND1t1cORndrdiscAND2t2c \
              tests/
        RETURN_STATUS=$(echo $?)
        ;;
    VERIFY-PERF-PDRDISC )
        pybot ${PYBOT_ARGS} \
              -v TOPOLOGY_PATH:${WORKING_TOPOLOGY} \
              -s "tests.perf" \
              --include pdrdiscAND1t1cORpdrdiscAND2t2c \
              tests/
        RETURN_STATUS=$(echo $?)
        ;;
    VERIFY-PERF-NDRCHK )
        pybot ${PYBOT_ARGS} \
              -v TOPOLOGY_PATH:${WORKING_TOPOLOGY} \
              -s "tests.perf" \
              --include ndrchkAND1t1cORndrchkAND2t2c \
              tests/
        RETURN_STATUS=$(echo $?)
        ;;
    PERFTEST_NDRCHK_DAILY )
        pybot ${PYBOT_ARGS} \
              -v TOPOLOGY_PATH:${WORKING_TOPOLOGY} \
              -s "tests.perf" \
              --include ndrchkAND1t1cORndrchkAND2t2c \
              tests/
        RETURN_STATUS=$(echo $?)
        ;;
    VERIFY-PERF-IP4 )
        pybot ${PYBOT_ARGS} \
              -v TOPOLOGY_PATH:${WORKING_TOPOLOGY} \
              -s "tests.perf" \
              --include ndrdiscANDnic_intel-x520-da2AND1t1cANDip4baseORndrdiscANDnic_intel-x520-da2AND1t1cANDip4fwdANDfib_2m \
              tests/
        RETURN_STATUS=$(echo $?)
        ;;
    VERIFY-PERF-IP6 )
        pybot ${PYBOT_ARGS} \
              -v TOPOLOGY_PATH:${WORKING_TOPOLOGY} \
              -s "tests.perf" \
              --include ndrdiscANDnic_intel-x520-da2AND1t1cANDip6baseORndrdiscANDnic_intel-x520-da2AND1t1cANDip6fwdANDfib_2m \
              tests/
        RETURN_STATUS=$(echo $?)
        ;;
    VERIFY-PERF-L2 )
        pybot ${PYBOT_ARGS} \
              -v TOPOLOGY_PATH:${WORKING_TOPOLOGY} \
              -s "tests.perf" \
              --include ndrdiscANDnic_intel-x520-da2AND1t1cANDl2xcbaseORndrdiscANDnic_intel-x520-da2AND1t1cANDl2bdbase \
              tests/
        RETURN_STATUS=$(echo $?)
        ;;
    VERIFY-PERF-LISP )
        pybot ${PYBOT_ARGS} \
              -v TOPOLOGY_PATH:${WORKING_TOPOLOGY} \
              -s "tests.perf" \
              --include ndrdiscANDnic_intel-x520-da2AND1t1cANDlisp \
              tests/
        RETURN_STATUS=$(echo $?)
        ;;
    VERIFY-PERF-VXLAN )
        pybot ${PYBOT_ARGS} \
              -v TOPOLOGY_PATH:${WORKING_TOPOLOGY} \
              -s "tests.perf" \
              --include ndrdiscANDnic_intel-x520-da2AND1t1cANDvxlan \
              tests/
        RETURN_STATUS=$(echo $?)
        ;;
    VERIFY-PERF-VHOST )
        pybot ${PYBOT_ARGS} \
              -v TOPOLOGY_PATH:${WORKING_TOPOLOGY} \
              -s "tests.perf" \
              --include ndrdiscANDnic_intel-x520-da2AND1t1cANDvhost \
              tests/
        RETURN_STATUS=$(echo $?)
        ;;
    PERFTEST_LONG )
        pybot ${PYBOT_ARGS} \
              -v TOPOLOGY_PATH:${WORKING_TOPOLOGY} \
              -s "tests.perf" \
              --exclude SKIP_PATCH \
              -i NDRPDRDISC \
              tests/
        RETURN_STATUS=$(echo $?)
        ;;
    PERFTEST_SHORT )
        pybot ${PYBOT_ARGS} \
              -v TOPOLOGY_PATH:${WORKING_TOPOLOGY} \
              -s "tests.perf" \
              -i NDRCHK \
              tests/
        RETURN_STATUS=$(echo $?)
        ;;
    PERFTEST_NIGHTLY )
        #run all available tests
        pybot ${PYBOT_ARGS} \
              -v TOPOLOGY_PATH:${WORKING_TOPOLOGY} \
              -s "tests.perf" \
              tests/
        RETURN_STATUS=$(echo $?)
        ;;
    * )
        # run full performance test suite and exit on fail
        pybot ${PYBOT_ARGS} \
              -v TOPOLOGY_PATH:${WORKING_TOPOLOGY} \
              -s "tests.perf" \
              tests/
        RETURN_STATUS=$(echo $?)
esac

# Pybot output post-processing
echo Post-processing test data...

python ${SCRIPT_DIR}/resources/tools/robot_output_parser.py \
       -i ${SCRIPT_DIR}/output.xml \
       -o ${SCRIPT_DIR}/output_perf_data.xml \
       -v ${VPP_STABLE_VER}
if [ ! $? -eq 0 ]; then
    echo "Parsing ${SCRIPT_DIR}/output.xml failed"
fi

# Archive artifacts
mkdir archive
for i in ${ARCHIVE_ARTIFACTS[@]}; do
    cp $( readlink -f ${i} | tr '\n' ' ' ) archive/
done

echo Post-processing finished.

exit ${RETURN_STATUS}
