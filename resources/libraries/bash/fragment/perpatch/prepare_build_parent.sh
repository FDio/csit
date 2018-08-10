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
# - ${VPP_DIR} - Assumed to be a local git repository, parent commit checked out.
# - build_new - Old contents removed, content of build-root copied here.
# Functions called:
# - die - Print to stderr and exit, defined in common_functions.sh

cd "${VPP_DIR}" || die 1 "Change directory operation failed."
rm -rf "build_new" || die 1 "Remove operation failed."
mkdir -p "build_new" || die 1 "Directory creation failed."
mv "build-root"/*".deb" "build_new"/ || die 1 "Move operation failed."
# The previous build could have left some incompatible leftovers,
# e.g. DPDK artifacts of different version.
# "make -C dpdk clean" does not actually remove such .deb file.
# Also, there usually is a copy of dpdk artifact in build-root.
git clean -dffx "dpdk"/ "build-root"/ || die 1 "Git clean operation failed."
# Finally, check out the parent commit.
git checkout HEAD~ || die 1 "Git checkout operation failed."
# Check for any other leftovers.
git status || die 1 "Git status operation failed."
