#!/bin/bash

set -x

sudo apt-get -y update
sudo apt-get -y install libpython2.7-dev python-virtualenv

virtualenv env
. env/bin/activate

echo pip install
pip install -r requirements.txt

PYTHONPATH=`pwd` pybot -L TRACE \
    -v TOPOLOGY_PATH:topologies/available/lf_testbed2-710-520.yaml \
    -s performance tests/
