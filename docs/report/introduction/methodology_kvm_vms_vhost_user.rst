KVM VMs vhost-user
------------------

QEMU is used for KVM VM vhost-user testing enviroment. By default,
standard QEMU version is used, preinstalled from OS repositories
(qemu-2.11.1 for Ubuntu 18.04, qemu-2.5.0 for Ubuntu 16.04). The path
to the QEMU binary can be adjusted in `Constants.py`.

FD.io CSIT performance lab is testing VPP vhost-user with KVM VMs using
following environment settings:

CSIT supports two types of VMs:

- **Image-VM**: used for all functional, VPP_device, and regular
  performance tests except NFV density tests.

- **Kernel-VM**: new VM type introduced for NFV density tests to provide
  greater in-VM application install flexibility and to further reduce
  test execution time by simpler VM lifecycle management.

Image-VM
~~~~~~~~

CSIT can use a pre-created VM image. The path to the image can be
adjusted in `Constants.py`. For convenience and full compatibility, the CSIT
repository contains a set of scripts to prepare a `Built-root
<https://buildroot.org/>`_-based embedded Linux image, with all the
dependencies needed to run DPDK Testpmd, DPDK L3Fwd, Linux bridge or
Linux IPv4 forwarding.

Buildroot was chosen for a VM image to make it lightweight and booting fast,
to limit its impact on overall testing duration.

In order to execute CSIT tests, the VM image must have following software
installed: qemu-guest-agent, sshd, bridge-utils, VirtIO support and DPDK
Testpmd/L3fwd applications. Username/password for the VM must be
``cisco``/``cisco``, a user with ``NOPASSWD`` sudo access. Interface naming
is based on the driver (management interface type is Intel E1000), all
E1000 interfaces will be named ``mgmt<n>`` and all VirtIO interfaces
will be named ``virtio<n>``. In VM ``/etc/init.d/qemu-guest-agent`` file,
the setting ``TRANSPORT=isa-serial:/dev/ttyS1`` must be present. The ttyS0
device is used by serial console and ttyS1 is dedicated to qemu-guest-agent
in QEMU setup.

Kernel-VM
~~~~~~~~~

CSIT can use a kernel KVM image as a boot kernel, as an alternative to
image VM. This option allows better configurability of what application
is running in VM userspace. Using root9p filesystem allows mapping the
host-OS filesystem as a read-only guest-OS filesystem.

Example of custom init script for the kernel-VM:

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
  echo vfio-pci > /sys/bus/pci/devices/0000:00:06.0/driver_override
  echo vfio-pci > /sys/bus/pci/devices/0000:00:07.0/driver_override
  echo 0000:00:06.0 > /sys/bus/pci/drivers/vfio-pci/bind
  echo 0000:00:07.0 > /sys/bus/pci/drivers/vfio-pci/bind
  $vnf_bin
  poweroff -f

QemuUtils library during runtime replaces the ``$vnf_bin`` variable by
the path to NF binary and its parameters. This allows CSIT to run any
application installed on host OS, for example the same version of VPP
as running in the host-OS.

Kernel-VM image must be available in the host filesystem as a
prerequisite. The path to kernel-VM image is defined in `Constants.py`.
