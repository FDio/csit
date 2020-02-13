#!/bin/bash
mkdir /dev/pts
mkdir /dev/hugepages
mount -t devpts -o "rw,noexec,nosuid,gid=5,mode=0620" devpts /dev/pts || true
mount -t tmpfs -o "rw,noexec,nosuid,size=10%,mode=0755" tmpfs /run
mount -t tmpfs -o "rw,noexec,nosuid,size=10%,mode=0755" tmpfs /tmp
mount -t hugetlbfs -o "rw,relatime,pagesize=2M" hugetlbfs /dev/hugepages
${unsafe_iommu}
${dpdk_dir}/usertools/dpdk-devbind.py -b vfio-pci 0000:00:06.0 0000:00:07.0
mkdir -p /var/run/vpp
${vnf_bin}
poweroff -f
