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
        paramiko==2.9.3 \
        pycrypto==2.6.1 \
        PyYAML==5.4.1 \
        requests==2.25.1 \
        robotframework==5.0.1 \
        scapy==2.4.5 \
        scp==0.14.4 \
        ansible==5.10.0 \
        ansible-core==2.12.7 \
        dill==0.3.5.1 \
        numpy==1.22.4 \
        scipy==1.8.1 \
        boto3==1.17.78 \
        botocore==1.20.78 \
        hdrhistogram==0.6.1 \
        pandas==1.4.2 \
        plotly==4.1.1 \
        PTable==0.9.2 \
        Sphinx==3.5.4 \
        sphinx-rtd-theme==0.5.2 \
        sphinxcontrib-applehelp==1.0.2 \
        sphinxcontrib-devhelp==1.0.2 \
        sphinxcontrib-htmlhelp==2.0.0 \
        sphinxcontrib-jsmath==1.0.1 \
        sphinxcontrib-programoutput==0.17 \
        sphinxcontrib-qthelp==1.0.3 \
        sphinxcontrib-robotdoc==0.11.0 \
        sphinxcontrib-serializinghtml==1.1.5 \
        ply==3.11 \
        jsonschema==4.1.0 \
        rfc3339-validator==0.1.4 \
        rfc3987==1.3.8 \
        alabaster==0.7.12 \
        attrs==21.4.0 \
        Babel==2.10.3 \
        bcrypt==3.2.2 \
        certifi==2022.6.15 \
        cffi==1.15.1 \
        chardet==4.0.0 \
        cryptography==36.0.2 \
        docutils==0.16 \
        future==0.18.2 \
        idna==2.10 \
        imagesize==1.4.1 \
        Jinja2==3.0.3 \
        jmespath==0.10.0 \
        MarkupSafe==2.1.1 \
        packaging==21.3 \
        pbr==5.9.0 \
        pycparser==2.21 \
        Pygments==2.12.0 \
        PyNaCl==1.5.0 \
        pyparsing==3.0.9 \
        pyrsistent==0.18.1 \
        python-dateutil==2.8.2 \
        pytz==2022.1 \
        resolvelib==0.5.4 \
        retrying==1.3.3 \
        s3transfer==0.4.2 \
        six==1.16.0 \
        snowballstemmer==2.2.0 \
        urllib3==1.26.10

RUN groupadd -g 1000 testuser \
 && useradd -rm -d /home/testuser -s /bin/bash -g testuser -G sudo -u 1000 testuser \
 && echo 'testuser:Csit1234' | chpasswd

RUN echo 'root:Csit1234' | chpasswd \
 && sed -i 's/#PermitRootLogin prohibit-password/PermitRootLogin yes/' /etc/ssh/sshd_config \
 && echo "export VISIBLE=now" >> /etc/profile

RUN service ssh start