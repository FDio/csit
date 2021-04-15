#!/usr/bin/env bash

# Copyright (c) 2021 Intel and/or its affiliates.
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


function gather_nginx () {

    # Ensure latest NGINX archive is downloaded.
    #
    # Variables read:
    # - TEST_CODE - The test selection string from environment or argument.
    # Hardcoded:
    # - nginx archive name to download if TEST_CODE is not time based.
    # Directories updated:
    # - ./ - Assumed ${DOWNLOAD_DIR}, nginx-*.tar.xz is downloaded if not there.
    # Functions called:
    # - die - Print to stderr and exit, defined in common.sh
    # Nginx Version
    set -exuo pipefail
    pushd "${DOWNLOAD_DIR}" || die "Pushd failed."
    nginx_repo="http://nginx.org/download/"
    # Use downloaded packages with specific version
    echo "Downloading NGINX package of specific version from repo ..."
    # Downloading NGINX version based on what VPP is using. Currently
    # it is not easy way to detect from VPP version automatically.
    nginx_stable_ver="${NGINX_VER}".tar.gz

    if [[ ! -f "${nginx_stable_ver}" ]]; then
        wget -nv --no-check-certificate \
        "${nginx_repo}/${nginx_stable_ver}"  || {
            die "Failed to get NGINX package from: ${nginx_repo}"
        }
    fi
    popd || die "Popd failed."
}


function common_dirs () {

    # Set global variables, create some directories (without touching content).
    # This function assumes running in remote testbed. It might override other
    # functions if included from common.sh.

    # Variables set:
    # - BASH_FUNCTION_DIR - Path to existing directory this file is located in.
    # - NGINX_DIR - Path to NGINX framework.
    # - CSIT_DIR - Path to CSIT framework.
    # Functions called:
    # - die - Print to stderr and exit.

    set -exuo pipefail
    NGINX_VER=$1
    this_file=$(readlink -e "${BASH_SOURCE[0]}") || {
        die "Some error during locating of this source file."
    }
    BASH_FUNCTION_DIR=$(dirname "${this_file}") || {
        die "Some error during dirname call."
    }
    CSIT_DIR=$(readlink -e "/tmp/openvpp-testing") || {
        die "Readlink failed."
    }
    DOWNLOAD_DIR=$(readlink -f "${CSIT_DIR}/download_dir") || {
        die "Readlink failed."
    }
    mkdir -p "${CSIT_DIR}/${NGINX_VER}" || die "Mkdir failed."
    NGINX_DIR=$(readlink -e "${CSIT_DIR}/${NGINX_VER}") || {
        die "Readlink failed."
    }
}



function nginx_compile () {

    # Compile NGINX archive.
    #
    # Variables read:
    # - NGINX_DIR - Path to NGINX framework.
    # - CSIT_DIR - Path to CSIT framework.
    # Functions called:
    # - die - Print to stderr and exit.

    set -exuo pipefail
    NGINX_INS_PATH="${DOWNLOAD_DIR}/${NGINX_VER}"
    pushd "${NGINX_DIR}" || die "Pushd failed"

    ./configure --prefix="${NGINX_INS_PATH}" \
                --sbin-path="${NGINX_INS_PATH}/sbin/nginx" \
                --conf-path="${NGINX_INS_PATH}/conf/nginx.conf" \
                --with-http_stub_status_module \
                --with-pcre \
                --with-http_realip_module || {
                  die 'Failed to configure NGINX'
                }
    make -j 16;make install || die "Failed to compile NGINX!"
}


function nginx_extract () {

    # Extract NGINX framework.
    #
    # Variables read:
    # - NGINX_DIR - Path to NGINX framework.
    # - CSIT_DIR - Path to CSIT framework.
    # Functions called:
    # - die - Print to stderr and exit.

    set -exuo pipefail

    pushd "${CSIT_DIR}" || die "Pushd failed"
    tar -xvf download_dir/${NGINX_VER}.tar.gz --strip=1 \
          --directory "${NGINX_DIR}" || {
          die "Failed to extract NGINX!"
    }
}

