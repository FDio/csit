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

FROM ubuntu:20.04
LABEL Description="CSIT vpp-device ubuntu 20.04 SUT image"
LABEL Version="master"

# Setup the environment
ENV DEBIAN_FRONTEND=noninteractive

# Configure locales
RUN apt-get update -qq \
 && apt-get install -y \
        apt-utils \
        locales \
 && sed -i 's/# \(en_US\.UTF-8 .*\)/\1/' /etc/locale.gen \
 && locale-gen en_US.UTF-8 \
 && dpkg-reconfigure --frontend=noninteractive locales \
 && update-locale LANG=en_US.UTF-8 \
 && TZ=Etc/UTC && ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone \
 && rm -r /var/lib/apt/lists/*
ENV LANG="en_US.UTF-8" LANGUAGE="en_US" LC_ALL="en_US.UTF-8"

# Install packages and Docker
RUN apt-get -q update \
 && apt-get install -y -qq \
        apt-transport-https \
        bridge-utils \
        ca-certificates \
        cloud-init \
        cmake \
        curl \
        dkms \
        gdb \
        gfortran \
        libapr1 \
        libblas-dev \
        libffi-dev \
        liblapack-dev \
        libmbedcrypto3 \
        libmbedtls12 \
        libmbedx509-0 \
        libnuma1 \
        libnuma-dev \
        libpcap-dev \
        libpixman-1-dev \
        libssl-dev \
        locales \
        net-tools \
        openssh-server \
        pciutils \
        python3-all \
        python3-apt \
        python3-cffi \
        python3-cffi-backend \
        python3-dev \
        python3-pip \
        python3-setuptools \
        python3-virtualenv \
        qemu-system \
        rsyslog \
        socat \
        software-properties-common \
        strongswan \
        ssh \
        sshpass \
        sudo \
        supervisor \
        tar \
        tcpdump \
        unzip \
        vim \
        wget \
        zlib1g-dev \
 && curl -fsSL https://get.docker.com | sh \
 && rm -rf /var/lib/apt/lists/*

# Fix permissions
RUN chown root:syslog /var/log \
 && chmod 755 /etc/default

# Create directory structure
RUN mkdir -p /tmp/dumps \
 && mkdir -p /var/cache/vpp/python \
 && mkdir -p /var/run/sshd

# CSIT PIP pre-cache
RUN pip3 install \
        ecdsa==0.13.3 \
        paramiko==2.6.0 \
        pycrypto==2.6.1 \
        pypcap==1.2.3 \
        PyYAML==5.1.1 \
        requests==2.22.0 \
        robotframework==3.1.2 \
        scapy==2.4.3 \
        scp==0.13.2 \
        ansible==2.10.7 \
        dill==0.2.8.2 \
        numpy==1.17.3 \
        hdrhistogram==0.6.1 \
        plotly==4.1.1 \
        PTable==0.9.2 \
        Sphinx==2.2.1 \
        sphinx-rtd-theme==0.4.0 \
        sphinxcontrib-programoutput==0.15 \
        sphinxcontrib-robotdoc==0.11.0 \
        ply==3.11 \
        alabaster==0.7.12 \
        Babel==2.7.0 \
        bcrypt==3.1.7 \
        certifi==2019.9.11 \
        cffi==1.13.2 \
        chardet==3.0.4 \
        cryptography==2.8 \
        docutils==0.15.2 \
        future==0.18.2 \
        idna==2.8 \
        imagesize==1.1.0 \
        Jinja2==2.10.3 \
        MarkupSafe==1.1.1 \
        packaging==19.2 \
        pbr==5.4.3 \
        pycparser==2.19 \
        Pygments==2.4.2 \
        PyNaCl==1.3.0 \
        pyparsing==2.4.4 \
        python-dateutil==2.8.1 \
        pytz==2019.3 \
        retrying==1.3.3 \
        six==1.13.0 \
        snowballstemmer==2.0.0 \
        sphinxcontrib-applehelp==1.0.1 \
        sphinxcontrib-devhelp==1.0.1 \
        sphinxcontrib-htmlhelp==1.0.2 \
        sphinxcontrib-jsmath==1.0.1 \
        sphinxcontrib-qthelp==1.0.2 \
        sphinxcontrib-serializinghtml==1.1.3 \
        urllib3==1.25.6

# ARM workaround
RUN pip3 install \
        pandas==0.25.3 \
        scipy==1.5.4

# SSH settings
RUN echo 'root:Csit1234' | chpasswd \
 && sed -i 's/#PermitRootLogin prohibit-password/PermitRootLogin yes/' /etc/ssh/sshd_config \
 && sed 's@session\s*required\s*pam_loginuid.so@session optional pam_loginuid.so@g' -i /etc/pam.d/sshd \
 && echo "export VISIBLE=now" >> /etc/profile

EXPOSE 2222

COPY supervisord.conf /etc/supervisor/supervisord.conf

CMD ["sh", "-c", "rm -f /dev/shm/db /dev/shm/global_vm /dev/shm/vpe-api; /usr/bin/supervisord -c /etc/supervisor/supervisord.conf; /usr/sbin/sshd -D -p 2222"]