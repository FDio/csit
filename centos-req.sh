#!/bin/bash
# Copyright (c) 2017 Red Hat Incorporated
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

set -x

BASEDIR=`dirname $0`

sudo yum install -y deltarpm
sudo yum update -y
sudo yum -y install epel-release
sudo yum install -y bridge-utils cloud-init dkms git glusterfs glusterfs-api glusterfs-devel gperftools ipxe-roms-qemu \
java-1.8.0-openjdk-devel java-1.8.0-openjdk-headless libibverbs libiscsi libpcap libpcap-devel libpng librados2 librbd1 \
librdmacm libseccomp libusb nfs-utils nss-devel openssl-devel pixman pkgconfig psmisc pulseaudio-libs python-devel python-pip \
python-setuptools python-virtualenv seabios-bin seavgabios-bin sgabios-bin socat spice-server strongswan unzip usbredir yum-utils zlib-devel

#sudo yum install -y qemu-system-x86-2.0.0-1.el7.6.x86_64
sudo yum groupinstall -y 'Development Tools'
sudo yum install -y redhat-lsb glibc-static java-1.8.0-openjdk-devel yum-utils
sudo yum install -y openssl-devel https://dl.fedoraproject.org/pub/epel/epel-release-latest-7.noarch.rpm apr-devel

sudo yum install -y chrpath libffi-devel rpm-build
sudo yum install -y https://kojipkgs.fedoraproject.org//packages/nasm/2.12.02/2.fc26/x86_64/nasm-2.12.02-2.fc26.x86_64.rpm
sudo yum install -y --enablerepo=epel libconfuse-devel ganglia-devel epel-rpm-macros

sudo yum install -y libcacard libcacard-devel libcacard-tools
sudo yum install -y centos-release-qemu-ev
sudo yum install -y qemu-img-ev qemu-kvm-tools-ev qemu-kvm-common-ev qemu-kvm-ev
sudo yum install -y qemu-system-x86
#sudo rpm -i http://cbs.centos.org/kojifiles/packages/qemu-kvm-ev/2.3.0/31.el7_2.21.1/x86_64/qemu-img-ev-2.3.0-31.el7_2.21.1.x86_64.rpm
#sudo rpm -i http://cbs.centos.org/kojifiles/packages/qemu-kvm-ev/2.3.0/31.el7_2.21.1/x86_64/libcacard-ev-2.3.0-31.el7_2.21.1.x86_64.rpm
#sudo rpm -i http://cbs.centos.org/kojifiles/packages/qemu-kvm-ev/2.3.0/31.el7_2.21.1/x86_64/libcacard-devel-ev-2.3.0-31.el7_2.21.1.x86_64.rpm
#sudo rpm -i http://cbs.centos.org/kojifiles/packages/qemu-kvm-ev/2.3.0/31.el7_2.21.1/x86_64/qemu-kvm-ev-debuginfo-2.3.0-31.el7_2.21.1.x86_64.rpm
#sudo rpm -i http://cbs.centos.org/kojifiles/packages/qemu-kvm-ev/2.3.0/31.el7_2.21.1/x86_64/qemu-kvm-tools-ev-2.3.0-31.el7_2.21.1.x86_64.rpm
#sudo rpm -i http://cbs.centos.org/kojifiles/packages/qemu-kvm-ev/2.3.0/31.el7_2.21.1/x86_64/qemu-kvm-common-ev-2.3.0-31.el7_2.21.1.x86_64.rpm
#sudo rpm -i http://cbs.centos.org/kojifiles/packages/qemu-kvm-ev/2.3.0/31.el7_2.21.1/x86_64/qemu-kvm-ev-2.3.0-31.el7_2.21.1.x86_64.rpm
#sudo rpm -i http://cbs.centos.org/kojifiles/packages/qemu-kvm-ev/2.3.0/31.el7_2.21.1/x86_64/libcacard-tools-ev-2.3.0-31.el7_2.21.1.x86_64.rpm
