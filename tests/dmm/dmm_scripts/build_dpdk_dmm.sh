#!/bin/bash

set -x

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
ROOTDIR=${SCRIPT_DIR}/../../../

#===============download json===================
echo "downloading JSON....."
JSON_C_DOWNLOAD_DIR=${ROOTDIR}/dmm/thirdparty/json/
mkdir ${JSON_C_DOWNLOAD_DIR}
cd ${JSON_C_DOWNLOAD_DIR}
JSON_C_URL="https://github.com/json-c/json-c/archive/json-c-0.12.1-20160607.tar.gz"
wget --no-check-certificate -O json-c-0.12.1.tar.gz https://github.com/json-c/json-c/archive/json-c-0.12.1-20160607.tar.gz
if [ $? -eq 0 ]
then
  echo "JSON download is SUCCESS"
else
  echo "JSON download has FAILED"
  exit 1
fi
