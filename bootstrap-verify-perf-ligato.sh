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

set -xo pipefail

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

LIGATO_REPO_URL=$(cat ${SCRIPT_DIR}/LIGATO_REPO_URL)
LIGATO_STABLE_VER=$(cat ${SCRIPT_DIR}/LIGATO_STABLE_VER)
VPP_COMMIT=$1
VPP_BUILD=$1
DOCKER_DEB="docker-ce_17.06.2~ce-0~ubuntu_amd64.deb"

# Clone & checkout stable vnf-agent
cd .. && git clone ${LIGATO_REPO_URL}/vpp-agent
# If the git clone fails, complain clearly and exit
if [ $? != 0 ]; then
    echo "Failed to run: git clone --depth 1 ${LIGATO_REPO_URL}/vpp-agent"
    exit 1
fi
cd vpp-agent && git checkout ${LIGATO_STABLE_VER}
# If the git checkout fails, complain clearly and exit
if [ $? != 0 ]; then
    echo "Failed to run: git checkout ${LIGATO_STABLE_VER}"
    exit 1
fi

# Install Docker
wget -q https://download.docker.com/linux/ubuntu/dists/xenial/pool/stable/amd64/${DOCKER_DEB}
sudo dpkg -i ${DOCKER_DEB}
# If installation fails, complain clearly and exit
if [ $? != 0 ]; then
    echo "Failed to install Docker"
    exit 1
fi

# Compile vnf-agent docker image
cd ${SCRIPT_DIR}/../vpp-agent/docker/dev_vpp_agent/ &&\
    ./build.sh --agent ${LIGATO_STABLE_VER} --vpp ${VPP_COMMIT} &&\
    ./shrink.sh
cd ${SCRIPT_DIR}/../vpp-agent/docker/prod_vpp_agent/ &&\
    ./build.sh &&\
    ./shrink.sh
# Export Docker image
sudo docker save prod_vpp_agent_shrink | gzip > prod_vpp_agent_shrink.tar.gz
# If image build fails, complain clearly and exit
if [ $? != 0 ]; then
    echo "Failed to build vpp-agent Docker image."
    exit 1
fi
DOCKER_IMAGE="$( readlink -f prod_vpp_agent_shrink.tar.gz | tr '\n' ' ' )"

cd ${SCRIPT_DIR}

sudo apt-get -y update
sudo apt-get -y install libpython2.7-dev python-virtualenv

WORKING_TOPOLOGY=""
export PYTHONPATH=${SCRIPT_DIR}

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
    python ${SCRIPT_DIR}/resources/tools/scripts/topo_container_copy.py -c -d ${INSTALLATION_DIR} -t $1
    python ${SCRIPT_DIR}/resources/tools/scripts/topo_reservation.py -c -t $1
}

# On script exit we cancel the reservation and installation and delete all vpp
# packages
trap "cancel_all ${WORKING_TOPOLOGY}" EXIT

python ${SCRIPT_DIR}/resources/tools/scripts/topo_container_copy.py\
    -t ${WORKING_TOPOLOGY} -d ${INSTALLATION_DIR} -i ${DOCKER_IMAGE}
if [ $? -eq 0 ]; then
    echo "Docker image copied and loaded on hosts from: ${WORKING_TOPOLOGY}"
else
    echo "Failed to copy and load Docker image to DUTs"
    exit 1
fi

case "$TEST_TAG" in
    # run specific performance tests based on jenkins job type variable
    PERFTEST_DAILY )
        pybot ${PYBOT_ARGS} \
              -v TOPOLOGY_PATH:${WORKING_TOPOLOGY} \
              -v DPDK_TEST:True \
              -s "tests.ligato.perf" \
              --include ndrdiscANDnic_intel-x520-da2AND1t1cORndrdiscANDnic_intel-x520-da2AND2t2c \
              tests/
        RETURN_STATUS=$(echo $?)
        ;;
    PERFTEST_SEMI_WEEKLY )
        pybot ${PYBOT_ARGS} \
              -v TOPOLOGY_PATH:${WORKING_TOPOLOGY} \
              -v DPDK_TEST:True \
              -s "tests.ligato.perf" \
              --include ndrdiscANDnic_intel-x710AND1t1cORndrdiscANDnic_intel-x710AND2t2cORndrdiscANDnic_intel-xl710AND1t1cORndrdiscANDnic_intel-xl710AND2t2c \
              tests/
        RETURN_STATUS=$(echo $?)
        ;;
    VERIFY-PERF-NDRDISC )
        pybot ${PYBOT_ARGS} \
              -v TOPOLOGY_PATH:${WORKING_TOPOLOGY} \
              -v DPDK_TEST:True \
              -s "tests.ligato.perf" \
              --include ndrdiscAND1t1cORndrdiscAND2t2c \
              tests/
        RETURN_STATUS=$(echo $?)
        ;;
    VERIFY-PERF-PDRDISC )
        pybot ${PYBOT_ARGS} \
              -v TOPOLOGY_PATH:${WORKING_TOPOLOGY} \
              -v DPDK_TEST:True \
              -s "tests.ligato.perf" \
              --include pdrdiscAND1t1cORpdrdiscAND2t2c \
              tests/
        RETURN_STATUS=$(echo $?)
        ;;
    VERIFY-PERF-NDRCHK )
        pybot ${PYBOT_ARGS} \
              -v TOPOLOGY_PATH:${WORKING_TOPOLOGY} \
              -v DPDK_TEST:True \
              -s "tests.ligato.perf" \
              --include ndrchkAND1t1cORndrchkAND2t2c \
              tests/
        RETURN_STATUS=$(echo $?)
        ;;
    PERFTEST_NDRCHK_DAILY )
        pybot ${PYBOT_ARGS} \
              -v TOPOLOGY_PATH:${WORKING_TOPOLOGY} \
              -v DPDK_TEST:True \
              -s "tests.ligato.perf" \
              --include ndrchkAND1t1cORndrchkAND2t2c \
              tests/
        RETURN_STATUS=$(echo $?)
        ;;
    VERIFY-PERF-IP4 )
        pybot ${PYBOT_ARGS} \
              -v TOPOLOGY_PATH:${WORKING_TOPOLOGY} \
              -v DPDK_TEST:True \
              -s "tests.ligato.perf" \
              --include ndrdiscANDnic_intel-x520-da2AND1t1cANDip4baseORndrdiscANDnic_intel-x520-da2AND1t1cANDip4fwdANDfib_2m \
              tests/
        RETURN_STATUS=$(echo $?)
        ;;
    VERIFY-PERF-IP6 )
        pybot ${PYBOT_ARGS} \
              -v TOPOLOGY_PATH:${WORKING_TOPOLOGY} \
              -v DPDK_TEST:True \
              -s "tests.ligato.perf" \
              --include ndrdiscANDnic_intel-x520-da2AND1t1cANDip6baseORndrdiscANDnic_intel-x520-da2AND1t1cANDip6fwdANDfib_2m \
              tests/
        RETURN_STATUS=$(echo $?)
        ;;
    VERIFY-PERF-L2 )
        pybot ${PYBOT_ARGS} \
              -v TOPOLOGY_PATH:${WORKING_TOPOLOGY} \
              -v DPDK_TEST:True \
              -s "tests.ligato.perf" \
              --include ndrdiscANDnic_intel-x520-da2AND1t1cANDl2xcbaseORndrdiscANDnic_intel-x520-da2AND1t1cANDl2bdbase \
              tests/
        RETURN_STATUS=$(echo $?)
        ;;
    VERIFY-PERF-LISP )
        pybot ${PYBOT_ARGS} \
              -v TOPOLOGY_PATH:${WORKING_TOPOLOGY} \
              -v DPDK_TEST:True \
              -s "tests.ligato.perf" \
              --include ndrdiscANDnic_intel-x520-da2AND1t1cANDlisp \
              tests/
        RETURN_STATUS=$(echo $?)
        ;;
    VERIFY-PERF-VXLAN )
        pybot ${PYBOT_ARGS} \
              -v TOPOLOGY_PATH:${WORKING_TOPOLOGY} \
              -v DPDK_TEST:True \
              -s "tests.ligato.perf" \
              --include ndrdiscANDnic_intel-x520-da2AND1t1cANDvxlan \
              tests/
        RETURN_STATUS=$(echo $?)
        ;;
    VERIFY-PERF-VHOST )
        pybot ${PYBOT_ARGS} \
              -v TOPOLOGY_PATH:${WORKING_TOPOLOGY} \
              -v DPDK_TEST:True \
              -s "tests.ligato.perf" \
              --include ndrdiscANDnic_intel-x520-da2AND1t1cANDvhost \
              tests/
        RETURN_STATUS=$(echo $?)
        ;;
    VPP-VERIFY-PERF-IP4 )
        pybot ${PYBOT_ARGS} \
              -v TOPOLOGY_PATH:${WORKING_TOPOLOGY} \
              -v DPDK_TEST:True \
              -s "tests.ligato.perf" \
              --include pdrchkANDnic_intel-x520-da2AND1t1cANDip4baseORpdrchkANDnic_intel-x520-da2AND1t1cANDip4fwdANDfib_2m \
              tests/
        RETURN_STATUS=$(echo $?)
        ;;
    VPP-VERIFY-PERF-IP6 )
        pybot ${PYBOT_ARGS} \
              -v TOPOLOGY_PATH:${WORKING_TOPOLOGY} \
              -v DPDK_TEST:True \
              -s "tests.ligato.perf" \
              --include pdrchkANDnic_intel-x520-da2AND1t1cANDip6baseORpdrchkANDnic_intel-x520-da2AND1t1cANDip6fwdANDfib_2m \
              tests/
        RETURN_STATUS=$(echo $?)
        ;;
    VPP-VERIFY-PERF-L2 )
        pybot ${PYBOT_ARGS} \
              -v TOPOLOGY_PATH:${WORKING_TOPOLOGY} \
              -v DPDK_TEST:True \
              -s "tests.ligato.perf" \
              --include pdrchkANDnic_intel-x520-da2AND1t1cANDl2xcbaseORpdrchkANDnic_intel-x520-da2AND1t1cANDl2bdbase \
              tests/
        RETURN_STATUS=$(echo $?)
        ;;
    VPP-VERIFY-PERF-LISP )
        pybot ${PYBOT_ARGS} \
              -v TOPOLOGY_PATH:${WORKING_TOPOLOGY} \
              -v DPDK_TEST:True \
              -s "tests.ligato.perf" \
              --include pdrchkANDnic_intel-x520-da2AND1t1cANDlisp \
              tests/
        RETURN_STATUS=$(echo $?)
        ;;
    VPP-VERIFY-PERF-VXLAN )
        pybot ${PYBOT_ARGS} \
              -v TOPOLOGY_PATH:${WORKING_TOPOLOGY} \
              -v DPDK_TEST:True \
              -s "tests.ligato.perf" \
              --include pdrchkANDnic_intel-x520-da2AND1t1cANDvxlan \
              tests/
        RETURN_STATUS=$(echo $?)
        ;;
    VPP-VERIFY-PERF-VHOST )
        pybot ${PYBOT_ARGS} \
              -v TOPOLOGY_PATH:${WORKING_TOPOLOGY} \
              -v DPDK_TEST:True \
              -s "tests.ligato.perf" \
              --include pdrdiscANDnic_intel-x520-da2AND1t1cANDvhost \
              tests/
        RETURN_STATUS=$(echo $?)
        ;;
    VPP-VERIFY-PERF-ACL )
        pybot ${PYBOT_ARGS} \
              -v TOPOLOGY_PATH:${WORKING_TOPOLOGY} \
              -v DPDK_TEST:True \
              -s "tests.ligato.perf" \
              --include pdrdiscANDnic_intel-x520-da2AND1t1cANDacl \
              --include pdrdiscANDnic_intel-x520-da2AND2t2cANDacl \
              tests/
        RETURN_STATUS=$(echo $?)
        ;;
    PERFTEST_LONG )
        pybot ${PYBOT_ARGS} \
              -v TOPOLOGY_PATH:${WORKING_TOPOLOGY} \
              -v DPDK_TEST:True \
              -s "tests.ligato.perf" \
              --exclude SKIP_PATCH \
              -i NDRPDRDISC \
              tests/
        RETURN_STATUS=$(echo $?)
        ;;
    PERFTEST_SHORT )
        pybot ${PYBOT_ARGS} \
              -v TOPOLOGY_PATH:${WORKING_TOPOLOGY} \
              -v DPDK_TEST:True \
              -s "tests.ligato.perf" \
              -i NDRCHK \
              tests/
        RETURN_STATUS=$(echo $?)
        ;;
    PERFTEST_NIGHTLY )
        #run all available tests
        pybot ${PYBOT_ARGS} \
              -v TOPOLOGY_PATH:${WORKING_TOPOLOGY} \
              -v DPDK_TEST:True \
              -s "tests.ligato.perf" \
              tests/
        RETURN_STATUS=$(echo $?)
        ;;
    * )
        # run full performance test suite and exit on fail
        pybot ${PYBOT_ARGS} \
              -v TOPOLOGY_PATH:${WORKING_TOPOLOGY} \
              -v DPDK_TEST:True \
              -s "tests.ligato.perf" \
              tests/
        RETURN_STATUS=$(echo $?)
esac

# Pybot output post-processing
echo Post-processing test data...

python ${SCRIPT_DIR}/resources/tools/scripts/robot_output_parser.py \
       -i ${SCRIPT_DIR}/output.xml \
       -o ${SCRIPT_DIR}/output_perf_data.xml \
       -v ${VPP_BUILD}
if [ ! $? -eq 0 ]; then
    echo "Parsing ${SCRIPT_DIR}/output.xml failed"
fi

# Archive artifacts
mkdir -p archive
for i in ${ARCHIVE_ARTIFACTS[@]}; do
    cp $( readlink -f ${i} | tr '\n' ' ' ) archive/
done

echo Post-processing finished.

exit ${RETURN_STATUS}
