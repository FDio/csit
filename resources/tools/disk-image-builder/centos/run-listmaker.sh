#!/bin/bash

# Copyright (c) 2018 Cisco and/or its affiliates.
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

RPMS_TMP_DIR=`mktemp -d`
RPMS_WANTED_FILE=$RPMS_TMP_DIR/rpms_wanted.txt
REPO_MOD_FILE=$RPMS_TMP_DIR/Centos-Vault.repo

if [ "$1" == "centos-7.3-1611" ]
then
    OS="centos-7.3-1611"
    VIRL_TOPOLOGY_FILE="listmaker/virl-listmaker-centos-7.3-1611.yaml"
echo '
# C7.3.1611
[C7.3.1611-base]
name=CentOS-7.3.1611 - Base
baseurl=http://vault.centos.org/7.3.1611/os/$basearch/
gpgcheck=1
gpgkey=file:///etc/pki/rpm-gpg/RPM-GPG-KEY-CentOS-7
enabled=1

[C7.3.1611-updates]
name=CentOS-7.3.1611 - Updates
baseurl=http://vault.centos.org/7.3.1611/updates/$basearch/
gpgcheck=1
gpgkey=file:///etc/pki/rpm-gpg/RPM-GPG-KEY-CentOS-7
enabled=1

[C7.3.1611-extras]
name=CentOS-7.3.1611 - Extras
baseurl=http://vault.centos.org/7.3.1611/extras/$basearch/
gpgcheck=1
gpgkey=file:///etc/pki/rpm-gpg/RPM-GPG-KEY-CentOS-7
enabled=1

[C7.3.1611-centosplus]
name=CentOS-7.3.1611 - CentOSPlus
baseurl=http://vault.centos.org/7.3.1611/centosplus/$basearch/
gpgcheck=1
gpgkey=file:///etc/pki/rpm-gpg/RPM-GPG-KEY-CentOS-7
enabled=0

[C7.3.1611-fasttrack]
name=CentOS-7.3.1611 - CentOSPlus
baseurl=http://vault.centos.org/7.3.1611/fasttrack/$basearch/
gpgcheck=1
gpgkey=file:///etc/pki/rpm-gpg/RPM-GPG-KEY-CentOS-7
enabled=0

' >  $REPO_MOD_FILE
else
    if [ "$1" == "centos-7.4-1711" ]
        then
            OS="centos-7.4-1711"
            VIRL_TOPOLOGY_FILE="listmaker/virl-listmaker-centos-7.4-1711.yaml"
    elif [ "$1" == "centos-7.6-1810" ]
        then
            OS="centos-7.6-1810"
            VIRL_TOPOLOGY_FILE="listmaker/virl-listmaker-centos-7.6-1810.yaml"
    else
        echo specify argument -- probably centos-7.3-1611 , centos-7.4-1711 or centos-7.6-1810
        exit 1
    fi
fi

RELEASE="${OS}_${DATE}_${VERSION}"
OUTPUT_DIR="lists/${RELEASE}"

echo "Building release ${RELEASE}."
echo "Storing data in ${OUTPUT_DIR}/."



# RPM packages wanted

echo '
#RPM_WANTLIST_INFRA
nfs-utils
cloud-init
pkgconfig
yum-utils
#RPM_WANTLIST_CSIT
python-devel
python-virtualenv
python-setuptools
redhat-rpm-config
epel-release
python-srpm-macros
python-rpm-macros
python34
python36-ply
python36-devel
python36-pip
python2-pip-8.1.2-8.el7.noarch http://dl.fedoraproject.org/pub/epel/7/x86_64/Packages/p/
openssl-devel
git
trousers
strongswan-5.7.2-1.el7.x86_64 http://mirror.math.princeton.edu/pub/epel/7/x86_64/Packages/s/
python-cffi
#RPM_WANTLIST_TLDK
tcpdump
#RPM_WANTLIST_VPP
elfutils-libelf
elfutils-libelf-devel
kernel-debug-devel
gcc
dkms-2.6.1-1.el7.noarch https://dl.fedoraproject.org/pub/epel/7/x86_64/Packages/d/
bridge-utils
selinux-policy
selinux-policy-devel
mbedtls-2.7.10-1.el7.x86_64 https://dl.fedoraproject.org/pub/epel/7/x86_64/Packages/m/
mbedtls-devel-2.7.10-1.el7.x86_64 https://dl.fedoraproject.org/pub/epel/7/x86_64/Packages/m/
#RPM_WANTLIST_TREX
zlib-devel
unzip
#RPM_WANTLIST_MISC
socat
psmisc
gperftools
glusterfs
glusterfs-api
libiscsi
libibverbs
libpcap
libpcap-devel
pixman
libpng
pulseaudio-libs
librados2
librbd1
librdmacm
libseccomp
spice-server
spice-server-devel
libusb
usbredir
glusterfs-devel
seavgabios-bin
sgabios-bin
ipxe-roms-qemu
nss-devel
seabios-bin
libffi-devel
boost-filesystem
#RPM_WANTLIST_NESTED
trousers
libnettle
gnutls
libcacard
libcacard-tools
libcacard-devel
device-mapper-multipath-libs
libepoxy
libibumad
qemu-img-ev-2.12.0-18.el7_6.3.1.x86_64 http://mirror.centos.org/centos/7/virt/x86_64/kvm-common/
qemu-kvm-tools-ev-2.12.0-18.el7_6.3.1.x86_64 http://mirror.centos.org/centos/7/virt/x86_64/kvm-common/
qemu-kvm-common-ev-2.12.0-18.el7_6.3.1.x86_64 http://mirror.centos.org/centos/7/virt/x86_64/kvm-common/
qemu-kvm-ev-2.12.0-18.el7_6.3.1.x86_64 http://mirror.centos.org/centos/7/virt/x86_64/kvm-common/
#RPM_WANTLIST_JAVA
java-1.8.0-openjdk-headless
java-1.8.0-openjdk-devel
' > $RPMS_WANTED_FILE

RPM_OUTPUTFILE="${OUTPUT_DIR}/rpm-packages.txt"
REPO_OUTPUTFILE="${OUTPUT_DIR}/Centos-Vault.repo"

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
###
### If there is a repo file specified install it. Freeze yum to release specified above to
### avoid updating to be packages newer then the specified Centos release. Most packages are
### installed with yum from a specified Centos version. The packages with urls after them
### have specific versions and they are installed by rpm from the url.
###

tmp2=$(mktemp)
echo '#!/bin/bash' > $tmp2

if [ -e ${REPO_MOD_FILE} ] ; then
    do_ssh cp /etc/yum.repos.d/CentOS-Base.repo /etc/yum.repos.d/CentOS-Base.back
    do_ssh mv /etc/yum.repos.d/CentOS-Vault.repo /etc/yum.repos.d/CentOS-Vault.back

    do_ssh "cat - > /tmp/tmp-Vault.repo" < ${REPO_MOD_FILE}
    do_ssh cp -f /tmp/tmp-Vault.repo /etc/yum.repos.d/CentOS-Vault.repo

    echo "sed -i '/gpgcheck=1/s/.*/&\nenabled=0/' /etc/yum.repos.d/CentOS-Base.repo" >> $tmp2
    do_ssh "cat - > /tmp/chrepo.sh" < ${tmp2}
    do_ssh chmod +x /tmp/chrepo.sh
    do_ssh /tmp/chrepo.sh
fi
PKG_SCRIPT=$(mktemp)
echo \
'while IFS='' read -r line || [[ -n $line ]] ; do
    array=( $line )
    if [[ -z ${array[0]}  ]] ; then :;
    elif [[ ${array[0]:0:1} == "#" ]] ; then :;
    else
        pkg="${array[0]}"
        url="${array[1]}"
        if [[ -z $url ]] ; then
            yum install -y $pkg
            echo $pkg >> /tmp/installedpackages.txt
        else
            rpm -i --force $url$pkg.rpm
            echo "$(rpm -q $pkg) $(echo $url)"  >> /tmp/installedpackages.txt
        fi
    fi
done < /tmp/rpms-wanted.txt
' > $PKG_SCRIPT

do_ssh "cat - > /tmp/installpackages.sh" < $PKG_SCRIPT
do_ssh "cat - > /tmp/rpms-wanted.txt" < $RPMS_WANTED_FILE
do_ssh chmod +x /tmp/installpackages.sh
do_ssh /tmp/installpackages.sh

###
### Extract package list with versions and urls
###
sshpass -p "$SSH_PASS" scp -o StrictHostKeyChecking=false -o UserKnownHostsFile=/dev/null  $SSH_USER@${ip}:/tmp/installedpackages.txt $RPM_TEMPFILE

if [ -e ${REPO_MOD_FILE} ] ; then
    cp $REPO_MOD_FILE $REPO_OUTPUTFILE
fi
cat $RPM_TEMPFILE | sort > $RPM_OUTPUTFILE
rm -f $RPM_TEMPFILE

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
