ARG UBUNTU_VERSION=20.04
FROM ubuntu:${UBUNTU_VERSION}

ENV MAVEN=https://aws-glue-etl-artifacts.s3.amazonaws.com/glue-common/apache-maven-3.6.0-bin.tar.gz
ENV SPARK=https://aws-glue-etl-artifacts.s3.amazonaws.com/glue-3.0/spark-3.1.1-amzn-0-bin-3.2.1-amzn-3.tgz
ENV GLUE=https://github.com/awslabs/aws-glue-libs.git
ENV GLUE_COMMIT=effa3f26f69c1f7309695552777410d634e83831

RUN mkdir glue

# get prerequisities
RUN apt-get update -qq \
 && apt-get install -y \
    apt-utils \
    locales \
 && sed -i 's/# \(en_US\.UTF-8 .*\)/\1/' /etc/locale.gen \
 && locale-gen en_US.UTF-8 \
 && dpkg-reconfigure --frontend=noninteractive locales \
 && update-locale LANG=en_US.UTF-8 \
 && TZ=Etc/UTC \
 && ln -snf /usr/share/zoneinfo/$TZ /etc/localtime \
 && echo $TZ > /etc/timezone \
 && rm -r /var/lib/apt/lists/*
ENV LANG="en_US.UTF-8" LANGUAGE="en_US" LC_ALL="en_US.UTF-8"

RUN apt-get update -qq \
 && apt-get install -y \
    python3 \
    python3-dev \
    python3-pip \
    procps \
    git \
    openjdk-8-jdk \
    tar \
    wget \
    zip \
 && ln -sfn /usr/bin/python3 /usr/bin/python \
 && ln -sfn /usr/bin/pip3 /usr/bin/pip \
 && rm -rf /var/lib/apt/lists/*

# do python prerequisities
RUN ln -sfn /usr/bin/python3 /usr/bin/python & \
    ln -sfn /usr/bin/pip3 /usr/bin/pip \
 && python3 -m pip install --user --upgrade pip \
 && python3 -m pip install --user awswrangler cython pynt

# prepare glue
WORKDIR ./glue
RUN git clone -b master $GLUE \
 && cd aws-glue-libs \
 && git checkout $GLUE_COMMIT \
 && cd ..

RUN wget $SPARK \
 && tar xfv spark-3.1.1-amzn-0-bin-3.2.1-amzn-3.tgz \
 && rm spark-3.1.1-amzn-0-bin-3.2.1-amzn-3.tgz

RUN wget $MAVEN \
 && tar zxfv apache-maven-3.6.0-bin.tar.gz \
 && rm apache-maven-3.6.0-bin.tar.gz

ENV SPARK_HOME /glue/spark-3.1.1-amzn-0-bin-3.2.1-amzn-3
ENV MAVEN_HOME /glue/apache-maven-3.6.0
ENV JAVA_HOME /usr/lib/jvm/java-8-openjdk-amd64
ENV GLUE_HOME /glue/aws-glue-libs
ENV LOCAL_HOME /root/.local/
ENV PATH $PATH:$MAVEN_HOME/bin:$SPARK_HOME/bin:$JAVA_HOME/bin:$GLUE_HOME/bin:$LOCAL_HOME/bin

RUN sh /glue/aws-glue-libs/bin/glue-setup.sh \
 && sed -i '/mvn -f/a rm /glue/aws-glue-libs/jarsv1/netty-*' /glue/aws-glue-libs/bin/glue-setup.sh \
 && sed -i '/mvn -f/a rm /glue/aws-glue-libs/jarsv1/javax.servlet-3.*' /glue/aws-glue-libs/bin/glue-setup.sh

RUN mkdir /app
WORKDIR /app

CMD ["bash"]