#!/usr/bin/env bash

# Copyright (c) 2023 Cisco and/or its affiliates.
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

set -exuo pipefail

# Assumptions:
# This script is used to cleanup the docker topology when bootstrapping
# a vpp device using CSIT_NO_CLEANUP=1, which preserves the container
# topology for further debugging. 
# Assumes a file named CSIT_STATE_VARS exists in the CSIT root
# directory, containing the environment variables required for cleaning
# up the topology.

BASH_ENTRY_DIR="$(dirname $(readlink -e "${BASH_SOURCE[0]}"))"

# Save bash functions in the current shell
declare -f > ${BASH_ENTRY_DIR}/CSIT_ENV_FUNCTIONS.sh

# Cleanup existing functions in the current shell
# to prevent conflicts when deactivating docker topology using
# sourced csit functions
functions=$(declare -F)
for function in $functions; do
   unset -f $function
done

BASH_FUNCTION_DIR="$(readlink -e "${BASH_ENTRY_DIR}/../function")"
source "${BASH_FUNCTION_DIR}/common.sh" || {
    echo "Source failed." >&2
    exit 1
}
source "${BASH_FUNCTION_DIR}/device.sh" || {
    echo "Source failed." >&2
    exit 1
}
common_dirs
activate_virtualenv
export env $(cat "${CSIT_DIR}/CSIT_STATE_VARS" | xargs) || die "Error setting CSIT_STATE_VARS"
deactivate_docker_topology
# Unset all exported CSIT_STATE environment variables after topology deactivation
unset $(cat "${CSIT_DIR}/CSIT_STATE_VARS" | sed -E 's/(.*)=.*/\1/' | xargs)
deactivate

# Source saved functions back into the shell
source ${BASH_ENTRY_DIR}/CSIT_ENV_FUNCTIONS.sh

# Cleanup saved functions and state
rm -f ${BASH_ENTRY_DIR}/CSIT_ENV_FUNCTIONS.sh
rm -f ${CSIT_DIR}/CSIT_STATE_VARS
