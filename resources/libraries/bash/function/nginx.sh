#!/usr/bin/env bash

# Copyright (c) 2021 Cisco and/or its affiliates.
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

    this_file=$(readlink -e "${BASH_SOURCE[0]}") || {
        die "Some error during locating of this source file."
    }
    BASH_FUNCTION_DIR=$(dirname "${this_file}") || {
        die "Some error during dirname call."
    }
    CSIT_DIR=$(readlink -e "/tmp/openvpp-testing") || {
        die "Readlink failed."
    }
    mkdir -p "${CSIT_DIR}/nginx" || die "Mkdir failed."
    NGINX_DIR=$(readlink -e "${CSIT_DIR}/nginx") || {
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

    pushd "${NGINX_DIR}" || die "Pushd failed"

    ./configure --with-http_stub_status_module \
            --with-http_ssl_module \
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
    tar -xvf download_dir/nginx*.tar.gz --strip=1 \
          --directory "${NGINX_DIR}" || {
          die "Failed to extract NGINX!"
    }
}

