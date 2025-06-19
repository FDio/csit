# Import necessary base images
ARG BASE_IMAGE
<<<<<<< HEAD   (cbccec job-spec: Remove xl710 NIC from 3n-alt)
FROM ${BASE_IMAGE}
=======
FROM ${BASE_IMAGE:-ubuntu} AS dpdk_stage

ARG DPDK_VERSION

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

RUN apt-get -q update \
 && apt-get install -y -qq \
      build-essential \
      ca-certificates \
      libnuma-dev \
      python3-all \
      python3-apt \
      python3-dev \
      python3-pip \
      python3-pyelftools \
      python3-setuptools \
      python3-venv \
      python3-virtualenv \
      wget \
      xz-utils \
 && wget --quiet http://fast.dpdk.org/rel/dpdk-$DPDK_VERSION.tar.xz \
 && mkdir --parents /dpdk \
 && tar --extract --file=dpdk-$DPDK_VERSION.tar.xz --directory=/dpdk --strip-components 1

# CSIT PIP pre-cache
RUN python3 -m venv venv \
 && venv/bin/pip3 install --upgrade --no-cache-dir pip \
 && venv/bin/pip3 install --upgrade setuptools \
 && venv/bin/pip3 install --upgrade wheel \
 && venv/bin/pip3 install \
      meson==0.64.1 \
      ninja

ENV PATH="$PATH:/venv/bin"

# Install DPDK
RUN cd /dpdk \
 && meson setup -Dexamples=l3fwd -Dc_args=-DRTE_LIBRTE_I40E_16BYTE_RX_DESC=y -Dplatform=generic build \
 && ninja -C build

FROM ${BASE_IMAGE:-ubuntu} AS csit_prod
>>>>>>> CHANGE (18879f fix(infra): Altra)

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
        libpcre2-dev \
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
        python3-venv \
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
        wget \
        zlib1g-dev \
 #&& ln -s -f /usr/lib/x86_64-linux-gnu/libc.a /usr/lib/x86_64-linux-gnu/liblibc.a \
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
RUN python3 -m venv venv \
    && venv/bin/pip3 install --upgrade --no-cache-dir pip \
    && venv/bin/pip3 install --upgrade setuptools \
    && venv/bin/pip3 install --upgrade wheel \
    && venv/bin/pip3 install \
        ecdsa==0.19.0 \
        paramiko==3.4.1 \
        pycryptodome==3.20.0 \
        python-dateutil==2.9.0 \
        PyYAML==6.0.1 \
        requests==2.32.2 \
        robotframework==7.0.1 \
        scapy==2.4.5 \
        scp==0.15.0 \
        ansible==10.2.0 \
        ansible-core==2.17.2 \
        dill==0.3.8 \
        numpy==2.0.1 \
        scipy==1.14.0 \
        ply==3.11 \
        jsonschema==4.23.0 \
        rfc3339-validator==0.1.4 \
        rfc3987==1.3.8 \
        pylint==3.2.6 \
        astroid==3.2.4 \
        attrs==24.2.0 \
        bcrypt==4.2.0 \
        certifi==2024.7.4 \
        cffi==1.17.0 \
        charset-normalizer==3.3.2 \
        cryptography==43.0.0 \
        idna==3.7 \
        isort==5.13.2 \
        Jinja2==3.1.4 \
        jsonschema-specifications==2023.12.1 \
        MarkupSafe==2.1.5 \
        mccabe==0.7.0 \
        packaging==24.1 \
        platformdirs==4.2.2 \
        ply==3.11 \
        pycparser==2.22 \
        PyNaCl==1.5.0 \
        referencing==0.35.1 \
        resolvelib==1.0.1 \
        rpds-py==0.20.0 \
        six==1.16.0 \
        tomli==2.0.1 \
        tomlkit==0.13.0 \
        typing_extensions==4.12.2 \
        urllib3==2.2.2\
        meson==0.64.1

RUN useradd -rm -d /home/testuser -s /bin/bash -g 1000 -G sudo testuser \
 && echo 'testuser:Csit1234' | chpasswd

RUN echo 'root:Csit1234' | chpasswd \
 && sed -i 's/#PermitRootLogin prohibit-password/PermitRootLogin yes/' /etc/ssh/sshd_config \
 && echo "export VISIBLE=now" >> /etc/profile

RUN service ssh start
