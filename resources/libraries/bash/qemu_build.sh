#!/bin/bash
# Copyright (c) 2018 Cisco and/or its affiliates.
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

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Include
source ${SCRIPT_DIR}/config/defaults
source ${SCRIPT_DIR}/shell/qemu_utils.sh

# Read configuration
while read line
do
    if echo $line | grep -F = &>/dev/null
    then
        varname=$(echo "$line" | cut -d '=' -f 1)
        cfg[$varname]=$(echo "$line" | cut -d '=' -f 2-)
    fi
done < ${SCRIPT_DIR}/config/config

# Read parameters
for i in "$@"; do
    case $i in
        --version=*)
            cfg['QEMU_INSTALL_VERSION']="${i#*=}"
            shift ;;
        --directory=*)
            cfg['QEMU_INSTALL_DIR']="${i#*=}"
            shift ;;
        --patch)
            cfg['QEMU_PATCH']=true
            shift ;;
        --force)
            cfg['QEMU_FORCE_INSTALL']=true
            shift ;;
        --target-list)
            cfg['QEMU_TARGET_LIST']="${i#*=}"
            shift ;;
        *)
            ;;
    esac
done

# Install qemu
qemu_utils.qemu_install ${cfg[QEMU_INSTALL_DIR]} ${cfg[QEMU_INSTALL_VERSION]} \
    ${cfg[QEMU_PATCH]} ${cfg[QEMU_FORCE_INSTALL]} ${cfg[QEMU_TARGET_LIST]}
