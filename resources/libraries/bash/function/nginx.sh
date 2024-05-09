#!/usr/bin/env bash

# Copyright (c) 2023 Intel and/or its affiliates.
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

    # Ensure stable NGINX archive is downloaded.
    #
    # Variables read:
    # - DOWNLOAD_DIR - Path to directory robot takes the build to test from.
    # - NGINX_VER - Version number of Nginx.
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
            die "Failed to get NGINX package from: ${nginx_repo}."
        }
    fi
    popd || die "Popd failed."
}


function common_dirs () {

    # Set global variables, create some directories (without touching content).
    # This function assumes running in remote testbed. It might override other
    # functions if included from common.sh.

    # Arguments:
    # - ${1} - Version number of Nginx.
    # Variables set:
    # - BASH_FUNCTION_DIR - Path to existing directory this file is located in.
    # - CSIT_DIR - Path to CSIT framework.
    # - DOWNLOAD_DIR - Path to directory robot takes the build to test from.
    # - NGINX_DIR - Path to NGINX framework.
    # - NGINX_VER - Version number of Nginx.
    # Functions called:
    # - die - Print to stderr and exit.

    set -exuo pipefail
    NGINX_VER="${1}"
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
    # - NGINX_INS_PATH - Path to NGINX install path.
    # Functions called:
    # - die - Print to stderr and exit.

    set -exuo pipefail
    NGINX_INS_PATH="${DOWNLOAD_DIR}/${NGINX_VER}"
    pushd "${NGINX_DIR}" || die "Pushd failed."

    # Set installation prefix.
    param="--prefix=${NGINX_INS_PATH} "
    # Set nginx binary pathname.
    param+="--sbin-path=${NGINX_INS_PATH}/sbin/nginx "
    # Set nginx.conf pathname.
    param+="--conf-path=${NGINX_INS_PATH}/conf/nginx.conf "
    # Enable ngx_http_stub_status_module.
    param+="--with-http_stub_status_module "
    # Force PCRE library usage.
    param+="--with-pcre "
    # Enable ngx_http_realip_module.
    param+="--with-http_realip_module "
    params=(${param})
    ./configure "${params[@]}" || die "Failed to configure NGINX!"
    make -j 16 || die "Failed to compile NGINX!"
    make install || die "Failed to install NGINX!"
}


function nginx_patch () {

    # Patch NGINX archive.
    #
    # This is needed when testing large payloads.
    # The patch has no reason to affect the performance in any way.
    #
    # Variables read:
    # - NGINX_DIR - Path to NGINX framework.
    # Functions called:
    # - die - Print to stderr and exit.

    set -exuo pipefail

    # Modify NGX_CONF_BUFFER, 10 MiB should be enough for now.
    sed -i "s/4096/1024 \* 1024 \* 10/" "${NGINX_DIR}/src/core/ngx_conf_file.c"
    # Exit code propagates to teh caller.
}


function nginx_extract () {

    # Extract NGINX framework.
    #
    # Variables read:
    # - NGINX_DIR - Path to NGINX framework.
    # - CSIT_DIR - Path to CSIT framework.
    # - DOWNLOAD_DIR - Path to directory robot takes the build to test from.
    # - NGINX_VER - Version number of Nginx.
    # Functions called:
    # - die - Print to stderr and exit.

    set -exuo pipefail

    pushd "${CSIT_DIR}" || die "Pushd failed."
    tar -xvf ${DOWNLOAD_DIR}/${NGINX_VER}.tar.gz --strip=1 \
          --directory "${NGINX_DIR}" || {
          die "Failed to extract NGINX!"
    }
}
