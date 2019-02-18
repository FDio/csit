#!/usr/bin/env bash

# Copyright (c) 2019 Cisco and/or its affiliates.
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
    # Generate temporary dockerfile based on $OS_ID variable
    #
    # variable read:
    # - OSID - detected OS from os-release fike

    set -exuo pipefail
    
    case ${OS_FAMILY} in
        debian)
                generate_dpkg_dockerfile || die
                ;;
        rhel)
                generate_rpm_dockerfile || die
                ;;
        *)
                die "Your system is not supported."
                ;;
    esac
}

function generate_dpkg_dockerfile () {
    # Create temporary Dockerfile for Debian based system with prepared VPP
    # artifacts in download_dir.
    #
    # Variables read:
    # - CSIT_DIR - Path to existing root of local CSIT git repository.
    # Variables set:
    # - DCR_DOCKERFILE - Temporary Docker file location

    set -exuo pipefail

    DCR_DOCKERFILE=$(mktemp)

    if [ ! -z "$(< ${CSIT_DIR}/VPP_DEVICE_IMAGE))" ]; then

    cat > ${DCR_DOCKERFILE} << __EOF__
FROM $(< ${CSIT_DIR}/VPP_DEVICE_IMAGE)
COPY ./*.deb /tmp/vpp/
RUN apt-get purge -y "*vpp*" \\
 || dpkg -i --force-all /tmp/vpp/*.deb \\
 && rm -f /tmp/vpp/*.deb
__EOF__

    else
        die "VPP_DEVICE_IMAGE not set"
    fi
}

function generate_rpm_dockerfile () {
    # Create temporary Dockerfile for RedHat based system with prepared VPP
    # artifacts in download_dir.
    #
    # Variables read:
    # - CSIT_DIR - Path to existing root of local CSIT git repository.
    # Variables set:
    # - DCR_DOCKERFILE - Temporary Docker file location

    set -exuo pipefail

    DCR_DOCKERFILE=$(mktemp)

    if [ ! -z "$(< ${CSIT_DIR}/VPP_DEVICE_IMAGE))" ]; then

    cat > ${DCR_DOCKERFILE} << __EOF__
FROM $(< ${CSIT_DIR}/VPP_DEVICE_IMAGE)
COPY ./*.rpm /tmp/vpp/
RUN yum -y remove "*vpp*" \\
 || rpm -ihv /tmp/vpp/*.rpm \\
 && rm -f /tmp/vpp/*.rpm
__EOF__

    else
        die "VPP_DEVICE_IMAGE not set"
    fi
}
