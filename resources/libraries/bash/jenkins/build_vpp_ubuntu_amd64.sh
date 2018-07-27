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


echo "Building using \"make build-root/vagrant/build.sh\""
[ "${DRYRUN:-x}" == "True" ] || make UNATTENDED=yes install-dep
[ "${DRYRUN:-x}" == "True" ] || make UNATTENDED=yes dpdk-install-dev
[ "${DRYRUN:-x}" == "True" ] || build-root/vagrant/build.sh

echo "*******************************************************************"
echo "* VPP $1 BUILD SUCCESSFULLY COMPLETED"
echo "*******************************************************************"

cp dpdk/vpp-dpdk-dkms*.deb build-root/
