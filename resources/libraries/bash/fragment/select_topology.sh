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

set -exuo pipefail

# Arguments:
# - ${1} - Nodeness, currently either "2n" or "3n".
# - ${2} - Hardware flavor, currently either "hsw" or "skx".
# Variables read:
# - CSIT_DIR - Path to directory with root of local CSIT git repository.
# Variables set:
# - TOPOLOGY_DIR - Path to directory holding topology yaml files.
# - TOPOLOGIES - Array of paths to suitable topology yaml files.
# - TOPOLOGIES_TAGS - Tag expression selecting tests compatible with topology.
# Functions called:
# - die - Print to stderr and exit, defined in common_functions.sh

TOPOLOGY_DIR="${CSIT_DIR}/topologies/available"

case "${1}_${2}" in
    3n_hsw)
        TOPOLOGIES=(
                    "${TOPOLOGY_DIR}/lf_3n_hsw_testbed1.yaml"
                    "${TOPOLOGY_DIR}/lf_3n_hsw_testbed2.yaml"
                    "${TOPOLOGY_DIR}/lf_3n_hsw_testbed3.yaml"
                   )
        TOPOLOGIES_TAGS="3_node_*_link_topo"
        ;;
    2n_skx)
        TOPOLOGIES=(
                    "${TOPOLOGY_DIR}/lf_2n_skx_testbed21.yaml"
                    #"${TOPOLOGY_DIR}/lf_2n_skx_testbed22.yaml"
                    #"${TOPOLOGY_DIR}/lf_2n_skx_testbed23.yaml"
                    "${TOPOLOGY_DIR}/lf_2n_skx_testbed24.yaml"
                   )
        TOPOLOGIES_TAGS="2_node_*_link_topo"
        ;;
    3n_skx)
        TOPOLOGIES=(
                    "${TOPOLOGY_DIR}/lf_3n_skx_testbed31.yaml"
                    "${TOPOLOGY_DIR}/lf_3n_skx_testbed32.yaml"
                   )
        TOPOLOGIES_TAGS="3_node_*_link_topo"
        ;;
    *)
        die 1 "Unknown specification: ${1}_${2}"
esac

if [[ -z "${TOPOLOGIES}" ]]; then
    die 1 "No applicable topology found!"
fi
