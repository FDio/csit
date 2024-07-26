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
        cgroup-tools \
        cloud-init \
        cmake \
        curl \
        dkms \
        ethtool \
        gdb \
        gfortran \
        libapr1 \
        libblas-dev \
        libffi-dev \
        libibverbs-dev \
        liblapack-dev \
        libmbedcrypto7 \
        libmbedtls14 \
        libmbedx509-1 \
        libnuma1 \
        libnuma-dev \
        libpcap-dev \
        libpixman-1-dev \
        libsctp-dev \
        libssl-dev \
        net-tools \
        ninja-build \
        openssh-server \
        pciutils \
        python3-all \
        python3-apt \
        python3-cffi \
        python3-cffi-backend \
        python3-dev \
        python3-pip \
        python3-pyelftools \
        python3-setuptools \
        python3-virtualenv \
        qemu-system \
        rdma-core \
        rsyslog \
        screen \
        socat \
        software-properties-common \
        strace \
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
 && ln -s -f /usr/lib/x86_64-linux-gnu/libc.a /usr/lib/x86_64-linux-gnu/liblibc.a \
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

# CSIT PIP pre-cache
RUN pip3 install \
        ecdsa==0.18.0 \
        paramiko==3.3.1 \
        pycrypto==2.6.1 \
        python-dateutil==2.8.2 \
        PyYAML==6.0.1 \
        requests==2.31.0 \
        robotframework==6.1.1 \
        scapy==2.4.5 \
        scp==0.14.5 \
        ansible==8.2.0 \
        ansible-core==2.15.2 \
        dill==0.3.7 \
        numpy==1.25.2 \
        scipy==1.11.1 \
        ply==3.11 \
        jsonschema==4.18.4 \
        rfc3339-validator==0.1.4 \
        rfc3987==1.3.8 \
        attrs==23.1.0 \
        bcrypt==4.0.1 \
        certifi==2023.7.22 \
        cffi==1.15.1 \
        charset-normalizer==3.2.0 \
        cryptography==41.0.3 \
        idna==3.4 \
        Jinja2==3.1.2 \
        jsonschema-specifications==2023.7.1 \
        MarkupSafe==2.1.3 \
        packaging==23.1 \
        pycparser==2.21 \
        PyNaCl==1.5.0 \
        referencing==0.30.0 \
        resolvelib==1.0.1 \
        rpds-py==0.9.2 \
        six==1.16.0 \
        urllib3==2.0.4 \
        meson==0.64.1

RUN groupadd -g 1000 testuser \
 && useradd -rm -d /home/testuser -s /bin/bash -g testuser -G sudo -u 1000 testuser \
 && echo 'testuser:Csit1234' | chpasswd

RUN echo 'root:Csit1234' | chpasswd \
 && sed -i 's/#PermitRootLogin prohibit-password/PermitRootLogin yes/' /etc/ssh/sshd_config \
 && echo "export VISIBLE=now" >> /etc/profile

RUN service ssh start
