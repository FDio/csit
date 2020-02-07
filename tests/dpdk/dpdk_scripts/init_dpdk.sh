#!/bin/bash

set -x

# Setting variables
DPDK_DIR=dpdk
ROOTDIR=/tmp/openvpp-testing
PWDDIR=$(pwd)

# set arch, default to x86_64 if none given
ARCH=${3:-"x86_64"}

# dpdk prefers "arm64" to "aarch64" and does not allow arm64 native target
if [ $ARCH == "aarch64" ]; then
    ARCH="arm64"
    MACHINE="armv8a"
else
    MACHINE="native"
fi

cd ${ROOTDIR}/${DPDK_DIR}/

# Binding
./usertools/dpdk-devbind.py -b vfio-pci $1 $2 || \
    { echo "Failed to bind interface $1 and $2 to vfio-pci"; exit 1; }

cd ${PWDDIR}
