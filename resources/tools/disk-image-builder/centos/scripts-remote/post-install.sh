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

echo ==========================Remove NetworkManager============================
systemctl disable NetworkManager
systemctl enable network
yum -y remove NetworkManager

cat - > /etc/sysconfig/network-scripts/ifcfg-eth0 <<"_EOF"
DEVICE=eth0
BOOTPROTO=dhcp
ONBOOT=yes
_EOF
echo =======================End Remove NetworkManager===========================

###
### RPMs
###
echo "********** INSTALLING RPMs **********"

# We're doing this the hard way as we're dealing with a bunch of
# rpm packages without using yum.

# Attempt up to five cycles of unpack/configure. There may be dependency
# problems during the first one(s).
echo ==========================yum update==============================
yum clean all
yum install -y deltarpm
yum update -y
yum install -y @base epel-release
echo ==========================end yum update==============================
attempt=1
MAX_ATTEMPTS=3
try_again=1

RPM_FILE=${TEMP_PATH}/rpm/rpm-packages.txt
while [ $attempt -le $MAX_ATTEMPTS ] && [ $try_again -eq 1 ]
do
  try_again=0
  while read name url
  do
    # use rpm command if url is present in the package file
    if [ ! -z $url ] ; then
      rpm -i $url$name || try_again=1
    else
      yum install -y $name || try_again=1
    fi
  done < $RPM_FILE
  attempt=$(( $attempt + 1 ))
done

if [[ ( $try_again == 1 ) ]]
then
  echo "Still encountered errors after ${MAX_ATTEMPTS} attempts."
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
## Changelog
##
echo "********** MOVING CHANGELOG AND VERSION FILES **********"

mv ${TEMP_PATH}/VERSION /
mv ${TEMP_PATH}/CHANGELOG /

echo "********** CLEANING UP **********"
rm -fr ${TEMP_PATH}
