# Import necessary base images
ARG BASE_IMAGE
FROM ${BASE_IMAGE}

ARG TREX_VERSION
ARG IPERF_VERSION

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
        build-essential \
        ca-certificates \
        cmake \
        curl \
        dkms \
        ethtool \
        gcc-9 \
        g++-9 \
        libibverbs-dev \
        libnuma1 \
        libnuma-dev \
        libpcap-dev \
        net-tools \
        openssh-server \
        pciutils \
        python3-all \
        python3-apt \
        python3-dev \
        python3-pip \
        python3-setuptools \
        python3-venv \
        python3-virtualenv \
        rdma-core \
        rsyslog \
        screen \
        socat \
        software-properties-common \
        strace \
        ssh \
        sshpass \
        sudo \
        tar \
        unzip \
        wget \
        zlib1g-dev \
 && rm -rf /var/lib/apt/lists/*

# Fix permissions
RUN chown root:syslog /var/log \
 && chmod 755 /etc/default

# Create directory structure
RUN mkdir -p /var/run/sshd

# CSIT PIP pre-cache
RUN python3 -m venv venv \
    && venv/bin/pip3 install --upgrade --no-cache-dir pip \
    && venv/bin/pip3 install --upgrade setuptools \
    && venv/bin/pip3 install --upgrade wheel \
    && pip3 install \
        PyYAML==6.0.1

# Install AB
RUN apt-get -q update \
 && apt-get install -y -qq \
        apache2-utils \
 && rm -rf /var/lib/apt/lists/*

# Install T-Rex
RUN wget -c https://github.com/cisco-system-traffic-generator/trex-core/archive/v${TREX_VERSION}.tar.gz -P /opt/ \
  && cd /opt/ \
  && tar xzfv v${TREX_VERSION}.tar.gz \
  && cd /opt/trex-core-${TREX_VERSION}/linux_dpdk/ \
  && ./b configure \
  && ./b build

# Install iPerf
RUN wget -c https://downloads.es.net/pub/iperf/iperf-${IPERF_VERSION}.tar.gz -P /opt/ \
  && cd /opt/ \
  && tar xzfv iperf-${IPERF_VERSION}.tar.gz \
  && cd /opt/iperf-${IPERF_VERSION} \
  && ./configure \
  && make \
  && make install

RUN groupadd -g 1000 testuser \
 && useradd -rm -d /home/testuser -s /bin/bash -g testuser -G sudo -u 1000 testuser \
 && echo 'testuser:Csit1234' | chpasswd

RUN echo 'root:Csit1234' | chpasswd \
 && sed -i 's/#PermitRootLogin prohibit-password/PermitRootLogin yes/' /etc/ssh/sshd_config \
 && echo "export VISIBLE=now" >> /etc/profile

RUN service ssh start
