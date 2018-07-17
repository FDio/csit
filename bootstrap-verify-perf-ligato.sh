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

        case ${JOB_NAME} in
            csit-vpp-*)
                # Use downloaded packages with specific version
                mkdir -p vpp_download
                cd vpp_download

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
    *dpdk*)
        DUT="dpdk"
        ;;
    *)
        echo "Unable to identify dut type based on JOB_NAME variable: ${JOB_NAME}"
        exit 1
        ;;
esac

# Extract VPP API to specific folder
dpkg -x vpp_download/vpp_*.deb /tmp/vpp

LIGATO_REPO_URL='https://github.com/ligato/'
VPP_AGENT_STABLE_VER=$(cat ${SCRIPT_DIR}/VPP_AGENT_STABLE_VER)
DOCKER_DEB="docker-ce_18.03.0~ce-0~ubuntu_amd64.deb"

# Clone & checkout stable vnf-agent
cd .. && git clone -b ${VPP_AGENT_STABLE_VER} --single-branch \
    ${LIGATO_REPO_URL}/vpp-agent vpp-agent
# If the git clone fails, complain clearly and exit
if [ $? != 0 ]; then
    echo "Failed to run: git clone ${LIGATO_REPO_URL}/vpp-agent"
    exit 1
fi
cd vpp-agent

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
for f in ${SCRIPT_DIR}/vpp_download/*; do
    sudo docker cp $f agentcnt:/opt/vpp-agent/dev/vpp/build-root/
done

# Recompile vpp-agent
sudo docker exec -i agentcnt \
    script -qec '. ~/.bashrc; cd /go/src/github.com/ligato/vpp-agent && make generate && make install'
if [ $? != 0 ]; then
    echo "Failed to build vpp-agent in Docker image."
    exit 1
fi
# Save container state
sudo docker commit `sudo docker ps -q` dev_vpp_agent:latest

# Build prod_vpp_agent docker image
cd docker/prod/ &&\
    sudo docker build --tag prod_vpp_agent --no-cache .
# Export Docker image
sudo docker save prod_vpp_agent | gzip > prod_vpp_agent.tar.gz
# Kill running agentcnt container
sudo docker rm -f agentcnt
# If image build fails, complain clearly and exit
if [ $? != 0 ]; then
    echo "Failed to build vpp-agent Docker image."
    exit 1
fi
DOCKER_IMAGE="$( readlink -f prod_vpp_agent.tar.gz | tr '\n' ' ' )"

cd ${SCRIPT_DIR}

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

# CSIT EXECUTION
PYBOT_ARGS="--consolewidth 100 --loglevel TRACE --variable TOPOLOGY_PATH:${WORKING_TOPOLOGY} --suite tests.${DUT}.perf"

case "$TEST_TAG" in
    # select specific performance tests based on jenkins job type variable
    VERIFY-PERF-PATCH )
        if [[ -z "$TEST_TAG_STRING" ]]; then
            # If nothing is specified, we will run pre-selected tests by
            # following tags. Items of array will be concatenated by OR in Robot
            # Framework.
            TEST_TAG_ARRAY=('mrrANDnic_intel-x710AND1cAND64bANDip4base'
                            'mrrANDnic_intel-x710AND1cAND78bANDip6base'
                            'mrrANDnic_intel-x710AND1cAND64bANDl2bdbase')
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
