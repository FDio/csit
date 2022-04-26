.. _drivers_methodology:

Drivers
-------

In general, a driver is a software library that allows
a higher-level software program to communicate with lower-level
components without detailed knowledge of the lower-level communication
protocol (or even lower-level access).

In CSIT, not only we use different drivers, but we use different types
of drivers. They can be roughly grouped into three categories:
Network drivers, UIO drivers and VPP plugins.

VPP plugin
~~~~~~~~~~

When VPP processes packets (headers, payload or both),
it expects them to be present in memory (or in memory cache at least),
conforming to a specific memory layout (which apparently depends on
whether DPDK plugin is used).

As different network card manufacturers use different internal layout
for packet data (due to their own performance reasons),
there are multiple translation layers (implemented as VPP plugins),
each suitable for some network devices.

Usually, the VPP plugin code does not communicate with the device directly,
but it uses a network driver for that.

Example names: dpdk_plugin.so, avf_plugin.so, rdma_plugin.so.

UIO driver
~~~~~~~~~~

Some network drivers reside in kernel and have access to communicate
(over PCIe or some other bus) with devices they support.
But some drivers are designed to run in user space, so they lack the access.

UIO drivers are kernel drivers that allow some form of communication
between network devices and userspace network drivers.
Usually they do that by mapping part of device memory into host physical memory,
this is how the device internal memory layout may get exposed.

In the past CSIT used igb-uio for some testbed, but now we use vfio-pci only.

This name is in topology yaml files, the value under "uio_driver" key.

Network driver
~~~~~~~~~~~~~~

These are the drivers intimately familiar with the inner workings of specific
network devices, so they can facilitate best network latency and throughput.

Their code usually is not in VPP git repository, but is linked during a build
from a third party library.

Sometimes, VPP plugin calls network driver directly (called native driver
when used like this). Other times, VPP plugin calls yet another library
that abstracts the specific driver, getting broader manufacturer support
(perhaps at a slight performance penalty).

Sometimes, the same driver can be available both natively and as a DPDK driver.
(I hear DPDK could use IAVF network driver, but it never does in CSIT,
probably because we do not create VF for it to use).

CSIT does not name userspace network drivers, as they are implied by
vpp plugin name.

DPDK internal driver
____________________

DPDK plugin is a VPP plugin that communicates with DPDK library.
DPDK library usually autodetects device manufacturer (without CSIT being able
to affect the outcome), and uses an internal network driver (which uses UIO driver
to communicate with the device).

CSIT does not name DPDK internal drivers, but they are visible in logs.
Example names: net_ixgbe, net_i40e.

NIC driver
~~~~~~~~~~

This is a misnomer (or at least a complicated construct) used in CSIT suites
and in autogen.

The name (value) can refer mainly to a native network driver tied with a VPP plugin
(examples: drma-core, avf), or dpdk plugin with autodetected network driver
(confusingly this nic driver value is vfio-pci).

DRV robot tag
_____________

This is the same as NIC driver, but uppercase, with underscores, and with DRV_
prefx.

Example values: DRV_AVF, DRV_VFIO_PCI, DRV_RDMA_CORE.

Kernel driver
~~~~~~~~~~~~~

Some tests avoid userspace network drivers, or they need a specific kernel driver
to correctly setup what userspace driver needs (e.g. AVF driver needs a VF
created from PF using i40e kernel driver).

Example names: i40e, ixgbe, mlx5_core, ice.

This name is in topology yaml file, the value under "driver" key.

TODOs
~~~~~

Explain driver usage from containers, from both guest and host part of VM.
Mention where IOMMU and DDIO fits in.
Link to document explaining PF, VF and SR-IOV.
Mention how kernel drivers are used for AF_XDP and GSO.
Add links to VPP documentation on their plugins.
