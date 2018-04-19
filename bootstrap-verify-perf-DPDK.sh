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

JOB_ARCHIVE_ARTIFACTS=(log.html output.xml report.html)
LOG_ARCHIVE_ARTIFACTS=(log.html output.xml report.html)
JOB_ARCHIVE_DIR="archive"
LOG_ARCHIVE_DIR="$WORKSPACE/archives"
mkdir -p ${JOB_ARCHIVE_DIR}
mkdir -p ${LOG_ARCHIVE_DIR}

# we will download the DPDK in the robot

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

#for DPDK test, we don't need to install the VPP deb
function cancel_all {
    python ${SCRIPT_DIR}/resources/tools/scripts/topo_reservation.py -c -t $1
}

# On script exit we cancel the reservation
trap "cancel_all ${WORKING_TOPOLOGY}" EXIT

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
    VERIFY-PERF-MRR )
        TAGS=('mrrAND1t1c'
              'mrrAND2t2c')
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
