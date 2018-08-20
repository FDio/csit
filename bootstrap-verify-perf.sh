#!/usr/bin/env bash
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

# FUNCTIONS
function warn () {
    # Prints the message to standard error.
    echo "$@" >&2
}

function die () {
    # Prints the message to standard error end exit with error code specified
    # by first argument.
    status="$1"
    shift
    warn "$@"
    exit "$status"
}

function help () {
    # Displays help message.
    die 1 "Usage: `basename $0` csit-[dpdk|vpp|ligato]-[2n-skx|3n-skx|3n-hsw]"
}

function cancel_all () {
    # Trap function to get into consistent state.
    python ${SCRIPT_DIR}/resources/tools/scripts/topo_cleanup.py -t $1 || {
        die 1 "Failure during execution of topology cleanup script!"
    }
    python ${SCRIPT_DIR}/resources/tools/scripts/topo_reservation.py -c -t $1 || {
        die 1 "Failure during execution of topology un-reservation script!"
    }
}

# VARIABLES
# Space separated list of available testbeds, described by topology files
TOPOLOGIES_3N_HSW=(topologies/available/lf_3n_hsw_testbed1.yaml
                   topologies/available/lf_3n_hsw_testbed2.yaml
                   topologies/available/lf_3n_hsw_testbed3.yaml)
TOPOLOGIES_2N_SKX=(topologies/available/lf_2n_skx_testbed21.yaml
                   topologies/available/lf_2n_skx_testbed24.yaml)
TOPOLOGIES_3N_SKX=(topologies/available/lf_3n_skx_testbed31.yaml
                   topologies/available/lf_3n_skx_testbed32.yaml)

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
export PYTHONPATH=${SCRIPT_DIR}

RESERVATION_DIR="/tmp/reservation_dir"
DOWNLOAD_DIR="${SCRIPT_DIR}/download_dir"
ARCHIVE_DIR="${SCRIPT_DIR}/archive"

mkdir -p ${DOWNLOAD_DIR} || {
    die 1 "Failed to create download dir!"
}
mkdir -p ${ARCHIVE_DIR} || {
    die 1 "Failed to create archive dir!"
}

# Get test code.
TEST_CODE=${JOB_NAME-}
if [[ -z ${TEST_CODE} ]]; then
    TEST_CODE=${1}
    shift
fi

# TOPOLOGY SELECTION
case "$TEST_CODE" in
    *2n-skx*)
        TOPOLOGIES=$TOPOLOGIES_2N_SKX
        TOPOLOGIES_TAGS="2_node_*_link_topo"
        ;;
    *3n-skx*)
        TOPOLOGIES=$TOPOLOGIES_3N_SKX
        TOPOLOGIES_TAGS="3_node_*_link_topo"
        ;;
    *)
        # Fallback to 3-node Haswell by default (backward compatibility)
        TOPOLOGIES=$TOPOLOGIES_3N_HSW
        TOPOLOGIES_TAGS="3_node_*_link_topo"
        ;;
esac

if [[ -z "${TOPOLOGIES}" ]]; then
    die 1 "No applicable topology found!"
fi

cd ${DOWNLOAD_DIR}
case "$TEST_CODE" in
    *hc2vpp*)
        DUT="hc2vpp"
        ;;
    *vpp*)
        DUT="vpp"

        case "$TEST_CODE" in
            csit-vpp-*)
                # Use downloaded packages with specific version
                if [[ "$TEST_CODE" == *daily* ]] || \
                   [[ "$TEST_CODE" == *weekly* ]] || \
                   [[ "$TEST_CODE" == *timed* ]];
                then
                    echo Downloading latest VPP packages from NEXUS...
                    bash ${SCRIPT_DIR}/resources/tools/scripts/download_install_vpp_pkgs.sh \
                        --skip-install || {
                        die 1 "Failed to get VPP packages!"
                    }
                else
                    echo Downloading VPP packages of specific version from NEXUS...
                    DPDK_STABLE_VER=$(cat ${SCRIPT_DIR}/DPDK_STABLE_VER)
                    VPP_STABLE_VER=$(cat ${SCRIPT_DIR}/VPP_STABLE_VER_UBUNTU)
                    bash ${SCRIPT_DIR}/resources/tools/scripts/download_install_vpp_pkgs.sh \
                        --skip-install --vpp ${VPP_STABLE_VER} --dkms ${DPDK_STABLE_VER} || {
                        die 1 "Failed to get VPP packages!"
                    }
                fi
                ;;
            vpp-csit-*)
                # Use local built packages.
                mv ../${DUT}*.deb ${DOWNLOAD_DIR}/
                ;;
            *)
                die 1 "Unable to identify job type from: ${TEST_CODE}!"
                ;;
        esac
        ;;
    *ligato*)
        DUT="kubernetes"

        case "$TEST_CODE" in
            csit-*)
                # Use downloaded packages with specific version
                if [[ "$TEST_CODE" == *daily* ]] || \
                   [[ "$TEST_CODE" == *weekly* ]] || \
                   [[ "$TEST_CODE" == *timed* ]];
                then
                    echo Downloading latest VPP packages from NEXUS...
                    bash ${SCRIPT_DIR}/resources/tools/scripts/download_install_vpp_pkgs.sh \
                        --skip-install || {
                        die 1 "Failed to get VPP packages!"
                    }
                else
                    echo Downloading VPP packages of specific version from NEXUS...
                    DPDK_STABLE_VER=$(cat ${SCRIPT_DIR}/DPDK_STABLE_VER)
                    VPP_STABLE_VER=$(cat ${SCRIPT_DIR}/VPP_STABLE_VER_UBUNTU)
                    bash ${SCRIPT_DIR}/resources/tools/scripts/download_install_vpp_pkgs.sh \
                        --skip-install --vpp ${VPP_STABLE_VER} --dkms ${DPDK_STABLE_VER} || {
                        die 1 "Failed to get VPP packages!"
                    }
                fi
                ;;
            vpp-csit-*)
                # Use local builded packages.
                mv ../${DUT}*.deb ${DOWNLOAD_DIR}/
                ;;
            *)
                die 1 "Unable to identify job type from: ${TEST_CODE}!"
                ;;
        esac
        # Extract VPP API to specific folder
        dpkg -x ${DOWNLOAD_DIR}/vpp_*.deb /tmp/vpp || {
            die 1 "Failed to extract ${DUT} package!"
        }

        LIGATO_REPO_URL="https://github.com/ligato/"
        VPP_AGENT_STABLE_VER=$(cat ${SCRIPT_DIR}/VPP_AGENT_STABLE_VER)
        DOCKER_DEB="docker-ce_18.03.0~ce-0~ubuntu_amd64.deb"

        # Clone & checkout stable vnf-agent
        cd ../..
        git clone -b ${VPP_AGENT_STABLE_VER} --single-branch \
            ${LIGATO_REPO_URL}/vpp-agent vpp-agent || {
            die 1 "Failed to run: git clone ${LIGATO_REPO_URL}/vpp-agent!"
        }
        cd vpp-agent

        # Install Docker
        wget -q https://download.docker.com/linux/ubuntu/dists/xenial/pool/stable/amd64/${DOCKER_DEB} || {
            die 1 "Failed to download Docker package!"
        }

        sudo dpkg -i ${DOCKER_DEB} || {
            die 1 "Failed to install Docker!"
        }

        # Pull ligato/dev_vpp_agent docker image and re-tag as local
        sudo docker pull ligato/dev-vpp-agent:${VPP_AGENT_STABLE_VER} || {
            die 1 "Failed to pull Docker image!"
        }

        sudo docker tag ligato/dev-vpp-agent:${VPP_AGENT_STABLE_VER}\
            dev_vpp_agent:latest || {
            die 1 "Failed to tag Docker image!"
        }

        # Start dev_vpp_agent container as daemon
        sudo docker run --rm -itd --name agentcnt dev_vpp_agent bash || {
            die 1 "Failed to run Docker image!"
        }

        # Copy latest vpp api into running container
        sudo docker cp /tmp/vpp/usr/share/vpp/api agentcnt:/usr/share/vpp || {
            die 1 "Failed to copy files Docker image!"
        }

        for f in ${DOWNLOAD_DIR}/*; do
            sudo docker cp $f agentcnt:/opt/vpp-agent/dev/vpp/build-root/ || {
                die 1 "Failed to copy files Docker image!"
            }
        done

        # Recompile vpp-agent
        sudo docker exec -i agentcnt \
            script -qec '. ~/.bashrc; cd /go/src/github.com/ligato/vpp-agent && make generate && make install' || {
            die 1 "Failed to build vpp-agent in Docker image!"
        }
        # Save container state
        sudo docker commit `sudo docker ps -q` dev_vpp_agent:latest || {
            die 1 "Failed to commit state of Docker image!"
        }

        # Build prod_vpp_agent docker image
        cd docker/prod/ &&\
            sudo docker build --tag prod_vpp_agent --no-cache . || {
                die 1 "Failed to build Docker image!"
            }
        # Export Docker image
        sudo docker save prod_vpp_agent | gzip > prod_vpp_agent.tar.gz || {
            die 1 "Failed to save Docker image!"
        }
        DOCKER_IMAGE="$( readlink -f prod_vpp_agent.tar.gz | tr '\n' ' ' )"
        rm -r ${DOWNLOAD_DIR}/vpp*
        mv ${DOCKER_IMAGE} ${DOWNLOAD_DIR}/
        ;;
    *dpdk*)
        DUT="dpdk"

        DPDK_REPO='https://fast.dpdk.org/rel/'
        # Use downloaded packages with specific version
        if [[ "$TEST_CODE" == *daily* ]] || \
           [[ "$TEST_CODE" == *weekly* ]] || \
           [[ "$TEST_CODE" == *timed* ]];
        then
            echo "Downloading latest DPDK packages from repo..."
            DPDK_STABLE_VER=$(wget --no-check-certificate --quiet -O - ${DPDK_REPO} | \
                grep -v '2015' | grep -Eo 'dpdk-[^\"]+xz' | tail -1)
        else
            echo "Downloading DPDK packages of specific version from repo..."
            DPDK_STABLE_VER='dpdk-18.05.tar.xz'
        fi
        if [[ ! -f ${DPDK_STABLE_VER} ]]; then
            wget --no-check-certificate ${DPDK_REPO}${DPDK_STABLE_VER} || {
                die 1 "Failed to get DPDK package from ${DPDK_REPO}!"
            }
        fi
        ;;
    *)
        die 1 "Unable to identify DUT type from: ${TEST_CODE}!"
        ;;
esac
cd ${SCRIPT_DIR}

if [[ ! "$(ls -A ${DOWNLOAD_DIR})" ]]; then
    die 1 "No artifacts downloaded!"
fi

# ENVIRONMENT PREPARATION
rm -rf env

pip install virtualenv || {
    die 1 "Failed to install virtual env!"
}
virtualenv --system-site-packages env || {
    die 1 "Failed to create virtual env!"
}
source env/bin/activate || {
    die 1 "Failed to activate virtual env!"
}
pip install -r requirements.txt || {
    die 1 "Failed to install requirements to virtual env!"
}

# We iterate over available topologies and wait until we reserve topology.
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

    if [ -n "${WORKING_TOPOLOGY}" ]; then
        # Exit the infinite while loop if we made a reservation.
        break
    fi

    # Wait ~3minutes before next try.
    SLEEP_TIME=$[ ( $RANDOM % 20 ) + 180 ]s
    echo "Sleeping ${SLEEP_TIME}"
    sleep ${SLEEP_TIME}
done

# Clean testbed before execution.
python ${SCRIPT_DIR}/resources/tools/scripts/topo_cleanup.py -t ${WORKING_TOPOLOGY} || {
    die 1 "Failed to cleanup topologies!"
}

# CSIT EXECUTION
PYBOT_ARGS="--outputdir ${ARCHIVE_DIR} --loglevel TRACE --variable TOPOLOGY_PATH:${WORKING_TOPOLOGY} --suite tests.${DUT}.perf"

# NIC SELECTION
# All topologies NICs
TOPOLOGIES_NICS=($(grep -hoPR "model: \K.*" topologies/available/* | sort -u))
# Selected topology NICs
TOPOLOGY_NICS=($(grep -hoPR "model: \K.*" ${WORKING_TOPOLOGY} | sort -u))
# All topologies NICs - Selected topology NICs
EXCLUDE_NICS=($(comm -13 <(printf '%s\n' "${TOPOLOGY_NICS[@]}") <(printf '%s\n' "${TOPOLOGIES_NICS[@]}")))

case "$TEST_CODE" in
    # Select specific performance tests based on jenkins job type variable.
    *ndrpdr-weekly* )
        TEST_TAG_ARRAY=(ndrpdrANDnic_intel-x520-da2AND1c
                        ndrpdrANDnic_intel-x520-da2AND2c
                        ndrpdrAND1cANDipsec
                        ndrpdrAND2cANDipsec)
        ;;
    *ndrpdr-timed* )
        ;;
    *mrr-daily* )
        TEST_TAG_ARRAY=(mrrAND64bAND1c
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
    * )
        if [[ -z "$TEST_TAG_STRING" ]]; then
            # If nothing is specified, we will run pre-selected tests by
            # following tags. Items of array will be concatenated by OR in Robot
            # Framework.
            TEST_TAG_ARRAY=(ndrpdrAND64bAND1cANDl2xcfwdANDbaseANDnic_intel-x710)
        else
            # If trigger contains tags, split them into array.
            TEST_TAG_ARRAY=(${TEST_TAG_STRING//:/ })
        fi
        ;;
esac

# We will add excluded NICs.
TEST_TAG_ARRAY+=("${EXCLUDE_NICS[@]/#/!NIC_}")

TAGS=()

# We will prefix with perftest to prevent running other tests (e.g. Functional).
prefix="perftestAND"
if [[ ${TEST_CODE} == vpp-* ]]; then
    # Automatic prefixing for VPP jobs to limit the NIC used and
    # traffic evaluation to MRR.
    prefix="${prefix}mrrANDnic_intel-x710AND"
fi
for TAG in "${TEST_TAG_ARRAY[@]}"; do
    if [[ ${TAG} == "!"* ]]; then
        # Exclude tags are not prefixed.
        TAGS+=("${TAG}")
    else
        TAGS+=("$prefix${TAG}")
    fi
done

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

# We will create additional archive if workspace variable is set. This way if
# script is running in jenkins all will be automatically archived to logs.fd.io.
if [[ -n ${WORKSPACE-} ]]; then
    cp -r ${ARCHIVE_DIR}/ $WORKSPACE/archives/
fi

exit ${RETURN_STATUS}
