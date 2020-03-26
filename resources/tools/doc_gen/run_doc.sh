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
virtualenv --python=$(which python3) ${WORKING_DIR}/env
. ${WORKING_DIR}/env/bin/activate

# Install CSIT requirements:
pip3 install --upgrade -r ../../../requirements.txt

export PYTHONPATH=`pwd`

# Generate rst files:
python3 gen_rst.py

# Remove all rst files from ./${WORKING_DIR}/env directory - we do not need them
find ./${WORKING_DIR}/env -type f -name '*.rst' | xargs rm -f

# Generate the documentation:
DATE=$(date -u '+%d-%b-%Y')
sphinx-build -v -c ${WORKING_DIR} -a  -b html -E -D release=$1 -D version="$1 documentation - $DATE" ${WORKING_DIR} ${BUILD_DIR}/

find . -type d -name 'env' | xargs rm -rf

echo Creating csit.doc.tar.gz ...
tar -czvf ./csit.docs.tar.gz ${BUILD_DIR}
