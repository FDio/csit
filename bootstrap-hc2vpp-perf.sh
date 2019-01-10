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

STREAM=$1
OS=$2
ODL=$3

# Space separated list of available testbeds, described by topology files
TOPOLOGIES="topologies/available/lf_3n_hsw_testbed1.yaml \
            topologies/available/lf_3n_hsw_testbed2.yaml \
            topologies/available/lf_3n_hsw_testbed3.yaml"

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Reservation dir
RESERVATION_DIR="/tmp/reservation_dir"
INSTALLATION_DIR="/tmp/install_dir"

PYBOT_ARGS="-W 150 -L TRACE"

JOB_ARCHIVE_ARTIFACTS=(log.html output.xml report.html honeycomb.log)
LOG_ARCHIVE_ARTIFACTS=(log.html output.xml report.html honeycomb.log)
JOB_ARCHIVE_DIR="archive"
LOG_ARCHIVE_DIR="$WORKSPACE/archives"
mkdir -p ${JOB_ARCHIVE_DIR}
mkdir -p ${LOG_ARCHIVE_DIR}

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
    python ${SCRIPT_DIR}/resources/tools/scripts/topo_installation.py -c -d ${INSTALLATION_DIR} -t $1 -hc True
    python ${SCRIPT_DIR}/resources/tools/scripts/topo_reservation.py -c -t $1
}

# On script exit we cancel the reservation and installation and delete all vpp
# packages
trap "cancel_all ${WORKING_TOPOLOGY}" EXIT

# Download VPP and HC packages from the current branch
echo Downloading packages...
CSIT_DIR=${SCRIPT_DIR}
source "${SCRIPT_DIR}/resources/libraries/bash/function/artifacts.sh"
source "${SCRIPT_DIR}/resources/libraries/bash/function/artifacts_hc.sh"
download_artifacts
download_artifacts_hc

if [ "${OS}" == "centos7" ]; then
    VPP_PKGS=(*.rpm)
else
    VPP_PKGS=(*.deb)
fi
echo ${VPP_PKGS[@]}

# Install packages
python ${SCRIPT_DIR}/resources/tools/scripts/topo_installation.py -t ${WORKING_TOPOLOGY} \
                                                       -d ${INSTALLATION_DIR} \
                                                       -p ${VPP_PKGS[@]} \
                                                       -hc True
if [ $? -eq 0 ]; then
    echo "VPP Installed on hosts from: ${WORKING_TOPOLOGY}"
else
    echo "Failed to copy vpp deb files to DUTs"
    exit 1
fi

# run full performance test suite and exit on fail
        pybot ${PYBOT_ARGS} \
              -v TOPOLOGY_PATH:${WORKING_TOPOLOGY} \
              -s "tests.honeycomb.perf" \
              --variable install_dir:${INSTALLATION_DIR} \
              tests/
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
