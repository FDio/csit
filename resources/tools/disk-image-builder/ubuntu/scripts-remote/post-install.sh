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

###
### APT
###
echo "********** INSTALLING APT PACKAGES **********"
echo -n > /etc/apt/sources.list

export DEBIAN_FRONTEND=noninteractive

# We're doing this the hard way as we're dealing with a bunch of
# .deb packages rather than any sources organized through APT.

# Attempt up to five cycles of unpack/configure. There may be dependency
# problems during the first one(s).

attempt=1
MAX_ATTEMPTS=5
try_again=1

while [ $attempt -le $MAX_ATTEMPTS ] && [ $try_again -eq 1 ]
do
  try_again=0
  echo "Attempting .deb package installation, attempt #${attempt}/${MAX_ATTEMPTS}"
  dpkg --unpack --recursive --skip-same-version ${TEMP_PATH}/deb || try_again=1
  dpkg --configure --pending || try_again=1
  if [ $try_again -eq 1 ]
  then
    echo Encountered errors.
  fi
  attempt=$(( $attempt + 1 ))
done

if [ $try_again -eq 1 ]
then
  echo "Still encountered errors after ${MAX_ATTEMPTS} attempts. Aborting".
  exit 1
fi

##
## PIP
##
echo "********** INSTALLING PIP PACKAGES **********"
pip install --no-index --find-links ${TEMP_PATH}/pip/ -r ${TEMP_PATH}/requirements.txt


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

##
## Java
##
echo "********** CREATING JAVA SHELL PROFILE **********"
mkdir -p /etc/profile.d
echo 'export JAVA_HOME=/usr/lib/jvm/java-8-openjdk-amd64' > /etc/profile.d/java.sh
echo 'export PATH=$JAVA_HOME/bin:$PATH' >> /etc/profile.d/java.sh

##
## Huge Pages
##
echo "********** CONFIGURING HUGE PAGES **********"
cat - > /etc/sysctl.d/90-csit.conf <<"_EOF"
# Number of 2MB hugepages desired
vm.nr_hugepages=1024

# Must be greater than or equal to (2 * vm.nr_hugepages).
vm.max_map_count=20000

# All groups allowed to access hugepages
vm.hugetlb_shm_group=0

# Shared Memory Max must be greator or equal to the total size of hugepages.
# For 2MB pages, TotalHugepageSize = vm.nr_hugepages * 2 * 1024 * 1024
# If the existing kernel.shmmax setting  (cat /sys/proc/kernel/shmmax)
# is greater than the calculated TotalHugepageSize then set this parameter
# to current shmmax value.
kernel.shmmax=2147483648
_EOF
ln -s /dev/null /etc/sysctl.d/80-vpp.conf

##
## Changelog
##
echo "********** MOVING CHANGELOG AND VERSION FILES **********"

mv ${TEMP_PATH}/VERSION /
mv ${TEMP_PATH}/CHANGELOG /

echo "********** CLEANING UP **********"
rm -fr ${TEMP_PATH}
