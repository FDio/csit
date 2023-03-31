FROM ubuntu:22.04

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
        libmbedcrypto7 \
        libmbedtls14 \
        libmbedx509-1 \
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
 && mkdir -p /var/run/sshd \
 && mkdir -p /var/log/vpp

RUN useradd -rm -d /home/testuser -s /bin/bash -g root -G sudo -u 1000 testuser \
 && echo 'testuser:Csit1234' | chpasswd

RUN service ssh start