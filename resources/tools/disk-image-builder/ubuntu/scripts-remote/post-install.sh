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

TEMP_PATH="/root/temp"

##
## APT packages
##
echo "********** INSTALLING APT PACKAGES **********"
echo -n > /etc/apt/sources.list

#
# This is ugly. Seems dpkg always errors out on qemu unless it's
# installed separately.
#
export DEBIAN_FRONTEND=noninteractive
dpkg -R -i ${TEMP_PATH}/deb || echo CONTINUING WITH ERRORS
dpkg -i ${TEMP_PATH}/deb/libpam-modules* ${TEMP_PATH}/deb/qemu*

##
## Pip
##
echo "********** INSTALLING PIP PACKAGES **********"
pip install --no-index --find-links ${TEMP_PATH}/pip/ -r ${TEMP_PATH}/requirements.txt


##
## Serial console
##
echo "********** CONFIGURING SERIAL CONSOLE AND DISABLING IPV6 **********"
cat - > /etc/init/ttyS0.conf <<"_EOF"
# ttyS0 - getty
#
# This service maintains a getty on ttyS0 from the point the system is
# started until it is shut down again.

start on stopped rc RUNLEVEL=[12345]
stop on runlevel [!12345]

respawn
exec /sbin/getty -L 115200 ttyS0 vt102
_EOF

cat - > /etc/default/grub <<"_EOF"
# If you change this file, run 'update-grub' afterwards to update
# /boot/grub/grub.cfg.
# For full documentation of the options in this file, see:
#   info -f grub -n 'Simple configuration'

GRUB_DEFAULT=0
GRUB_TIMEOUT=1
GRUB_DISTRIBUTOR=`lsb_release -i -s 2> /dev/null || echo Debian`
GRUB_CMDLINE_LINUX="console=tty0 console=ttyS0,115200n8 ipv6.disable=1"

GRUB_TERMINAL=serial
GRUB_SERIAL_COMMAND="serial --speed=115200 --unit=0 --word=8 --parity=no --stop=1"

# Uncomment if you don't want GRUB to pass "root=UUID=xxx" parameter to Linux
#GRUB_DISABLE_LINUX_UUID=true

# Uncomment to disable generation of recovery mode menu entries
#GRUB_DISABLE_RECOVERY="true"

# Uncomment to get a beep at grub start
#GRUB_INIT_TUNE="480 440 1"
_EOF

update-grub


echo "********** CREATING HISTORIC LINK FOR QEMU, COPY NESTED VM IMAGE **********"
mkdir -p /opt/qemu/bin
ln -s /usr/bin/qemu-system-x86_64 /opt/qemu/bin/qemu-system-x86_64

mkdir -p /var/lib/vm

echo "Embedding nested VM image on this image"
mkdir /var/lib/vm/images
cp ${TEMP_PATH}/nested-vm/* /var/lib/vm/images/
# There should only be one file at this time
ln -s /var/lib/vm/images/* /var/lib/vm/vhost-nested.img

ls -lR /var/lib/vm

# Mount hugepages directory for nested VM
mkdir -p /mnt/huge
echo 'hugetlbfs	/mnt/huge	hugetlbfs	mode=1770,gid=111	0	0' >> /etc/fstab

echo "********** MOVING CHANGELOG AND VERSION FILES **********"

mv ${TEMP_PATH}/VERSION /
mv ${TEMP_PATH}/CHANGELOG /

echo "********** CLEANING UP **********"
rm -fr ${TEMP_PATH}
