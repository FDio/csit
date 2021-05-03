#!/bin/bash

set -x

# set default values in config array
typeset -A CFG
typeset -A DIR

DIR[WORKING]=_tmp

# Create working directories
mkdir ${DIR[WORKING]}

# Create virtual environment
virtualenv -p $(which python3) ${DIR[WORKING]}/env
source ${DIR[WORKING]}/env/bin/activate

# FIXME: Temporary hack until all docker dns will be solved
# echo "nameserver 172.17.0.1" > /etc/resolv.conf

# Install python dependencies:
pip3 install -r requirements.txt

export PYTHONPATH=`pwd`:`pwd`/../../../

python pal.py \
    --specification specifications/converter \
    --logging INFO \

RETURN_STATUS=$(echo $?)
exit ${RETURN_STATUS}
