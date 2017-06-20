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
TOPOLOGIES="topologies/available/lf_testbed1.yaml \
            topologies/available/lf_testbed2.yaml \
            topologies/available/lf_testbed3.yaml"

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Reservation dir
RESERVATION_DIR="/tmp/reservation_dir"

PYBOT_ARGS="-W 150"

ARCHIVE_ARTIFACTS=(log.html output.xml report.html output_perf_data.xml)

# we will download the DPDK in the robot

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

#for DPDK test, we don't need to install the VPP deb
function cancel_all {
    python ${SCRIPT_DIR}/resources/tools/scripts/topo_reservation.py -c -t $1
}

# On script exit we cancel the reservation
trap "cancel_all ${WORKING_TOPOLOGY}" EXIT

case "$TEST_TAG" in
    # run specific performance tests based on jenkins job type variable
    PERFTEST_LONG )
        pybot ${PYBOT_ARGS} \
              -L TRACE \
              -v TOPOLOGY_PATH:${WORKING_TOPOLOGY} \
              -v DPDK_TEST:True \
              -s "tests.dpdk.perf" \
              --exclude SKIP_PATCH \
              -i NDRPDRDISC \
              tests/dpdk/
        RETURN_STATUS=$(echo $?)
        ;;
    PERFTEST_SHORT )
        pybot ${PYBOT_ARGS} \
              -L TRACE \
              -v TOPOLOGY_PATH:${WORKING_TOPOLOGY} \
              -v DPDK_TEST:True \
              -s "tests.dpdk.perf" \
              -i NDRCHK \
              tests/dpdk/
        RETURN_STATUS=$(echo $?)
        ;;
   PERFTEST_NIGHTLY )
        #run all available tests
        pybot ${PYBOT_ARGS} \
              -L TRACE \
              -v TOPOLOGY_PATH:${WORKING_TOPOLOGY} \
              -v DPDK_TEST:True \
              -s "tests.dpdk.perf" \
              tests/dpdk/
        RETURN_STATUS=$(echo $?)
        ;;
    * )
        # run full performance test suite and exit on fail
        pybot ${PYBOT_ARGS} \
              -L TRACE \
              -v TOPOLOGY_PATH:${WORKING_TOPOLOGY} \
              -v DPDK_TEST:True \
              -s "tests.dpdk.perf" \
              tests/dpdk/
        RETURN_STATUS=$(echo $?)
esac

# Pybot output post-processing
echo Post-processing test data...

python ${SCRIPT_DIR}/resources/tools/scripts/robot_output_parser.py \
       -i ${SCRIPT_DIR}/output.xml \
       -o ${SCRIPT_DIR}/output_perf_data.xml
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
