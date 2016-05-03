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
TOPOLOGIES="topologies/available/lf_testbed2-710-520.yaml"
VPP_STABLE_VER="1.0.0-437~g8f15e92_amd64"
VPP_REPO_URL="https://nexus.fd.io/service/local/repositories/fd.io.dev/content/io/fd/vpp"

# Reservation dir
RESERVATION_DIR="/tmp/reservation_dir"
INSTALLATION_DIR="/tmp/install_dir"

PYBOT_ARGS="--noncritical MULTI_THREAD"

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
    PYBOT_ARGS="${PYBOT_ARGS} --exitonfailure"
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

CUR_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
WORKING_TOPOLOGY=""
export PYTHONPATH=${CUR_DIR}

sudo apt-get -y update
sudo apt-get -y install libpython2.7-dev python-virtualenv

virtualenv env
. env/bin/activate

echo pip install
pip install -r requirements.txt

# We iterate over available topologies and wait until we reserve topology
while :; do
    for TOPOLOGY in ${TOPOLOGIES};
    do
        python ${CUR_DIR}/resources/tools/topo_reservation.py -t ${TOPOLOGY}
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
    python ${CUR_DIR}/resources/tools/topo_installation.py -c -d ${INSTALLATION_DIR} -t $1
    python ${CUR_DIR}/resources/tools/topo_reservation.py -c -t $1
}

# On script exit we cancel the reservation and installation and delete all vpp
# packages
trap "cancel_all ${WORKING_TOPOLOGY}" EXIT

python ${CUR_DIR}/resources/tools/topo_installation.py -t ${WORKING_TOPOLOGY} \
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
        pybot -L TRACE \
              -v TOPOLOGY_PATH:${WORKING_TOPOLOGY} \
              -i perftest_long \
              tests/
        ;;
    PERFTEST_SHORT )
        pybot -L TRACE \
              -v TOPOLOGY_PATH:${WORKING_TOPOLOGY} \
              -i perftest_short \
              tests/
        ;;
    PERFTEST_LONG_BRIDGE )
        pybot -L TRACE \
              -v TOPOLOGY_PATH:${WORKING_TOPOLOGY} \
              -s performance.long_bridge_domain \
              tests/
        ;;
    PERFTEST_LONG_IPV4 )
        pybot -L TRACE \
              -v TOPOLOGY_PATH:${WORKING_TOPOLOGY} \
              -s performance.long_ipv4 \
              tests/
        ;;
    PERFTEST_LONG_IPV6 )
        pybot -L TRACE \
              -v TOPOLOGY_PATH:${WORKING_TOPOLOGY} \
              -s performance.long_ipv6 \
              tests/
        ;;
    PERFTEST_LONG_XCONNECT )
        pybot -L TRACE \
              -v TOPOLOGY_PATH:${WORKING_TOPOLOGY} \
              -s performance.long_xconnect \
              tests/
        ;;
    PERFTEST_LONG_XCONNECT_DOT1Q )
        pybot -L TRACE \
              -v TOPOLOGY_PATH:${WORKING_TOPOLOGY} \
              -s performance.long_xconnect_dot1q \
              tests/
        ;;
    * )
        # run full performance test suite and exit on fail
        pybot ${PYBOT_ARGS} \
              -L TRACE \
              -v TOPOLOGY_PATH:${WORKING_TOPOLOGY} \
              -s performance \
              tests/
esac

