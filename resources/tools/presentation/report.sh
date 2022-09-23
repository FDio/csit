#!/bin/bash

clear

ROOT_DIR=`pwd`
DIR[WORKING]=${ROOT_DIR}/_tmp

mkdir ${DIR[WORKING]}

# Create virtual environment
virtualenv -p $(which python3) ${DIR[WORKING]}/env
source ${DIR[WORKING]}/env/bin/activate

pip3 install -r requirements.txt

export PYTHONPATH=`pwd`:`pwd`/../../../ || die "Export failed!"

ls -la _tmp/env/lib/python3.10/site-packages

all_options=("pal.py")
all_options+=("--specification" "specifications/report")
all_options+=("--release" "${GERRIT_BRANCH:-master}")
all_options+=("--week" $(date "+%V"))
all_options+=("--logging" "INFO")
all_options+=("--force")

set +e
python "${all_options[@]}"
set -e
