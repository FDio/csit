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

# TODO: Make sure this works on other distros/archs too.

# Arguments:
# - ${1} - String identifier for echo, required (to avoid inheriting context).
# Variables read:
# - VPP_DIR - Path to existing directory, parent to accessed directories.
# Directories updated:
# - ${VPP_DIR} - Whole subtree, many files (re)created by the build process.
# - ${VPP_DIR}/build-root - Final build artifacts for CSIT end up here.
# - ${VPP_DIR}/dpdk - The dpdk artifact is built, but moved to build-root/.
# Functions called:
# - die - Print to stderr and exit, defined in common_functions.sh

cd "${VPP_DIR}" || die 1 "Change directory command failed."
echo 'Building using "make build-root/vagrant/build.sh"'
# TODO: Do we want to support "${DRYRUN}" == "True"?
make UNATTENDED=yes install-dep || die 1 "Make install-dep failed."
# If the same DPDK version is detected, .deb is not built, thus uninstall.
INSTALLED_DEB_VER=$(sudo dpkg-query --showformat='${Version}'\
     --show vpp-dpdk-dev || true)
if [[ -n "${INSTALLED_DEB_VER}" ]]; then
    # DEBUG
    sudo dpkg -l "vpp-dpdk-dev"
    sudo dpkg --purge "vpp-dpdk-dev" || {
        die 1 "Dpdk package uninstalation failed."
    }
fi
make UNATTENDED=yes dpdk-install-dev || die 1 "Make dpdk-install-dev failed."
"build-root/vagrant/build.sh" || die 1 "Vagrant VPP build script failed."
# CSIT also needs the DPDK artifacts, which is not in build-root.
mv -v "dpdk/vpp-dpdk-dkms"*".deb" "build-root"/ || die 1 "*.deb move failed."

echo "*******************************************************************"
echo "* VPP ${1} BUILD SUCCESSFULLY COMPLETED" || die 1 "Argument not found."
echo "*******************************************************************"
