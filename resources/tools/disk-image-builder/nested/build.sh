#!/bin/sh -e

# Copyright (c) 2016 Cisco and/or its affiliates.
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

# Note: In order to limit the damage this script can do, it is recommended
# to NOT run as root.

#
# 1. Download buildroot
# 2. Build buildroot kernel and root file system as per
#    config files included in this package
# 3. Create empty disk image and extract buildroot root
#    file system onto it, make it bootable
# 4. Apply any patches/additions included in this package
#
BUILD_DIR="$(dirname $0)/build"

BUILDROOT_NAME='buildroot-2016.02'
BUILDROOT_DIR="${BUILD_DIR}/${BUILDROOT_NAME}"
BUILDROOT_TARBALL="${BUILDROOT_NAME}.tar.gz"
BUILDROOT_URL="https://buildroot.org/downloads/${BUILDROOT_TARBALL}"
BUILDROOT_OUTPUT="${BUILDROOT_DIR}/output/images/rootfs.tar"

DISK_FREE_SIZE=8388608              # Min. free space on disk (8 MB)
DISK_ROUND_TO_NEAREST=16777216      # Round disk size up to nearest (16 MB)

VERSION=$(cat $(dirname $0)/CHANGELOG  | grep '^## ' | head -1 | sed -e 's/.*\[\(.*\)\].*/\1/')
if [ "${VERSION}" = "" ]
then
  echo "Unable to determine build version from CHANGELOG file. Make sure"
  echo "that there is an entry for the most recent version in CHANGELOG,"
  echo "and that the entry is formated like"
  echo
  echo "## [1.0] - 2016-05-16"
  exit 1
fi

mkdir -p ${BUILD_DIR}

echo Building version: ${VERSION}
echo $VERSION > ${BUILD_DIR}/VERSION
echo "NESTED_VERSION=${VERSION}" > ${BUILD_DIR}/VERSION_HIDDEN
img_name="${BUILD_DIR}/csit-nested-${VERSION}.img"

# Normally no need to touch the variables below
DISK_SECT_SIZE=512
DISK_HEADS=16
DISK_SECT_PER_TRACK=63
DISK_RESERVED_SECTORS=2048

MOUNT_TMPDIR="${BUILD_DIR}/tmp-mount"

set -e

# Download buildroot if not already there
wget -P ${BUILD_DIR} -N $BUILDROOT_URL
tar -C ${BUILD_DIR} -xzf ${BUILD_DIR}/$BUILDROOT_TARBALL

# Apply DPDK patch to buildroot. Do not fail if this patch has already been applied.
patch -N -d ${BUILDROOT_DIR} -p1 < buildroot-patches/dpdk.patch || /bin/true

cp -p buildroot-config $BUILDROOT_DIR/.config
cp -p kernel-defconfig $BUILDROOT_DIR/kernel-defconfig
make -C $BUILDROOT_DIR

if [ ! -f ${BUILDROOT_OUTPUT} ]
then
  echo "Buildroot compiled OK, but root file system ${BUILDROOT_OUTPUT}"
  echo "does not exist. Somethig is wrong. Exiting."
  exit 1
fi

# If we got here, it means we downloaded (if applicable) and built (if
# applicable) buildroot OK.
#
# Now let's calculate the required disk size, and build an empty disk.

buildroot_size=$(stat -c%s ${BUILDROOT_OUTPUT})
desired_size=$(( ${buildroot_size} + ${DISK_FREE_SIZE} ))
rounded_size=$(( ((${desired_size}/${DISK_ROUND_TO_NEAREST})+1) * \
                  ${DISK_ROUND_TO_NEAREST} ))

echo "Actual root FS size: ${buildroot_size}"
echo "Root FS size + desired free space (${DISK_FREE_SIZE}): ${desired_size}"
echo "Root FS size rounded to nearest ${DISK_ROUND_TO_NEAREST}:" \
  "${rounded_size} ($(( ${rounded_size} / 1024 / 1024 )) MB)"

# In a normal world, we'd be creating a full-size empty image with "dd", an
# then use fdisk to partition it, and a tool like "kpartx" to map this into
# individual partitions. We'd then map the partition we're interested in.
# However, in order to avoid messing with /dev/mapper, we can also create
# our actual partition first, and then merge it with the MBR+partition table
# "prefix" to obtain our full disk.

sectors=$(( ${rounded_size} / ${DISK_SECT_SIZE} ))

disk_prefix=${img_name}.prefix
disk_main=${img_name}.main

dd if=/dev/zero of=${disk_prefix} bs=${DISK_SECT_SIZE} \
  count=${DISK_RESERVED_SECTORS}
dd if=/dev/zero of=${disk_main} bs=${DISK_SECT_SIZE} \
  count=$(( $sectors - ${DISK_RESERVED_SECTORS} ))

# Format and mount the root file system
mkfs.ext2 -F -L root ${disk_main}
mkdir -p ${MOUNT_TMPDIR}
sudo mount -o loop ${disk_main} ${MOUNT_TMPDIR}
trap "sudo umount ${MOUNT_TMPDIR}" EXIT

# Extract the root filesystem
echo "Extracting root filesystem..."
sudo tar -C ${MOUNT_TMPDIR} -xf ${BUILDROOT_OUTPUT}

# Apply any patches
echo "Applying patches/modifications"
mydir=$(pwd)
cd ${MOUNT_TMPDIR}
sudo run-parts -v  ${mydir}/image-patches
cd ${mydir}

# Copy version and changelog
sudo cp ${BUILD_DIR}/VERSION ${MOUNT_TMPDIR}/
sudo cp ${mydir}/CHANGELOG ${MOUNT_TMPDIR}/
# Also embed this into a hidden file that we can easily retrieve with
# "cat <disk image> | strings | grep NESTED_VERSION"
sudo cp ${BUILD_DIR}/VERSION_HIDDEN ${MOUNT_TMPDIR}/.VERSION.HIDDEN

# Unmount root filesystem
sudo umount ${MOUNT_TMPDIR}
trap EXIT
rmdir ${MOUNT_TMPDIR}

# Now create our larger disk
cat ${disk_prefix} ${disk_main} > ${img_name}
rm -f ${disk_prefix} ${disk_main}

# Create partition table on the disk
sed -e 's/\s*\([\+0-9a-zA-Z]*\).*/\1/' << _EOF | fdisk -H ${DISK_HEADS} -S ${DISK_SECT_PER_TRACK} ${img_name}
  o # clear the in memory partition table
  n # new partition
  p # primary partition
  1 # partition number 1
  ${DISK_RESERVED_SECTORS} # Start a few KB into the disk, leave room for GRUB
    # Default - all the way through the end of the disk
  a # make a partition bootable
  1 # bootable partition is partition 1
  p # print the in-memory partition table
  w # write the partition table
  q # and we're done
_EOF

disk_cylinders=$(fdisk -l -H ${DISK_HEADS} -S ${DISK_SECT_PER_TRACK} ${img_name} | \
  grep cylinders | \
  sed -e 's/.* \([0-9][0-9]*\) cylinders.*/\1/')

echo "Disk has ${disk_cylinders} cylinders"

# Install GRUB bootloader on the disk image
${BUILDROOT_DIR}/output/host/sbin/grub --device-map=/dev/null <<_EOF
device (hd0) ${img_name}
geometry (hd0) ${disk_cylinders} ${DISK_HEADS} ${DISK_SECT_PER_TRACK}
root (hd0,0)
setup (hd0)
quit
_EOF

echo
echo
echo
echo "Your image should be ready in:"
ls -l ${img_name}
