#!/usr/bin/env bash
# Copyright (c) 2021 Intel and/or its affiliates.
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

# Helper functions for starting nginx.

set -exuo pipefail

# Assumptions:
# + There is a directory holding CSIT code to use (this script is there).
# + At least one of the following is true:
# ++ JOB_NAME environment variable is set,
# ++ or this entry script has access to arguments.
# Consequences (and specific assumptions) are multiple,
# examine tree of functions for current description.

# Vsap Mode
START_NGINX_MODE=$1

# RPS or CPS.
RPS_CPS=$2

# Nginx process number.
CORE_NUM=$3

# Packet Mode
TLS_TCP=$4

# Core IDLE .
CPU_IDLE_CORES_STR=$5


BASH_ENTRY_DIR="$(dirname $(readlink -e "${BASH_SOURCE[0]}"))"
BASH_FUNCTION_DIR="$(readlink -e "${BASH_ENTRY_DIR}/../function")"
source "${BASH_FUNCTION_DIR}/nginx.sh" || die "Source failed."
export_vsap_vcl_conf || die 'Export vcl conf failed'
set_ngignx_conf ${CORE_NUM} ${RPS_CPS} ${TLS_TCP} \
|| die "set ngignx conf failed"
start_nginx ${START_NGINX_MODE} || die "start nginx failed"
tasket_cores_to_nginx_pid ${CPU_IDLE_CORES_STR} \
|| die "tasket env core to nginx failed"
