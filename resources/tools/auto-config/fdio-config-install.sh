#!/bin/bash
# Copyright (c) 2016 Cisco and/or its affiliates.
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at:
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

set -x

CSIT_INSTALL_DIR="./csit"
CSIT_TEMP_DIR="/tmp/openvpp-testing"

unset FORCE
for i in "$@"; do
    case $i in
        --directory=*)
            CSIT_INSTALL_DIR="${i#*=}"
            shift ;;
        --force)
            FORCE=1
            shift ;;
        *)
            ;;
    esac
done

if [ $FORCE ]; then
    echo "FORCE -----------------------------------------"
    rm -fr ${CSIT_INSTALL_DIR}
    rm -fr ${CSIT_TEMP_DIR}
fi

if [[ ! -d ${CSIT_INSTALL_DIR} ]]; then
    echo "CLONE -----------------------------------------"
    git clone https://gerrit.fd.io/r/csit ${CSIT_INSTALL_DIR}
    pushd ${CSIT_INSTALL_DIR}
    CSIT_INSTALL_DIR=$(pwd)
    git review -d 7507
else
    pushd ${CSIT_INSTALL_DIR}
    CSIT_INSTALL_DIR=$(pwd)
fi

if [[ ! -d ${CSIT_TEMP_DIR} ]]; then
    mkdir ${CSIT_TEMP_DIR}
    cp -r ${CSIT_INSTALL_DIR}/resources ${CSIT_TEMP_DIR}/.
fi

if [[ $PATH != *"/resources/tools/auto-config"* ]]; then
    export PATH=${CSIT_INSTALL_DIR}/resources/tools/auto-config:$PATH
fi

if [[ $PYTHONPATH != *"${CSIT_INSTALL_DIR}"* ]]; then
    export PYTHONPATH=${CSIT_INSTALL_DIR}:$PYTHONPATH
fi

cd ${CSIT_INSTALL_DIR}/resources/tools/auto-config

set +x
# popd
