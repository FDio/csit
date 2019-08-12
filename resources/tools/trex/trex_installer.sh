#!/bin/bash

set -exuo pipefail

TREX_VERSION=$1

TREX_DOWNLOAD_REPO="https://github.com/cisco-system-traffic-generator/trex-core/archive/"
TREX_DOWNLOAD_PACKAGE="v${TREX_VERSION}.zip"
TREX_PACKAGE_URL="${TREX_DOWNLOAD_REPO}${TREX_DOWNLOAD_PACKAGE}"
TARGET_DIR="/opt/"
TREX_DIR="trex-core-${TREX_VERSION}/"
TREX_INSTALL_DIR="${TARGET_DIR}${TREX_DIR}"

if [[ "$(id -u)" != "0" ]]; then
    echo "Please use root or sudo to be able to access target installation directory: ${TARGET_DIR}"
    exit 1
fi

WORKING_DIR=$(mktemp -d) || exit 1

cleanup () {
    rm -rf ${WORKING_DIR}
}
trap cleanup EXIT

if [[ -d "${TREX_INSTALL_DIR}" ]]; then
    echo "T-REX aleready installed: ${TREX_INSTALL_DIR}"
else
    wget -P "${WORKING_DIR}" "${TREX_PACKAGE_URL}" || exit 1
    unzip "${WORKING_DIR}/${TREX_DOWNLOAD_PACKAGE}" -d "${TARGET_DIR}" || exit 1
    cd "${TREX_INSTALL_DIR}/linux_dpdk/" && ./b configure && ./b build || exit 1
    cd "${TREX_INSTALL_DIR}/scripts/ko/src" && make && make install || exit 1
fi

dir_with_patch="/tmp/openvpp-testing/resources/patch/trex/2.54"
dir_to_patch="/opt/trex-core-2.54/"
dir_to_patch+="/scripts/automation/trex_control_plane/interactive/trex/common/"
pushd "${dir_to_patch}"
set +e
patch -N < "${dir_with_patch}/no_stats_clear_on_connect.patch"
status="${?}"
set -e
if [[ "${status}" == "0" ]]; then
    echo "Trex patched and ready."
else
    echo "Patch has been probably applied already."
popd
