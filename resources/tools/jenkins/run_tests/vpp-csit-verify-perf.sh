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

set -exu -o pipefail

# Assumptions:
# CSIT cloned as `pwd`/csit
# VPP build copied there, e.g. $ cp build-root/*.deb csit/
# Possibly also with DPDK .deb files.

# Export test type.
export TEST_TAG="VERIFY-PERF-PATCH"

#cp build-root/*.deb csit/
#if [ -e dpdk/vpp-dpdk-dkms*.deb ]
#then
#    cp dpdk/vpp-dpdk-dkms*.deb csit/
#else
#    cp /w/dpdk/vpp-dpdk-dkms*.deb csit/ 2>/dev/null || :
#    cp /var/cache/apt/archives/vpp-dpdk-dkms*.deb csit/ 2>/dev/null || :
#fi

# run the script
"$csit_dir/bootstrap-verify-perf.sh" "$csit_dir"/*.deb

# vim: ts=4 ts=4 sts=4 et :
