#!/usr/bin/env bash

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

function generate_dockerfile () {
    # Get and/or install VPP artifacts from packagecloud.io.
    #
    # Variables read:
    # - CSIT_DIR - Path to existing root of local CSIT git repository.
    # Variables set:
    # - REPO_URL - FD.io Packagecloud repository.
    # - DCR_DOCKERFILE - Generated temorary dockerfile

    set -exuo pipefail

    os_id=$(grep '^ID=' /etc/os-release | cut -f2- -d= | sed -e 's/\"//g') || {
        die "Get OS release failed."
    }

    case ${os_id} in
	ubuntu)
		generate_dpkg_dockerfile || die
		;;
	cenots|opensuse)
		generate_rpm_dockerfile || die
		;;
	*)
		die "${os_id} is not yet supported."
		;;
    esac
}

function generate_dpkg_dockerfile () {
    # Get and/or install Ubuntu VPP artifacts from packagecloud.io.
    #
    # Variables read:
    # - REPO_URL - FD.io Packagecloud repository.
    # - VPP_VERSION - VPP version.
    # - INSTALL - If install packages or download only. Default: download

    set -exuo pipefail

    DCR_DOCKERFILE=$(mktemp)

    cat > ${DCR_DOCKERFILE} << __EOF__
FROM $(< ${CSIT_DIR}/VPP_DEVICE_IMAGE)
COPY ./*.deb /tmp/vpp/
RUN apt-get purge -y "*vpp*" \\
 || dpkg -i --force-all /tmp/vpp/*.deb \\
 && rm -f /tmp/vpp/*.deb
__EOF__
}

function generate_rpm_dockerfile () {
    # Get and/or install CentOS VPP artifacts from packagecloud.io.
    #
    # Variables read:
    # - REPO_URL - FD.io Packagecloud repository.
    # - VPP_VERSION - VPP version.
    # - INSTALL - If install packages or download only. Default: download

    set -exuo pipefail

    DCR_DOCKERFILE=$(mktemp)

    cat > ${DCR_DOCKERFILE} << __EOF__
FROM $(< ${CSIT_DIR}/VPP_DEVICE_IMAGE)
COPY ./*.rpm /tmp/vpp/
RUN yum -y remove "*vpp*" \\
 || rpm -ihv /tmp/vpp/*.rpm \\
 && rm -f /tmp/vpp/*.rpm
__EOF__
}
