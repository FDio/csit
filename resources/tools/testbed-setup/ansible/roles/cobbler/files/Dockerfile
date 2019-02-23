# Copyright (c) 2019 Cisco and/or its affiliates.
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

FROM centos:7

MAINTAINER csit-dev <csit-dev@lists.fd.io>
LABEL Description="CSIT cobbler service image."
LABEL Version="0.1"

# Build arguments
ARG cobbler_pass
ARG cobbler_web_pass
ARG cobbler_ip_addr
ARG cobbler_http_port

# Install dependencies
RUN yum -y install epel-release \
    && yum -y install \
        cobbler \
        cobbler-web \
        python-pip \
        curl \
        dhcp \
        bind \
        file \
        debmirror \
        net-tools \
        rsync \
        pykickstart \
        supervisor \
        wget \
        which \
    && yum clean all \
    &&  rm -rf /var/cache/yum

# Workaround for Cobbler 2.8.4 bug
RUN pip2.7 install -U django==1.9.13

# Copy CSIT configration
COPY supervisord/supervisord.conf /etc/supervisord.conf
COPY etc/cobbler/dhcp.template /etc/cobbler/dhcp.template
COPY var/lib/cobbler/kickstarts/*.ks /var/lib/cobbler/kickstarts/
COPY etc/httpd/conf.d/cobbler_web.conf /etc/httpd/conf.d/cobbler_web.conf

# Change Cobbler WEB password
RUN printf "%s:%s:%s\n" cobbler Cobbler "$( printf "%s:%s:%s" cobbler Cobbler $cobbler_web_pass | md5sum | awk '{print $1}' )" > "/etc/cobbler/users.digest"

# Create Cobbler directories
RUN mkdir -p /var/lib/cobbler/config/distros.d \
    && mkdir -p /var/lib/cobbler/config/files.d \
    && mkdir -p /var/lib/cobbler/config/images.d \
    && mkdir -p /var/lib/cobbler/config/mgmtclasses.d \
    && mkdir -p /var/lib/cobbler/config/packages.d \
    && mkdir -p /var/lib/cobbler/config/profiles.d \
    && mkdir -p /var/lib/cobbler/config/repos.d \
    && mkdir -p /var/lib/cobbler/config/systems.d \
    && mkdir -p /var/www/cobbler/links/ \
    && touch /usr/share/cobbler/web/cobbler.wsgi

RUN sed -i \
    -e "/^default_password_crypted/ s|:.*$|: \"$cobbler_pass\"|" \
    -e "/^next_server:/ s/:.*$/: $cobbler_ip_addr/" \
    -e "/^server/ s/:.*$/: $cobbler_ip_addr/" \
    -e "/^http_port:/ s/:.*$/: $cobbler_http_port/" \
    /etc/cobbler/settings

# Expose TFTP WWW COBBLER
EXPOSE 69
EXPOSE 80
EXPOSE 443
EXPOSE 25151

ENTRYPOINT /usr/bin/supervisord -c /etc/supervisord.conf
