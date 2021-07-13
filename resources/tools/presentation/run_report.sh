#!/bin/bash

set -x

RELEASE=$1

# set default values in config array
typeset -A CFG
typeset -A DIR

DIR[WORKING]=_tmp

# Create working directories
mkdir ${DIR[WORKING]}

# Create virtual environment
virtualenv -p $(which python3) ${DIR[WORKING]}/env
source ${DIR[WORKING]}/env/bin/activate

# FIXME: s3 config (until migrated to vault, then account will be reset)
mkdir -p ${HOME}/.aws
echo "
[nomad-s3]
aws_access_key_id = csit
aws_secret_access_key = Csit1234" >> ${HOME}/.aws/credentials

# Install python dependencies:
pip3 install -r requirements.txt

export PYTHONPATH=`pwd`:`pwd`/../../../

python pal.py \
    --specification specifications/report \
    --release ${RELEASE} \
    --week "30" \
    --logging INFO \
    --force

RETURN_STATUS=$(echo $?)
exit ${RETURN_STATUS}
