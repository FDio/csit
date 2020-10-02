#!/bin/bash
mkdir /dev/pts
mkdir /dev/hugepages
mount -t devpts -o "rw,noexec,nosuid,gid=5,mode=0620" devpts /dev/pts || true
mount -t tmpfs -o "rw,noexec,nosuid,size=10%,mode=0755" tmpfs /run
mount -t tmpfs -o "rw,noexec,nosuid,size=10%,mode=0755" tmpfs /tmp
mount -t hugetlbfs -o "rw,relatime,pagesize=2M" hugetlbfs /dev/hugepages
echo Y > /sys/module/vfio/parameters/enable_unsafe_noiommu_mode
ip address add dev ens6 ${ip_address_l}
ip link set dev ens6 up
ip route add default via ${ip_address_r}
${vnf_bin}
poweroff -f
