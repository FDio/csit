#!/bin/bash
mkdir /dev/pts
mkdir /dev/hugepages
mount -t devpts -o "rw,noexec,nosuid,gid=5,mode=0620" devpts /dev/pts || true
mount -t tmpfs -o "rw,noexec,nosuid,size=10%,mode=0755" tmpfs /run
cp -r /tmp/openvpp-testing /run
mount -t tmpfs -o "rw,noexec,nosuid,size=10%,mode=0755" tmpfs /tmp
cp -r /run/openvpp-testing /tmp
mount -t hugetlbfs -o "rw,relatime,pagesize=2M" hugetlbfs /dev/hugepages
echo Y > /sys/module/vfio/parameters/enable_unsafe_noiommu_mode

# Qemu virtio-net-pci mgmt
ip address add dev ens3 10.0.2.15/24
ip link set dev ens3 up
ip route add default via 10.0.2.2

# Qemu virtio-net-pci vhost1
ip address add dev ens6 ${ip_address_l}
ip link set dev ens6 up
ip route add ${ip_route_r} via ${ip_address_r}

# Payload
${vnf_bin}

# Safenet
poweroff -f