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
ARG COBBLER_PASS
ARG COBBLER_WEB_PASS
ARG COBBLER_IP_ADDR
ARG COBBLER_HTTP_PORT

# Map volumes
VOLUME [ "/var/www/cobbler", \
         "/var/lib/tftp", \
         "/var/lib/cobbler/config", \
         "/var/lib/cobbler/backup", \
         "/var/run/supervisor", \
         "/mnt" ]

# Install dependencies
RUN yum -y install epel-release \
    && yum -y install \
        cobbler \
        cobbler-web \
        python-pip \
        curl \
        dhcp \
        bind \
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

# Copy CSIT dhcp template
COPY etc/cobbler/dhcp.template /etc/cobbler/dhcp.template

# Copy CSIT kickstart
COPY var/lib/cobbler/kickstarts/*.ks /var/lib/cobbler/kickstarts/

# Expose TFTP WWW COBBLER
EXPOSE 69
EXPOSE 80
EXPOSE 443
EXPOSE 25151

# Change cobbler WEB password
RUN printf "%s:%s:%s\n" cobbler Cobbler "$( printf "%s:%s:%s" cobbler Cobbler $COBBLER_WEB_PASS | md5sum | awk '{print $1}' )" > "/etc/cobbler/users.digest"

RUN (for dir in distros.d files.d images.d mgmtclasses.d packages.d profiles.d \
     repos.d systems.d; \
     do \
       mkdir -p /var/lib/cobbler/config/$dir; \
     done)
RUN touch /usr/share/cobbler/web/cobbler.wsgi

RUN sed -i \
    -e "/^default_password_crypted/ s|:.*$|: \"$COBBLER_PASS\"|" \
    -e "/^next_server:/ s/:.*$/: $COBBLER_IP_ADDR/" \
    -e "/^server/ s/:.*$/: $COBBLER_IP_ADDR/" \
    -e "/^http_port:/ s/:.*$/: $COBBLER_HTTP_PORT/" \
    /etc/cobbler/settings

ENTRYPOINT /usr/bin/supervisord -c /etc/supervisord.conf
