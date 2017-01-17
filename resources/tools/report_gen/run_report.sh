#!/bin/bash

WORKING_DIR='_tmp'
BUILD_DIR='_build'
SOURCE_DIR='../../../docs/report'
PLOT_DIR='../../../../plots'

# Clean-up when finished:
trap 'rm -rf ${WORKING_DIR}; exit' EXIT
trap 'rm -rf ${WORKING_DIR}; exit' ERR

# Remove the old build:
rm -rf ${BUILD_DIR} || true
rm -rf ${WORKING_DIR} || true

# Create working directories
mkdir ${BUILD_DIR}

# Create virtual environment:
virtualenv ${WORKING_DIR}/env
. ${WORKING_DIR}/env/bin/activate

# Install CSIT requirements:
pip install -r ../../../requirements.txt
# Install Sphinx:
pip install -r requirements.txt

export PYTHONPATH=`pwd`

# Remove all rst files from ./${WORKING_DIR}/env directory - we do not need them
find ./${WORKING_DIR}/env -type f -name '*.rst' | xargs rm -f

# Generate the documentation:
sphinx-build -v -c . -a -b html ${SOURCE_DIR} ${BUILD_DIR}/
cp ${PLOT_DIR}/* ${BUILD_DIR}/_static/

find . -type d -name 'env' | xargs rm -rf

echo Creating csit.report.tar.gz ...
tar -czvf ./csit.report.tar.gz ${BUILD_DIR}

