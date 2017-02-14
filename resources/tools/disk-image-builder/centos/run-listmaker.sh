#!/bin/bash

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

# This script is to spin up a simulation in VIRL, and fetch the URLs for all packages
# that the user would obtain if they did an "yum update" today.
#
# This entire step is neither secure nor portable. The assumption --for now-- is that
# this will only ever be run in LF CSIT VIRL lab. Should the requirement arise to
# run this elsewhere, then additional work may be required to make this more
# portable.

# This script requires that the following two environment variables be defined-
#
# $VIRL_USER
# $VIRL_PASSWORD

VERSION=$(cat $(dirname $0)/CHANGELOG  | grep '^## ' | head -1 | sed -e 's/.*\[\(.*\)\].*/\1/')
if [ "${VERSION}" = "" ]
then
  echo "Unable to determine build version from CHANGELOG file. Make sure"
  echo "that there is an entry for the most recent version in CHANGELOG,"
  echo "and that the entry is formated like"
  echo
  echo "## [1.0] - 2016-05-20"
  exit 1
fi
DATE=$(date +%Y-%m-%d)

if [ "$1" == "centos-7-1511" ]
then
    OS="centos-7-1511"
    VIRL_TOPOLOGY_FILE="listmaker/virl-listmaker-centos-7-1511.yaml"
elif [ "$1" == "centos-7.3-1611" ]
then
    OS="centos-7.3-1611"
    VIRL_TOPOLOGY_FILE="listmaker/virl-listmaker-centos-7.3-1611.yaml"
else
    echo specify argument -- probably centos-7-1511 or centos-7.3-1611
    exit 1
fi

RELEASE="${OS}_${DATE}_${VERSION}"
OUTPUT_DIR="lists/${RELEASE}"

echo "Building release ${RELEASE}."
echo "Storing data in ${OUTPUT_DIR}/."


# RPM packages wanted

RPM_WANTLIST_INFRA="nfs-utils cloud-init pkgconfig yum-utils"
RPM_WANTLIST_CSIT="python-devel python-pip python-virtualenv python-setuptools python-pip openssl-devel git strongswan"
RPM_WANTLIST_VPP="dkms bridge-utils"
RPM_WANTLIST_TREX="zlib-devel unzip"
RPM_WANTLIST_MISC="gperftools glusterfs glusterfs-api libiscsi libibverbs libpcap libpcap-devel libgfrpc libgfxdr libpixman libpng14 pulseaudio-libs librados2 librbd1 librdmacm libseccomp spice-server libusb usbredir glusterfs-devel seavgabios-bin sgabios-bin ipxe-roms-qemu nss-devel seabios-bin"

RPM_WANTLIST_NESTED="qemu-img-ev-2.3.0-31.el7_2.21.1.x86_64.rpm libcacard-ev-2.3.0-31.el7_2.21.1.x86_64.rpm libcacard-devel-ev-2.3.0-31.el7_2.21.1.x86_64.rpm qemu-kvm-ev-debuginfo-2.3.0-31.el7_2.21.1.x86_64.rpm qemu-kvm-tools-ev-2.3.0-31.el7_2.21.1.x86_64.rpm qemu-kvm-common-ev-2.3.0-31.el7_2.21.1.x86_64.rpm qemu-kvm-ev-2.3.0-31.el7_2.21.1.x86_64.rpm libcacard-tools-ev-2.3.0-31.el7_2.21.1.x86_64.rpm"
RPM_WANTLIST_JAVA="java-1.8.0-openjdk-headless java-1.8.0-openjdk-devel"
#RPM_WANTLIST_DOCKER="docker-engine"

### For now, do not include WANTLIST_NESTED in the main list. We're installing qemu
### separately because of the possible need for specific versions but the supported version seem to be ok for Centos 7.3
##
RPM_WANTLIST="$RPM_WANTLIST_INFRA $RPM_WANTLIST_CSIT $RPM_WANTLIST_VPP $RPM_WANTLIST_TREX $RPM_WANTLIST_MISC $RPM_WANTLIST_JAVA"

RPM_OUTPUTFILE="${OUTPUT_DIR}/rpm-packages.txt"

# Python requirements file. Can point to a manually crafted file
# here, or to the actual CSIT requirements file, or to a symlink.

PIP_REQUIREMENTS="../../../../requirements.txt"
if [ ! -f ${PIP_REQUIREMENTS} ]
then
  echo "PIP requirements file ${PIP_REQUIREMENTS} not found."
  exit 1
fi

PIP_OUTPUTFILE="${OUTPUT_DIR}/pip-requirements.txt"

# These will be used for SSH to the listmaker VM, and must match with what
# was defined in the listmaker VM's kickstart file.
SSH_USER="root"
SSH_PASS="csit"

###
### Spin up simulation
###
if [ "$VIRL_USER" = "" ] || [ "$VIRL_PASSWORD" = "" ]
then
  echo '$VIRL_USER and $VIRL_PASSWORD environment variables must be defined'
  exit 1
fi

output=$(virl_std_client -u ${VIRL_USER} -p ${VIRL_PASSWORD} \
  simengine-launch -f ${VIRL_TOPOLOGY_FILE} 2>&1)
id=$(echo "${output}" | grep "Simulation ID is " | cut -f 4 -d ' ')

if [ "$id" = "" ]
then
  echo "Did not get a simulation ID. Aborting."
  echo "Output was:"
  echo "${output}"
  exit 1
fi

echo My ID is ${id}
function stop_sim {
  virl_std_client -u ${VIRL_USER} -p ${VIRL_PASSWORD} simengine-stop --session ${id}
}
trap stop_sim EXIT

ip="None"
while [ "${ip}" = "None" ] || [ "${ip}" = "" ]
do
  sleep 5
  output=$(virl_std_client -u ${VIRL_USER} -p ${VIRL_PASSWORD} simengine-interfaces --session ${id} --nodes listmaker --interfaces management 2>&1)
  ip=$(echo "${output}" | grep "u'ip-address" | cut -f 4 -d "'" | cut -f 1 -d '/')
done
echo "IP is $ip"

sleep 10

if ping -w 60 -c 2 $ip > /dev/null
then
  echo Host $ip alive
else
  echo Host $ip failed to respond to ping
  exit 1
fi

# Wait for SSH to be up
while ! nc -z $ip 22
do
  sleep 3
done

if [ ! -d ${OUTPUT_DIR} ]; then
    mkdir -p $OUTPUT_DIR
fi

###
### SSH to the VM and perform package installation. Before each step,
### dry-run and grab the URLs of the packages that would be installed.
###

function do_ssh {
  # Helper function: SSH and avoid password prompt
  sshpass -p $SSH_PASS ssh -o StrictHostKeyChecking=false -o UserKnownHostsFile=/dev/null \
    -o LogLevel=error ${SSH_USER}@${ip} "$@"
}

RPM_TEMPFILE=$(mktemp)
RPM_TEMPFILE2=$(mktemp)
RPM_URL_TEMPFILE=$(mktemp)
do_ssh yum clean all
do_ssh yum install -y @base
do_ssh yum install -y deltarpm
do_ssh yum update -y
do_ssh yum -y install epel-release
do_ssh yum update -y
do_ssh yum -y install $RPM_WANTLIST
for i in ${RPM_WANTLIST} ; do
    echo $i >> $RPM_TEMPFILE
done

###
### Install qemu ($RPM_WANTLIST_NESTED) separately from PPA in case specific versions are required.
###
for i in ${RPM_WANTLIST_NESTED};  do
    echo $i http://cbs.centos.org/kojifiles/packages/qemu-kvm-ev/2.3.0/31.el7_2.21.1/x86_64/ >> $RPM_URL_TEMPFILE
done
###
### Try 2 times for dependencies. Not in yum repo so it is not automatic"
###
for i in ${RPM_WANTLIST_NESTED};  do
    do_ssh rpm -i http://cbs.centos.org/kojifiles/packages/qemu-kvm-ev/2.3.0/31.el7_2.21.1/x86_64/$i
done
for i in ${RPM_WANTLIST_NESTED};  do
    do_ssh rpm -i http://cbs.centos.org/kojifiles/packages/qemu-kvm-ev/2.3.0/31.el7_2.21.1/x86_64/$i
done


cat $RPM_TEMPFILE | sort > $RPM_TEMPFILE2
rm -f $RPM_TEMPFILE
cat $RPM_TEMPFILE2 > $RPM_OUTPUTFILE
cat $RPM_URL_TEMPFILE >> $RPM_OUTPUTFILE
rm -f $RPM_TEMPFILE2
rm -f $RPM_URL_TEMPFILE

### Get Python data. We do this by installing as per our
### requirements.txt file while fetching a list of all
### installed modules before and after, and then comparing.

PIP_TEMPFILE_BEFORE=$(mktemp)
PIP_TEMPFILE_AFTER=$(mktemp)
do_ssh "cat - > /tmp/requirements.txt" < ${PIP_REQUIREMENTS}
do_ssh pip list | sort > $PIP_TEMPFILE_BEFORE
do_ssh pip install -r /tmp/requirements.txt
do_ssh pip list | sort > $PIP_TEMPFILE_AFTER

comm -1 -3 ${PIP_TEMPFILE_BEFORE} ${PIP_TEMPFILE_AFTER} | \
  sed -e 's/\(.*\) (\(.*\))/\1==\2/' > $PIP_OUTPUTFILE
rm -f $PIP_TEMPFILE_BEFORE
rm -f $PIP_TEMPFILE_AFTER

###
### Stop VIRL session
###
virl_std_client -u ${VIRL_USER} -p ${VIRL_PASSWORD} simengine-stop --session ${id}
trap "" EXIT
