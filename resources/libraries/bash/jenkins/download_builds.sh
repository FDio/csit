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

# Bash script fragment, to be sourced from main.sh

set -exuo pipefail

cd "${VPP_DIR}"
rm -rf build-root build_parent build_new archive
wget -N --progress=dot:giga "https://jenkins.fd.io/sandbox/job/vpp-csit-verify-hw-perf-master-up/1/artifact/*zip*/archive.zip"
unzip archive.zip
mv archive/build_parent ./
mv archive/build_new ./
cp -r build_new/*.deb csit/
# Create symlinks so that if job fails on robot test, results can be archived.
ln -s csit csit_new
