#!/bin/bash

set -x

# Setting variables
# set arch, default to x86_64 if none given
ARCH=${1:-"x86_64"}
PATCH=$2

# dpdk prefers "arm64" to "aarch64" and does not allow arm64 native target
if [ $ARCH == "aarch64" ]; then
    ARCH="arm64"
    MACHINE="armv8a"
else
    MACHINE="native"
fi

DPDK_DIR=dpdk
ROOTDIR=/tmp/openvpp-testing
PWDDIR=$(pwd)

# Compile the l3fwd
export RTE_SDK=${ROOTDIR}/${DPDK_DIR}/
export RTE_TARGET=${ARCH}-${MACHINE}-linuxapp-gcc
cd ${RTE_SDK}/examples/l3fwd
sudo sed -i 's/^#define RTE_TEST_RX_DESC_DEFAULT 128/#define RTE_TEST_RX_DESC_DEFAULT 2048/g' ./main.c
sudo sed -i 's/^#define RTE_TEST_TX_DESC_DEFAULT 512/#define RTE_TEST_TX_DESC_DEFAULT 2048/g' ./main.c

chmod +x ${PATCH} && source ${PATCH}

make clean
make -j || \
    { echo "Failed to compile l3fwd"; exit 1; }
cd ${PWDDIR}

