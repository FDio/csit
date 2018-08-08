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

# FIXME: Add documentation.

# TODO: Cherry-pick improvements from ci-management: jjb/vpp/include-raw-vpp-build.sh

# FIXME: Simplify even more, or make sure this works on other environments too.


OS_ID=$(grep '^ID=' /etc/os-release | cut -f2- -d= | sed -e 's/\"//g')
OS_VERSION_ID=$(grep '^VERSION_ID=' /etc/os-release | cut -f2- -d= | sed -e 's/\"//g')

echo OS_ID: $OS_ID
echo OS_VERSION_ID: $OS_VERSION_ID

echo "Building using \"make build-root/vagrant/build.sh\""
[ "x${DRYRUN}" == "xTrue" ] || make UNATTENDED=yes install-dep
[ "x${DRYRUN}" == "xTrue" ] || make UNATTENDED=yes dpdk-install-dev
[ "x${DRYRUN}" == "xTrue" ] || build-root/vagrant/build.sh

echo "*******************************************************************"
echo "* VPP BUILD SUCCESSFULLY COMPLETED"
echo "*******************************************************************"

cp dpdk/vpp-dpdk-dkms*.deb build-root/
