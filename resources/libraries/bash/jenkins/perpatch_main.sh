#!/bin/env bash

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

# Assumptions:
# + Jenkins ${WORKDIR} holds VPP repo with patch under test checked out.
# + It contains csit subdirectory with CSIT code to use (this script is there).
# FIXME: job name, jenkins comment, ...?

BASH_LIBRARY_DIR=$(dirname $(readlink -e "${BASH_SOURCE[0]}"))
source "${BASH_LIBRARY_DIR}/common_dirs.sh"
VPP_DIR=$(readlink -e "$CSIT_DIR/..")
# TODO: Unify archive dire handling.
ARCHIVE_DIR="${CSIT_DIR}"
if [[ "$VPP_DIR" != "$WORKSPACE" ]]; then
    echo "VPP dir does not match workspace!"
    exit 1
fi
source "${BASH_LIBRARY_DIR}/common_functions.sh"
#source "${BASH_LIBRARY_DIR}/setup_vpp_dpdk_dev_env.sh"
#source "${BASH_LIBRARY_DIR}/build_vpp_ubuntu_amd64.sh"
#source "${BASH_LIBRARY_DIR}/prepare_build_parent.sh"
#source "${BASH_LIBRARY_DIR}/build_vpp_ubuntu_amd64.sh"
#source "${BASH_LIBRARY_DIR}/prepare_test_new.sh"
#
source "${BASH_LIBRARY_DIR}/download_builds.sh"

source "${BASH_LIBRARY_DIR}/select_topology.sh" "2n" "skx"
source "${BASH_LIBRARY_DIR}/activate_csit_virtualenv.sh"
source "${BASH_LIBRARY_DIR}/reserve_testbed.sh"
source "${BASH_LIBRARY_DIR}/clean_testbeds.sh"
source "${BASH_LIBRARY_DIR}/select_perpatch_tags.sh"
source "${BASH_LIBRARY_DIR}/compose_pybot_arguments.sh"
source "${BASH_LIBRARY_DIR}/run_pybot.sh" "strict"
source "${BASH_LIBRARY_DIR}/prepare_test_parent.sh"
source "${BASH_LIBRARY_DIR}/run_pybot.sh" "strict"
source "${BASH_LIBRARY_DIR}/unreserve_testbed.sh"
source "${BASH_LIBRARY_DIR}/compare_test_results.sh"
# TODO: Make sure archiving works as expected.
