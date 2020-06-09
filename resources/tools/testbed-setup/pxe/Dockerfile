# Copyright (c) 2020 Cisco and/or its affiliates.
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

FROM alpine

MAINTAINER csit-dev <csit-dev@lists.fd.io>
LABEL Description="PXE service image."
LABEL Version="1.0"

RUN apk add --update-cache dnsmasq wget \
 && rm -rf /var/cache/apk/* \
 && mkdir -p /var/lib/tftpboot

# Add Ubuntu netboot image.
RUN wget http://ports.ubuntu.com/ubuntu-ports/dists/bionic-updates/main/installer-arm64/current/images/netboot/netboot.tar.gz -P / \
 && mkdir -p /var/lib/tftpboot/ubuntu-installer/ \
 && tar -zxvf /netboot.tar.gz --strip-components=2 -C /var/lib/tftpboot/ubuntu-installer/ \
 && rm -rf /netboot.tar.gz \
 && wget http://archive.ubuntu.com/ubuntu/dists/bionic-updates/main/installer-amd64/current/images/netboot/netboot.tar.gz -P / \
 && mkdir -p /var/lib/tftpboot/ubuntu-installer/ \
 && tar -zxvf /netboot.tar.gz --strip-components=2 -C /var/lib/tftpboot/ubuntu-installer/ \
 && cp /var/lib/tftpboot/ubuntu-installer/amd64/boot-screens/l* /var/lib/tftpboot/ubuntu-installer/amd64/ \
 && rm -rf /netboot.tar.gz \
 && wget http://archive.ubuntu.com/ubuntu/dists/bionic/main/uefi/grub2-amd64/current/grubnetx64.efi.signed \
 && mv grubnetx64.efi.signed /var/lib/tftpboot/ubuntu-installer/amd64/grubnetx64.efi

# Configure PXE.
COPY tftpboot/ /var/lib/tftpboot/

# Configure DNSMASQ.
COPY etc/ /etc

# Start dnsmasq. It picks up default configuration from /etc/dnsmasq.conf and
# /etc/default/dnsmasq plus any command line switch
ENTRYPOINT ["sh","-c","dnsmasq","--interface=$E_INT","--listen-address=$E_ADD"]
