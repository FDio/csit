#!/bin/bash

WORKING_DIR='tmp'
BUILD_DIR='_build'

# Clean-up when finished:
trap 'rm -rf ${WORKING_DIR}; exit' EXIT
trap 'rm -rf ${WORKING_DIR}; exit' ERR

# Remove the old build:
rm -rf ${BUILD_DIR} || true
rm -rf ${WORKING_DIR} || true

# Create working directories
mkdir ${BUILD_DIR}
mkdir --parents ${WORKING_DIR}/resources/libraries/python/
mkdir --parents ${WORKING_DIR}/resources/libraries/robot/
mkdir --parents ${WORKING_DIR}/tests/

# Copy the Sphinx source files:
cp -r src/* ${WORKING_DIR}/

# Copy the source files to be processed:
rsync -a --include '*/' --include '*.py' --exclude '*' ../../../resources/libraries/python/ ${WORKING_DIR}/resources/libraries/python/
cp ../../../resources/__init__.py ${WORKING_DIR}/resources/
cp ../../../resources/libraries/__init__.py ${WORKING_DIR}/resources/libraries/
rsync -a --include '*/' --include '*.robot' --exclude '*' ../../../resources/libraries/robot/ ${WORKING_DIR}/resources/libraries/robot/
rsync -a --include '*/' --include '*.robot' --exclude '*' ../../../tests/ ${WORKING_DIR}/tests/

# Create virtual environment:
virtualenv ${WORKING_DIR}/env
. ${WORKING_DIR}/env/bin/activate

# Install CSIT requirements:
pip install -r ../../../requirements.txt
# Install Sphinx:
pip install -r ${WORKING_DIR}/requirements.txt

export PYTHONPATH=`pwd`

# Generate rst files:
./gen_rst.py

# Generate the documentation:
sphinx-build -vvv -b html ${WORKING_DIR}/ ${BUILD_DIR}/