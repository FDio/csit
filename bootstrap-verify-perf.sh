#!/bin/bash
# Copyright (c) 2016 Cisco and/or its affiliates.
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
TOPOLOGIES="topologies/available/lf_testbed1.yaml"
#TOPOLOGIES="topologies/available/lf_testbed1-X710-X520.yaml \
#            topologies/available/lf_testbed2-X710-X520.yaml \
#            topologies/available/lf_testbed3-X710-X520.yaml"

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

VPP_STABLE_VER=$(cat ${SCRIPT_DIR}/VPP_STABLE_VER)
VPP_REPO_URL=$(cat ${SCRIPT_DIR}/VPP_REPO_URL)

# Reservation dir
RESERVATION_DIR="/tmp/reservation_dir"
INSTALLATION_DIR="/tmp/install_dir"

PYBOT_ARGS="-W 150 --noncritical PERFTEST --exclude SKIP_PATCH"

ARCHIVE_ARTIFACTS=(log.html output.xml report.html output_perf_data.xml)

# If we run this script from CSIT jobs we want to use stable vpp version
if [[ ${JOB_NAME} == csit-* ]] ;
then
    mkdir vpp_download
    cd vpp_download
    #download vpp build from nexus and set VPP_DEBS variable
    wget -q "${VPP_REPO_URL}/vpp/${VPP_STABLE_VER}/vpp-${VPP_STABLE_VER}.deb" || exit
    wget -q "${VPP_REPO_URL}/vpp-dbg/${VPP_STABLE_VER}/vpp-dbg-${VPP_STABLE_VER}.deb" || exit
    wget -q "${VPP_REPO_URL}/vpp-dev/${VPP_STABLE_VER}/vpp-dev-${VPP_STABLE_VER}.deb" || exit
    wget -q "${VPP_REPO_URL}/vpp-dpdk-dev/${VPP_STABLE_VER}/vpp-dpdk-dev-${VPP_STABLE_VER}.deb" || exit
    wget -q "${VPP_REPO_URL}/vpp-dpdk-dkms/${VPP_STABLE_VER}/vpp-dpdk-dkms-${VPP_STABLE_VER}.deb" || exit
    wget -q "${VPP_REPO_URL}/vpp-lib/${VPP_STABLE_VER}/vpp-lib-${VPP_STABLE_VER}.deb" || exit
    VPP_DEBS="$( readlink -f *.deb | tr '\n' ' ' )"
    cd ..

# If we run this script from vpp project we want to use local build
elif [[ ${JOB_NAME} == vpp-* ]] ;
then
    #use local packages provided as argument list
    # Jenkins VPP deb paths (convert to full path)
    VPP_DEBS="$( readlink -f $@ | tr '\n' ' ' )"
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
    PERFTEST_LONG )
        pybot ${PYBOT_ARGS} \
              -L TRACE \
              -v TOPOLOGY_PATH:${WORKING_TOPOLOGY} \
              -i perftest_long \
              tests/
        RETURN_STATUS=$(echo $?)
        ;;
    PERFTEST_SHORT )
        pybot ${PYBOT_ARGS} \
              -L TRACE \
              -v TOPOLOGY_PATH:${WORKING_TOPOLOGY} \
              -i perftest_short \
              tests/
        RETURN_STATUS=$(echo $?)
        ;;
    PERFTEST_LONG_BRIDGE )
        pybot ${PYBOT_ARGS} \
              -L TRACE \
              -v TOPOLOGY_PATH:${WORKING_TOPOLOGY} \
              -s "performance.Long_Bridge_Domain*" \
              tests/
        RETURN_STATUS=$(echo $?)
        ;;
    PERFTEST_LONG_IPV4 )
        pybot ${PYBOT_ARGS} \
              -L TRACE \
              -v TOPOLOGY_PATH:${WORKING_TOPOLOGY} \
              -s "performance.Long_IPv4*" \
              tests/
        RETURN_STATUS=$(echo $?)
        ;;
    PERFTEST_LONG_IPV6 )
        pybot ${PYBOT_ARGS} \
              -L TRACE \
              -v TOPOLOGY_PATH:${WORKING_TOPOLOGY} \
              -s "performance.Long_IPv6*" \
              tests/
        RETURN_STATUS=$(echo $?)
        ;;
    PERFTEST_LONG_XCONNECT )
        pybot ${PYBOT_ARGS} \
              -L TRACE \
              -v TOPOLOGY_PATH:${WORKING_TOPOLOGY} \
              -s "performance.Long_Xconnect*" \
              tests/
        RETURN_STATUS=$(echo $?)
        ;;
    PERFTEST_LONG_XCONNECT_DOT1Q )
        pybot ${PYBOT_ARGS} \
              -L TRACE \
              -v TOPOLOGY_PATH:${WORKING_TOPOLOGY} \
              -s "performance.Long_Xconnect_Dot1q*" \
        RETURN_STATUS=$(echo $?)
        ;;
    PERFTEST_NDR )
        pybot ${PYBOT_ARGS} \
              -L TRACE \
              -v TOPOLOGY_PATH:${WORKING_TOPOLOGY} \
              -s performance -i NDR \
              tests/
        RETURN_STATUS=$(echo $?)
        ;;
    PERFTEST_PDR )
        pybot ${PYBOT_ARGS} \
              -L TRACE \
              -v TOPOLOGY_PATH:${WORKING_TOPOLOGY} \
              -s performance -i PDR \
              tests/
        RETURN_STATUS=$(echo $?)
        ;;
    * )
        # run full performance test suite and exit on fail
        pybot ${PYBOT_ARGS} \
              -L TRACE \
              -v TOPOLOGY_PATH:${WORKING_TOPOLOGY} \
              -s performance \
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
