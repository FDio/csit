KVM VMs vhost-user
------------------

QEMU is used for VPP-VM testing enviroment. By default, standard QEMU version
preinstalled from OS repositories is used on VIRL/vpp_device functional testing
(qemu-2.11.x for Ubuntu 18.04, qemu-2.5.0 for Ubuntu 16.04). For perfomance
testing QEMU is downloaded from `project homepage <qemu.org>`_ and compiled
during testing. This allows framework to easily inject QEMU patches in case of
need. In QEMU version <2.8 we used it for increasing QEMU virtion queue size.
In CSIT setup DUTs have small VM image `/var/lib/vm/vhost-nested.img`. QEMU
binary can be adjusted in global settings. VM image must have installed at least
qemu-guest-agent, sshd, bridge-utils, VirtIO support and Testpmd/L3fwd
application. Username/password for the VM must be cisco/cisco and
NOPASSWD sudo access. The interface naming is based on driver (management
interface type is Intel E1000), all E1000 interfaces will be named mgmt<n> and
all VirtIO interfaces will be named virtio<n>. In VM
"/etc/init.d/qemu-guest-agent" you must set "TRANSPORT=isa-serial:/dev/ttyS1"
because ttyS0 is used by serial console and ttyS1 is dedicated for
qemu-guest-agent in QEMU setup. There is python library for QEMU setup, start
and some utilities "resources/libraries/python/QemuUtils.py"

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
