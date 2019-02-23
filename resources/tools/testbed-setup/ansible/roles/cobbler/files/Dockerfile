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
ARG cobbler_sys_pass
ARG cobbler_web_pass
ARG cobbler_ip_addr
ARG cobbler_http_port=60080
ARG cobbler_https_port=60443

# Install dependencies
RUN yum -y install epel-release \
    && yum -y install \
        cobbler \
        cobbler-web \
        fence-agents \
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
    && rm -rf /var/cache/yum

# Workaround for Cobbler 2.8.4 bug
RUN pip2.7 install -U django==1.9.13

# Copy CSIT configration
COPY supervisord/supervisord.conf /etc/supervisord.conf
COPY etc/cobbler/dhcp.template /etc/cobbler/dhcp.template
COPY var/lib/cobbler/kickstarts/*.ks /var/lib/cobbler/kickstarts/
COPY etc/httpd/conf.d/cobbler_web.conf /etc/httpd/conf.d/cobbler_web.conf

RUN sed -i \
    -e "/^default_password_crypted/ s|:.*$|: \"${cobbler_sys_pass}\"|" \
    -e "/^next_server:/ s/:.*$/: ${cobbler_ip_addr}/" \
    -e "/^server/ s/:.*$/: ${cobbler_ip_addr}/" \
    -e "/^http_port:/ s/:.*$/: ${cobbler_http_port}/" \
    -e "/^pxe_just_once:/ s/:.*$/: 1/" \
    -e "/^manage_dhcp:/ s/:.*$/: 1/" \
    /etc/cobbler/settings \
    && sed -i "s/service %s restart/supervisorctl restart %s/g" \
    /usr/lib/python2.7/site-packages/cobbler/modules/sync_post_restart_services.py \
    && sed -i "s/Listen 80/Listen ${cobbler_http_port}/g" \
    /etc/httpd/conf/httpd.conf \
    && sed -i "s/Listen 443 https/Listen ${cobbler_https_port} https/g" \
    /etc/httpd/conf.d/ssl.conf

# Change Cobbler WEB password
RUN echo -n "cobbler:Cobbler:${cobbler_web_pass}" \
    | md5sum \
    | cut -d' ' -f1 \
    | xargs printf "%s:%s:%s\n" cobbler Cobbler  > "/etc/cobbler/users.digest"

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

# Expose TFTP WWW COBBLER
EXPOSE 69
EXPOSE $cobbler_http_port
EXPOSE $cobbler_https_port
EXPOSE 25151

ENTRYPOINT /usr/bin/supervisord -c /etc/supervisord.conf
