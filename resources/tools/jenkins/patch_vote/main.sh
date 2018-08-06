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

set -exu -o pipefail

# Assumptions:
# + Jenkins ${WORKDIR} (or some other directory)
#   holds VPP repo with patch under test checked out.
# + It contains csit subdirectory with CSIT code to use (this script is there).
# FIXME: job name, jenkins comment, ...?

script_dir=$(dirname $(readlink -e "${BASH_SOURCE[0]}"))
tools_dir=$(readlink -e "$script_dir/..")
csit_dir=$(readlink -e "$tools_dir/../../..")
vpp_dir=$(readlink -e "$csit_dir/..")
#source "$tools_dir/vpp_build/setup_vpp_dpdk_dev_env.sh"
#source "$tools_dir/vpp_build/build_vpp_ubuntu_amd64.sh"
#source "$script_dir/prepare_build_parent.sh"
#source "$tools_dir/vpp_build/build_vpp_ubuntu_amd64.sh"
#
source "$script_dir/download_builds.sh"
#
source "$script_dir/prepare_test_new.sh"
source "$tools_dir/run_tests/vpp_csit_verify_perf.sh"
source "$script_dir/prepare_test_parent.sh"
source "$tools_dir/run_tests/vpp_csit_verify_perf.sh"
