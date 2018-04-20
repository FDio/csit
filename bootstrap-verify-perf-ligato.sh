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

# Reservation dir
RESERVATION_DIR="/tmp/reservation_dir"
INSTALLATION_DIR="/tmp/install_dir"

PYBOT_ARGS="-W 150 -L TRACE"

JOB_ARCHIVE_ARTIFACTS=(log.html output.xml report.html)
LOG_ARCHIVE_ARTIFACTS=(log.html output.xml report.html)
JOB_ARCHIVE_DIR="archive"
LOG_ARCHIVE_DIR="$WORKSPACE/archives"
mkdir -p ${JOB_ARCHIVE_DIR}
mkdir -p ${LOG_ARCHIVE_DIR}

# If we run this script from CSIT jobs we want to use stable vpp version
if [[ ${JOB_NAME} == csit-* ]] ;
then
    mkdir -p vpp/build-root
    cd vpp/build-root

    if [[ ${TEST_TAG} == *DAILY ]] || \
       [[ ${TEST_TAG} == *WEEKLY ]];
    then
        # Download the latest VPP build .deb install packages
        echo Downloading VPP packages...
        bash ${SCRIPT_DIR}/resources/tools/scripts/download_install_vpp_pkgs.sh --skip-install

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
        # Temporary disable using dpdk
        # wget -q "${VPP_REPO_URL}/vpp-dpdk-dkms/${DPDK_STABLE_VER}/vpp-dpdk-dkms-${DPDK_STABLE_VER}${VPP_CLASSIFIER}.deb" || exit
        wget -q "${VPP_REPO_URL}/vpp-lib/${VPP_STABLE_VER}/vpp-lib-${VPP_STABLE_VER}${VPP_CLASSIFIER}.deb" || exit
        wget -q "${VPP_REPO_URL}/vpp-plugins/${VPP_STABLE_VER}/vpp-plugins-${VPP_STABLE_VER}${VPP_CLASSIFIER}.deb" || exit
        VPP_DEBS="$( readlink -f *.deb | tr '\n' ' ' )"
    fi

    # Temporary workaround as ligato docker file requires specific file name
    rename -v 's/^(.*)-(\d.*)-deb.deb/$1_$2.deb/' *.deb
    cd ${SCRIPT_DIR}

# If we run this script from vpp project we want to use local build
elif [[ ${JOB_NAME} == vpp-* ]] ;
then
    mkdir -p vpp/build-root
    # Use local packages provided as argument list
    # Jenkins VPP deb paths (convert to full path)
    VPP_DEBS="$( readlink -f $@ | tr '\n' ' ' )"
    # Take vpp package and get the vpp version
    VPP_STABLE_VER="$( expr match $1 'vpp-\(.*\)-deb.deb' )"
    # Move files to build-root for packing
    for deb in ${VPP_DEBS}; do mv ${deb} vpp/build-root/; done
else
    echo "Unable to identify job type based on JOB_NAME variable: ${JOB_NAME}"
    exit 1
fi

# Extract VPP API to specific folder
dpkg -x vpp/build-root/vpp_${VPP_STABLE_VER}.deb /tmp/vpp
# Compress all VPP debs and remove temporary directory
tar -zcvf ${SCRIPT_DIR}/vpp.tar.gz vpp/* && rm -R vpp

LIGATO_REPO_URL=$(cat ${SCRIPT_DIR}/LIGATO_REPO_URL)
VPP_AGENT_STABLE_VER=$(cat ${SCRIPT_DIR}/VPP_AGENT_STABLE_VER)
DOCKER_DEB="docker-ce_18.03.0~ce-0~ubuntu_amd64.deb"

# Clone & checkout stable vnf-agent
cd .. && git clone ${LIGATO_REPO_URL}/vpp-agent
# If the git clone fails, complain clearly and exit
if [ $? != 0 ]; then
    echo "Failed to run: git clone --depth 1 ${LIGATO_REPO_URL}/vpp-agent"
    exit 1
fi
cd vpp-agent && git checkout tags/${VPP_AGENT_STABLE_VER}
# If the git checkout fails, complain clearly and exit
if [ $? != 0 ]; then
    echo "Failed to run: git checkout ${VPP_AGENT_STABLE_VER}"
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

# Pull ligato/dev_vpp_agent docker image and re-tag as local
sudo docker pull ligato/dev-vpp-agent:${VPP_AGENT_STABLE_VER}
sudo docker tag ligato/dev-vpp-agent:${VPP_AGENT_STABLE_VER}\
    dev_vpp_agent:latest

# Start dev_vpp_agent container as daemon
sudo docker run --rm -itd --name agentcnt dev_vpp_agent bash
# Copy latest vpp api into running container
sudo docker cp /tmp/vpp/usr/share/vpp/api agentcnt:/usr/share/vpp
# Recompile vpp-agent
sudo docker exec -i agentcnt \
    script -qec '. ~/.bashrc; cd /root/go/src/github.com/ligato/vpp-agent && make generate && make install'
if [ $? != 0 ]; then
    echo "Failed to build vpp-agent in Docker image."
    exit 1
fi
# Extract vpp-agent
rm -rf agent
mkdir -p agent
sudo docker cp agentcnt:/root/go/bin/vpp-agent agent/
sudo docker cp agentcnt:/root/go/bin/vpp-agent-ctl agent/
sudo docker cp agentcnt:/root/go/bin/agentctl agent/
tar -zcvf ${SCRIPT_DIR}/../vpp-agent/docker/prod_vpp_agent/agent.tar.gz agent
# Kill running container
sudo docker rm -f agentcnt

# Build prod_vpp_agent docker image
cd ${SCRIPT_DIR}/../vpp-agent/docker/prod_vpp_agent/ &&\
    mv ${SCRIPT_DIR}/vpp.tar.gz . &&\
    sudo docker build -t prod_vpp_agent --no-cache .
# Export Docker image
sudo docker save prod_vpp_agent | gzip > prod_vpp_agent.tar.gz
# If image build fails, complain clearly and exit
if [ $? != 0 ]; then
    echo "Failed to build vpp-agent Docker image."
    exit 1
fi
DOCKER_IMAGE="$( readlink -f prod_vpp_agent.tar.gz | tr '\n' ' ' )"

cd ${SCRIPT_DIR}

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

python ${SCRIPT_DIR}/resources/tools/scripts/topo_container_copy.py \
    -t ${WORKING_TOPOLOGY} -d ${INSTALLATION_DIR} -i ${DOCKER_IMAGE}
if [ $? -eq 0 ]; then
    echo "Docker image copied and loaded on hosts from: ${WORKING_TOPOLOGY}"
else
    echo "Failed to copy and load Docker image to DUTs"
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

case "$TEST_TAG" in
    # run specific performance tests based on jenkins job type variable
    PERFTEST_DAILY )
        pybot ${PYBOT_ARGS} \
              -v TOPOLOGY_PATH:${WORKING_TOPOLOGY} \
              -s "tests.${DUT}.perf" \
              --include ndrdiscANDnic_intel-x520-da2AND1t1cORndrdiscANDnic_intel-x520-da2AND2t2c \
              --include ndrdiscAND1t1cANDipsecORndrdiscAND2t2cANDipsec \
              tests/
        RETURN_STATUS=$(echo $?)
        ;;
    PERFTEST_SEMI_WEEKLY )
        pybot ${PYBOT_ARGS} \
              -v TOPOLOGY_PATH:${WORKING_TOPOLOGY} \
              -s "tests.${DUT}.perf" \
              --include ndrdiscANDnic_intel-x710AND1t1cORndrdiscANDnic_intel-x710AND2t2cORndrdiscANDnic_intel-xl710AND1t1cORndrdiscANDnic_intel-xl710AND2t2c \
              tests/
        RETURN_STATUS=$(echo $?)
        ;;
    PERFTEST_MRR_DAILY )
        pybot ${PYBOT_ARGS} \
              -v TOPOLOGY_PATH:${WORKING_TOPOLOGY} \
              -s "tests.${DUT}.perf" \
              --include mrrAND64bAND1t1c \
              --include mrrAND64bAND2t2c \
              --include mrrAND64bAND4t4c \
              --include mrrAND78bAND1t1c \
              --include mrrAND78bAND2t2c \
              --include mrrAND78bAND4t4c \
              --include mrrANDimixAND1t1cANDvhost \
              --include mrrANDimixAND2t2cANDvhost \
              --include mrrANDimixAND4t4cANDvhost \
              --include mrrANDimixAND1t1cANDmemif \
              --include mrrANDimixAND2t2cANDmemif \
              --include mrrANDimixAND4t4cANDmemif \
              tests/
        RETURN_STATUS=$(echo $?)
        ;;
    VERIFY-PERF-NDRDISC )
        pybot ${PYBOT_ARGS} \
              -v TOPOLOGY_PATH:${WORKING_TOPOLOGY} \
              -s "tests.${DUT}.perf" \
              --include ndrdiscAND1t1cORndrdiscAND2t2c \
              tests/
        RETURN_STATUS=$(echo $?)
        ;;
    VERIFY-PERF-PDRDISC )
        pybot ${PYBOT_ARGS} \
              -v TOPOLOGY_PATH:${WORKING_TOPOLOGY} \
              -s "tests.${DUT}.perf" \
              --include pdrdiscAND1t1cORpdrdiscAND2t2c \
              tests/
        RETURN_STATUS=$(echo $?)
        ;;
    VERIFY-PERF-MRR )
        pybot ${PYBOT_ARGS} \
              -v TOPOLOGY_PATH:${WORKING_TOPOLOGY} \
              -s "tests.${DUT}.perf" \
              --include mrrAND1t1cORmrrAND2t2c \
              tests/
        RETURN_STATUS=$(echo $?)
        ;;
    VERIFY-PERF-IP4 )
        pybot ${PYBOT_ARGS} \
              -v TOPOLOGY_PATH:${WORKING_TOPOLOGY} \
              -s "tests.${DUT}.perf" \
              --include ndrdiscANDnic_intel-x520-da2AND1t1cANDip4baseORndrdiscANDnic_intel-x520-da2AND1t1cANDip4fwdANDfib_2m \
              tests/
        RETURN_STATUS=$(echo $?)
        ;;
    VERIFY-PERF-IP6 )
        pybot ${PYBOT_ARGS} \
              -v TOPOLOGY_PATH:${WORKING_TOPOLOGY} \
              -s "tests.${DUT}.perf" \
              --include ndrdiscANDnic_intel-x520-da2AND1t1cANDip6baseORndrdiscANDnic_intel-x520-da2AND1t1cANDip6fwdANDfib_2m \
              tests/
        RETURN_STATUS=$(echo $?)
        ;;
    VERIFY-PERF-L2 )
        pybot ${PYBOT_ARGS} \
              -v TOPOLOGY_PATH:${WORKING_TOPOLOGY} \
              -s "tests.${DUT}.perf" \
              --include ndrdiscANDnic_intel-x520-da2AND1t1cANDl2xcbaseORndrdiscANDnic_intel-x520-da2AND1t1cANDl2bdbase \
              tests/
        RETURN_STATUS=$(echo $?)
        ;;
    VERIFY-PERF-LISP )
        pybot ${PYBOT_ARGS} \
              -v TOPOLOGY_PATH:${WORKING_TOPOLOGY} \
              -s "tests.${DUT}.perf" \
              --include ndrdiscANDnic_intel-x520-da2AND1t1cANDlisp \
              tests/
        RETURN_STATUS=$(echo $?)
        ;;
    VERIFY-PERF-VXLAN )
        pybot ${PYBOT_ARGS} \
              -v TOPOLOGY_PATH:${WORKING_TOPOLOGY} \
              -s "tests.${DUT}.perf" \
              --include ndrdiscANDnic_intel-x520-da2AND1t1cANDvxlan \
              tests/
        RETURN_STATUS=$(echo $?)
        ;;
    VERIFY-PERF-VHOST )
        pybot ${PYBOT_ARGS} \
              -v TOPOLOGY_PATH:${WORKING_TOPOLOGY} \
              -s "tests.${DUT}.perf" \
              --include ndrdiscANDnic_intel-x520-da2AND1t1cANDvhost \
              tests/
        RETURN_STATUS=$(echo $?)
        ;;
    VERIFY-PERF-MEMIF )
        pybot ${PYBOT_ARGS} \
              -v TOPOLOGY_PATH:${WORKING_TOPOLOGY} \
              -s "tests.${DUT}.perf" \
              --include ndrdiscANDnic_intel-x520-da2AND1t1cANDmemif \
              tests/
        RETURN_STATUS=$(echo $?)
        ;;
    VERIFY-PERF-IPSECHW )
        pybot ${PYBOT_ARGS} \
              -v TOPOLOGY_PATH:${WORKING_TOPOLOGY} \
              -s "tests.${DUT}.perf.crypto" \
              --include ndrdiscANDnic_intel-xl710AND1t1cANDipsechw \
              --include ndrdiscANDnic_intel-xl710AND2t2cANDipsechw \
              --include mrrANDnic_intel-xl710AND1t1cANDipsechw \
              --include mrrANDnic_intel-xl710AND2t2cANDipsechw \
              tests/
        RETURN_STATUS=$(echo $?)
        ;;
    VPP-VERIFY-PERF-IP4 )
        pybot ${PYBOT_ARGS} \
              -v TOPOLOGY_PATH:${WORKING_TOPOLOGY} \
              -s "tests.${DUT}.perf" \
              --include mrrANDnic_intel-x520-da2AND1t1cANDip4baseORmrrANDnic_intel-x520-da2AND1t1cANDip4fwdANDfib_2m \
              tests/
        RETURN_STATUS=$(echo $?)
        ;;
    VPP-VERIFY-PERF-IP6 )
        pybot ${PYBOT_ARGS} \
              -v TOPOLOGY_PATH:${WORKING_TOPOLOGY} \
              -s "tests.${DUT}.perf" \
              --include mrrANDnic_intel-x520-da2AND1t1cANDip6baseORmrrANDnic_intel-x520-da2AND1t1cANDip6fwdANDfib_2m \
              tests/
        RETURN_STATUS=$(echo $?)
        ;;
    VPP-VERIFY-PERF-L2 )
        pybot ${PYBOT_ARGS} \
              -v TOPOLOGY_PATH:${WORKING_TOPOLOGY} \
              -s "tests.${DUT}.perf" \
              --include mrrANDnic_intel-x520-da2AND1t1cANDl2xcbaseORmrrANDnic_intel-x520-da2AND1t1cANDl2bdbase \
              tests/
        RETURN_STATUS=$(echo $?)
        ;;
    VPP-VERIFY-PERF-LISP )
        pybot ${PYBOT_ARGS} \
              -v TOPOLOGY_PATH:${WORKING_TOPOLOGY} \
              -s "tests.${DUT}.perf" \
              --include pdrchkANDnic_intel-x520-da2AND1t1cANDlisp \
              tests/
        RETURN_STATUS=$(echo $?)
        ;;
    VPP-VERIFY-PERF-VXLAN )
        pybot ${PYBOT_ARGS} \
              -v TOPOLOGY_PATH:${WORKING_TOPOLOGY} \
              -s "tests.${DUT}.perf" \
              --include pdrchkANDnic_intel-x520-da2AND1t1cANDvxlan \
              tests/
        RETURN_STATUS=$(echo $?)
        ;;
    VPP-VERIFY-PERF-VHOST )
        pybot ${PYBOT_ARGS} \
              -v TOPOLOGY_PATH:${WORKING_TOPOLOGY} \
              -s "tests.${DUT}.perf" \
              --include pdrdiscANDnic_intel-x520-da2AND1t1cANDvhost \
              tests/
        RETURN_STATUS=$(echo $?)
        ;;
    VPP-VERIFY-PERF-MEMIF )
        pybot ${PYBOT_ARGS} \
              -v TOPOLOGY_PATH:${WORKING_TOPOLOGY} \
              -s "tests.${DUT}.perf" \
              --include pdrdiscANDnic_intel-x520-da2AND1t1cANDmemif \
              --include pdrdiscANDnic_intel-x520-da2AND2t2cANDmemif \
              --include mrrANDnic_intel-x520-da2AND1t1cANDmemif \
              --include mrrANDnic_intel-x520-da2AND2t2cANDmemif \
              tests/
        RETURN_STATUS=$(echo $?)
        ;;
    VPP-VERIFY-PERF-ACL )
        pybot ${PYBOT_ARGS} \
              -v TOPOLOGY_PATH:${WORKING_TOPOLOGY} \
              -s "tests.${DUT}.perf" \
              --include pdrdiscANDnic_intel-x520-da2AND1t1cANDacl \
              --include pdrdiscANDnic_intel-x520-da2AND2t2cANDacl \
              tests/
        RETURN_STATUS=$(echo $?)
        ;;
    VPP-VERIFY-PERF-IPSECHW )
        pybot ${PYBOT_ARGS} \
              -v TOPOLOGY_PATH:${WORKING_TOPOLOGY} \
              -s "tests.${DUT}.perf.crypto" \
              --include pdrdiscANDnic_intel-xl710AND1t1cANDipsechw \
              --include pdrdiscANDnic_intel-xl710AND2t2cANDipsechw \
              --include mrrANDnic_intel-xl710AND1t1cANDipsechw \
              --include mrrANDnic_intel-xl710AND2t2cANDipsechw \
              tests/
        RETURN_STATUS=$(echo $?)
        ;;
    * )
        # run full performance test suite and exit on fail
        pybot ${PYBOT_ARGS} \
              -v TOPOLOGY_PATH:${WORKING_TOPOLOGY} \
              -s "tests.${DUT}.perf" \
              --include ndrdiscAND1t1cAND64b \
              --include ndrdiscAND2t2cAND64b \
              --include pdrdiscAND1t1cAND64b \
              --include pdrdiscAND2t2cAND64b \
              tests/
        RETURN_STATUS=$(echo $?)
esac

# Archive JOB artifacts in jenkins
for i in ${JOB_ARCHIVE_ARTIFACTS[@]}; do
    cp $( readlink -f ${i} | tr '\n' ' ' ) ${JOB_ARCHIVE_DIR}/
done
# Archive JOB artifacts to logs.fd.io
for i in ${LOG_ARCHIVE_ARTIFACTS[@]}; do
    cp $( readlink -f ${i} | tr '\n' ' ' ) ${LOG_ARCHIVE_DIR}/
done

exit ${RETURN_STATUS}
