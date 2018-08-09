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

# Variables read:
# - VPP_DIR - Path to existing directory, parent to accessed directories.
# Directories read:
# - build-root - Existing directory with built VPP artifacts (including DPDK).
# Directories updated:
# - $VPP_DIR - Assument to be a local git repository, parent commit is checked out.
# - build_new - Old contents removed, content of build-root copied here.

cd "${VPP_DIR}"
rm -rf build_new
cp -r build-root build_new
# The previous build could have left some incompatible leftovers,
# e.g. DPDK artifacts of different version.
make wipe && make -C dpdk clean
git checkout HEAD~
