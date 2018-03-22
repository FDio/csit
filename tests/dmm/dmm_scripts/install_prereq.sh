#!/bin/bash

export DEBIAN_FRONTEND=noninteractive

echo " deb http://in.archive.ubuntu.com/ubuntu/ trusty main restricted" | sudo tee -a /etc/apt/sources.list
echo " deb-src http://in.archive.ubuntu.com/ubuntu/ trusty main restricted" | sudo tee -a /etc/apt/sources.list
echo " deb http://in.archive.ubuntu.com/ubuntu/ trusty-updates main restricted" | sudo tee -a /etc/apt/sources.list
echo " deb-src http://in.archive.ubuntu.com/ubuntu/ trusty-updates main restricted" | sudo tee -a /etc/apt/sources.list
echo " deb http://in.archive.ubuntu.com/ubuntu/ trusty universe" | sudo tee -a /etc/apt/sources.list
echo " deb-src http://in.archive.ubuntu.com/ubuntu/ trusty universe" | sudo tee -a /etc/apt/sources.list
echo " deb http://in.archive.ubuntu.com/ubuntu/ trusty-updates universe" | sudo tee -a /etc/apt/sources.list
echo " deb-src http://in.archive.ubuntu.com/ubuntu/ trusty-updates universe" | sudo tee -a /etc/apt/sources.list
echo " deb http://in.archive.ubuntu.com/ubuntu/ trusty multiverse" | sudo tee -a /etc/apt/sources.list
echo " deb-src http://in.archive.ubuntu.com/ubuntu/ trusty multiverse" | sudo tee -a /etc/apt/sources.list
echo " deb http://in.archive.ubuntu.com/ubuntu/ trusty-updates multiverse" | sudo tee -a /etc/apt/sources.list
echo " deb-src http://in.archive.ubuntu.com/ubuntu/ trusty-updates multiverse" | sudo tee -a /etc/apt/sources.list
echo " deb http://in.archive.ubuntu.com/ubuntu/ trusty-backports main restricted universe multiverse" | sudo tee -a /etc/apt/sources.list
echo " deb-src http://in.archive.ubuntu.com/ubuntu/ trusty-backports main restricted universe multiverse" | sudo tee -a /etc/apt/sources.list
echo " deb http://security.ubuntu.com/ubuntu trusty-security main restricted" | sudo tee -a /etc/apt/sources.list
echo " deb-src http://security.ubuntu.com/ubuntu trusty-security main restricted" | sudo tee -a /etc/apt/sources.list
echo " deb http://security.ubuntu.com/ubuntu trusty-security universe" | sudo tee -a /etc/apt/sources.list
echo " deb-src http://security.ubuntu.com/ubuntu trusty-security universe" | sudo tee -a /etc/apt/sources.list
echo " deb http://security.ubuntu.com/ubuntu trusty-security multiverse" | sudo tee -a /etc/apt/sources.list
echo " deb-src http://security.ubuntu.com/ubuntu trusty-security multiverse" | sudo tee -a /etc/apt/sources.list
echo " deb http://extras.ubuntu.com/ubuntu trusty main" | sudo tee -a /etc/apt/sources.list
echo " deb-src http://extras.ubuntu.com/ubuntu trusty main" | sudo tee -a /etc/apt/sources.list

sudo apt-get -y update

sudo apt-get install -yq git cmake gcc g++ automake libtool wget lsof lshw pciutils net-tools tcpdump libpcre3 libpcre3-dev zlibc zlib1g zlib1g-dev
