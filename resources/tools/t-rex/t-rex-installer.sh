#!/bin/sh

TREX_VERSION="2.06"

TREX_DOWNLOAD_REPO="https://github.com/cisco-system-traffic-generator/trex-core/archive/"
TREX_DOWNLOAD_PACKAGE="v${TREX_VERSION}.zip"
TREX_PACKAGE_URL="${TREX_DOWNLOAD_REPO}${TREX_DOWNLOAD_PACKAGE}"
TARGET_DIR="/opt/"
TREX_DIR="trex-core-${TREX_VERSION}/"
TREX_INSTALL_DIR="${TARGET_DIR}${TREX_DIR}"

if test "$(id -u)" -ne 0
then
    echo "Please use root or sudo to be able to access target installation directory: ${TARGET_DIR}"
    exit 1
fi

WORKING_DIR=$(mktemp -d)
test $? -eq 0 || exit 1

cleanup () {
    rm -r ${WORKING_DIR}
}

trap cleanup EXIT

test -d ${TREX_INSTALL_DIR} && echo "T-REX aleready installed: ${TREX_INSTALL_DIR}" && exit 0

wget -P ${WORKING_DIR} ${TREX_PACKAGE_URL}
test $? -eq 0 || exit 1

unzip ${WORKING_DIR}/${TREX_DOWNLOAD_PACKAGE} -d ${TARGET_DIR}
test $? -eq 0 || exit 1

cd ${TREX_INSTALL_DIR}/linux_dpdk/ && ./b configure && ./b build || exit 1
cd ${TREX_INSTALL_DIR}/scripts/ko/src && make && make install || exit 1

