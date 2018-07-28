SUT Configuration - Host OS Linux
---------------------------------

System provisioning is done by combination of PXE boot unattented
install and
`Ansible <https://www.ansible.com>`_ described in `CSIT Testbed Setup`_.

Below a subset of the running configuration:

#. Haswell - Ubuntu 16.04.1 LTS

::

    $ lsb_release -a
    No LSB modules are available.
    Distributor ID:	Ubuntu
    Description:	Ubuntu 16.04.1 LTS
    Release:	16.04
    Codename:	xenial

#. Skylake - Ubuntu 18.04 LTS

::

    $ lsb_release -a
    No LSB modules are available.
    Distributor ID: Ubuntu
    Description:    Ubuntu 18.04 LTS
    Release:        18.04
    Codename:       bionic

**Kernel boot parameters used in CSIT performance testbeds**

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

**Applied command line boot parameters:**

#. Haswell - Ubuntu 16.04.1 LTS

::

    $ cat /proc/cmdline
    BOOT_IMAGE=/vmlinuz-4.4.0-72-generic root=UUID=35ea11e4-e44f-4f67-8cbe-12f09c49ed90 ro isolcpus=1-17,19-35 nohz_full=1-17,19-35 rcu_nocbs=1-17,19-35 intel_pstate=disable console=tty0 console=ttyS0,115200n8

#. Skylake - Ubuntu 18.04 LTS

::

    $ cat /proc/cmdline
    BOOT_IMAGE=/vmlinuz-4.15.0-23-generic root=UUID=3fa246fd-1b80-4361-bb90-f339a6bbed51 ro isolcpus=1-27,29-55,57-83,85-111 nohz_full=1-27,29-55,57-83,85-111 rcu_nocbs=1-27,29-55,57-83,85-111 numa_balancing=disable intel_pstate=disable intel_iommu=on iommu=pt nmi_watchdog=0 audit=0 nosoftlockup processor.max_cstate=1 intel_idle.max_cstate=1 hpet=disable tsc=reliable mce=off console=tty0 console=ttyS0,115200n8


