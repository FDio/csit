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

FROM ubuntu:18.04
LABEL Description="CSIT vpp-device ubuntu 18.04 SUT image"
LABEL Version="master"

# Setup the environment
ENV DEBIAN_FRONTEND=noninteractive
ENV LANG='en_US.UTF-8' LANGUAGE='en_US:en' LC_ALL='en_US.UTF-8'
ENV NOTVISIBLE "in users profile"
ENV VPP_PYTHON_PREFIX=/var/cache/vpp/python

# Install packages and Docker
RUN apt-get -q update \
 && apt-get install -y -qq \
        # general tools
        apt-transport-https \
        bridge-utils \
        cloud-init \
        curl \
        gdb \
        locales \
        net-tools \
        openssh-server \
        pciutils \
        rsyslog \
        software-properties-common \
        ssh \
        sudo \
        supervisor \
        tar \
        vim \
        wget \
        # csit requirements
        cmake \
        dkms \
        gfortran \
        libblas-dev \
        libffi-dev \
        liblapack-dev \
        libpcap-dev \
        libssl-dev \
        python-all \
        python-apt \
        python-cffi \
        python-cffi-backend \
        python-dev \
        python-enum34 \
        python-pip \
        python-setuptools \
        python-virtualenv \
        python3-all \
        python3-apt \
        python3-cffi \
        python3-cffi-backend \
        python3-dev \
        python3-pip \
        python3-setuptools \
        python3-virtualenv \
        qemu-system \
        socat \
        strongswan \
        unzip \
        tcpdump \
        zlib1g-dev \
        # vpp requirements
        ca-certificates \
        libapr1 \
        libmbedcrypto1 \
        libmbedtls10 \
        libmbedx509-0 \
        libnuma1 \
        sshpass \
 && curl -L https://packagecloud.io/fdio/master/gpgkey | sudo apt-key add - \
 && curl -s https://packagecloud.io/install/repositories/fdio/master/script.deb.sh | sudo bash \
 && curl -fsSL https://get.docker.com | sh \
 && rm -rf /var/lib/apt/lists/*

# Configure locales
RUN locale-gen en_US.UTF-8 \
 && dpkg-reconfigure locales

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
        ansible==2.7.8 \
        dill==0.2.8.2 \
        numpy==1.17.3 \
        hdrhistogram==0.6.1 \
        plotly==4.1.1 \
        PTable==0.9.2 \
        Sphinx==2.2.1 \
        sphinx-rtd-theme==0.4.0 \
        sphinxcontrib-programoutput==0.15 \
        sphinxcontrib-robotdoc==0.11.0 \
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
        scipy==1.1.0

# SSH settings
RUN echo 'root:Csit1234' | chpasswd \
 && sed -i 's/#PermitRootLogin prohibit-password/PermitRootLogin yes/' /etc/ssh/sshd_config \
 && sed 's@session\s*required\s*pam_loginuid.so@session optional pam_loginuid.so@g' -i /etc/pam.d/sshd \
 && echo "export VISIBLE=now" >> /etc/profile

EXPOSE 2222

COPY supervisord.conf /etc/supervisor/supervisord.conf

CMD ["sh", "-c", "rm -f /dev/shm/db /dev/shm/global_vm /dev/shm/vpe-api; /usr/bin/supervisord -c /etc/supervisor/supervisord.conf; /usr/sbin/sshd -D -p 2222"]