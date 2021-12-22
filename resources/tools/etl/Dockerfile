ARG CENTOS_VERSION=8
FROM centos:${CENTOS_VERSION}

ENV MAVEN=https://aws-glue-etl-artifacts.s3.amazonaws.com/glue-common/apache-maven-3.6.0-bin.tar.gz
ENV SPARK=https://aws-glue-etl-artifacts.s3.amazonaws.com/glue-3.0/spark-3.1.1-amzn-0-bin-3.2.1-amzn-3.tgz
ENV GLUE=https://github.com/awslabs/aws-glue-libs.git
ENV GLUE_COMMIT=effa3f26f69c1f7309695552777410d634e83831

RUN mkdir glue

# get prerequisities
RUN yum install -y \
    krb5-devel \
    python38 \
    python38-pip \
    python38-devel \
    java-1.8.0-openjdk \
    java-1.8.0-openjdk-devel \
    git \
    tar \
    wget \
    zip \
 && yum groupinstall -y 'Development Tools' \
 && yum clean all \
 && rm -rf /var/cache/yum \
 && mv $(rpm -q -l java-1.8.0-openjdk-devel | grep "/bin$" | rev | cut -d"/" -f2- |rev) /usr/lib/jvm/jdk

# do python prerequisities
RUN ln -sfn /usr/bin/python3.8 /usr/bin/python3 & \
    ln -sfn /usr/bin/python3 /usr/bin/python & \
    ln -sfn /usr/bin/pip3.8 /usr/bin/pip3 & \
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
ENV JAVA_HOME /usr/lib/jvm/jdk
ENV GLUE_HOME /glue/aws-glue-libs
ENV LOCAL_HOME /root/.local/
ENV PATH $PATH:$MAVEN_HOME/bin:$SPARK_HOME/bin:$JAVA_HOME/bin:$GLUE_HOME/bin:$LOCAL_HOME/bin

RUN sh /glue/aws-glue-libs/bin/glue-setup.sh \
 && sed -i '/mvn -f/a rm /glue/aws-glue-libs/jarsv1/netty-*' /glue/aws-glue-libs/bin/glue-setup.sh \
 && sed -i '/mvn -f/a rm /glue/aws-glue-libs/jarsv1/javax.servlet-3.*' /glue/aws-glue-libs/bin/glue-setup.sh

RUN mkdir /app
WORKDIR /app

CMD ["bash"]