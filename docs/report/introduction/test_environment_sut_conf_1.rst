SUT Settings - Linux
--------------------

System provisioning is done by combination of PXE boot unattented
install and
`Ansible <https://www.ansible.com>`_ described in `CSIT Testbed Setup`_.

Below a subset of the running configuration:

1. Ubuntu 18.04.x LTS

::

    $ lsb_release -a
    No LSB modules are available.
    Distributor ID: Ubuntu
    Description:    Ubuntu 18.04.3 LTS
    Release:        18.04
    Codename:       bionic

Linux Boot Parameters
~~~~~~~~~~~~~~~~~~~~~

- **isolcpus=<cpu number>-<cpu number>** used for all cpu cores apart from
  first core of each socket used for running VPP worker threads and Qemu/LXC
  processes
  https://www.kernel.org/doc/Documentation/admin-guide/kernel-parameters.txt
- **intel_pstate=disable** - [X86] Do not enable intel_pstate as the default
  scaling driver for the supported processors. Intel P-State driver decide what
  P-state (CPU core power state) to use based on requesting policy from the
  cpufreq core. [X86 - Either 32-bit or 64-bit x86]
  https://www.kernel.org/doc/Documentation/cpu-freq/intel-pstate.txt
- **nohz_full=<cpu number>-<cpu number>** - [KNL,BOOT] In kernels built with
  CONFIG_NO_HZ_FULL=y, set the specified list of CPUs whose tick will be stopped
  whenever possible. The boot CPU will be forced outside the range to maintain
  the timekeeping. The CPUs in this range must also be included in the
  rcu_nocbs= set. Specifies the adaptive-ticks CPU cores, causing kernel to
  avoid sending scheduling-clock interrupts to listed cores as long as they have
  a single runnable task. [KNL - Is a kernel start-up parameter, SMP - The
  kernel is an SMP kernel].
  https://www.kernel.org/doc/Documentation/timers/NO_HZ.txt
- **rcu_nocbs** - [KNL] In kernels built with CONFIG_RCU_NOCB_CPU=y, set the
  specified list of CPUs to be no-callback CPUs, that never queue RCU callbacks
  (read-copy update).
  https://www.kernel.org/doc/Documentation/admin-guide/kernel-parameters.txt
- **numa_balancing=disable** - [KNL,X86] Disable automatic NUMA balancing.
- **intel_iommu=enable** - [DMAR] Enable Intel IOMMU driver (DMAR) option.
- **iommu=on, iommu=pt** - [x86, IA-64] Disable IOMMU bypass, using IOMMU for
  PCI devices.
- **nmi_watchdog=0** - [KNL,BUGS=X86] Debugging features for SMP kernels. Turn
  hardlockup detector in nmi_watchdog off.
- **nosoftlockup** - [KNL] Disable the soft-lockup detector.
- **tsc=reliable** - Disable clocksource stability checks for TSC.
  [x86] reliable: mark tsc clocksource as reliable, this disables clocksource
  verification at runtime, as well as the stability checks done at bootup.
  Used to enable high-resolution timer mode on older hardware, and in
  virtualized environment.
- **hpet=disable** - [X86-32,HPET] Disable HPET and use PIT instead.

Hugepages Configuration
~~~~~~~~~~~~~~~~~~~~~~~

Huge pages are namaged via sysctl configuration located in
`/etc/sysctl.d/90-csit.conf` on each testbed. Default huge page size is 2M.
The exact amount of huge pages depends on testbed. All the values are defined
in `Ansible inventory - hosts` files.
