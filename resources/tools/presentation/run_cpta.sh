#!/bin/bash

set -x

# set default values in config array
typeset -A DIR

DIR[WORKING]=_tmp

## Install system dependencies
#sudo apt-get -y update
#sudo apt-get -y install libxml2 libxml2-dev libxslt-dev build-essential \
#    zlib1g-dev unzip

# Create working directories
mkdir ${DIR[WORKING]}

# Create virtual environment
virtualenv ${DIR[WORKING]}/env
. ${DIR[WORKING]}/env/bin/activate

# Install python dependencies:
pip install -r requirements.txt

export PYTHONPATH=`pwd`

STATUS=$(python pal.py \
    --specification specification_CPTA.yaml \
    --logging INFO \
    --force)
RETURN_STATUS=$?

( cd ../presentation_new && python pal.py \
    --specification specification_CPTA.yaml \
    --logging INFO \
    --force )

echo ${STATUS}
exit ${RETURN_STATUS}
