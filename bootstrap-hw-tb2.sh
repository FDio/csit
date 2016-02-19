#!/bin/bash

virtualenv env
. env/bin/activate

echo pip install
pip install -r requirements.txt

PYTHONPATH=`pwd` pybot -L TRACE \
    -v TOPOLOGY_PATH:topologies/available/lf_testbed2-710-520.yaml \
    -s performance tests/
