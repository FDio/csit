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
# that the user would obtain if they did an "apt-get update", "apt-get upgrade" today.
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

if [ "$1" = "ubuntu-14.04.4" ]
then
    OS="ubuntu-14.04.4"
    VIRL_TOPOLOGY_FILE="listmaker/virl-listmaker-ubuntu-14.04.4.yaml"
elif [ "$1" = "ubuntu-16.04.1" ]
then
    OS="ubuntu-16.04.1"
    VIRL_TOPOLOGY_FILE="listmaker/virl-listmaker-ubuntu-16.04.1.yaml"
else
    echo "Please provide OS as parameter:"
    echo "Options: ${0} [ubuntu-14.04.4|ubuntu-16.04.1]"
    exit 1
fi

RELEASE="${OS}_${DATE}_${VERSION}"
OUTPUT_DIR="lists/${RELEASE}"

echo "Building release ${RELEASE}."
echo "Storing data in ${OUTPUT_DIR}/."


# APT packages wanted

APT_WANTLIST_INFRA="nfs-common cloud-init"
APT_WANTLIST_CSIT="python-dev python-pip python-virtualenv git strongswan socat"
APT_WANTLIST_TLDK="libpcap0.8-dev libpcap-dev cmake tcpdump"
APT_WANTLIST_VPP="dkms bridge-utils libmbedcrypto0 libmbedtls10 libmbedx509-0"
APT_WANTLIST_TREX="zlib1g-dev unzip"
APT_WANTLIST_NESTED="qemu-system-x86"
APT_WANTLIST_JAVA="openjdk-8-jdk-headless"
APT_WANTLIST_DMM="git cmake gcc g++ automake libtool wget lsof lshw pciutils net-tools tcpdump libpcre3 libpcre3-dev zlibc zlib1g zlib1g-dev psmisc autoconf"
#Docker is currently disabled due to issues with apt repositories retrieval
#APT_WANTLIST_DOCKER="docker-engine"

# For now, let us NOT incude WANTLIST_NESTED in the below. We're installing qemu
# separately from a separate source.
APT_WANTLIST="$APT_WANTLIST_INFRA $APT_WANTLIST_CSIT $APT_WANTLIST_VPP $APT_WANTLIST_TREX $APT_WANTLIST_TLDK $APT_WANTLIST_DMM"

APT_OUTPUTFILE="${OUTPUT_DIR}/apt-packages.txt"

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

mkdir -p $OUTPUT_DIR

###
### SSH to the VM and perform package installation. Before each step,
### dry-run and grab the URLs of the packages that would be installed.
###

function do_ssh {
  # Helper function: SSH and avoid password prompt
  sshpass -p $SSH_PASS ssh -o StrictHostKeyChecking=false -o UserKnownHostsFile=/dev/null \
    -o LogLevel=error ${SSH_USER}@${ip} "$@"
}

if [ "$OS" = "ubuntu-14.04.4" ]
then
do_ssh "cat - > /etc/apt/sources.list" <<_EOF
deb http://us.archive.ubuntu.com/ubuntu/ trusty main restricted
deb-src http://us.archive.ubuntu.com/ubuntu/ trusty main restricted
deb http://us.archive.ubuntu.com/ubuntu/ trusty-updates main restricted
deb-src http://us.archive.ubuntu.com/ubuntu/ trusty-updates main restricted
deb http://us.archive.ubuntu.com/ubuntu/ trusty universe
deb-src http://us.archive.ubuntu.com/ubuntu/ trusty universe
deb http://us.archive.ubuntu.com/ubuntu/ trusty-updates universe
deb-src http://us.archive.ubuntu.com/ubuntu/ trusty-updates universe
deb http://us.archive.ubuntu.com/ubuntu/ trusty multiverse
deb-src http://us.archive.ubuntu.com/ubuntu/ trusty multiverse
deb http://us.archive.ubuntu.com/ubuntu/ trusty-updates multiverse
deb-src http://us.archive.ubuntu.com/ubuntu/ trusty-updates multiverse
deb http://us.archive.ubuntu.com/ubuntu/ trusty-backports main restricted universe multiverse
deb-src http://us.archive.ubuntu.com/ubuntu/ trusty-backports main restricted universe multiverse
deb http://security.ubuntu.com/ubuntu trusty-security main restricted
deb-src http://security.ubuntu.com/ubuntu trusty-security main restricted
deb http://security.ubuntu.com/ubuntu trusty-security universe
deb-src http://security.ubuntu.com/ubuntu trusty-security universe
deb http://security.ubuntu.com/ubuntu trusty-security multiverse
deb-src http://security.ubuntu.com/ubuntu trusty-security multiverse
_EOF
elif [ "$OS" = "ubuntu-16.04.1" ]
then
do_ssh "cat - > /etc/apt/sources.list" <<_EOF
deb http://us.archive.ubuntu.com/ubuntu/ xenial main restricted
deb-src http://us.archive.ubuntu.com/ubuntu/ xenial main restricted
deb http://us.archive.ubuntu.com/ubuntu/ xenial-updates main restricted
deb-src http://us.archive.ubuntu.com/ubuntu/ xenial-updates main restricted
deb http://us.archive.ubuntu.com/ubuntu/ xenial universe
deb-src http://us.archive.ubuntu.com/ubuntu/ xenial universe
deb http://us.archive.ubuntu.com/ubuntu/ xenial-updates universe
deb-src http://us.archive.ubuntu.com/ubuntu/ xenial-updates universe
deb http://us.archive.ubuntu.com/ubuntu/ xenial multiverse
deb-src http://us.archive.ubuntu.com/ubuntu/ xenial multiverse
deb http://us.archive.ubuntu.com/ubuntu/ xenial-updates multiverse
deb-src http://us.archive.ubuntu.com/ubuntu/ xenial-updates multiverse
deb http://us.archive.ubuntu.com/ubuntu/ xenial-backports main restricted universe multiverse
deb-src http://us.archive.ubuntu.com/ubuntu/ xenial-backports main restricted universe multiverse
deb http://security.ubuntu.com/ubuntu xenial-security main restricted
deb-src http://security.ubuntu.com/ubuntu xenial-security main restricted
deb http://security.ubuntu.com/ubuntu xenial-security universe
deb-src http://security.ubuntu.com/ubuntu xenial-security universe
deb http://security.ubuntu.com/ubuntu xenial-security multiverse
deb-src http://security.ubuntu.com/ubuntu xenial-security multiverse
_EOF
fi

### FIXME: Need error handling around all this
do_ssh apt-get update

APT_TEMPFILE=$(mktemp)
do_ssh apt-get --print-uris -y dist-upgrade >> $APT_TEMPFILE
do_ssh DEBIAN_FRONTEND=noninteractive apt-get -y dist-upgrade
do_ssh apt-get --print-uris -y install $APT_WANTLIST >> $APT_TEMPFILE
do_ssh DEBIAN_FRONTEND=noninteractive apt-get -y install $APT_WANTLIST

### Install qemu ($APT_WANTLIST_NESTED) separately from PPA
if [ "$OS" = "ubuntu-14.04.4" ]
then
do_ssh "cat - >> /etc/apt/sources.list" <<_EOF
# For a custom qemu build
deb http://ppa.launchpad.net/syseleven-platform/virtualization/ubuntu trusty main
deb-src http://ppa.launchpad.net/syseleven-platform/virtualization/ubuntu trusty main
_EOF
fi
do_ssh apt-get --allow-unauthenticated update
do_ssh apt-get --print-uris --allow-unauthenticated -y install $APT_WANTLIST_NESTED >> $APT_TEMPFILE
do_ssh DEBIAN_FRONTEND=noninteractive apt-get --allow-unauthenticated -y install $APT_WANTLIST_NESTED

### Install Java ($APT_WANTLIST_JAVA) separately from PPA
if [ "$OS" = "ubuntu-14.04.4" ]
then
do_ssh "cat - >> /etc/apt/sources.list" <<_EOF
# For java
deb http://ppa.launchpad.net/openjdk-r/ppa/ubuntu trusty main
_EOF
fi
do_ssh apt-get --allow-unauthenticated update
do_ssh apt-get --print-uris --allow-unauthenticated -y install $APT_WANTLIST_JAVA >> $APT_TEMPFILE
do_ssh DEBIAN_FRONTEND=noninteractive apt-get --allow-unauthenticated -y install $APT_WANTLIST_JAVA

### Install Docker ($APT_WANTLIST_DOCKER) separately from PPA
#if [ "$OS" = "ubuntu-14.04.4" ]
#then
#do_ssh "cat - >> /etc/apt/sources.list" <<_EOF
## For Docker
#deb https://apt.dockerproject.org/repo ubuntu-trusty main
#_EOF
#elif [ "$OS" = "ubuntu-16.04.1" ]
#then
#do_ssh "cat - >> /etc/apt/sources.list" <<_EOF
## For Docker
#deb https://apt.dockerproject.org/repo ubuntu-xenial main
#_EOF
#fi
#do_ssh apt-get --allow-unauthenticated update
#do_ssh apt-get --print-uris --allow-unauthenticated -y install $APT_WANTLIST_DOCKER >> $APT_TEMPFILE
#do_ssh DEBIAN_FRONTEND=noninteractive apt-get --allow-unauthenticated -y install $APT_WANTLIST_DOCKER

cat $APT_TEMPFILE | grep MD5Sum | sort > $APT_OUTPUTFILE
rm -f $APT_TEMPFILE

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
