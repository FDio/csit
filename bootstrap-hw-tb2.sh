#!/bin/bash

set -x

# space separated list of available testbeds, described by topology files
TOPOLOGIES="topologies/available/lf_testbed2-710-520.yaml"

CUR_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
WORKING_TOPOLOGY=""

sudo apt-get -y update
sudo apt-get -y install libpython2.7-dev python-virtualenv

virtualenv env
. env/bin/activate

echo pip install
pip install -r requirements.txt

#we iterate over available topologies and wait until we reserve topology
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
        #exit the infinite while loop if we made a reservation
        break
    fi

    #wait 20 - 30 sec. before next try
    SLEEP_TIME=$[ ( $RANDOM % 20 ) + 10 ]s
    echo "Sleeping ${SLEEP_TIME}"
    sleep ${SLEEP_TIME}
done

function cancel_reservation {
    python ${CUR_DIR}/resources/tools/topo_reservation.py -c -t $1
}

#on script exit we cancel the reservation
trap "cancel_reservation ${WORKING_TOPOLOGY}" EXIT

#run performance test suite
PYTHONPATH=`pwd` pybot -L TRACE \
    -v TOPOLOGY_PATH:${WORKING_TOPOLOGY} \
    -s performance tests/
