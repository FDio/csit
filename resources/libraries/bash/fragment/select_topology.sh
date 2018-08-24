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

function select_topology () {

    set -exuo pipefail

    # Arguments:
    # - ${1} - Nodeness, currently either "2n" or "3n".
    # - ${2} - Hardware flavor, currently either "hsw" or "skx".
    # Variables read:
    # - CSIT_DIR - Path to existing root of local CSIT git repository.
    # - TOPOLOGIES_DIR - Path to existing directory with available tpologies.
    # Variables set:
    # - TOPOLOGIES - Array of paths to suitable topology yaml files.
    # - TOPOLOGIES_TAGS - Tag expression selecting tests for the topology.
    # Functions called:
    # - die - Print to stderr and exit, defined in common_functions.sh

    case "${1}_${2}" in
        3n_hsw)
            TOPOLOGIES=(
                        #"${TOPOLOGIES_DIR}/lf_3n_hsw_testbed1.yaml"
                        #"${TOPOLOGIES_DIR}/lf_3n_hsw_testbed2.yaml"
                        #"${TOPOLOGIES_DIR}/lf_3n_hsw_testbed3.yaml"
                       )
            TOPOLOGIES_TAGS="3_node_*_link_topo"
            ;;
        2n_skx)
            TOPOLOGIES=(
                        #"${TOPOLOGIES_DIR}/lf_2n_skx_testbed21.yaml"
                        ##"${TOPOLOGIES_DIR}/lf_2n_skx_testbed22.yaml"
                        "${TOPOLOGIES_DIR}/lf_2n_skx_testbed23.yaml"
                        #"${TOPOLOGIES_DIR}/lf_2n_skx_testbed24.yaml"
                       )
            TOPOLOGIES_TAGS="2_node_*_link_topo"
            ;;
        3n_skx)
            TOPOLOGIES=(
                        #"${TOPOLOGIES_DIR}/lf_3n_skx_testbed31.yaml"
                        #"${TOPOLOGIES_DIR}/lf_3n_skx_testbed32.yaml"
                       )
            TOPOLOGIES_TAGS="3_node_*_link_topo"
            ;;
        *)
            die 1 "Unknown specification: ${1}_${2}"
    esac

    if [[ -z "${TOPOLOGIES-}" ]]; then
        die 1 "No applicable topology found!"
    fi
}
