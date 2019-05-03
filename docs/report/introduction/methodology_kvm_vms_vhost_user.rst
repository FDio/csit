KVM VMs vhost-user
------------------

QEMU is used for vhost testing enviroment. By default, standard QEMU version
preinstalled from OS repositories is used (qemu-2.11.1 for Ubuntu 18.04,
qemu-2.5.0 for Ubuntu 16.04) and the path to the QEMU binary can be adjusted
in `Constants.py`.

FD.io CSIT performance lab is testing VPP vhost with KVM VMs using
following environment settings:

- Tests with varying Qemu virtio queue (a.k.a. vring) sizes: [vr1024] 1024
  descriptors to optimize for packet throughput.
- Tests with varying Linux :abbr:`CFS (Completely Fair Scheduler)`
  settings: [cfs] default settings, [cfsrr1] CFS RoundRobin(1) policy
  applied to all data plane threads handling test packet path including
  all VPP worker threads and all Qemu testpmd poll-mode threads.
- Resulting test cases are all combinations with [vr1024] and
  [cfs,cfsrr1] settings.
- Adjusted Linux kernel :abbr:`CFS (Completely Fair Scheduler)`
  scheduler policy for data plane threads used in CSIT is documented in
  `CSIT Performance Environment Tuning wiki
  <https://wiki.fd.io/view/CSIT/csit-perf-env-tuning-ubuntu1604>`_.
- The purpose is to verify performance impact (MRR and NDR/PDR
  throughput) and same test measurements repeatability, by making VPP
  and VM data plane threads less susceptible to other Linux OS system
  tasks hijacking CPU cores running those data plane threads.

CSIT does support two types VM definitions: Image or Kernel.

Image VM
~~~~~~~~

CSIT can use a pre-created VM image. The path to image can be adjusted in
`Constants.py`. For convenience and full compatibility CSIT repository contains
a set of scripts to prepare `Built-root <https://buildroot.org/>`_ based
embedded Linux image with all the dependencies needed to run DPDK testpmd, DPDK
l3fwd, Linux bridge or Linux IPv4 forwarding.

Built-root was chosen for a VM image to be lightweight and booting time
should not impact tests duration.

VM image must have installed at least qemu-guest-agent, sshd, bridge-utils,
VirtIO support and DPDK Testpmd/L3fwd application. Username/password for the VM
must be cisco/cisco and NOPASSWD sudo access. The interface naming is based on
driver (management interface type is Intel E1000), all E1000 interfaces will be
named mgmt<n> and all VirtIO interfaces will be named virtio<n>. In VM
"/etc/init.d/qemu-guest-agent" must be set to "TRANSPORT=isa-serial:/dev/ttyS1"
because ttyS0 is used by serial console and ttyS1 is dedicated for
qemu-guest-agent in QEMU setup.

Kernel VM
~~~~~~~~~

As an alternative to image VM, CSIT can use a kernel KVM image as a boot kernel.
This option allows better configurability of what application is running in VM
userspace. As a filesystem root9p is used which allows to map the host OS
filesystem as read only guest OS filesystem.

Example of custom init script for the kernel VM:

::
  #!/bin/bash
  mount -t sysfs -o "nodev,noexec,nosuid" sysfs /sys
  mount -t proc -o "nodev,noexec,nosuid" proc /proc
  mkdir /dev/pts
  mkdir /dev/hugepages
  mount -t devpts -o "rw,noexec,nosuid,gid=5,mode=0620" devpts /dev/pts || true
  mount -t tmpfs -o "rw,noexec,nosuid,size=10%,mode=0755" tmpfs /run
  mount -t tmpfs -o "rw,noexec,nosuid,size=10%,mode=0755" tmpfs /tmp
  mount -t hugetlbfs -o "rw,relatime,pagesize=2M" hugetlbfs /dev/hugepages
  echo 0000:00:06.0 > /sys/bus/pci/devices/0000:00:06.0/driver/unbind
  echo 0000:00:07.0 > /sys/bus/pci/devices/0000:00:07.0/driver/unbind
  echo uio_pci_generic > /sys/bus/pci/devices/0000:00:06.0/driver_override
  echo uio_pci_generic > /sys/bus/pci/devices/0000:00:07.0/driver_override
  echo 0000:00:06.0 > /sys/bus/pci/drivers/uio_pci_generic/bind
  echo 0000:00:07.0 > /sys/bus/pci/drivers/uio_pci_generic/bind
  $vnf_bin
  poweroff -f

The `$vnf_bin` variable is replaced, during runtime by the QemuUtils libraries,
by the path to NF binary and its parameters. This allows CSIT to run the
applications installed on host OS, for example VPP of the same version as
running on host OS.

Kernel KVM image must be available on host filesystem as a prerequisite.
The path to kernel image is defined in `Constants.py`.