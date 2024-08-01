#!/usr/bin/env bash

# Copyright (c) 2024 Cisco and/or its affiliates.
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


function go_install () {

    # Install Go.

    OS_ARCH=$(uname -m) || die "Failed to get arch."
    case "${OS_ARCH}" in
        x86_64) architecture="amd64" ;;
        aarch64) architecture="arm64" ;;
    esac

    go_version="go1.20.2.linux-${architecture}.tar.gz"
    go_url="https://go.dev/dl"
    wget "${go_url}/${go_version}"
    rm -rf "/usr/local/go"
    tar -C "/usr/local" -xzf "go1.20.2.linux-${architecture}.tar.gz"
    rm "go1.20.2.linux-${architecture}.tar.gz"
    export PATH=$PATH:/usr/local/go/bin
}


function hugo_build_site () {

    # Build site via Hugo.
    #
    # Variable read:
    # - ${CSIT_DIR} - CSIT main directory.
    # Functions called:
    # - die - Print to stderr and exit.

    if ! installed hugo; then
        hugo_install || die "Please install Hugo!"
    fi

    pushd "${CSIT_DIR}"/docs || die "Pushd failed!"
    hugo || die "Failed to run Hugo build!"
    popd || die "Popd failed!"
}


function hugo_init_modules () {

    # Initialize Hugo modules.
    #
    # Variable read:
    # - ${CSIT_DIR} - CSIT main directory.
    # Functions called:
    # - die - Print to stderr and exit.

    if ! installed hugo; then
        hugo_install || die "Please install Hugo!"
    fi

    hugo_book_url="github.com/alex-shpak/hugo-book"
    hugo_book_version="v0.0.0-20230424134111-d86d5e70c7c0"
    hugo_book_link="${hugo_book_url}@${hugo_book_version}"
    pushd "${CSIT_DIR}"/docs || die "Pushd failed!"
    export PATH=$PATH:/usr/local/go/bin
    hugo mod get "${hugo_book_link}" || die "Failed to run Hugo mod!"
    popd || die "Popd failed!"
}


function hugo_install () {

    # Install Hugo Extended.

    OS_ARCH=$(uname -m) || die "Failed to get arch."
    case "${OS_ARCH}" in
        x86_64) architecture="amd64" ;;
        aarch64) architecture="arm64" ;;
    esac

    hugo_version="v0.111.3/hugo_extended_0.111.3_linux-${architecture}.deb"
    hugo_url="https://github.com/gohugoio/hugo/releases/download"
    hugo_link="${hugo_url}/${hugo_version}"
    wget -O "hugo.deb" "${hugo_link}" || die "Failed to install Hugo!"
    dpkg -i "hugo.deb" || die "Failed to install Hugo!"
    rm "hugo.deb" || die "Failed to install Hugo!"
}


function installed () {

    # Check if the given utility is installed. Fail if not installed.
    #
    # Arguments:
    # - ${1} - Utility to check.
    # Returns (implicitly):
    # - 0 - If command is installed.
    # - 1 - If command is not installed.

    set -exuo pipefail

    command -v "${1}"
}
