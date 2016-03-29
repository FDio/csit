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

# Reservation dir
RESERVATION_DIR="/tmp/reservation_dir"

# Jenkins VPP deb paths (convert to full path)
VPP_DEBS="$( readlink -f $@ | tr '\n' ' ' )"

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

    # Wait 10 - 30 sec. before next try
    SLEEP_TIME=$[ ( $RANDOM % 20 ) + 10 ]s
    echo "Sleeping ${SLEEP_TIME}"
    sleep ${SLEEP_TIME}
done

python ${CUR_DIR}/resources/tools/topo_installation.py -t ${WORKING_TOPOLOGY} \
                                                       -d ${RESERVATION_DIR} \
                                                       -p ${VPP_DEBS}
if [ $? -eq 0 ]; then
    echo "VPP Installed on hosts from: ${WORKING_TOPOLOGY}"
else
    echo "Failed to copy vpp deb files to DUTs"
    exit $?
fi

function cancel_reservation {
    python ${CUR_DIR}/resources/tools/topo_reservation.py -c -t $1
}

# On script exit we cancel the reservation and delete all vpp packages
trap "cancel_reservation ${WORKING_TOPOLOGY}" EXIT

# run performance test suite
pybot -L TRACE \
    -v TOPOLOGY_PATH:${WORKING_TOPOLOGY} \
    -s performance tests/
