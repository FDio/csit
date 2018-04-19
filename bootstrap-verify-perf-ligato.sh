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
    mkdir -p vpp/build-root
    cd vpp/build-root

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
        #Temporary if arch will not be removed from VPP_STABLE_VER_UBUNTU
        #VPP_STABLE_VER=${VPP_STABLE_VER%_amd64}
        bash ${SCRIPT_DIR}/resources/tools/scripts/download_install_vpp_pkgs.sh \
            --skip-install --vpp ${VPP_STABLE_VER} --dkms ${DPDK_STABLE_VER}
    # Jenkins VPP deb paths (convert to full path)
    VPP_DEBS="$( readlink -f *.deb | tr '\n' ' ' )"
    # Take vpp package and get the vpp version
    VPP_STABLE_VER="$( expr match $(ls *.deb | head -n 1) 'vpp_\(.*\)_amd64.deb' )"

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
cd vpp-agent && git checkout ${VPP_AGENT_STABLE_VER}
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

PYBOT_ARGS="--consolewidth 120 --loglevel TRACE --variable TOPOLOGY_PATH:${WORKING_TOPOLOGY} --suite tests.${DUT}.perf"

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
    VERIFY-PERF-PATCH )
        if [[ -z "$TEST_TAG_STRING" ]]; then
            # If nothing is specified, we will run pre-selected tests by
            # following tags. Items of array will be concatenated by OR in Robot
            # Framework.
            TEST_TAG_ARRAY=('mrrANDnic_intel-x710AND1t1cAND64bANDip4base'
                            'mrrANDnic_intel-x710AND1t1cAND78bANDip6base'
                            'mrrANDnic_intel-x710AND1t1cAND64bANDl2bdbase')
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
        EXPANDED_TAGS+=(" --include ${TAG} ")
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
