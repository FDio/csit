Test Environment
================

CSIT performance tests are executed on the three identical physical
testbeds hosted by Linux Foundation for FD.io project. Each testbed
consists of two servers acting as Systems Under Test (SUT) and one
server acting as Traffic Generator (TG).

Server Specification and Configuration
--------------------------------------

Complete specification and configuration of compute servers used in CSIT
physical testbeds is maintained on wiki page
`CSIT LF Testbeds <https://wiki.fd.io/view/CSIT/CSIT_LF_testbed>`_.

SUT Configuration
-----------------

**Host configuration**

All hosts are Cisco UCS C240-M4 (2x Intel(R) Xeon(R) CPU E5-2699 v3 @ 2.30GHz,
18c, 512GB RAM)

::

    $ lscpu
    Architecture:          x86_64
    CPU op-mode(s):        32-bit, 64-bit
    Byte Order:            Little Endian
    CPU(s):                36
    On-line CPU(s) list:   0-35
    Thread(s) per core:    1
    Core(s) per socket:    18
    Socket(s):             2
    NUMA node(s):          2
    Vendor ID:             GenuineIntel
    CPU family:            6
    Model:                 63
    Model name:            Intel(R) Xeon(R) CPU E5-2699 v3 @ 2.30GHz
    Stepping:              2
    CPU MHz:               2294.249
    BogoMIPS:              4589.82
    Virtualization:        VT-x
    L1d cache:             32K
    L1i cache:             32K
    L2 cache:              256K
    L3 cache:              46080K
    NUMA node0 CPU(s):     0-17
    NUMA node1 CPU(s):     18-35
    Flags:                 fpu vme de pse tsc msr pae mce cx8 apic sep mtrr pge mca cmov pat pse36 clflush dts acpi mmx fxsr sse sse2 ss ht tm pbe syscall nx pdpe1gb rdtscp lm constant_tsc arch_perfmon pebs bts rep_good nopl xtopology nonstop_tsc aperfmperf eagerfpu pni pclmulqdq dtes64 monitor ds_cpl vmx smx est tm2 ssse3 sdbg fma cx16 xtpr pdcm pcid dca sse4_1 sse4_2 x2apic movbe popcnt tsc_deadline_timer aes xsave avx f16c rdrand lahf_lm abm epb tpr_shadow vnmi flexpriority ept vpid fsgsbase tsc_adjust bmi1 avx2 smep bmi2 erms invpcid cqm xsaveopt cqm_llc cqm_occup_llc dtherm arat pln pts

**BIOS settings**

::

    C240 /bios # show advanced detail
    Set-up parameters:
        Intel(R) VT-d ATS Support: Enabled
        Adjacent Cache Line Prefetcher: Enabled
        All Onboard LOM Ports: Enabled
        Altitude: 300 M
        Bits per second: 115200
        Power Technology: Performance
        Channel Interleaving: Auto
        Intel(R) VT-d Coherency Support: Disabled
        Console Redirection: COM 0
        Number of Enabled Cores: All
        Energy Performance: Performance
        CPU Performance: Enterprise
        DCU IP Prefetcher: Enabled
        DCU Streamer Prefetch: Enabled
        Demand Scrub: Enabled
        Direct Cache Access Support: Auto
        Enhanced Intel Speedstep(R) Tec: Disabled
        Execute Disable: Enabled
        Flow Control: None
        Hardware Prefetcher: Enabled
        Intel(R) Hyper-Threading Techno: Disabled
        Intel(R) Turbo Boost Technology: Disabled
        Intel(R) VT: Enabled
        Intel(R) VT-d: Enabled
        Intel(R) Interrupt Remapping: Enabled
        Legacy USB Support: Enabled
        Extended APIC: XAPIC
        LOM Port 1 OptionROM: Enabled
        LOM Port 2 OptionROM: Enabled
        MMIO above 4GB: Enabled
        NUMA: Enabled
        PCI ROM CLP: Disabled
        Package C State Limit: C6 Retention
        Intel(R) Pass Through DMA: Disabled
        Patrol Scrub: Enabled
        xHCI Mode: Disabled
        All PCIe Slots OptionROM: Enabled
        PCIe Slot:1 OptionROM: Disabled
        PCIe Slot:2 OptionROM: Disabled
        PCIe Slot:3 OptionROM: Disabled
        PCIe Slot:4 OptionROM: Disabled
        PCIe Slot:5 OptionROM: Disabled
        PCIe Slot:6 OptionROM: Disabled
        PCIe Slot:HBA Link Speed: GEN3
        PCIe Slot:HBA OptionROM: Enabled
        PCIe Slot:MLOM OptionROM: Enabled
        PCIe Slot:N1 OptionROM: Enabled
        PCIe Slot:N2 OptionROM: Enabled
        Processor Power state C1 Enhanc: Disabled
        Processor C3 Report: Disabled
        Processor C6 Report: Disabled
        P-STATE Coordination: HW ALL
        Putty KeyPad: ESCN
        Energy Performance Tuning: BIOS
        QPI Link Frequency Select: Auto
        QPI Snoop Mode: Home Snoop
        Rank Interleaving: Auto
        Redirection After BIOS POST: Always Enable
        PCH SATA Mode: AHCI
        Select Memory RAS: Maximum Performance
        SR-IOV Support: Enabled
        Terminal Type: VT100
        Port 60/64 Emulation: Enabled
        Workload Configuration: Balanced
        CDN Support for VIC: Disabled
        Out-of-Band Management: Disabled

**NIC models and placement**

In addition to CIMC and Management, each TG has 4x Intel X710 10GB NIC
(=8 ports) and 2x Intel XL710 40GB NIC (=4 ports), whereas each SUT has:

- 1x Intel X520 NIC (10GB, 2 ports),
- 1x Cisco VIC 1385 (40GB, 2 ports),
- 1x Intel XL710 NIC (40GB, 2 ports),
- 1x Intel X710 NIC (10GB, 2 ports),
- 1x Cisco VIC 1227 (10GB, 2 ports).

This allows for a total of five ring topologies, each using ports on
specific NIC model, enabling per NIC model benchmarking.

- 0a:00.0 Ethernet controller: Intel Corporation 82599ES 10-Gigabit SFI/SFP+
  Network Connection (rev 01) Subsystem: Intel Corporation Ethernet Server
  Adapter X520-2
- 0a:00.1 Ethernet controller: Intel Corporation 82599ES 10-Gigabit SFI/SFP+
  Network Connection (rev 01) Subsystem: Intel Corporation Ethernet Server
  Adapter X520-2
- 06:00.0 Ethernet controller: Cisco Systems Inc VIC Ethernet NIC (rev a2)
  Subsystem: Cisco Systems Inc VIC 1227 PCIe Ethernet NIC
- 07:00.0 Ethernet controller: Cisco Systems Inc VIC Ethernet NIC (rev a2)
  Subsystem: Cisco Systems Inc VIC 1227 PCIe Ethernet NIC
- 13:00.0 Ethernet controller: Cisco Systems Inc VIC Ethernet NIC (rev a2)
  Subsystem: Cisco Systems Inc VIC 1385 PCIe Ethernet NIC
- 15:00.0 Ethernet controller: Cisco Systems Inc VIC Ethernet NIC (rev a2)
  Subsystem: Cisco Systems Inc VIC 1385 PCIe Ethernet NIC
- 85:00.0 Ethernet controller: Intel Corporation Ethernet Controller XL710
  for 40GbE QSFP+ (rev 01) Subsystem: Intel Corporation Ethernet Converged
  Network Adapter XL710-Q2
- 85:00.1 Ethernet controller: Intel Corporation Ethernet Controller XL710
  for 40GbE QSFP+ (rev 01) Subsystem: Intel Corporation Ethernet Converged
  Network Adapter XL710-Q2
- 87:00.0 Ethernet controller: Intel Corporation Ethernet Controller X710 for
  10GbE SFP+ (rev 01) Subsystem: Intel Corporation Ethernet Converged Network
  Adapter X710-2
- 87:00.1 Ethernet controller: Intel Corporation Ethernet Controller X710 for
  10GbE SFP+ (rev 01) Subsystem: Intel Corporation Ethernet Converged Network
  Adapter X710-2

SUT Configuration - Host OS Linux
---------------------------------

Software details (OS, configuration) of physical testbeds are maintained
on wiki page
`CSIT LF Testbeds <https://wiki.fd.io/view/CSIT/CSIT_LF_testbed>`_.

System provisioning is done by combination of PXE boot unattented
install and
`Ansible <https://www.ansible.com>`_ described in `CSIT Testbed Setup`_.

Below a subset of the running configuration:

::

    $ lsb_release -a
    No LSB modules are available.
    Distributor ID:	Ubuntu
    Description:	Ubuntu 16.04.1 LTS
    Release:	16.04
    Codename:	xenial

::

    $ cat /sys/devices/system/node/node*/meminfo
    Node 0 MemTotal:       264048168 kB
    Node 0 MemFree:        257730716 kB
    Node 0 MemUsed:         6317452 kB
    Node 0 Active:          1079920 kB
    Node 0 Inactive:         470064 kB
    Node 0 Active(anon):     674772 kB
    Node 0 Inactive(anon):   248572 kB
    Node 0 Active(file):     405148 kB
    Node 0 Inactive(file):   221492 kB
    Node 0 Unevictable:           0 kB
    Node 0 Mlocked:               0 kB
    Node 0 Dirty:                12 kB
    Node 0 Writeback:             0 kB
    Node 0 FilePages:       1270432 kB
    Node 0 Mapped:            20116 kB
    Node 0 AnonPages:        279548 kB
    Node 0 Shmem:            643796 kB
    Node 0 KernelStack:        3376 kB
    Node 0 PageTables:         1316 kB
    Node 0 NFS_Unstable:          0 kB
    Node 0 Bounce:                0 kB
    Node 0 WritebackTmp:          0 kB
    Node 0 Slab:              80428 kB
    Node 0 SReclaimable:      38288 kB
    Node 0 SUnreclaim:        42140 kB
    Node 0 AnonHugePages:    270336 kB
    Node 0 HugePages_Total:  2048
    Node 0 HugePages_Free:   2048
    Node 0 HugePages_Surp:      0
    Node 1 MemTotal:       264237596 kB
    Node 1 MemFree:        256758976 kB
    Node 1 MemUsed:         7478620 kB
    Node 1 Active:          1746052 kB
    Node 1 Inactive:         981104 kB
    Node 1 Active(anon):    1272936 kB
    Node 1 Inactive(anon):   849968 kB
    Node 1 Active(file):     473116 kB
    Node 1 Inactive(file):   131136 kB
    Node 1 Unevictable:           0 kB
    Node 1 Mlocked:               0 kB
    Node 1 Dirty:                 0 kB
    Node 1 Writeback:             0 kB
    Node 1 FilePages:       2715284 kB
    Node 1 Mapped:            75928 kB
    Node 1 AnonPages:         11920 kB
    Node 1 Shmem:           2111036 kB
    Node 1 KernelStack:        2576 kB
    Node 1 PageTables:         1348 kB
    Node 1 NFS_Unstable:          0 kB
    Node 1 Bounce:                0 kB
    Node 1 WritebackTmp:          0 kB
    Node 1 Slab:              90604 kB
    Node 1 SReclaimable:      55384 kB
    Node 1 SUnreclaim:        35220 kB
    Node 1 AnonHugePages:      6144 kB
    Node 1 HugePages_Total:  2048
    Node 1 HugePages_Free:   2048
    Node 1 HugePages_Surp:      0

**Kernel boot parameters used in CSIT performance testbeds**

- **isolcpus=<cpu number>-<cpu number>** used for all cpu cores apart from
  first core of each socket used for running VPP worker threads and Qemu/LXC
  processes https://www.kernel.org/doc/Documentation/kernel-parameters.txt
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
  https://www.kernel.org/doc/Documentation/kernel-parameters.txt

**Applied command line boot parameters:**

::

    $ cat /proc/cmdline
    BOOT_IMAGE=/vmlinuz-4.4.0-72-generic root=UUID=35ea11e4-e44f-4f67-8cbe-12f09c49ed90 ro isolcpus=1-17,19-35 nohz_full=1-17,19-35 rcu_nocbs=1-17,19-35 intel_pstate=disable console=tty0 console=ttyS0,115200n8

**Mount listing**

::

    $ cat /proc/mounts
    sysfs /sys sysfs rw,nosuid,nodev,noexec,relatime 0 0
    proc /proc proc rw,nosuid,nodev,noexec,relatime 0 0
    udev /dev devtmpfs rw,nosuid,relatime,size=264125468k,nr_inodes=66031367,mode=755 0 0
    devpts /dev/pts devpts rw,nosuid,noexec,relatime,gid=5,mode=620,ptmxmode=000 0 0
    tmpfs /run tmpfs rw,nosuid,noexec,relatime,size=52828580k,mode=755 0 0
    /dev/sda2 / ext4 rw,relatime,errors=remount-ro,data=ordered 0 0
    securityfs /sys/kernel/security securityfs rw,nosuid,nodev,noexec,relatime 0 0
    tmpfs /dev/shm tmpfs rw,nosuid,nodev 0 0
    tmpfs /run/lock tmpfs rw,nosuid,nodev,noexec,relatime,size=5120k 0 0
    tmpfs /sys/fs/cgroup tmpfs ro,nosuid,nodev,noexec,mode=755 0 0
    cgroup /sys/fs/cgroup/systemd cgroup rw,nosuid,nodev,noexec,relatime,xattr,release_agent=/lib/systemd/systemd-cgroups-agent,name=systemd 0 0
    pstore /sys/fs/pstore pstore rw,nosuid,nodev,noexec,relatime 0 0
    cgroup /sys/fs/cgroup/freezer cgroup rw,nosuid,nodev,noexec,relatime,freezer 0 0
    cgroup /sys/fs/cgroup/net_cls,net_prio cgroup rw,nosuid,nodev,noexec,relatime,net_cls,net_prio 0 0
    cgroup /sys/fs/cgroup/cpu,cpuacct cgroup rw,nosuid,nodev,noexec,relatime,cpu,cpuacct 0 0
    cgroup /sys/fs/cgroup/memory cgroup rw,nosuid,nodev,noexec,relatime,memory 0 0
    cgroup /sys/fs/cgroup/blkio cgroup rw,nosuid,nodev,noexec,relatime,blkio 0 0
    cgroup /sys/fs/cgroup/perf_event cgroup rw,nosuid,nodev,noexec,relatime,perf_event 0 0
    cgroup /sys/fs/cgroup/devices cgroup rw,nosuid,nodev,noexec,relatime,devices 0 0
    cgroup /sys/fs/cgroup/cpuset cgroup rw,nosuid,nodev,noexec,relatime,cpuset,clone_children 0 0
    cgroup /sys/fs/cgroup/hugetlb cgroup rw,nosuid,nodev,noexec,relatime,hugetlb 0 0
    cgroup /sys/fs/cgroup/pids cgroup rw,nosuid,nodev,noexec,relatime,pids 0 0
    systemd-1 /proc/sys/fs/binfmt_misc autofs rw,relatime,fd=26,pgrp=1,timeout=0,minproto=5,maxproto=5,direct 0 0
    hugetlbfs /dev/hugepages hugetlbfs rw,relatime 0 0
    debugfs /sys/kernel/debug debugfs rw,relatime 0 0
    mqueue /dev/mqueue mqueue rw,relatime 0 0
    tracefs /sys/kernel/debug/tracing tracefs rw,relatime 0 0
    fusectl /sys/fs/fuse/connections fusectl rw,relatime 0 0
    /dev/sda1 /boot ext4 rw,relatime,data=ordered 0 0
    none /mnt/huge hugetlbfs rw,relatime,pagesize=2048k 0 0
    lxcfs /var/lib/lxcfs fuse.lxcfs rw,nosuid,nodev,relatime,user_id=0,group_id=0,allow_other 0 0

**Package listing**

::

    $ dpkg -l
    Desired=Unknown/Install/Remove/Purge/Hold
    | Status=Not/Inst/Conf-files/Unpacked/halF-conf/Half-inst/trig-aWait/Trig-pend
    |/ Err?=(none)/Reinst-required (Status,Err: uppercase=bad)
    ||/ Name                                                              Version                               Architecture                          Description
    +++-=================================================================-=====================================-=====================================-========================================================================================================================================
    ii  accountsservice                                                   0.6.40-2ubuntu11.1                    amd64                                 query and manipulate user account information
    ii  acl                                                               2.2.52-3                              amd64                                 Access control list utilities
    ii  adduser                                                           3.113+nmu3ubuntu4                     all                                   add and remove users and groups
    ii  apparmor                                                          2.10.95-0ubuntu2.6                    amd64                                 user-space parser utility for AppArmor
    ii  apt                                                               1.2.12~ubuntu16.04.1                  amd64                                 commandline package manager
    ii  apt-utils                                                         1.2.12~ubuntu16.04.1                  amd64                                 package management related utility programs
    ii  autoconf                                                          2.69-9                                all                                   automatic configure script builder
    ii  automake                                                          1:1.15-4ubuntu1                       all                                   Tool for generating GNU Standards-compliant Makefiles
    ii  autotools-dev                                                     20150820.1                            all                                   Update infrastructure for config.{guess,sub} files
    ii  base-files                                                        9.4ubuntu4.2                          amd64                                 Debian base system miscellaneous files
    ii  base-passwd                                                       3.5.39                                amd64                                 Debian base system master password and group files
    ii  bash                                                              4.3-14ubuntu1.1                       amd64                                 GNU Bourne Again SHell
    ii  binutils                                                          2.26.1-1ubuntu1~16.04.3               amd64                                 GNU assembler, linker and binary utilities
    ii  bridge-utils                                                      1.5-9ubuntu1                          amd64                                 Utilities for configuring the Linux Ethernet bridge
    ii  bsdutils                                                          1:2.27.1-6ubuntu3.1                   amd64                                 basic utilities from 4.4BSD-Lite
    ii  build-essential                                                   12.1ubuntu2                           amd64                                 Informational list of build-essential packages
    ii  busybox-initramfs                                                 1:1.22.0-15ubuntu1                    amd64                                 Standalone shell setup for initramfs
    ii  busybox-static                                                    1:1.22.0-15ubuntu1                    amd64                                 Standalone rescue shell with tons of builtin utilities
    ii  bzip2                                                             1.0.6-8                               amd64                                 high-quality block-sorting file compressor - utilities
    ii  ca-certificates                                                   20160104ubuntu1                       all                                   Common CA certificates
    ii  ca-certificates-java                                              20160321                              all                                   Common CA certificates (JKS keystore)
    ii  cgroup-bin                                                        0.41-7ubuntu1                         all                                   control and monitor control groups (transitional package)
    ii  cgroup-lite                                                       1.11                                  all                                   Light-weight package to set up cgroups at system boot
    ii  cgroup-tools                                                      0.41-7ubuntu1                         amd64                                 control and monitor control groups (tools)
    ii  cloud-image-utils                                                 0.27-0ubuntu24                        all                                   cloud image management utilities
    ii  console-setup                                                     1.108ubuntu15.2                       all                                   console font and keymap setup program
    ii  console-setup-linux                                               1.108ubuntu15.2                       all                                   Linux specific part of console-setup
    ii  coreutils                                                         8.25-2ubuntu2                         amd64                                 GNU core utilities
    ii  cpio                                                              2.11+dfsg-5ubuntu1                    amd64                                 GNU cpio -- a program to manage archives of files
    ii  cpp                                                               4:5.3.1-1ubuntu1                      amd64                                 GNU C preprocessor (cpp)
    ii  cpp-5                                                             5.4.0-6ubuntu1~16.04.2                amd64                                 GNU C preprocessor
    ii  cpu-checker                                                       0.7-0ubuntu7                          amd64                                 tools to help evaluate certain CPU (or BIOS) features
    ii  cpufrequtils                                                      008-1                                 amd64                                 utilities to deal with the cpufreq Linux kernel feature
    ii  crda                                                              3.13-1                                amd64                                 wireless Central Regulatory Domain Agent
    ii  cron                                                              3.0pl1-128ubuntu2                     amd64                                 process scheduling daemon
    ii  crudini                                                           0.7-1                                 amd64                                 utility for manipulating ini files
    ii  dash                                                              0.5.8-2.1ubuntu2                      amd64                                 POSIX-compliant shell
    ii  dbus                                                              1.10.6-1ubuntu3                       amd64                                 simple interprocess messaging system (daemon and utilities)
    ii  debconf                                                           1.5.58ubuntu1                         all                                   Debian configuration management system
    ii  debconf-i18n                                                      1.5.58ubuntu1                         all                                   full internationalization support for debconf
    ii  debianutils                                                       4.7                                   amd64                                 Miscellaneous utilities specific to Debian
    ii  debootstrap                                                       1.0.78+nmu1ubuntu1.3                  all                                   Bootstrap a basic Debian system
    ii  dh-python                                                         2.20151103ubuntu1.1                   all                                   Debian helper tools for packaging Python libraries and applications
    ii  diffutils                                                         1:3.3-3                               amd64                                 File comparison utilities
    ii  distro-info                                                       0.14build1                            amd64                                 provides information about the distributions' releases
    ii  distro-info-data                                                  0.28ubuntu0.1                         all                                   information about the distributions' releases (data files)
    ii  dkms                                                              2.2.0.3-2ubuntu11.2                   all                                   Dynamic Kernel Module Support Framework
    ii  dmidecode                                                         3.0-2ubuntu0.1                        amd64                                 SMBIOS/DMI table decoder
    ii  dns-root-data                                                     2015052300+h+1                        all                                   DNS root data including root zone and DNSSEC key
    ii  dnsmasq-base                                                      2.75-1ubuntu0.16.04.2                 amd64                                 Small caching DNS proxy and DHCP/TFTP server
    ii  dpkg                                                              1.18.4ubuntu1.1                       amd64                                 Debian package management system
    ii  dpkg-dev                                                          1.18.4ubuntu1.1                       all                                   Debian package development tools
    ii  e2fslibs:amd64                                                    1.42.13-1ubuntu1                      amd64                                 ext2/ext3/ext4 file system libraries
    ii  e2fsprogs                                                         1.42.13-1ubuntu1                      amd64                                 ext2/ext3/ext4 file system utilities
    ii  eject                                                             2.1.5+deb1+cvs20081104-13.1           amd64                                 ejects CDs and operates CD-Changers under Linux
    ii  expect                                                            5.45-7                                amd64                                 Automates interactive applications
    ii  fakeroot                                                          1.20.2-1ubuntu1                       amd64                                 tool for simulating superuser privileges
    ii  file                                                              1:5.25-2ubuntu1                       amd64                                 Determines file type using "magic" numbers
    ii  findutils                                                         4.6.0+git+20160126-2                  amd64                                 utilities for finding files--find, xargs
    ii  fontconfig-config                                                 2.11.94-0ubuntu1.1                    all                                   generic font configuration library - configuration
    ii  fonts-dejavu-core                                                 2.35-1                                all                                   Vera font family derivate with additional characters
    ii  g++                                                               4:5.3.1-1ubuntu1                      amd64                                 GNU C++ compiler
    ii  g++-5                                                             5.4.0-6ubuntu1~16.04.2                amd64                                 GNU C++ compiler
    ii  gcc                                                               4:5.3.1-1ubuntu1                      amd64                                 GNU C compiler
    ii  gcc-5                                                             5.4.0-6ubuntu1~16.04.2                amd64                                 GNU C compiler
    ii  gcc-5-base:amd64                                                  5.4.0-6ubuntu1~16.04.2                amd64                                 GCC, the GNU Compiler Collection (base package)
    ii  gcc-6-base:amd64                                                  6.0.1-0ubuntu1                        amd64                                 GCC, the GNU Compiler Collection (base package)
    ii  genisoimage                                                       9:1.1.11-3ubuntu1                     amd64                                 Creates ISO-9660 CD-ROM filesystem images
    ii  gettext-base                                                      0.19.7-2ubuntu3                       amd64                                 GNU Internationalization utilities for the base system
    ii  gir1.2-glib-2.0:amd64                                             1.46.0-3ubuntu1                       amd64                                 Introspection data for GLib, GObject, Gio and GModule
    ii  git                                                               1:2.7.4-0ubuntu1                      amd64                                 fast, scalable, distributed revision control system
    ii  git-man                                                           1:2.7.4-0ubuntu1                      all                                   fast, scalable, distributed revision control system (manual pages)
    ii  gnupg                                                             1.4.20-1ubuntu3.1                     amd64                                 GNU privacy guard - a free PGP replacement
    ii  gpgv                                                              1.4.20-1ubuntu3.1                     amd64                                 GNU privacy guard - signature verification tool
    ii  grep                                                              2.25-1~16.04.1                        amd64                                 GNU grep, egrep and fgrep
    ii  grub-common                                                       2.02~beta2-36ubuntu3.1                amd64                                 GRand Unified Bootloader (common files)
    ii  grub-gfxpayload-lists                                             0.7                                   amd64                                 GRUB gfxpayload blacklist
    ii  grub-pc                                                           2.02~beta2-36ubuntu3.1                amd64                                 GRand Unified Bootloader, version 2 (PC/BIOS version)
    ii  grub-pc-bin                                                       2.02~beta2-36ubuntu3.1                amd64                                 GRand Unified Bootloader, version 2 (PC/BIOS binaries)
    ii  grub2-common                                                      2.02~beta2-36ubuntu3.1                amd64                                 GRand Unified Bootloader (common files for version 2)
    ii  gzip                                                              1.6-4ubuntu1                          amd64                                 GNU compression utilities
    ii  hostname                                                          3.16ubuntu2                           amd64                                 utility to set/show the host name or domain name
    ii  ifupdown                                                          0.8.10ubuntu1                         amd64                                 high level tools to configure network interfaces
    ii  init                                                              1.29ubuntu2                           amd64                                 System-V-like init utilities - metapackage
    ii  init-system-helpers                                               1.29ubuntu2                           all                                   helper tools for all init systems
    ii  initramfs-tools                                                   0.122ubuntu8.1                        all                                   generic modular initramfs generator (automation)
    ii  initramfs-tools-bin                                               0.122ubuntu8.1                        amd64                                 binaries used by initramfs-tools
    ii  initramfs-tools-core                                              0.122ubuntu8.1                        all                                   generic modular initramfs generator (core tools)
    ii  initscripts                                                       2.88dsf-59.3ubuntu2                   amd64                                 scripts for initializing and shutting down the system
    ii  insserv                                                           1.14.0-5ubuntu3                       amd64                                 boot sequence organizer using LSB init.d script dependency information
    ii  installation-report                                               2.60ubuntu1                           all                                   system installation report
    ii  iproute2                                                          4.3.0-1ubuntu3                        amd64                                 networking and traffic control tools
    ii  iptables                                                          1.6.0-2ubuntu3                        amd64                                 administration tools for packet filtering and NAT
    ii  iputils-ping                                                      3:20121221-5ubuntu2                   amd64                                 Tools to test the reachability of network hosts
    ii  ipxe-qemu                                                         1.0.0+git-20150424.a25a16d-1ubuntu1   all                                   PXE boot firmware - ROM images for qemu
    ii  isc-dhcp-client                                                   4.3.3-5ubuntu12.1                     amd64                                 DHCP client for automatically obtaining an IP address
    ii  isc-dhcp-common                                                   4.3.3-5ubuntu12.1                     amd64                                 common files used by all of the isc-dhcp packages
    ii  iso-codes                                                         3.65-1                                all                                   ISO language, territory, currency, script codes and their translations
    ii  iw                                                                3.17-1                                amd64                                 tool for configuring Linux wireless devices
    ii  java-common                                                       0.56ubuntu2                           all                                   Base package for Java runtimes
    ii  kbd                                                               1.15.5-1ubuntu4                       amd64                                 Linux console font and keytable utilities
    ii  keyboard-configuration                                            1.108ubuntu15.2                       all                                   system-wide keyboard preferences
    ii  klibc-utils                                                       2.0.4-8ubuntu1.16.04.1                amd64                                 small utilities built with klibc for early boot
    ii  kmod                                                              22-1ubuntu4                           amd64                                 tools for managing Linux kernel modules
    ii  krb5-locales                                                      1.13.2+dfsg-5                         all                                   Internationalization support for MIT Kerberos
    ii  language-selector-common                                          0.165.3                               all                                   Language selector for Ubuntu
    ii  laptop-detect                                                     0.13.7ubuntu2                         amd64                                 attempt to detect a laptop
    ii  less                                                              481-2.1                               amd64                                 pager program similar to more
    ii  libaccountsservice0:amd64                                         0.6.40-2ubuntu11.1                    amd64                                 query and manipulate user account information - shared libraries
    ii  libacl1:amd64                                                     2.2.52-3                              amd64                                 Access control list shared library
    ii  libaio1:amd64                                                     0.3.110-2                             amd64                                 Linux kernel AIO access library - shared library
    ii  libalgorithm-diff-perl                                            1.19.03-1                             all                                   module to find differences between files
    ii  libalgorithm-diff-xs-perl                                         0.04-4build1                          amd64                                 module to find differences between files (XS accelerated)
    ii  libalgorithm-merge-perl                                           0.08-3                                all                                   Perl module for three-way merge of textual data
    ii  libapparmor-perl                                                  2.10.95-0ubuntu2.6                    amd64                                 AppArmor library Perl bindings
    ii  libapparmor1:amd64                                                2.10.95-0ubuntu2                      amd64                                 changehat AppArmor library
    ii  libapr1:amd64                                                     1.5.2-3                               amd64                                 Apache Portable Runtime Library
    ii  libapt-inst2.0:amd64                                              1.2.12~ubuntu16.04.1                  amd64                                 deb package format runtime library
    ii  libapt-pkg5.0:amd64                                               1.2.12~ubuntu16.04.1                  amd64                                 package management runtime library
    ii  libasan2:amd64                                                    5.4.0-6ubuntu1~16.04.2                amd64                                 AddressSanitizer -- a fast memory error detector
    ii  libasn1-8-heimdal:amd64                                           1.7~git20150920+dfsg-4ubuntu1         amd64                                 Heimdal Kerberos - ASN.1 library
    ii  libasound2:amd64                                                  1.1.0-0ubuntu1                        amd64                                 shared library for ALSA applications
    ii  libasound2-data                                                   1.1.0-0ubuntu1                        all                                   Configuration files and profiles for ALSA drivers
    ii  libasprintf0v5:amd64                                              0.19.7-2ubuntu3                       amd64                                 GNU library to use fprintf and friends in C++
    ii  libasyncns0:amd64                                                 0.8-5build1                           amd64                                 Asynchronous name service query library
    ii  libatm1:amd64                                                     1:2.5.1-1.5                           amd64                                 shared library for ATM (Asynchronous Transfer Mode)
    ii  libatomic1:amd64                                                  5.4.0-6ubuntu1~16.04.2                amd64                                 support library providing __atomic built-in functions
    ii  libattr1:amd64                                                    1:2.4.47-2                            amd64                                 Extended attribute shared library
    ii  libaudit-common                                                   1:2.4.5-1ubuntu2                      all                                   Dynamic library for security auditing - common files
    ii  libaudit1:amd64                                                   1:2.4.5-1ubuntu2                      amd64                                 Dynamic library for security auditing
    ii  libavahi-client3:amd64                                            0.6.32~rc+dfsg-1ubuntu2               amd64                                 Avahi client library
    ii  libavahi-common-data:amd64                                        0.6.32~rc+dfsg-1ubuntu2               amd64                                 Avahi common data files
    ii  libavahi-common3:amd64                                            0.6.32~rc+dfsg-1ubuntu2               amd64                                 Avahi common library
    ii  libblkid1:amd64                                                   2.27.1-6ubuntu3.1                     amd64                                 block device ID library
    ii  libbluetooth3:amd64                                               5.37-0ubuntu5                         amd64                                 Library to use the BlueZ Linux Bluetooth stack
    ii  libboost-iostreams1.58.0:amd64                                    1.58.0+dfsg-5ubuntu3.1                amd64                                 Boost.Iostreams Library
    ii  libboost-random1.58.0:amd64                                       1.58.0+dfsg-5ubuntu3.1                amd64                                 Boost Random Number Library
    ii  libboost-system1.58.0:amd64                                       1.58.0+dfsg-5ubuntu3.1                amd64                                 Operating system (e.g. diagnostics support) library
    ii  libboost-thread1.58.0:amd64                                       1.58.0+dfsg-5ubuntu3.1                amd64                                 portable C++ multi-threading
    ii  libbrlapi0.6:amd64                                                5.3.1-2ubuntu2.1                      amd64                                 braille display access via BRLTTY - shared library
    ii  libbsd0:amd64                                                     0.8.2-1                               amd64                                 utility functions from BSD systems - shared library
    ii  libbz2-1.0:amd64                                                  1.0.6-8                               amd64                                 high-quality block-sorting file compressor library - runtime
    ii  libc-bin                                                          2.23-0ubuntu3                         amd64                                 GNU C Library: Binaries
    ii  libc-dev-bin                                                      2.23-0ubuntu3                         amd64                                 GNU C Library: Development binaries
    ii  libc6:amd64                                                       2.23-0ubuntu3                         amd64                                 GNU C Library: Shared libraries
    ii  libc6-dev:amd64                                                   2.23-0ubuntu3                         amd64                                 GNU C Library: Development Libraries and Header Files
    ii  libcaca0:amd64                                                    0.99.beta19-2build2~gcc5.2            amd64                                 colour ASCII art library
    ii  libcacard0:amd64                                                  1:2.5.0-2                             amd64                                 Virtual Common Access Card (CAC) Emulator (runtime library)
    ii  libcap-ng0:amd64                                                  0.7.7-1                               amd64                                 An alternate POSIX capabilities library
    ii  libcap2:amd64                                                     1:2.24-12                             amd64                                 POSIX 1003.1e capabilities (library)
    ii  libcap2-bin                                                       1:2.24-12                             amd64                                 POSIX 1003.1e capabilities (utilities)
    ii  libcc1-0:amd64                                                    5.4.0-6ubuntu1~16.04.2                amd64                                 GCC cc1 plugin for GDB
    ii  libcgroup1:amd64                                                  0.41-7ubuntu1                         amd64                                 control and monitor control groups (library)
    ii  libcilkrts5:amd64                                                 5.4.0-6ubuntu1~16.04.2                amd64                                 Intel Cilk Plus language extensions (runtime)
    ii  libcomerr2:amd64                                                  1.42.13-1ubuntu1                      amd64                                 common error description library
    ii  libcpufreq0                                                       008-1                                 amd64                                 shared library to deal with the cpufreq Linux kernel feature
    ii  libcryptsetup4:amd64                                              2:1.6.6-5ubuntu2                      amd64                                 disk encryption support - shared library
    ii  libcups2:amd64                                                    2.1.3-4                               amd64                                 Common UNIX Printing System(tm) - Core library
    ii  libcurl3-gnutls:amd64                                             7.47.0-1ubuntu2.1                     amd64                                 easy-to-use client-side URL transfer library (GnuTLS flavour)
    ii  libdb5.3:amd64                                                    5.3.28-11                             amd64                                 Berkeley v5.3 Database Libraries [runtime]
    ii  libdbus-1-3:amd64                                                 1.10.6-1ubuntu3                       amd64                                 simple interprocess messaging system (library)
    ii  libdbus-glib-1-2:amd64                                            0.106-1                               amd64                                 simple interprocess messaging system (GLib-based shared library)
    ii  libdebconfclient0:amd64                                           0.198ubuntu1                          amd64                                 Debian Configuration Management System (C-implementation library)
    ii  libdevmapper1.02.1:amd64                                          2:1.02.110-1ubuntu10                  amd64                                 Linux Kernel Device Mapper userspace library
    ii  libdns-export162                                                  1:9.10.3.dfsg.P4-8ubuntu1.1           amd64                                 Exported DNS Shared Library
    ii  libdpkg-perl                                                      1.18.4ubuntu1.1                       all                                   Dpkg perl modules
    ii  libdrm-amdgpu1:amd64                                              2.4.67-1ubuntu0.16.04.2               amd64                                 Userspace interface to amdgpu-specific kernel DRM services -- runtime
    ii  libdrm-intel1:amd64                                               2.4.67-1ubuntu0.16.04.2               amd64                                 Userspace interface to intel-specific kernel DRM services -- runtime
    ii  libdrm-nouveau2:amd64                                             2.4.67-1ubuntu0.16.04.2               amd64                                 Userspace interface to nouveau-specific kernel DRM services -- runtime
    ii  libdrm-radeon1:amd64                                              2.4.67-1ubuntu0.16.04.2               amd64                                 Userspace interface to radeon-specific kernel DRM services -- runtime
    ii  libdrm2:amd64                                                     2.4.67-1ubuntu0.16.04.2               amd64                                 Userspace interface to kernel DRM services -- runtime
    ii  libedit2:amd64                                                    3.1-20150325-1ubuntu2                 amd64                                 BSD editline and history libraries
    ii  libelf1:amd64                                                     0.165-3ubuntu1                        amd64                                 library to read and write ELF files
    ii  liberror-perl                                                     0.17-1.2                              all                                   Perl module for error/exception handling in an OO-ish way
    ii  libestr0                                                          0.1.10-1                              amd64                                 Helper functions for handling strings (lib)
    ii  libexpat1:amd64                                                   2.1.0-7ubuntu0.16.04.2                amd64                                 XML parsing C library - runtime library
    ii  libexpat1-dev:amd64                                               2.1.0-7ubuntu0.16.04.2                amd64                                 XML parsing C library - development kit
    ii  libfakeroot:amd64                                                 1.20.2-1ubuntu1                       amd64                                 tool for simulating superuser privileges - shared libraries
    ii  libfdisk1:amd64                                                   2.27.1-6ubuntu3.1                     amd64                                 fdisk partitioning library
    ii  libfdt1:amd64                                                     1.4.0+dfsg-2                          amd64                                 Flat Device Trees manipulation library
    ii  libffi6:amd64                                                     3.2.1-4                               amd64                                 Foreign Function Interface library runtime
    ii  libfile-fcntllock-perl                                            0.22-3                                amd64                                 Perl module for file locking with fcntl(2)
    ii  libflac8:amd64                                                    1.3.1-4                               amd64                                 Free Lossless Audio Codec - runtime C library
    ii  libfontconfig1:amd64                                              2.11.94-0ubuntu1.1                    amd64                                 generic font configuration library - runtime
    ii  libfontenc1:amd64                                                 1:1.1.3-1                             amd64                                 X11 font encoding library
    ii  libfreetype6:amd64                                                2.6.1-0.1ubuntu2                      amd64                                 FreeType 2 font engine, shared library files
    ii  libfribidi0:amd64                                                 0.19.7-1                              amd64                                 Free Implementation of the Unicode BiDi algorithm
    ii  libfuse2:amd64                                                    2.9.4-1ubuntu3                        amd64                                 Filesystem in Userspace (library)
    ii  libgcc-5-dev:amd64                                                5.4.0-6ubuntu1~16.04.2                amd64                                 GCC support library (development files)
    ii  libgcc1:amd64                                                     1:6.0.1-0ubuntu1                      amd64                                 GCC support library
    ii  libgcrypt20:amd64                                                 1.6.5-2ubuntu0.2                      amd64                                 LGPL Crypto library - runtime library
    ii  libgdbm3:amd64                                                    1.8.3-13.1                            amd64                                 GNU dbm database routines (runtime version)
    ii  libgirepository-1.0-1:amd64                                       1.46.0-3ubuntu1                       amd64                                 Library for handling GObject introspection data (runtime library)
    ii  libgl1-mesa-dri:amd64                                             11.2.0-1ubuntu2.2                     amd64                                 free implementation of the OpenGL API -- DRI modules
    ii  libgl1-mesa-glx:amd64                                             11.2.0-1ubuntu2.2                     amd64                                 free implementation of the OpenGL API -- GLX runtime
    ii  libglapi-mesa:amd64                                               11.2.0-1ubuntu2.2                     amd64                                 free implementation of the GL API -- shared library
    ii  libglib2.0-0:amd64                                                2.48.1-1~ubuntu16.04.1                amd64                                 GLib library of C routines
    ii  libglib2.0-bin                                                    2.48.1-1~ubuntu16.04.1                amd64                                 Programs for the GLib library
    ii  libglib2.0-data                                                   2.48.1-1~ubuntu16.04.1                all                                   Common files for GLib library
    ii  libglib2.0-dev                                                    2.48.1-1~ubuntu16.04.1                amd64                                 Development files for the GLib library
    ii  libgmp10:amd64                                                    2:6.1.0+dfsg-2                        amd64                                 Multiprecision arithmetic library
    ii  libgnutls-openssl27:amd64                                         3.4.10-4ubuntu1.1                     amd64                                 GNU TLS library - OpenSSL wrapper
    ii  libgnutls30:amd64                                                 3.4.10-4ubuntu1.1                     amd64                                 GNU TLS library - main runtime library
    ii  libgomp1:amd64                                                    5.4.0-6ubuntu1~16.04.2                amd64                                 GCC OpenMP (GOMP) support library
    ii  libgpg-error0:amd64                                               1.21-2ubuntu1                         amd64                                 library for common error values and messages in GnuPG components
    ii  libgssapi-krb5-2:amd64                                            1.13.2+dfsg-5                         amd64                                 MIT Kerberos runtime libraries - krb5 GSS-API Mechanism
    ii  libgssapi3-heimdal:amd64                                          1.7~git20150920+dfsg-4ubuntu1         amd64                                 Heimdal Kerberos - GSSAPI support library
    ii  libhcrypto4-heimdal:amd64                                         1.7~git20150920+dfsg-4ubuntu1         amd64                                 Heimdal Kerberos - crypto library
    ii  libheimbase1-heimdal:amd64                                        1.7~git20150920+dfsg-4ubuntu1         amd64                                 Heimdal Kerberos - Base library
    ii  libheimntlm0-heimdal:amd64                                        1.7~git20150920+dfsg-4ubuntu1         amd64                                 Heimdal Kerberos - NTLM support library
    ii  libhogweed4:amd64                                                 3.2-1                                 amd64                                 low level cryptographic library (public-key cryptos)
    ii  libhx509-5-heimdal:amd64                                          1.7~git20150920+dfsg-4ubuntu1         amd64                                 Heimdal Kerberos - X509 support library
    ii  libice6:amd64                                                     2:1.0.9-1                             amd64                                 X11 Inter-Client Exchange library
    ii  libicu55:amd64                                                    55.1-7                                amd64                                 International Components for Unicode
    ii  libidn11:amd64                                                    1.32-3ubuntu1.1                       amd64                                 GNU Libidn library, implementation of IETF IDN specifications
    ii  libisc-export160                                                  1:9.10.3.dfsg.P4-8ubuntu1.1           amd64                                 Exported ISC Shared Library
    ii  libiscsi2:amd64                                                   1.12.0-2                              amd64                                 iSCSI client shared library
    ii  libisl15:amd64                                                    0.16.1-1                              amd64                                 manipulating sets and relations of integer points bounded by linear constraints
    ii  libitm1:amd64                                                     5.4.0-6ubuntu1~16.04.2                amd64                                 GNU Transactional Memory Library
    ii  libjpeg-turbo8:amd64                                              1.4.2-0ubuntu3                        amd64                                 IJG JPEG compliant runtime library.
    ii  libjpeg8:amd64                                                    8c-2ubuntu8                           amd64                                 Independent JPEG Group's JPEG runtime library (dependency package)
    ii  libjson-c2:amd64                                                  0.11-4ubuntu2                         amd64                                 JSON manipulation library - shared library
    ii  libk5crypto3:amd64                                                1.13.2+dfsg-5                         amd64                                 MIT Kerberos runtime libraries - Crypto Library
    ii  libkeyutils1:amd64                                                1.5.9-8ubuntu1                        amd64                                 Linux Key Management Utilities (library)
    ii  libklibc                                                          2.0.4-8ubuntu1.16.04.1                amd64                                 minimal libc subset for use with initramfs
    ii  libkmod2:amd64                                                    22-1ubuntu4                           amd64                                 libkmod shared library
    ii  libkrb5-26-heimdal:amd64                                          1.7~git20150920+dfsg-4ubuntu1         amd64                                 Heimdal Kerberos - libraries
    ii  libkrb5-3:amd64                                                   1.13.2+dfsg-5                         amd64                                 MIT Kerberos runtime libraries
    ii  libkrb5support0:amd64                                             1.13.2+dfsg-5                         amd64                                 MIT Kerberos runtime libraries - Support library
    ii  liblcms2-2:amd64                                                  2.6-3ubuntu2                          amd64                                 Little CMS 2 color management library
    ii  libldap-2.4-2:amd64                                               2.4.42+dfsg-2ubuntu3.1                amd64                                 OpenLDAP libraries
    ii  libllvm3.8:amd64                                                  1:3.8-2ubuntu4                        amd64                                 Modular compiler and toolchain technologies, runtime library
    ii  liblocale-gettext-perl                                            1.07-1build1                          amd64                                 module using libc functions for internationalization in Perl
    ii  liblsan0:amd64                                                    5.4.0-6ubuntu1~16.04.2                amd64                                 LeakSanitizer -- a memory leak detector (runtime)
    ii  libltdl-dev:amd64                                                 2.4.6-0.1                             amd64                                 System independent dlopen wrapper for GNU libtool
    ii  libltdl7:amd64                                                    2.4.6-0.1                             amd64                                 System independent dlopen wrapper for GNU libtool
    ii  liblxc1                                                           2.0.7-0ubuntu1~16.04.2                amd64                                 Linux Containers userspace tools (library)
    ii  liblz4-1:amd64                                                    0.0~r131-2ubuntu2                     amd64                                 Fast LZ compression algorithm library - runtime
    ii  liblzma5:amd64                                                    5.1.1alpha+20120614-2ubuntu2          amd64                                 XZ-format compression library
    ii  libmagic1:amd64                                                   1:5.25-2ubuntu1                       amd64                                 File type determination library using "magic" numbers
    ii  libmnl0:amd64                                                     1.0.3-5                               amd64                                 minimalistic Netlink communication library
    ii  libmount1:amd64                                                   2.27.1-6ubuntu3.1                     amd64                                 device mounting library
    ii  libmpc3:amd64                                                     1.0.3-1                               amd64                                 multiple precision complex floating-point library
    ii  libmpdec2:amd64                                                   2.4.2-1                               amd64                                 library for decimal floating point arithmetic (runtime library)
    ii  libmpfr4:amd64                                                    3.1.4-1                               amd64                                 multiple precision floating-point computation
    ii  libmpx0:amd64                                                     5.4.0-6ubuntu1~16.04.2                amd64                                 Intel memory protection extensions (runtime)
    ii  libncurses5:amd64                                                 6.0+20160213-1ubuntu1                 amd64                                 shared libraries for terminal handling
    ii  libncursesw5:amd64                                                6.0+20160213-1ubuntu1                 amd64                                 shared libraries for terminal handling (wide character support)
    ii  libnetfilter-conntrack3:amd64                                     1.0.5-1                               amd64                                 Netfilter netlink-conntrack library
    ii  libnettle6:amd64                                                  3.2-1                                 amd64                                 low level cryptographic library (symmetric and one-way cryptos)
    ii  libnewt0.52:amd64                                                 0.52.18-1ubuntu2                      amd64                                 Not Erik's Windowing Toolkit - text mode windowing with slang
    ii  libnfnetlink0:amd64                                               1.0.1-3                               amd64                                 Netfilter netlink library
    ii  libnih-dbus1:amd64                                                1.0.3-4.3ubuntu1                      amd64                                 NIH D-Bus Bindings Library
    ii  libnih1:amd64                                                     1.0.3-4.3ubuntu1                      amd64                                 NIH Utility Library
    ii  libnl-3-200:amd64                                                 3.2.27-1                              amd64                                 library for dealing with netlink sockets
    ii  libnl-genl-3-200:amd64                                            3.2.27-1                              amd64                                 library for dealing with netlink sockets - generic netlink
    ii  libnspr4:amd64                                                    2:4.12-0ubuntu0.16.04.1               amd64                                 NetScape Portable Runtime Library
    ii  libnss3:amd64                                                     2:3.23-0ubuntu0.16.04.1               amd64                                 Network Security Service libraries
    ii  libnss3-nssdb                                                     2:3.23-0ubuntu0.16.04.1               all                                   Network Security Security libraries - shared databases
    ii  libnuma1:amd64                                                    2.0.11-1ubuntu1                       amd64                                 Libraries for controlling NUMA policy
    ii  libogg0:amd64                                                     1.3.2-1                               amd64                                 Ogg bitstream library
    ii  libopus0:amd64                                                    1.1.2-1ubuntu1                        amd64                                 Opus codec runtime library
    ii  libp11-kit0:amd64                                                 0.23.2-3                              amd64                                 Library for loading and coordinating access to PKCS#11 modules - runtime
    ii  libpam-cgfs                                                       2.0.6-0ubuntu1~16.04.1                amd64                                 PAM module for managing cgroups for LXC
    ii  libpam-modules:amd64                                              1.1.8-3.2ubuntu2                      amd64                                 Pluggable Authentication Modules for PAM
    ii  libpam-modules-bin                                                1.1.8-3.2ubuntu2                      amd64                                 Pluggable Authentication Modules for PAM - helper binaries
    ii  libpam-runtime                                                    1.1.8-3.2ubuntu2                      all                                   Runtime support for the PAM library
    ii  libpam0g:amd64                                                    1.1.8-3.2ubuntu2                      amd64                                 Pluggable Authentication Modules library
    ii  libpcap-dev                                                       1.7.4-2                               all                                   development library for libpcap (transitional package)
    ii  libpcap0.8:amd64                                                  1.7.4-2                               amd64                                 system interface for user-level packet capture
    ii  libpcap0.8-dev                                                    1.7.4-2                               amd64                                 development library and header files for libpcap0.8
    ii  libpci3:amd64                                                     1:3.3.1-1.1ubuntu1                    amd64                                 Linux PCI Utilities (shared library)
    ii  libpciaccess0:amd64                                               0.13.4-1                              amd64                                 Generic PCI access library for X
    ii  libpcre16-3:amd64                                                 2:8.38-3.1                            amd64                                 Perl 5 Compatible Regular Expression Library - 16 bit runtime files
    ii  libpcre3:amd64                                                    2:8.38-3.1                            amd64                                 Perl 5 Compatible Regular Expression Library - runtime files
    ii  libpcre3-dev:amd64                                                2:8.38-3.1                            amd64                                 Perl 5 Compatible Regular Expression Library - development files
    ii  libpcre32-3:amd64                                                 2:8.38-3.1                            amd64                                 Perl 5 Compatible Regular Expression Library - 32 bit runtime files
    ii  libpcrecpp0v5:amd64                                               2:8.38-3.1                            amd64                                 Perl 5 Compatible Regular Expression Library - C++ runtime files
    ii  libpcsclite1:amd64                                                1.8.14-1ubuntu1.16.04.1               amd64                                 Middleware to access a smart card using PC/SC (library)
    ii  libperl5.22:amd64                                                 5.22.1-9                              amd64                                 shared Perl library
    ii  libpixman-1-0:amd64                                               0.33.6-1                              amd64                                 pixel-manipulation library for X and cairo
    ii  libplymouth4:amd64                                                0.9.2-3ubuntu13.1                     amd64                                 graphical boot animation and logger - shared libraries
    ii  libpng12-0:amd64                                                  1.2.54-1ubuntu1                       amd64                                 PNG library - runtime
    ii  libpolkit-gobject-1-0:amd64                                       0.105-14.1                            amd64                                 PolicyKit Authorization API
    ii  libpopt0:amd64                                                    1.16-10                               amd64                                 lib for parsing cmdline parameters
    ii  libprocps4:amd64                                                  2:3.3.10-4ubuntu2                     amd64                                 library for accessing process information from /proc
    ii  libpulse0:amd64                                                   1:8.0-0ubuntu3                        amd64                                 PulseAudio client libraries
    ii  libpython-all-dev:amd64                                           2.7.11-1                              amd64                                 package depending on all supported Python development packages
    ii  libpython-dev:amd64                                               2.7.11-1                              amd64                                 header files and a static library for Python (default)
    ii  libpython-stdlib:amd64                                            2.7.11-1                              amd64                                 interactive high-level object-oriented language (default python version)
    ii  libpython2.7:amd64                                                2.7.12-1~16.04                        amd64                                 Shared Python runtime library (version 2.7)
    ii  libpython2.7-dev:amd64                                            2.7.12-1~16.04                        amd64                                 Header files and a static library for Python (v2.7)
    ii  libpython2.7-minimal:amd64                                        2.7.12-1~16.04                        amd64                                 Minimal subset of the Python language (version 2.7)
    ii  libpython2.7-stdlib:amd64                                         2.7.12-1~16.04                        amd64                                 Interactive high-level object-oriented language (standard library, version 2.7)
    ii  libpython3-stdlib:amd64                                           3.5.1-3                               amd64                                 interactive high-level object-oriented language (default python3 version)
    ii  libpython3.5-minimal:amd64                                        3.5.2-2~16.01                         amd64                                 Minimal subset of the Python language (version 3.5)
    ii  libpython3.5-stdlib:amd64                                         3.5.2-2~16.01                         amd64                                 Interactive high-level object-oriented language (standard library, version 3.5)
    ii  libquadmath0:amd64                                                5.4.0-6ubuntu1~16.04.2                amd64                                 GCC Quad-Precision Math Library
    ii  librados2                                                         10.2.2-0ubuntu0.16.04.2               amd64                                 RADOS distributed object store client library
    ii  librbd1                                                           10.2.2-0ubuntu0.16.04.2               amd64                                 RADOS block device client library
    ii  libreadline6:amd64                                                6.3-8ubuntu2                          amd64                                 GNU readline and history libraries, run-time libraries
    ii  libroken18-heimdal:amd64                                          1.7~git20150920+dfsg-4ubuntu1         amd64                                 Heimdal Kerberos - roken support library
    ii  librtmp1:amd64                                                    2.4+20151223.gitfa8646d-1build1       amd64                                 toolkit for RTMP streams (shared library)
    ii  libsasl2-2:amd64                                                  2.1.26.dfsg1-14build1                 amd64                                 Cyrus SASL - authentication abstraction library
    ii  libsasl2-modules:amd64                                            2.1.26.dfsg1-14build1                 amd64                                 Cyrus SASL - pluggable authentication modules
    ii  libsasl2-modules-db:amd64                                         2.1.26.dfsg1-14build1                 amd64                                 Cyrus SASL - pluggable authentication modules (DB)
    ii  libsdl1.2debian:amd64                                             1.2.15+dfsg1-3                        amd64                                 Simple DirectMedia Layer
    ii  libseccomp2:amd64                                                 2.2.3-3ubuntu3                        amd64                                 high level interface to Linux seccomp filter
    ii  libselinux1:amd64                                                 2.4-3build2                           amd64                                 SELinux runtime shared libraries
    ii  libsemanage-common                                                2.3-1build3                           all                                   Common files for SELinux policy management libraries
    ii  libsemanage1:amd64                                                2.3-1build3                           amd64                                 SELinux policy management library
    ii  libsepol1:amd64                                                   2.4-2                                 amd64                                 SELinux library for manipulating binary security policies
    ii  libsigsegv2:amd64                                                 2.10-4                                amd64                                 Library for handling page faults in a portable way
    ii  libslang2:amd64                                                   2.3.0-2ubuntu1                        amd64                                 S-Lang programming library - runtime version
    ii  libsm6:amd64                                                      2:1.2.2-1                             amd64                                 X11 Session Management library
    ii  libsmartcols1:amd64                                               2.27.1-6ubuntu3.1                     amd64                                 smart column output alignment library
    ii  libsndfile1:amd64                                                 1.0.25-10                             amd64                                 Library for reading/writing audio files
    ii  libspice-server1:amd64                                            0.12.6-4ubuntu0.1                     amd64                                 Implements the server side of the SPICE protocol
    ii  libsqlite3-0:amd64                                                3.11.0-1ubuntu1                       amd64                                 SQLite 3 shared library
    ii  libss2:amd64                                                      1.42.13-1ubuntu1                      amd64                                 command-line interface parsing library
    ii  libssl1.0.0:amd64                                                 1.0.2g-1ubuntu4.5                     amd64                                 Secure Sockets Layer toolkit - shared libraries
    ii  libstdc++-5-dev:amd64                                             5.4.0-6ubuntu1~16.04.2                amd64                                 GNU Standard C++ Library v3 (development files)
    ii  libstdc++6:amd64                                                  5.4.0-6ubuntu1~16.04.2                amd64                                 GNU Standard C++ Library v3
    ii  libsystemd0:amd64                                                 229-4ubuntu10                         amd64                                 systemd utility library
    ii  libtasn1-6:amd64                                                  4.7-3ubuntu0.16.04.1                  amd64                                 Manage ASN.1 structures (runtime)
    ii  libtcl8.6:amd64                                                   8.6.5+dfsg-2                          amd64                                 Tcl (the Tool Command Language) v8.6 - run-time library files
    ii  libtext-charwidth-perl                                            0.04-7build5                          amd64                                 get display widths of characters on the terminal
    ii  libtext-iconv-perl                                                1.7-5build4                           amd64                                 converts between character sets in Perl
    ii  libtext-wrapi18n-perl                                             0.06-7.1                              all                                   internationalized substitute of Text::Wrap
    ii  libtinfo5:amd64                                                   6.0+20160213-1ubuntu1                 amd64                                 shared low-level terminfo library for terminal handling
    ii  libtk8.6:amd64                                                    8.6.5-1                               amd64                                 Tk toolkit for Tcl and X11 v8.6 - run-time files
    ii  libtool                                                           2.4.6-0.1                             all                                   Generic library support script
    ii  libtsan0:amd64                                                    5.4.0-6ubuntu1~16.04.2                amd64                                 ThreadSanitizer -- a Valgrind-based detector of data races (runtime)
    ii  libtxc-dxtn-s2tc0:amd64                                           0~git20131104-1.1                     amd64                                 Texture compression library for Mesa
    ii  libubsan0:amd64                                                   5.4.0-6ubuntu1~16.04.2                amd64                                 UBSan -- undefined behaviour sanitizer (runtime)
    ii  libudev1:amd64                                                    229-4ubuntu10                         amd64                                 libudev shared library
    ii  libusb-0.1-4:amd64                                                2:0.1.12-28                           amd64                                 userspace USB programming library
    ii  libusb-1.0-0:amd64                                                2:1.0.20-1                            amd64                                 userspace USB programming library
    ii  libusbredirparser1:amd64                                          0.7.1-1                               amd64                                 Parser for the usbredir protocol (runtime)
    ii  libustr-1.0-1:amd64                                               1.0.4-5                               amd64                                 Micro string library: shared library
    ii  libutempter0:amd64                                                1.1.6-3                               amd64                                 privileged helper for utmp/wtmp updates (runtime)
    ii  libuuid1:amd64                                                    2.27.1-6ubuntu3.1                     amd64                                 Universally Unique ID library
    ii  libvorbis0a:amd64                                                 1.3.5-3                               amd64                                 decoder library for Vorbis General Audio Compression Codec
    ii  libvorbisenc2:amd64                                               1.3.5-3                               amd64                                 encoder library for Vorbis General Audio Compression Codec
    ii  libwind0-heimdal:amd64                                            1.7~git20150920+dfsg-4ubuntu1         amd64                                 Heimdal Kerberos - stringprep implementation
    ii  libwrap0:amd64                                                    7.6.q-25                              amd64                                 Wietse Venema's TCP wrappers library
    ii  libx11-6:amd64                                                    2:1.6.3-1ubuntu2                      amd64                                 X11 client-side library
    ii  libx11-data                                                       2:1.6.3-1ubuntu2                      all                                   X11 client-side library
    ii  libx11-xcb1:amd64                                                 2:1.6.3-1ubuntu2                      amd64                                 Xlib/XCB interface library
    ii  libxau6:amd64                                                     1:1.0.8-1                             amd64                                 X11 authorisation library
    ii  libxaw7:amd64                                                     2:1.0.13-1                            amd64                                 X11 Athena Widget library
    ii  libxcb-dri2-0:amd64                                               1.11.1-1ubuntu1                       amd64                                 X C Binding, dri2 extension
    ii  libxcb-dri3-0:amd64                                               1.11.1-1ubuntu1                       amd64                                 X C Binding, dri3 extension
    ii  libxcb-glx0:amd64                                                 1.11.1-1ubuntu1                       amd64                                 X C Binding, glx extension
    ii  libxcb-present0:amd64                                             1.11.1-1ubuntu1                       amd64                                 X C Binding, present extension
    ii  libxcb-shape0:amd64                                               1.11.1-1ubuntu1                       amd64                                 X C Binding, shape extension
    ii  libxcb-sync1:amd64                                                1.11.1-1ubuntu1                       amd64                                 X C Binding, sync extension
    ii  libxcb1:amd64                                                     1.11.1-1ubuntu1                       amd64                                 X C Binding
    ii  libxcomposite1:amd64                                              1:0.4.4-1                             amd64                                 X11 Composite extension library
    ii  libxdamage1:amd64                                                 1:1.1.4-2                             amd64                                 X11 damaged region extension library
    ii  libxdmcp6:amd64                                                   1:1.1.2-1.1                           amd64                                 X11 Display Manager Control Protocol library
    ii  libxen-4.6:amd64                                                  4.6.0-1ubuntu4.2                      amd64                                 Public libs for Xen
    ii  libxenstore3.0:amd64                                              4.6.0-1ubuntu4.2                      amd64                                 Xenstore communications library for Xen
    ii  libxext6:amd64                                                    2:1.3.3-1                             amd64                                 X11 miscellaneous extension library
    ii  libxfixes3:amd64                                                  1:5.0.1-2                             amd64                                 X11 miscellaneous 'fixes' extension library
    ii  libxft2:amd64                                                     2.3.2-1                               amd64                                 FreeType-based font drawing library for X
    ii  libxi6:amd64                                                      2:1.7.6-1                             amd64                                 X11 Input extension library
    ii  libxinerama1:amd64                                                2:1.1.3-1                             amd64                                 X11 Xinerama extension library
    ii  libxml2:amd64                                                     2.9.3+dfsg1-1ubuntu0.1                amd64                                 GNOME XML library
    ii  libxmu6:amd64                                                     2:1.1.2-2                             amd64                                 X11 miscellaneous utility library
    ii  libxmuu1:amd64                                                    2:1.1.2-2                             amd64                                 X11 miscellaneous micro-utility library
    ii  libxpm4:amd64                                                     1:3.5.11-1                            amd64                                 X11 pixmap library
    ii  libxrandr2:amd64                                                  2:1.5.0-1                             amd64                                 X11 RandR extension library
    ii  libxrender1:amd64                                                 1:0.9.9-0ubuntu1                      amd64                                 X Rendering Extension client library
    ii  libxshmfence1:amd64                                               1.2-1                                 amd64                                 X shared memory fences - shared library
    ii  libxss1:amd64                                                     1:1.2.2-1                             amd64                                 X11 Screen Saver extension library
    ii  libxt6:amd64                                                      1:1.1.5-0ubuntu1                      amd64                                 X11 toolkit intrinsics library
    ii  libxtables11:amd64                                                1.6.0-2ubuntu3                        amd64                                 netfilter xtables library
    ii  libxtst6:amd64                                                    2:1.2.2-1                             amd64                                 X11 Testing -- Record extension library
    ii  libxv1:amd64                                                      2:1.0.10-1                            amd64                                 X11 Video extension library
    ii  libxxf86dga1:amd64                                                2:1.1.4-1                             amd64                                 X11 Direct Graphics Access extension library
    ii  libxxf86vm1:amd64                                                 1:1.1.4-1                             amd64                                 X11 XFree86 video mode extension library
    ii  libyajl2:amd64                                                    2.1.0-2                               amd64                                 Yet Another JSON Library
    ii  linux-base                                                        4.0ubuntu1                            all                                   Linux image base package
    ii  linux-firmware                                                    1.157.2                               all                                   Firmware for Linux kernel drivers
    ii  linux-generic                                                     4.4.0.72.78                           amd64                                 Complete Generic Linux kernel and headers
    ii  linux-headers-4.4.0-72                                            4.4.0-72.93                           all                                   Header files related to Linux kernel version 4.4.0
    ii  linux-headers-4.4.0-72-generic                                    4.4.0-72.93                           amd64                                 Linux kernel headers for version 4.4.0 on 64 bit x86 SMP
    ii  linux-headers-generic                                             4.4.0.72.78                           amd64                                 Generic Linux kernel headers
    ii  linux-image-4.4.0-72-generic                                      4.4.0-72.93                           amd64                                 Linux kernel image for version 4.4.0 on 64 bit x86 SMP
    ii  linux-image-extra-4.4.0-72-generic                                4.4.0-72.93                           amd64                                 Linux kernel extra modules for version 4.4.0 on 64 bit x86 SMP
    ii  linux-image-generic                                               4.4.0.72.78                           amd64                                 Generic Linux kernel image
    ii  linux-libc-dev:amd64                                              4.4.0-72.93                           amd64                                 Linux Kernel Headers for development
    ii  locales                                                           2.23-0ubuntu3                         all                                   GNU C Library: National Language (locale) data [support]
    ii  login                                                             1:4.2-3.1ubuntu5                      amd64                                 system login tools
    ii  logrotate                                                         3.8.7-2ubuntu2                        amd64                                 Log rotation utility
    ii  lsb-base                                                          9.20160110ubuntu0.2                   all                                   Linux Standard Base init script functionality
    ii  lsb-release                                                       9.20160110ubuntu0.2                   all                                   Linux Standard Base version reporting utility
    ii  lxc                                                               2.0.7-0ubuntu1~16.04.2                all                                   Transitional package for lxc1
    ii  lxc-common                                                        2.0.7-0ubuntu1~16.04.2                amd64                                 Linux Containers userspace tools (common tools)
    ii  lxc-templates                                                     2.0.7-0ubuntu1~16.04.2                amd64                                 Linux Containers userspace tools (templates)
    ii  lxc1                                                              2.0.7-0ubuntu1~16.04.2                amd64                                 Linux Containers userspace tools
    ii  lxcfs                                                             2.0.6-0ubuntu1~16.04.1                amd64                                 FUSE based filesystem for LXC
    ii  m4                                                                1.4.17-5                              amd64                                 macro processing language
    ii  make                                                              4.1-6                                 amd64                                 utility for directing compilation
    ii  makedev                                                           2.3.1-93ubuntu1                       all                                   creates device files in /dev
    ii  manpages                                                          4.04-2                                all                                   Manual pages about using a GNU/Linux system
    ii  manpages-dev                                                      4.04-2                                all                                   Manual pages about using GNU/Linux for development
    ii  mawk                                                              1.3.3-17ubuntu2                       amd64                                 a pattern scanning and text processing language
    ii  mime-support                                                      3.59ubuntu1                           all                                   MIME files 'mime.types' & 'mailcap', and support programs
    ii  mount                                                             2.27.1-6ubuntu3.1                     amd64                                 tools for mounting and manipulating filesystems
    ii  mountall                                                          2.54ubuntu1                           amd64                                 filesystem mounting tool
    ii  msr-tools                                                         1.3-2                                 amd64                                 Utilities for modifying MSRs from userspace
    ii  multiarch-support                                                 2.23-0ubuntu3                         amd64                                 Transitional package to ensure multiarch compatibility
    ii  ncurses-base                                                      6.0+20160213-1ubuntu1                 all                                   basic terminal type definitions
    ii  ncurses-bin                                                       6.0+20160213-1ubuntu1                 amd64                                 terminal-related programs and man pages
    ii  ncurses-term                                                      6.0+20160213-1ubuntu1                 all                                   additional terminal type definitions
    ii  net-tools                                                         1.60-26ubuntu1                        amd64                                 NET-3 networking toolkit
    ii  netbase                                                           5.3                                   all                                   Basic TCP/IP networking system
    ii  netcat-openbsd                                                    1.105-7ubuntu1                        amd64                                 TCP/IP swiss army knife
    ii  openjdk-8-jre-headless:amd64                                      8u131-b11-0ubuntu1.16.04.2            amd64                                 OpenJDK Java runtime, using Hotspot JIT (headless)
    ii  openssh-client                                                    1:7.2p2-4ubuntu2.1                    amd64                                 secure shell (SSH) client, for secure access to remote machines
    ii  openssh-server                                                    1:7.2p2-4ubuntu2.1                    amd64                                 secure shell (SSH) server, for secure access from remote machines
    ii  openssh-sftp-server                                               1:7.2p2-4ubuntu2.1                    amd64                                 secure shell (SSH) sftp server module, for SFTP access from remote machines
    ii  openssl                                                           1.0.2g-1ubuntu4.5                     amd64                                 Secure Sockets Layer toolkit - cryptographic utility
    ii  os-prober                                                         1.70ubuntu3                           amd64                                 utility to detect other OSes on a set of drives
    ii  passwd                                                            1:4.2-3.1ubuntu5                      amd64                                 change and administer password and group data
    ii  patch                                                             2.7.5-1                               amd64                                 Apply a diff file to an original
    ii  pciutils                                                          1:3.3.1-1.1ubuntu1                    amd64                                 Linux PCI Utilities
    ii  perl                                                              5.22.1-9                              amd64                                 Larry Wall's Practical Extraction and Report Language
    ii  perl-base                                                         5.22.1-9                              amd64                                 minimal Perl system
    ii  perl-modules-5.22                                                 5.22.1-9                              all                                   Core Perl modules
    ii  pkg-config                                                        0.29.1-0ubuntu1                       amd64                                 manage compile and link flags for libraries
    ii  plymouth                                                          0.9.2-3ubuntu13.1                     amd64                                 boot animation, logger and I/O multiplexer
    ii  plymouth-theme-ubuntu-text                                        0.9.2-3ubuntu13.1                     amd64                                 boot animation, logger and I/O multiplexer - ubuntu text theme
    ii  procps                                                            2:3.3.10-4ubuntu2                     amd64                                 /proc file system utilities
    ii  python                                                            2.7.11-1                              amd64                                 interactive high-level object-oriented language (default version)
    ii  python-all                                                        2.7.11-1                              amd64                                 package depending on all supported Python runtime versions
    ii  python-all-dev                                                    2.7.11-1                              amd64                                 package depending on all supported Python development packages
    ii  python-apt                                                        1.1.0~beta1build1                     amd64                                 Python interface to libapt-pkg
    ii  python-apt-common                                                 1.1.0~beta1build1                     all                                   Python interface to libapt-pkg (locales)
    ii  python-dev                                                        2.7.11-1                              amd64                                 header files and a static library for Python (default)
    ii  python-iniparse                                                   0.4-2.2                               all                                   access and modify configuration data in INI files (Python 2)
    ii  python-minimal                                                    2.7.11-1                              amd64                                 minimal subset of the Python language (default version)
    ii  python-pip                                                        8.1.1-2ubuntu0.2                      all                                   alternative Python package installer
    ii  python-pip-whl                                                    8.1.1-2ubuntu0.2                      all                                   alternative Python package installer
    ii  python-pkg-resources                                              20.7.0-1                              all                                   Package Discovery and Resource Access using pkg_resources
    ii  python-setuptools                                                 20.7.0-1                              all                                   Python Distutils Enhancements
    ii  python-six                                                        1.10.0-3                              all                                   Python 2 and 3 compatibility library (Python 2 interface)
    ii  python-virtualenv                                                 15.0.1+ds-3                           all                                   Python virtual environment creator
    ii  python-wheel                                                      0.29.0-1                              all                                   built-package format for Python
    ii  python2.7                                                         2.7.12-1~16.04                        amd64                                 Interactive high-level object-oriented language (version 2.7)
    ii  python2.7-dev                                                     2.7.12-1~16.04                        amd64                                 Header files and a static library for Python (v2.7)
    ii  python2.7-minimal                                                 2.7.12-1~16.04                        amd64                                 Minimal subset of the Python language (version 2.7)
    ii  python3                                                           3.5.1-3                               amd64                                 interactive high-level object-oriented language (default python3 version)
    ii  python3-apt                                                       1.1.0~beta1build1                     amd64                                 Python 3 interface to libapt-pkg
    ii  python3-chardet                                                   2.3.0-2                               all                                   universal character encoding detector for Python3
    ii  python3-dbus                                                      1.2.0-3                               amd64                                 simple interprocess messaging system (Python 3 interface)
    ii  python3-gi                                                        3.20.0-0ubuntu1                       amd64                                 Python 3 bindings for gobject-introspection libraries
    ii  python3-lxc                                                       2.0.7-0ubuntu1~16.04.2                amd64                                 Linux Containers userspace tools (Python 3.x bindings)
    ii  python3-minimal                                                   3.5.1-3                               amd64                                 minimal subset of the Python language (default python3 version)
    ii  python3-pkg-resources                                             20.7.0-1                              all                                   Package Discovery and Resource Access using pkg_resources
    ii  python3-requests                                                  2.9.1-3                               all                                   elegant and simple HTTP library for Python3, built for human beings
    ii  python3-six                                                       1.10.0-3                              all                                   Python 2 and 3 compatibility library (Python 3 interface)
    ii  python3-urllib3                                                   1.13.1-2ubuntu0.16.04.1               all                                   HTTP library with thread-safe connection pooling for Python3
    ii  python3-virtualenv                                                15.0.1+ds-3                           all                                   Python virtual environment creator
    ii  python3.5                                                         3.5.2-2~16.01                         amd64                                 Interactive high-level object-oriented language (version 3.5)
    ii  python3.5-minimal                                                 3.5.2-2~16.01                         amd64                                 Minimal subset of the Python language (version 3.5)
    ii  qemu-block-extra:amd64                                            1:2.5+dfsg-5ubuntu10.5                amd64                                 extra block backend modules for qemu-system and qemu-utils
    ii  qemu-system-common                                                1:2.5+dfsg-5ubuntu10.5                amd64                                 QEMU full system emulation binaries (common files)
    ii  qemu-system-x86                                                   1:2.5+dfsg-5ubuntu10.5                amd64                                 QEMU full system emulation binaries (x86)
    ii  qemu-utils                                                        1:2.5+dfsg-5ubuntu10.5                amd64                                 QEMU utilities
    ii  readline-common                                                   6.3-8ubuntu2                          all                                   GNU readline and history libraries, common files
    ii  rename                                                            0.20-4                                all                                   Perl extension for renaming multiple files
    ii  resolvconf                                                        1.78ubuntu2                           all                                   name server information handler
    ii  rsync                                                             3.1.1-3ubuntu1                        amd64                                 fast, versatile, remote (and local) file-copying tool
    ii  rsyslog                                                           8.16.0-1ubuntu3                       amd64                                 reliable system and kernel logging daemon
    ii  screen                                                            4.3.1-2build1                         amd64                                 terminal multiplexer with VT100/ANSI terminal emulation
    ii  seabios                                                           1.8.2-1ubuntu1                        all                                   Legacy BIOS implementation
    ii  sed                                                               4.2.2-7                               amd64                                 The GNU sed stream editor
    ii  sensible-utils                                                    0.0.9                                 all                                   Utilities for sensible alternative selection
    ii  sgml-base                                                         1.26+nmu4ubuntu1                      all                                   SGML infrastructure and SGML catalog file support
    ii  shared-mime-info                                                  1.5-2ubuntu0.1                        amd64                                 FreeDesktop.org shared MIME database and spec
    ii  sharutils                                                         1:4.15.2-1                            amd64                                 shar, unshar, uuencode, uudecode
    ii  socat                                                             1.7.3.1-1                             amd64                                 multipurpose relay for bidirectional data transfer
    ii  ssh-import-id                                                     5.5-0ubuntu1                          all                                   securely retrieve an SSH public key and install it locally
    ii  sudo                                                              1.8.16-0ubuntu1.1                     amd64                                 Provide limited super user privileges to specific users
    ii  systemd                                                           229-4ubuntu10                         amd64                                 system and service manager
    ii  systemd-sysv                                                      229-4ubuntu10                         amd64                                 system and service manager - SysV links
    ii  sysv-rc                                                           2.88dsf-59.3ubuntu2                   all                                   System-V-like runlevel change mechanism
    ii  sysvinit-utils                                                    2.88dsf-59.3ubuntu2                   amd64                                 System-V-like utilities
    ii  tar                                                               1.28-2.1                              amd64                                 GNU version of the tar archiving utility
    ii  tasksel                                                           3.34ubuntu3                           all                                   tool for selecting tasks for installation on Debian systems
    ii  tasksel-data                                                      3.34ubuntu3                           all                                   official tasks used for installation of Debian systems
    ii  tcl-expect:amd64                                                  5.45-7                                amd64                                 Automates interactive applications (Tcl package)
    ii  tcl8.6                                                            8.6.5+dfsg-2                          amd64                                 Tcl (the Tool Command Language) v8.6 - shell
    ii  tcpd                                                              7.6.q-25                              amd64                                 Wietse Venema's TCP wrapper utilities
    ii  tk8.6                                                             8.6.5-1                               amd64                                 Tk toolkit for Tcl and X11 v8.6 - windowing shell
    ii  tzdata                                                            2016g-0ubuntu0.16.04                  all                                   time zone and daylight-saving time data
    ii  ubuntu-keyring                                                    2012.05.19                            all                                   GnuPG keys of the Ubuntu archive
    ii  ubuntu-minimal                                                    1.361                                 amd64                                 Minimal core of Ubuntu
    ii  ucf                                                               3.0036                                all                                   Update Configuration File(s): preserve user changes to config files
    ii  udev                                                              229-4ubuntu10                         amd64                                 /dev/ and hotplug management daemon
    ii  uidmap                                                            1:4.2-3.1ubuntu5.3                    amd64                                 programs to help use subuids
    ii  ureadahead                                                        0.100.0-19                            amd64                                 Read required files in advance
    ii  usbutils                                                          1:007-4                               amd64                                 Linux USB utilities
    ii  util-linux                                                        2.27.1-6ubuntu3.1                     amd64                                 miscellaneous system utilities
    ii  uuid-runtime                                                      2.27.1-6ubuntu3.2                     amd64                                 runtime components for the Universally Unique ID library
    ii  vim-common                                                        2:7.4.1689-3ubuntu1.1                 amd64                                 Vi IMproved - Common files
    ii  vim-tiny                                                          2:7.4.1689-3ubuntu1.1                 amd64                                 Vi IMproved - enhanced vi editor - compact version
    ii  virtualenv                                                        15.0.1+ds-3                           all                                   Python virtual environment creator
    ii  wamerican                                                         7.1-1                                 all                                   American English dictionary words for /usr/share/dict
    ii  wget                                                              1.17.1-1ubuntu1.1                     amd64                                 retrieves files from the web
    ii  whiptail                                                          0.52.18-1ubuntu2                      amd64                                 Displays user-friendly dialog boxes from shell scripts
    ii  wireless-regdb                                                    2015.07.20-1ubuntu1                   all                                   wireless regulatory database
    ii  x11-common                                                        1:7.7+13ubuntu3                       all                                   X Window System (X.Org) infrastructure
    ii  x11-utils                                                         7.7+3                                 amd64                                 X11 utilities
    ii  xauth                                                             1:1.0.9-1ubuntu2                      amd64                                 X authentication utility
    ii  xbitmaps                                                          1.1.1-2                               all                                   Base X bitmaps
    ii  xdg-user-dirs                                                     0.15-2ubuntu6                         amd64                                 tool to manage well known user directories
    ii  xkb-data                                                          2.16-1ubuntu1                         all                                   X Keyboard Extension (XKB) configuration data
    ii  xml-core                                                          0.13+nmu2                             all                                   XML infrastructure and XML catalog file support
    ii  xterm                                                             322-1ubuntu1                          amd64                                 X terminal emulator
    ii  xz-utils                                                          5.1.1alpha+20120614-2ubuntu2          amd64                                 XZ-format compression utilities
    ii  zlib1g:amd64                                                      1:1.2.8.dfsg-2ubuntu4                 amd64                                 compression library - runtime
    ii  zlib1g-dev:amd64                                                  1:1.2.8.dfsg-2ubuntu4                 amd64                                 compression library - development

**Kernel module listing**

::

    $ lsmod | sort
    8250_fintek            16384  0
    ablk_helper            16384  1 aesni_intel
    acpi_pad               24576  0
    acpi_power_meter       20480  0
    aesni_intel           167936  0
    aes_x86_64             20480  1 aesni_intel
    ahci                   36864  0
    authenc                16384  1 intel_qat
    autofs4                40960  2
    bridge                126976  0
    coretemp               16384  0
    crc32_pclmul           16384  0
    crct10dif_pclmul       16384  0
    cryptd                 20480  3 ghash_clmulni_intel,aesni_intel,ablk_helper
    dca                    16384  2 igb,ixgbe
    edac_core              53248  1 sb_edac
    enclosure              16384  1 ses
    enic                   81920  0
    fjes                   28672  0
    fnic                  106496  0
    gf128mul               16384  1 lrw
    ghash_clmulni_intel    16384  0
    glue_helper            16384  1 aesni_intel
    hid                   118784  2 hid_generic,usbhid
    hid_generic            16384  0
    i2c_algo_bit           16384  1 igb
    i40e                  286720  0
    igb                   196608  0
    igb_uio                16384  0
    input_leds             16384  0
    intel_powerclamp       16384  0
    intel_qat             110592  2 qat_dh895xccvf,qat_dh895xcc
    intel_rapl             20480  0
    ip6_udp_tunnel         16384  1 vxlan
    ipmi_msghandler        49152  2 ipmi_ssif,ipmi_si
    ipmi_si                57344  0
    ipmi_ssif              24576  0
    iptable_filter         16384  1
    iptable_mangle         16384  1
    iptable_nat            16384  1
    ip_tables              24576  3 iptable_filter,iptable_mangle,iptable_nat
    ipt_MASQUERADE         16384  1
    irqbypass              16384  1 kvm
    ixgbe                 290816  0
    joydev                 20480  0
    kvm                   544768  1 kvm_intel
    kvm_intel             172032  0
    libahci                32768  1 ahci
    libfc                 114688  2 fnic,libfcoe
    libfcoe                65536  1 fnic
    llc                    16384  2 stp,bridge
    lpc_ich                24576  0
    lrw                    16384  1 aesni_intel
    mac_hid                16384  0
    mdio                   16384  1 ixgbe
    megaraid_sas          135168  3
    mei                    98304  1 mei_me
    mei_me                 36864  0
    Module                  Size  Used by
    nf_conntrack          106496  4 nf_nat,nf_nat_ipv4,nf_nat_masquerade_ipv4,nf_conntrack_ipv4
    nf_conntrack_ipv4      16384  1
    nf_defrag_ipv4         16384  1 nf_conntrack_ipv4
    nf_nat                 24576  2 nf_nat_ipv4,nf_nat_masquerade_ipv4
    nf_nat_ipv4            16384  1 iptable_nat
    nf_nat_masquerade_ipv4    16384  1 ipt_MASQUERADE
    pps_core               20480  1 ptp
    ptp                    20480  3 igb,i40e,ixgbe
    qat_dh895xcc           20480  0
    qat_dh895xccvf         20480  0
    sb_edac                32768  0
    scsi_transport_fc      61440  2 fnic,libfc
    ses                    20480  0
    shpchp                 36864  0
    stp                    16384  1 bridge
    udp_tunnel             16384  1 vxlan
    uio                    20480  2 uio_pci_generic,igb_uio
    uio_pci_generic        16384  0
    usbhid                 49152  0
    veth                   16384  0
    vxlan                  49152  2 i40e,ixgbe
    wmi                    20480  0
    x86_pkg_temp_thermal    16384  0
    x_tables               36864  6 xt_CHECKSUM,ip_tables,xt_tcpudp,ipt_MASQUERADE,iptable_filter,iptable_mangle
    xt_CHECKSUM            16384  1
    xt_tcpudp              16384  5

**Sysctl listing**

::

    $ sysctl -a
    abi.vsyscall32 = 1
    debug.exception-trace = 1
    debug.kprobes-optimization = 1
    dev.cdrom.autoclose = 1
    dev.cdrom.autoeject = 0
    dev.cdrom.check_media = 0
    dev.cdrom.debug = 0
    dev.cdrom.info = CD-ROM information, Id: cdrom.c 3.20 2003/12/17
    dev.cdrom.info =
    dev.cdrom.info = drive name:
    dev.cdrom.info = drive speed:
    dev.cdrom.info = drive # of slots:
    dev.cdrom.info = Can close tray:
    dev.cdrom.info = Can open tray:
    dev.cdrom.info = Can lock tray:
    dev.cdrom.info = Can change speed:
    dev.cdrom.info = Can select disk:
    dev.cdrom.info = Can read multisession:
    dev.cdrom.info = Can read MCN:
    dev.cdrom.info = Reports media changed:
    dev.cdrom.info = Can play audio:
    dev.cdrom.info = Can write CD-R:
    dev.cdrom.info = Can write CD-RW:
    dev.cdrom.info = Can read DVD:
    dev.cdrom.info = Can write DVD-R:
    dev.cdrom.info = Can write DVD-RAM:
    dev.cdrom.info = Can read MRW:
    dev.cdrom.info = Can write MRW:
    dev.cdrom.info = Can write RAM:
    dev.cdrom.info =
    dev.cdrom.info =
    dev.cdrom.lock = 0
    dev.hpet.max-user-freq = 64
    dev.mac_hid.mouse_button2_keycode = 97
    dev.mac_hid.mouse_button3_keycode = 100
    dev.mac_hid.mouse_button_emulation = 0
    dev.raid.speed_limit_max = 200000
    dev.raid.speed_limit_min = 1000
    dev.scsi.logging_level = 0
    fs.aio-max-nr = 65536
    fs.aio-nr = 0
    fs.binfmt_misc.status = enabled
    fs.dentry-state = 69970	58326	45	0	0	0
    fs.dir-notify-enable = 1
    fs.epoll.max_user_watches = 108185784
    fs.file-max = 52706330
    fs.file-nr = 1224	0	52706330
    fs.inode-nr = 42965	369
    fs.inode-state = 42965	369	0	0	0	0	0
    fs.inotify.max_queued_events = 16384
    fs.inotify.max_user_instances = 128
    fs.inotify.max_user_watches = 8192
    fs.lease-break-time = 45
    fs.leases-enable = 1
    fs.mount-max = 100000
    fs.mqueue.msg_default = 10
    fs.mqueue.msg_max = 10
    fs.mqueue.msgsize_default = 8192
    fs.mqueue.msgsize_max = 8192
    fs.mqueue.queues_max = 256
    fs.nr_open = 1048576
    fs.overflowgid = 65534
    fs.overflowuid = 65534
    fs.pipe-max-size = 1048576
    fs.pipe-user-pages-hard = 0
    fs.pipe-user-pages-soft = 16384
    fs.protected_hardlinks = 1
    fs.protected_symlinks = 1
    fs.quota.allocated_dquots = 0
    fs.quota.cache_hits = 0
    fs.quota.drops = 0
    fs.quota.free_dquots = 0
    fs.quota.lookups = 0
    fs.quota.reads = 0
    fs.quota.syncs = 0
    fs.quota.writes = 0
    fs.suid_dumpable = 0
    kernel.acct = 4	2	30
    kernel.acpi_video_flags = 0
    kernel.auto_msgmni = 0
    kernel.bootloader_type = 114
    kernel.bootloader_version = 2
    kernel.cad_pid = 1
    kernel.cap_last_cap = 37
    kernel.compat-log = 1
    kernel.core_pattern = core
    kernel.core_pipe_limit = 0
    kernel.core_uses_pid = 0
    kernel.ctrl-alt-del = 0
    kernel.dmesg_restrict = 0
    kernel.domainname = (none)
    kernel.ftrace_dump_on_oops = 0
    kernel.ftrace_enabled = 1
    kernel.hardlockup_all_cpu_backtrace = 0
    kernel.hardlockup_panic = 0
    kernel.hostname = t2-sut1
    kernel.hotplug =
    kernel.hung_task_check_count = 4194304
    kernel.hung_task_panic = 0
    kernel.hung_task_timeout_secs = 120
    kernel.hung_task_warnings = 10
    kernel.io_delay_type = 1
    kernel.kexec_load_disabled = 0
    kernel.keys.gc_delay = 300
    kernel.keys.maxbytes = 20000
    kernel.keys.maxkeys = 200
    kernel.keys.persistent_keyring_expiry = 259200
    kernel.keys.root_maxbytes = 25000000
    kernel.keys.root_maxkeys = 1000000
    kernel.kptr_restrict = 1
    kernel.kstack_depth_to_print = 12
    kernel.max_lock_depth = 1024
    kernel.modprobe = /sbin/modprobe
    kernel.modules_disabled = 0
    kernel.moksbstate_disabled = 0
    kernel.msg_next_id = -1
    kernel.msgmax = 8192
    kernel.msgmnb = 16384
    kernel.msgmni = 32000
    kernel.ngroups_max = 65536
    kernel.nmi_watchdog = 1
    kernel.ns_last_pid = 11764
    kernel.numa_balancing = 1
    kernel.numa_balancing_scan_delay_ms = 1000
    kernel.numa_balancing_scan_period_max_ms = 60000
    kernel.numa_balancing_scan_period_min_ms = 1000
    kernel.numa_balancing_scan_size_mb = 256
    kernel.osrelease = 4.4.0-72-generic
    kernel.ostype = Linux
    kernel.overflowgid = 65534
    kernel.overflowuid = 65534
    kernel.panic = 0
    kernel.panic_on_io_nmi = 0
    kernel.panic_on_oops = 0
    kernel.panic_on_unrecovered_nmi = 0
    kernel.panic_on_warn = 0
    kernel.perf_cpu_time_max_percent = 25
    kernel.perf_event_max_sample_rate = 12500
    kernel.perf_event_mlock_kb = 516
    kernel.perf_event_paranoid = 1
    kernel.pid_max = 36864
    kernel.poweroff_cmd = /sbin/poweroff
    kernel.print-fatal-signals = 0
    kernel.printk = 4	4	1	7
    kernel.printk_delay = 0
    kernel.printk_ratelimit = 5
    kernel.printk_ratelimit_burst = 10
    kernel.pty.max = 4096
    kernel.pty.nr = 1
    kernel.pty.reserve = 1024
    kernel.random.boot_id = f683c836-6fc6-492a-a23b-62ab21895040
    kernel.random.entropy_avail = 200
    kernel.random.poolsize = 4096
    kernel.random.read_wakeup_threshold = 64
    kernel.random.urandom_min_reseed_secs = 60
    kernel.random.uuid = 144ff2ba-1bc7-4836-8fb7-6aaa0ab7e65f
    kernel.random.write_wakeup_threshold = 896
    kernel.randomize_va_space = 0
    kernel.real-root-dev = 0
    kernel.sched_autogroup_enabled = 1
    kernel.sched_cfs_bandwidth_slice_us = 5000
    kernel.sched_child_runs_first = 0
    kernel.sched_domain.cpu0.domain0.busy_factor = 32
    kernel.sched_domain.cpu0.domain0.busy_idx = 3
    kernel.sched_domain.cpu0.domain0.cache_nice_tries = 2
    kernel.sched_domain.cpu0.domain0.flags = 25647
    kernel.sched_domain.cpu0.domain0.forkexec_idx = 0
    kernel.sched_domain.cpu0.domain0.idle_idx = 2
    kernel.sched_domain.cpu0.domain0.imbalance_pct = 125
    kernel.sched_domain.cpu0.domain0.max_interval = 72
    kernel.sched_domain.cpu0.domain0.max_newidle_lb_cost = 1309
    kernel.sched_domain.cpu0.domain0.min_interval = 36
    kernel.sched_domain.cpu0.domain0.name = NUMA
    kernel.sched_domain.cpu0.domain0.newidle_idx = 0
    kernel.sched_domain.cpu0.domain0.wake_idx = 0
    kernel.sched_domain.cpu18.domain0.busy_factor = 32
    kernel.sched_domain.cpu18.domain0.busy_idx = 3
    kernel.sched_domain.cpu18.domain0.cache_nice_tries = 2
    kernel.sched_domain.cpu18.domain0.flags = 25647
    kernel.sched_domain.cpu18.domain0.forkexec_idx = 0
    kernel.sched_domain.cpu18.domain0.idle_idx = 2
    kernel.sched_domain.cpu18.domain0.imbalance_pct = 125
    kernel.sched_domain.cpu18.domain0.max_interval = 72
    kernel.sched_domain.cpu18.domain0.max_newidle_lb_cost = 2026
    kernel.sched_domain.cpu18.domain0.min_interval = 36
    kernel.sched_domain.cpu18.domain0.name = NUMA
    kernel.sched_domain.cpu18.domain0.newidle_idx = 0
    kernel.sched_domain.cpu18.domain0.wake_idx = 0
    kernel.sched_latency_ns = 24000000
    kernel.sched_migration_cost_ns = 500000
    kernel.sched_min_granularity_ns = 3000000
    kernel.sched_nr_migrate = 32
    kernel.sched_rr_timeslice_ms = 25
    kernel.sched_rt_period_us = 1000000
    kernel.sched_rt_runtime_us = 950000
    kernel.sched_shares_window_ns = 10000000
    kernel.sched_time_avg_ms = 1000
    kernel.sched_tunable_scaling = 1
    kernel.sched_wakeup_granularity_ns = 4000000
    kernel.secure_boot = 0
    kernel.sem = 32000	1024000000	500	32000
    kernel.sem_next_id = -1
    kernel.sg-big-buff = 32768
    kernel.shm_next_id = -1
    kernel.shm_rmid_forced = 0
    kernel.shmall = 18446744073692774399
    kernel.shmmax = 8589934592
    kernel.shmmni = 4096
    kernel.soft_watchdog = 1
    kernel.softlockup_all_cpu_backtrace = 0
    kernel.softlockup_panic = 0
    kernel.stack_tracer_enabled = 0
    kernel.sysctl_writes_strict = 0
    kernel.sysrq = 176
    kernel.tainted = 12288
    kernel.threads-max = 4126960
    kernel.timer_migration = 1
    kernel.traceoff_on_warning = 0
    kernel.tracepoint_printk = 0
    kernel.unknown_nmi_panic = 0
    kernel.unprivileged_bpf_disabled = 0
    kernel.unprivileged_userns_apparmor_policy = 1
    kernel.unprivileged_userns_clone = 1
    kernel.usermodehelper.bset = 4294967295	63
    kernel.usermodehelper.inheritable = 4294967295	63
    kernel.version = #93-Ubuntu SMP Fri Mar 31 14:07:41 UTC 2017
    kernel.watchdog = 1
    kernel.watchdog_cpumask = 0,18
    kernel.watchdog_thresh = 10
    kernel.yama.ptrace_scope = 1
    net.core.bpf_jit_enable = 0
    net.core.busy_poll = 0
    net.core.busy_read = 0
    net.core.default_qdisc = pfifo_fast
    net.core.dev_weight = 64
    net.core.flow_limit_cpu_bitmap = 0,00000000
    net.core.flow_limit_table_len = 4096
    net.core.max_skb_frags = 17
    net.core.message_burst = 10
    net.core.message_cost = 5
    net.core.netdev_budget = 300
    net.core.netdev_max_backlog = 1000
    net.core.netdev_rss_key = 29:61:61:e6:4e:d5:d0:a2:dc:81:6a:c8:44:1b:e2:8d:c8:6f:6a:2b:64:62:98:08:bb:63:48:8e:96:d1:6a:15:32:ca:da:8d:3c:0a:ee:a6:f8:59:be:63:33:47:e9:cf:d7:01:e3:18
    net.core.netdev_tstamp_prequeue = 1
    net.core.optmem_max = 20480
    net.core.rmem_default = 212992
    net.core.rmem_max = 212992
    net.core.rps_sock_flow_entries = 0
    net.core.somaxconn = 128
    net.core.tstamp_allow_data = 1
    net.core.warnings = 0
    net.core.wmem_default = 212992
    net.core.wmem_max = 212992
    net.core.xfrm_acq_expires = 30
    net.core.xfrm_aevent_etime = 10
    net.core.xfrm_aevent_rseqth = 2
    net.core.xfrm_larval_drop = 1
    net.fan.vxlan = 4
    net.ipv4.cipso_cache_bucket_size = 10
    net.ipv4.cipso_cache_enable = 1
    net.ipv4.cipso_rbm_optfmt = 0
    net.ipv4.cipso_rbm_strictvalid = 1
    net.ipv4.conf.all.accept_local = 0
    net.ipv4.conf.all.accept_redirects = 0
    net.ipv4.conf.all.accept_source_route = 0
    net.ipv4.conf.all.arp_accept = 0
    net.ipv4.conf.all.arp_announce = 0
    net.ipv4.conf.all.arp_filter = 0
    net.ipv4.conf.all.arp_ignore = 0
    net.ipv4.conf.all.arp_notify = 0
    net.ipv4.conf.all.bootp_relay = 0
    net.ipv4.conf.all.disable_policy = 0
    net.ipv4.conf.all.disable_xfrm = 0
    net.ipv4.conf.all.force_igmp_version = 0
    net.ipv4.conf.all.forwarding = 1
    net.ipv4.conf.all.igmpv2_unsolicited_report_interval = 10000
    net.ipv4.conf.all.igmpv3_unsolicited_report_interval = 1000
    net.ipv4.conf.all.ignore_routes_with_linkdown = 0
    net.ipv4.conf.all.log_martians = 0
    net.ipv4.conf.all.mc_forwarding = 0
    net.ipv4.conf.all.medium_id = 0
    net.ipv4.conf.all.promote_secondaries = 0
    net.ipv4.conf.all.proxy_arp = 0
    net.ipv4.conf.all.proxy_arp_pvlan = 0
    net.ipv4.conf.all.route_localnet = 0
    net.ipv4.conf.all.rp_filter = 1
    net.ipv4.conf.all.secure_redirects = 1
    net.ipv4.conf.all.send_redirects = 1
    net.ipv4.conf.all.shared_media = 1
    net.ipv4.conf.all.src_valid_mark = 0
    net.ipv4.conf.all.tag = 0
    net.ipv4.conf.default.accept_local = 0
    net.ipv4.conf.default.accept_redirects = 1
    net.ipv4.conf.default.accept_source_route = 1
    net.ipv4.conf.default.arp_accept = 0
    net.ipv4.conf.default.arp_announce = 0
    net.ipv4.conf.default.arp_filter = 0
    net.ipv4.conf.default.arp_ignore = 0
    net.ipv4.conf.default.arp_notify = 0
    net.ipv4.conf.default.bootp_relay = 0
    net.ipv4.conf.default.disable_policy = 0
    net.ipv4.conf.default.disable_xfrm = 0
    net.ipv4.conf.default.force_igmp_version = 0
    net.ipv4.conf.default.forwarding = 1
    net.ipv4.conf.default.igmpv2_unsolicited_report_interval = 10000
    net.ipv4.conf.default.igmpv3_unsolicited_report_interval = 1000
    net.ipv4.conf.default.ignore_routes_with_linkdown = 0
    net.ipv4.conf.default.log_martians = 0
    net.ipv4.conf.default.mc_forwarding = 0
    net.ipv4.conf.default.medium_id = 0
    net.ipv4.conf.default.promote_secondaries = 0
    net.ipv4.conf.default.proxy_arp = 0
    net.ipv4.conf.default.proxy_arp_pvlan = 0
    net.ipv4.conf.default.route_localnet = 0
    net.ipv4.conf.default.rp_filter = 1
    net.ipv4.conf.default.secure_redirects = 1
    net.ipv4.conf.default.send_redirects = 1
    net.ipv4.conf.default.shared_media = 1
    net.ipv4.conf.default.src_valid_mark = 0
    net.ipv4.conf.default.tag = 0
    net.ipv4.conf.enp25s0f0.accept_local = 0
    net.ipv4.conf.enp25s0f0.accept_redirects = 1
    net.ipv4.conf.enp25s0f0.accept_source_route = 1
    net.ipv4.conf.enp25s0f0.arp_accept = 0
    net.ipv4.conf.enp25s0f0.arp_announce = 0
    net.ipv4.conf.enp25s0f0.arp_filter = 0
    net.ipv4.conf.enp25s0f0.arp_ignore = 0
    net.ipv4.conf.enp25s0f0.arp_notify = 0
    net.ipv4.conf.enp25s0f0.bootp_relay = 0
    net.ipv4.conf.enp25s0f0.disable_policy = 0
    net.ipv4.conf.enp25s0f0.disable_xfrm = 0
    net.ipv4.conf.enp25s0f0.force_igmp_version = 0
    net.ipv4.conf.enp25s0f0.forwarding = 1
    net.ipv4.conf.enp25s0f0.igmpv2_unsolicited_report_interval = 10000
    net.ipv4.conf.enp25s0f0.igmpv3_unsolicited_report_interval = 1000
    net.ipv4.conf.enp25s0f0.ignore_routes_with_linkdown = 0
    net.ipv4.conf.enp25s0f0.log_martians = 0
    net.ipv4.conf.enp25s0f0.mc_forwarding = 0
    net.ipv4.conf.enp25s0f0.medium_id = 0
    net.ipv4.conf.enp25s0f0.promote_secondaries = 0
    net.ipv4.conf.enp25s0f0.proxy_arp = 0
    net.ipv4.conf.enp25s0f0.proxy_arp_pvlan = 0
    net.ipv4.conf.enp25s0f0.route_localnet = 0
    net.ipv4.conf.enp25s0f0.rp_filter = 1
    net.ipv4.conf.enp25s0f0.secure_redirects = 1
    net.ipv4.conf.enp25s0f0.send_redirects = 1
    net.ipv4.conf.enp25s0f0.shared_media = 1
    net.ipv4.conf.enp25s0f0.src_valid_mark = 0
    net.ipv4.conf.enp25s0f0.tag = 0
    net.ipv4.conf.lo.accept_local = 0
    net.ipv4.conf.lo.accept_redirects = 1
    net.ipv4.conf.lo.accept_source_route = 1
    net.ipv4.conf.lo.arp_accept = 0
    net.ipv4.conf.lo.arp_announce = 0
    net.ipv4.conf.lo.arp_filter = 0
    net.ipv4.conf.lo.arp_ignore = 0
    net.ipv4.conf.lo.arp_notify = 0
    net.ipv4.conf.lo.bootp_relay = 0
    net.ipv4.conf.lo.disable_policy = 1
    net.ipv4.conf.lo.disable_xfrm = 1
    net.ipv4.conf.lo.force_igmp_version = 0
    net.ipv4.conf.lo.forwarding = 1
    net.ipv4.conf.lo.igmpv2_unsolicited_report_interval = 10000
    net.ipv4.conf.lo.igmpv3_unsolicited_report_interval = 1000
    net.ipv4.conf.lo.ignore_routes_with_linkdown = 0
    net.ipv4.conf.lo.log_martians = 0
    net.ipv4.conf.lo.mc_forwarding = 0
    net.ipv4.conf.lo.medium_id = 0
    net.ipv4.conf.lo.promote_secondaries = 0
    net.ipv4.conf.lo.proxy_arp = 0
    net.ipv4.conf.lo.proxy_arp_pvlan = 0
    net.ipv4.conf.lo.route_localnet = 0
    net.ipv4.conf.lo.rp_filter = 0
    net.ipv4.conf.lo.secure_redirects = 1
    net.ipv4.conf.lo.send_redirects = 1
    net.ipv4.conf.lo.shared_media = 1
    net.ipv4.conf.lo.src_valid_mark = 0
    net.ipv4.conf.lo.tag = 0
    net.ipv4.conf.lxcbr0.accept_local = 0
    net.ipv4.conf.lxcbr0.accept_redirects = 1
    net.ipv4.conf.lxcbr0.accept_source_route = 1
    net.ipv4.conf.lxcbr0.arp_accept = 0
    net.ipv4.conf.lxcbr0.arp_announce = 0
    net.ipv4.conf.lxcbr0.arp_filter = 0
    net.ipv4.conf.lxcbr0.arp_ignore = 0
    net.ipv4.conf.lxcbr0.arp_notify = 0
    net.ipv4.conf.lxcbr0.bootp_relay = 0
    net.ipv4.conf.lxcbr0.disable_policy = 0
    net.ipv4.conf.lxcbr0.disable_xfrm = 0
    net.ipv4.conf.lxcbr0.force_igmp_version = 0
    net.ipv4.conf.lxcbr0.forwarding = 1
    net.ipv4.conf.lxcbr0.igmpv2_unsolicited_report_interval = 10000
    net.ipv4.conf.lxcbr0.igmpv3_unsolicited_report_interval = 1000
    net.ipv4.conf.lxcbr0.ignore_routes_with_linkdown = 0
    net.ipv4.conf.lxcbr0.log_martians = 0
    net.ipv4.conf.lxcbr0.mc_forwarding = 0
    net.ipv4.conf.lxcbr0.medium_id = 0
    net.ipv4.conf.lxcbr0.promote_secondaries = 0
    net.ipv4.conf.lxcbr0.proxy_arp = 0
    net.ipv4.conf.lxcbr0.proxy_arp_pvlan = 0
    net.ipv4.conf.lxcbr0.route_localnet = 0
    net.ipv4.conf.lxcbr0.rp_filter = 1
    net.ipv4.conf.lxcbr0.secure_redirects = 1
    net.ipv4.conf.lxcbr0.send_redirects = 1
    net.ipv4.conf.lxcbr0.shared_media = 1
    net.ipv4.conf.lxcbr0.src_valid_mark = 0
    net.ipv4.conf.lxcbr0.tag = 0
    net.ipv4.fwmark_reflect = 0
    net.ipv4.icmp_echo_ignore_all = 0
    net.ipv4.icmp_echo_ignore_broadcasts = 1
    net.ipv4.icmp_errors_use_inbound_ifaddr = 0
    net.ipv4.icmp_ignore_bogus_error_responses = 1
    net.ipv4.icmp_msgs_burst = 50
    net.ipv4.icmp_msgs_per_sec = 1000
    net.ipv4.icmp_ratelimit = 1000
    net.ipv4.icmp_ratemask = 6168
    net.ipv4.igmp_link_local_mcast_reports = 1
    net.ipv4.igmp_max_memberships = 20
    net.ipv4.igmp_max_msf = 10
    net.ipv4.igmp_qrv = 2
    net.ipv4.inet_peer_maxttl = 600
    net.ipv4.inet_peer_minttl = 120
    net.ipv4.inet_peer_threshold = 65664
    net.ipv4.ip_default_ttl = 64
    net.ipv4.ip_dynaddr = 0
    net.ipv4.ip_early_demux = 1
    net.ipv4.ip_forward = 1
    net.ipv4.ip_forward_use_pmtu = 0
    net.ipv4.ip_local_port_range = 32768	60999
    net.ipv4.ip_local_reserved_ports =
    net.ipv4.ip_no_pmtu_disc = 0
    net.ipv4.ip_nonlocal_bind = 0
    net.ipv4.ipfrag_high_thresh = 4194304
    net.ipv4.ipfrag_low_thresh = 3145728
    net.ipv4.ipfrag_max_dist = 64
    net.ipv4.ipfrag_secret_interval = 0
    net.ipv4.ipfrag_time = 30
    net.ipv4.neigh.default.anycast_delay = 100
    net.ipv4.neigh.default.app_solicit = 0
    net.ipv4.neigh.default.base_reachable_time_ms = 30000
    net.ipv4.neigh.default.delay_first_probe_time = 5
    net.ipv4.neigh.default.gc_interval = 30
    net.ipv4.neigh.default.gc_stale_time = 60
    net.ipv4.neigh.default.gc_thresh1 = 128
    net.ipv4.neigh.default.gc_thresh2 = 512
    net.ipv4.neigh.default.gc_thresh3 = 1024
    net.ipv4.neigh.default.locktime = 100
    net.ipv4.neigh.default.mcast_resolicit = 0
    net.ipv4.neigh.default.mcast_solicit = 3
    net.ipv4.neigh.default.proxy_delay = 80
    net.ipv4.neigh.default.proxy_qlen = 64
    net.ipv4.neigh.default.retrans_time_ms = 1000
    net.ipv4.neigh.default.ucast_solicit = 3
    net.ipv4.neigh.default.unres_qlen = 31
    net.ipv4.neigh.default.unres_qlen_bytes = 65536
    net.ipv4.neigh.enp25s0f0.anycast_delay = 100
    net.ipv4.neigh.enp25s0f0.app_solicit = 0
    net.ipv4.neigh.enp25s0f0.base_reachable_time_ms = 30000
    net.ipv4.neigh.enp25s0f0.delay_first_probe_time = 5
    net.ipv4.neigh.enp25s0f0.gc_stale_time = 60
    net.ipv4.neigh.enp25s0f0.locktime = 100
    net.ipv4.neigh.enp25s0f0.mcast_resolicit = 0
    net.ipv4.neigh.enp25s0f0.mcast_solicit = 3
    net.ipv4.neigh.enp25s0f0.proxy_delay = 80
    net.ipv4.neigh.enp25s0f0.proxy_qlen = 64
    net.ipv4.neigh.enp25s0f0.retrans_time_ms = 1000
    net.ipv4.neigh.enp25s0f0.ucast_solicit = 3
    net.ipv4.neigh.enp25s0f0.unres_qlen = 31
    net.ipv4.neigh.enp25s0f0.unres_qlen_bytes = 65536
    net.ipv4.neigh.lo.anycast_delay = 100
    net.ipv4.neigh.lo.app_solicit = 0
    net.ipv4.neigh.lo.base_reachable_time_ms = 30000
    net.ipv4.neigh.lo.delay_first_probe_time = 5
    net.ipv4.neigh.lo.gc_stale_time = 60
    net.ipv4.neigh.lo.locktime = 100
    net.ipv4.neigh.lo.mcast_resolicit = 0
    net.ipv4.neigh.lo.mcast_solicit = 3
    net.ipv4.neigh.lo.proxy_delay = 80
    net.ipv4.neigh.lo.proxy_qlen = 64
    net.ipv4.neigh.lo.retrans_time_ms = 1000
    net.ipv4.neigh.lo.ucast_solicit = 3
    net.ipv4.neigh.lo.unres_qlen = 31
    net.ipv4.neigh.lo.unres_qlen_bytes = 65536
    net.ipv4.neigh.lxcbr0.anycast_delay = 100
    net.ipv4.neigh.lxcbr0.app_solicit = 0
    net.ipv4.neigh.lxcbr0.base_reachable_time_ms = 30000
    net.ipv4.neigh.lxcbr0.delay_first_probe_time = 5
    net.ipv4.neigh.lxcbr0.gc_stale_time = 60
    net.ipv4.neigh.lxcbr0.locktime = 100
    net.ipv4.neigh.lxcbr0.mcast_resolicit = 0
    net.ipv4.neigh.lxcbr0.mcast_solicit = 3
    net.ipv4.neigh.lxcbr0.proxy_delay = 80
    net.ipv4.neigh.lxcbr0.proxy_qlen = 64
    net.ipv4.neigh.lxcbr0.retrans_time_ms = 1000
    net.ipv4.neigh.lxcbr0.ucast_solicit = 3
    net.ipv4.neigh.lxcbr0.unres_qlen = 31
    net.ipv4.neigh.lxcbr0.unres_qlen_bytes = 65536
    net.ipv4.ping_group_range = 1	0
    net.ipv4.route.error_burst = 1250
    net.ipv4.route.error_cost = 250
    net.ipv4.route.gc_elasticity = 8
    net.ipv4.route.gc_interval = 60
    net.ipv4.route.gc_min_interval = 0
    net.ipv4.route.gc_min_interval_ms = 500
    net.ipv4.route.gc_thresh = -1
    net.ipv4.route.gc_timeout = 300
    net.ipv4.route.max_size = 2147483647
    net.ipv4.route.min_adv_mss = 256
    net.ipv4.route.min_pmtu = 552
    net.ipv4.route.mtu_expires = 600
    net.ipv4.route.redirect_load = 5
    net.ipv4.route.redirect_number = 9
    net.ipv4.route.redirect_silence = 5120
    net.ipv4.tcp_abort_on_overflow = 0
    net.ipv4.tcp_adv_win_scale = 1
    net.ipv4.tcp_allowed_congestion_control = cubic reno
    net.ipv4.tcp_app_win = 31
    net.ipv4.tcp_autocorking = 1
    net.ipv4.tcp_available_congestion_control = cubic reno
    net.ipv4.tcp_base_mss = 1024
    net.ipv4.tcp_challenge_ack_limit = 1000
    net.ipv4.tcp_congestion_control = cubic
    net.ipv4.tcp_dsack = 1
    net.ipv4.tcp_early_retrans = 3
    net.ipv4.tcp_ecn = 2
    net.ipv4.tcp_ecn_fallback = 1
    net.ipv4.tcp_fack = 1
    net.ipv4.tcp_fastopen = 1
    net.ipv4.tcp_fastopen_key = 00000000-00000000-00000000-00000000
    net.ipv4.tcp_fin_timeout = 60
    net.ipv4.tcp_frto = 2
    net.ipv4.tcp_fwmark_accept = 0
    net.ipv4.tcp_invalid_ratelimit = 500
    net.ipv4.tcp_keepalive_intvl = 75
    net.ipv4.tcp_keepalive_probes = 9
    net.ipv4.tcp_keepalive_time = 7200
    net.ipv4.tcp_limit_output_bytes = 262144
    net.ipv4.tcp_low_latency = 0
    net.ipv4.tcp_max_orphans = 262144
    net.ipv4.tcp_max_reordering = 300
    net.ipv4.tcp_max_syn_backlog = 2048
    net.ipv4.tcp_max_tw_buckets = 262144
    net.ipv4.tcp_mem = 6188856	8251809	12377712
    net.ipv4.tcp_min_rtt_wlen = 300
    net.ipv4.tcp_min_tso_segs = 2
    net.ipv4.tcp_moderate_rcvbuf = 1
    net.ipv4.tcp_mtu_probing = 0
    net.ipv4.tcp_no_metrics_save = 0
    net.ipv4.tcp_notsent_lowat = -1
    net.ipv4.tcp_orphan_retries = 0
    net.ipv4.tcp_pacing_ca_ratio = 120
    net.ipv4.tcp_pacing_ss_ratio = 200
    net.ipv4.tcp_probe_interval = 600
    net.ipv4.tcp_probe_threshold = 8
    net.ipv4.tcp_recovery = 1
    net.ipv4.tcp_reordering = 3
    net.ipv4.tcp_retrans_collapse = 1
    net.ipv4.tcp_retries1 = 3
    net.ipv4.tcp_retries2 = 15
    net.ipv4.tcp_rfc1337 = 0
    net.ipv4.tcp_rmem = 4096	87380	6291456
    net.ipv4.tcp_sack = 1
    net.ipv4.tcp_slow_start_after_idle = 1
    net.ipv4.tcp_stdurg = 0
    net.ipv4.tcp_syn_retries = 6
    net.ipv4.tcp_synack_retries = 5
    net.ipv4.tcp_syncookies = 1
    net.ipv4.tcp_thin_dupack = 0
    net.ipv4.tcp_thin_linear_timeouts = 0
    net.ipv4.tcp_timestamps = 1
    net.ipv4.tcp_tso_win_divisor = 3
    net.ipv4.tcp_tw_recycle = 0
    net.ipv4.tcp_tw_reuse = 0
    net.ipv4.tcp_window_scaling = 1
    net.ipv4.tcp_wmem = 4096	16384	4194304
    net.ipv4.tcp_workaround_signed_windows = 0
    net.ipv4.udp_mem = 12377712	16503618	24755424
    net.ipv4.udp_rmem_min = 4096
    net.ipv4.udp_wmem_min = 4096
    net.ipv4.xfrm4_gc_thresh = 2147483647
    net.ipv6.anycast_src_echo_reply = 0
    net.ipv6.auto_flowlabels = 1
    net.ipv6.bindv6only = 0
    net.ipv6.conf.all.accept_dad = 1
    net.ipv6.conf.all.accept_ra = 1
    net.ipv6.conf.all.accept_ra_defrtr = 1
    net.ipv6.conf.all.accept_ra_from_local = 0
    net.ipv6.conf.all.accept_ra_min_hop_limit = 1
    net.ipv6.conf.all.accept_ra_mtu = 1
    net.ipv6.conf.all.accept_ra_pinfo = 1
    net.ipv6.conf.all.accept_ra_rt_info_max_plen = 0
    net.ipv6.conf.all.accept_ra_rtr_pref = 1
    net.ipv6.conf.all.accept_redirects = 1
    net.ipv6.conf.all.accept_source_route = 0
    net.ipv6.conf.all.autoconf = 1
    net.ipv6.conf.all.dad_transmits = 1
    net.ipv6.conf.all.disable_ipv6 = 0
    net.ipv6.conf.all.force_mld_version = 0
    net.ipv6.conf.all.force_tllao = 0
    net.ipv6.conf.all.forwarding = 0
    net.ipv6.conf.all.hop_limit = 64
    net.ipv6.conf.all.ignore_routes_with_linkdown = 0
    net.ipv6.conf.all.max_addresses = 16
    net.ipv6.conf.all.max_desync_factor = 600
    net.ipv6.conf.all.mc_forwarding = 0
    net.ipv6.conf.all.mldv1_unsolicited_report_interval = 10000
    net.ipv6.conf.all.mldv2_unsolicited_report_interval = 1000
    net.ipv6.conf.all.mtu = 1280
    net.ipv6.conf.all.ndisc_notify = 0
    net.ipv6.conf.all.proxy_ndp = 0
    net.ipv6.conf.all.regen_max_retry = 3
    net.ipv6.conf.all.router_probe_interval = 60
    net.ipv6.conf.all.router_solicitation_delay = 1
    net.ipv6.conf.all.router_solicitation_interval = 4
    net.ipv6.conf.all.router_solicitations = 3
    sysctl: reading key "net.ipv6.conf.all.stable_secret"
    net.ipv6.conf.all.suppress_frag_ndisc = 1
    net.ipv6.conf.all.temp_prefered_lft = 86400
    net.ipv6.conf.all.temp_valid_lft = 604800
    net.ipv6.conf.all.use_oif_addrs_only = 0
    net.ipv6.conf.all.use_tempaddr = 2
    net.ipv6.conf.default.accept_dad = 1
    net.ipv6.conf.default.accept_ra = 1
    net.ipv6.conf.default.accept_ra_defrtr = 1
    net.ipv6.conf.default.accept_ra_from_local = 0
    net.ipv6.conf.default.accept_ra_min_hop_limit = 1
    net.ipv6.conf.default.accept_ra_mtu = 1
    net.ipv6.conf.default.accept_ra_pinfo = 1
    net.ipv6.conf.default.accept_ra_rt_info_max_plen = 0
    net.ipv6.conf.default.accept_ra_rtr_pref = 1
    net.ipv6.conf.default.accept_redirects = 1
    net.ipv6.conf.default.accept_source_route = 0
    net.ipv6.conf.default.autoconf = 1
    net.ipv6.conf.default.dad_transmits = 1
    net.ipv6.conf.default.disable_ipv6 = 0
    net.ipv6.conf.default.force_mld_version = 0
    net.ipv6.conf.default.force_tllao = 0
    net.ipv6.conf.default.forwarding = 0
    net.ipv6.conf.default.hop_limit = 64
    net.ipv6.conf.default.ignore_routes_with_linkdown = 0
    net.ipv6.conf.default.max_addresses = 16
    net.ipv6.conf.default.max_desync_factor = 600
    net.ipv6.conf.default.mc_forwarding = 0
    net.ipv6.conf.default.mldv1_unsolicited_report_interval = 10000
    net.ipv6.conf.default.mldv2_unsolicited_report_interval = 1000
    net.ipv6.conf.default.mtu = 1280
    net.ipv6.conf.default.ndisc_notify = 0
    net.ipv6.conf.default.proxy_ndp = 0
    net.ipv6.conf.default.regen_max_retry = 3
    net.ipv6.conf.default.router_probe_interval = 60
    net.ipv6.conf.default.router_solicitation_delay = 1
    net.ipv6.conf.default.router_solicitation_interval = 4
    net.ipv6.conf.default.router_solicitations = 3
    sysctl: reading key "net.ipv6.conf.default.stable_secret"
    net.ipv6.conf.default.suppress_frag_ndisc = 1
    net.ipv6.conf.default.temp_prefered_lft = 86400
    net.ipv6.conf.default.temp_valid_lft = 604800
    net.ipv6.conf.default.use_oif_addrs_only = 0
    net.ipv6.conf.default.use_tempaddr = 2
    net.ipv6.conf.enp25s0f0.accept_dad = 1
    net.ipv6.conf.enp25s0f0.accept_ra = 1
    net.ipv6.conf.enp25s0f0.accept_ra_defrtr = 1
    net.ipv6.conf.enp25s0f0.accept_ra_from_local = 0
    net.ipv6.conf.enp25s0f0.accept_ra_min_hop_limit = 1
    net.ipv6.conf.enp25s0f0.accept_ra_mtu = 1
    net.ipv6.conf.enp25s0f0.accept_ra_pinfo = 1
    net.ipv6.conf.enp25s0f0.accept_ra_rt_info_max_plen = 0
    net.ipv6.conf.enp25s0f0.accept_ra_rtr_pref = 1
    net.ipv6.conf.enp25s0f0.accept_redirects = 1
    net.ipv6.conf.enp25s0f0.accept_source_route = 0
    net.ipv6.conf.enp25s0f0.autoconf = 1
    net.ipv6.conf.enp25s0f0.dad_transmits = 1
    net.ipv6.conf.enp25s0f0.disable_ipv6 = 0
    net.ipv6.conf.enp25s0f0.force_mld_version = 0
    net.ipv6.conf.enp25s0f0.force_tllao = 0
    net.ipv6.conf.enp25s0f0.forwarding = 0
    net.ipv6.conf.enp25s0f0.hop_limit = 64
    net.ipv6.conf.enp25s0f0.ignore_routes_with_linkdown = 0
    net.ipv6.conf.enp25s0f0.max_addresses = 16
    net.ipv6.conf.enp25s0f0.max_desync_factor = 600
    net.ipv6.conf.enp25s0f0.mc_forwarding = 0
    net.ipv6.conf.enp25s0f0.mldv1_unsolicited_report_interval = 10000
    net.ipv6.conf.enp25s0f0.mldv2_unsolicited_report_interval = 1000
    net.ipv6.conf.enp25s0f0.mtu = 1500
    net.ipv6.conf.enp25s0f0.ndisc_notify = 0
    net.ipv6.conf.enp25s0f0.proxy_ndp = 0
    net.ipv6.conf.enp25s0f0.regen_max_retry = 3
    net.ipv6.conf.enp25s0f0.router_probe_interval = 60
    net.ipv6.conf.enp25s0f0.router_solicitation_delay = 1
    net.ipv6.conf.enp25s0f0.router_solicitation_interval = 4
    net.ipv6.conf.enp25s0f0.router_solicitations = 3
    sysctl: reading key "net.ipv6.conf.enp25s0f0.stable_secret"
    net.ipv6.conf.enp25s0f0.suppress_frag_ndisc = 1
    net.ipv6.conf.enp25s0f0.temp_prefered_lft = 86400
    net.ipv6.conf.enp25s0f0.temp_valid_lft = 604800
    net.ipv6.conf.enp25s0f0.use_oif_addrs_only = 0
    net.ipv6.conf.enp25s0f0.use_tempaddr = 0
    net.ipv6.conf.lo.accept_dad = -1
    net.ipv6.conf.lo.accept_ra = 1
    net.ipv6.conf.lo.accept_ra_defrtr = 1
    net.ipv6.conf.lo.accept_ra_from_local = 0
    net.ipv6.conf.lo.accept_ra_min_hop_limit = 1
    net.ipv6.conf.lo.accept_ra_mtu = 1
    net.ipv6.conf.lo.accept_ra_pinfo = 1
    net.ipv6.conf.lo.accept_ra_rt_info_max_plen = 0
    net.ipv6.conf.lo.accept_ra_rtr_pref = 1
    net.ipv6.conf.lo.accept_redirects = 1
    net.ipv6.conf.lo.accept_source_route = 0
    net.ipv6.conf.lo.autoconf = 1
    net.ipv6.conf.lo.dad_transmits = 1
    net.ipv6.conf.lo.disable_ipv6 = 0
    net.ipv6.conf.lo.force_mld_version = 0
    net.ipv6.conf.lo.force_tllao = 0
    net.ipv6.conf.lo.forwarding = 0
    net.ipv6.conf.lo.hop_limit = 64
    net.ipv6.conf.lo.ignore_routes_with_linkdown = 0
    net.ipv6.conf.lo.max_addresses = 16
    net.ipv6.conf.lo.max_desync_factor = 600
    net.ipv6.conf.lo.mc_forwarding = 0
    net.ipv6.conf.lo.mldv1_unsolicited_report_interval = 10000
    net.ipv6.conf.lo.mldv2_unsolicited_report_interval = 1000
    net.ipv6.conf.lo.mtu = 65536
    net.ipv6.conf.lo.ndisc_notify = 0
    net.ipv6.conf.lo.proxy_ndp = 0
    net.ipv6.conf.lo.regen_max_retry = 3
    net.ipv6.conf.lo.router_probe_interval = 60
    net.ipv6.conf.lo.router_solicitation_delay = 1
    net.ipv6.conf.lo.router_solicitation_interval = 4
    net.ipv6.conf.lo.router_solicitations = 3
    sysctl: reading key "net.ipv6.conf.lo.stable_secret"
    net.ipv6.conf.lo.suppress_frag_ndisc = 1
    net.ipv6.conf.lo.temp_prefered_lft = 86400
    net.ipv6.conf.lo.temp_valid_lft = 604800
    net.ipv6.conf.lo.use_oif_addrs_only = 0
    net.ipv6.conf.lo.use_tempaddr = -1
    net.ipv6.conf.lxcbr0.accept_dad = 0
    net.ipv6.conf.lxcbr0.accept_ra = 1
    net.ipv6.conf.lxcbr0.accept_ra_defrtr = 1
    net.ipv6.conf.lxcbr0.accept_ra_from_local = 0
    net.ipv6.conf.lxcbr0.accept_ra_min_hop_limit = 1
    net.ipv6.conf.lxcbr0.accept_ra_mtu = 1
    net.ipv6.conf.lxcbr0.accept_ra_pinfo = 1
    net.ipv6.conf.lxcbr0.accept_ra_rt_info_max_plen = 0
    net.ipv6.conf.lxcbr0.accept_ra_rtr_pref = 1
    net.ipv6.conf.lxcbr0.accept_redirects = 1
    net.ipv6.conf.lxcbr0.accept_source_route = 0
    net.ipv6.conf.lxcbr0.autoconf = 1
    net.ipv6.conf.lxcbr0.dad_transmits = 1
    net.ipv6.conf.lxcbr0.disable_ipv6 = 0
    net.ipv6.conf.lxcbr0.force_mld_version = 0
    net.ipv6.conf.lxcbr0.force_tllao = 0
    net.ipv6.conf.lxcbr0.forwarding = 0
    net.ipv6.conf.lxcbr0.hop_limit = 64
    net.ipv6.conf.lxcbr0.ignore_routes_with_linkdown = 0
    net.ipv6.conf.lxcbr0.max_addresses = 16
    net.ipv6.conf.lxcbr0.max_desync_factor = 600
    net.ipv6.conf.lxcbr0.mc_forwarding = 0
    net.ipv6.conf.lxcbr0.mldv1_unsolicited_report_interval = 10000
    net.ipv6.conf.lxcbr0.mldv2_unsolicited_report_interval = 1000
    net.ipv6.conf.lxcbr0.mtu = 1500
    net.ipv6.conf.lxcbr0.ndisc_notify = 0
    net.ipv6.conf.lxcbr0.proxy_ndp = 0
    net.ipv6.conf.lxcbr0.regen_max_retry = 3
    net.ipv6.conf.lxcbr0.router_probe_interval = 60
    net.ipv6.conf.lxcbr0.router_solicitation_delay = 1
    net.ipv6.conf.lxcbr0.router_solicitation_interval = 4
    net.ipv6.conf.lxcbr0.router_solicitations = 3
    sysctl: reading key "net.ipv6.conf.lxcbr0.stable_secret"
    net.ipv6.conf.lxcbr0.suppress_frag_ndisc = 1
    net.ipv6.conf.lxcbr0.temp_prefered_lft = 86400
    net.ipv6.conf.lxcbr0.temp_valid_lft = 604800
    net.ipv6.conf.lxcbr0.use_oif_addrs_only = 0
    net.ipv6.conf.lxcbr0.use_tempaddr = 2
    net.ipv6.flowlabel_consistency = 1
    net.ipv6.flowlabel_state_ranges = 0
    net.ipv6.fwmark_reflect = 0
    net.ipv6.icmp.ratelimit = 1000
    net.ipv6.idgen_delay = 1
    net.ipv6.idgen_retries = 3
    net.ipv6.ip6frag_high_thresh = 4194304
    net.ipv6.ip6frag_low_thresh = 3145728
    net.ipv6.ip6frag_secret_interval = 0
    net.ipv6.ip6frag_time = 60
    net.ipv6.ip_nonlocal_bind = 0
    net.ipv6.mld_max_msf = 64
    net.ipv6.mld_qrv = 2
    net.ipv6.neigh.default.anycast_delay = 100
    net.ipv6.neigh.default.app_solicit = 0
    net.ipv6.neigh.default.base_reachable_time_ms = 30000
    net.ipv6.neigh.default.delay_first_probe_time = 5
    net.ipv6.neigh.default.gc_interval = 30
    net.ipv6.neigh.default.gc_stale_time = 60
    net.ipv6.neigh.default.gc_thresh1 = 128
    net.ipv6.neigh.default.gc_thresh2 = 512
    net.ipv6.neigh.default.gc_thresh3 = 1024
    net.ipv6.neigh.default.locktime = 0
    net.ipv6.neigh.default.mcast_resolicit = 0
    net.ipv6.neigh.default.mcast_solicit = 3
    net.ipv6.neigh.default.proxy_delay = 80
    net.ipv6.neigh.default.proxy_qlen = 64
    net.ipv6.neigh.default.retrans_time_ms = 1000
    net.ipv6.neigh.default.ucast_solicit = 3
    net.ipv6.neigh.default.unres_qlen = 31
    net.ipv6.neigh.default.unres_qlen_bytes = 65536
    net.ipv6.neigh.enp25s0f0.anycast_delay = 100
    net.ipv6.neigh.enp25s0f0.app_solicit = 0
    net.ipv6.neigh.enp25s0f0.base_reachable_time_ms = 30000
    net.ipv6.neigh.enp25s0f0.delay_first_probe_time = 5
    net.ipv6.neigh.enp25s0f0.gc_stale_time = 60
    net.ipv6.neigh.enp25s0f0.locktime = 0
    net.ipv6.neigh.enp25s0f0.mcast_resolicit = 0
    net.ipv6.neigh.enp25s0f0.mcast_solicit = 3
    net.ipv6.neigh.enp25s0f0.proxy_delay = 80
    net.ipv6.neigh.enp25s0f0.proxy_qlen = 64
    net.ipv6.neigh.enp25s0f0.retrans_time_ms = 1000
    net.ipv6.neigh.enp25s0f0.ucast_solicit = 3
    net.ipv6.neigh.enp25s0f0.unres_qlen = 31
    net.ipv6.neigh.enp25s0f0.unres_qlen_bytes = 65536
    net.ipv6.neigh.lo.anycast_delay = 100
    net.ipv6.neigh.lo.app_solicit = 0
    net.ipv6.neigh.lo.base_reachable_time_ms = 30000
    net.ipv6.neigh.lo.delay_first_probe_time = 5
    net.ipv6.neigh.lo.gc_stale_time = 60
    net.ipv6.neigh.lo.locktime = 0
    net.ipv6.neigh.lo.mcast_resolicit = 0
    net.ipv6.neigh.lo.mcast_solicit = 3
    net.ipv6.neigh.lo.proxy_delay = 80
    net.ipv6.neigh.lo.proxy_qlen = 64
    net.ipv6.neigh.lo.retrans_time_ms = 1000
    net.ipv6.neigh.lo.ucast_solicit = 3
    net.ipv6.neigh.lo.unres_qlen = 31
    net.ipv6.neigh.lo.unres_qlen_bytes = 65536
    net.ipv6.neigh.lxcbr0.anycast_delay = 100
    net.ipv6.neigh.lxcbr0.app_solicit = 0
    net.ipv6.neigh.lxcbr0.base_reachable_time_ms = 30000
    net.ipv6.neigh.lxcbr0.delay_first_probe_time = 5
    net.ipv6.neigh.lxcbr0.gc_stale_time = 60
    net.ipv6.neigh.lxcbr0.locktime = 0
    net.ipv6.neigh.lxcbr0.mcast_resolicit = 0
    net.ipv6.neigh.lxcbr0.mcast_solicit = 3
    net.ipv6.neigh.lxcbr0.proxy_delay = 80
    net.ipv6.neigh.lxcbr0.proxy_qlen = 64
    net.ipv6.neigh.lxcbr0.retrans_time_ms = 1000
    net.ipv6.neigh.lxcbr0.ucast_solicit = 3
    net.ipv6.neigh.lxcbr0.unres_qlen = 31
    net.ipv6.neigh.lxcbr0.unres_qlen_bytes = 65536
    net.ipv6.route.gc_elasticity = 9
    net.ipv6.route.gc_interval = 30
    net.ipv6.route.gc_min_interval = 0
    net.ipv6.route.gc_min_interval_ms = 500
    net.ipv6.route.gc_thresh = 1024
    net.ipv6.route.gc_timeout = 60
    net.ipv6.route.max_size = 4096
    net.ipv6.route.min_adv_mss = 1220
    net.ipv6.route.mtu_expires = 600
    net.ipv6.xfrm6_gc_thresh = 2147483647
    net.netfilter.nf_conntrack_acct = 0
    net.netfilter.nf_conntrack_buckets = 65536
    net.netfilter.nf_conntrack_checksum = 1
    net.netfilter.nf_conntrack_count = 2
    net.netfilter.nf_conntrack_events = 1
    net.netfilter.nf_conntrack_expect_max = 1024
    net.netfilter.nf_conntrack_generic_timeout = 600
    net.netfilter.nf_conntrack_helper = 1
    net.netfilter.nf_conntrack_icmp_timeout = 30
    net.netfilter.nf_conntrack_log_invalid = 0
    net.netfilter.nf_conntrack_max = 262144
    net.netfilter.nf_conntrack_tcp_be_liberal = 0
    net.netfilter.nf_conntrack_tcp_loose = 1
    net.netfilter.nf_conntrack_tcp_max_retrans = 3
    net.netfilter.nf_conntrack_tcp_timeout_close = 10
    net.netfilter.nf_conntrack_tcp_timeout_close_wait = 60
    net.netfilter.nf_conntrack_tcp_timeout_established = 432000
    net.netfilter.nf_conntrack_tcp_timeout_fin_wait = 120
    net.netfilter.nf_conntrack_tcp_timeout_last_ack = 30
    net.netfilter.nf_conntrack_tcp_timeout_max_retrans = 300
    net.netfilter.nf_conntrack_tcp_timeout_syn_recv = 60
    net.netfilter.nf_conntrack_tcp_timeout_syn_sent = 120
    net.netfilter.nf_conntrack_tcp_timeout_time_wait = 120
    net.netfilter.nf_conntrack_tcp_timeout_unacknowledged = 300
    net.netfilter.nf_conntrack_timestamp = 0
    net.netfilter.nf_conntrack_udp_timeout = 30
    net.netfilter.nf_conntrack_udp_timeout_stream = 180
    net.netfilter.nf_log.0 = NONE
    net.netfilter.nf_log.1 = NONE
    net.netfilter.nf_log.10 = NONE
    net.netfilter.nf_log.11 = NONE
    net.netfilter.nf_log.12 = NONE
    net.netfilter.nf_log.2 = NONE
    net.netfilter.nf_log.3 = NONE
    net.netfilter.nf_log.4 = NONE
    net.netfilter.nf_log.5 = NONE
    net.netfilter.nf_log.6 = NONE
    net.netfilter.nf_log.7 = NONE
    net.netfilter.nf_log.8 = NONE
    net.netfilter.nf_log.9 = NONE
    net.nf_conntrack_max = 262144
    net.unix.max_dgram_qlen = 512
    vm.admin_reserve_kbytes = 8192
    vm.block_dump = 0
    vm.compact_unevictable_allowed = 1
    vm.dirty_background_bytes = 0
    vm.dirty_background_ratio = 10
    vm.dirty_bytes = 0
    vm.dirty_expire_centisecs = 3000
    vm.dirty_ratio = 20
    vm.dirty_writeback_centisecs = 500
    vm.dirtytime_expire_seconds = 43200
    vm.drop_caches = 0
    vm.extfrag_threshold = 500
    vm.hugepages_treat_as_movable = 0
    vm.hugetlb_shm_group = 0
    vm.laptop_mode = 0
    vm.legacy_va_layout = 0
    vm.lowmem_reserve_ratio = 256	256	32	1
    vm.max_map_count = 200000
    vm.memory_failure_early_kill = 0
    vm.memory_failure_recovery = 1
    vm.min_free_kbytes = 90112
    vm.min_slab_ratio = 5
    vm.min_unmapped_ratio = 1
    vm.mmap_min_addr = 65536
    vm.nr_hugepages = 4096
    vm.nr_hugepages_mempolicy = 4096
    vm.nr_overcommit_hugepages = 0
    vm.nr_pdflush_threads = 0
    vm.numa_zonelist_order = default
    vm.oom_dump_tasks = 1
    vm.oom_kill_allocating_task = 0
    vm.overcommit_kbytes = 0
    vm.overcommit_memory = 0
    vm.overcommit_ratio = 50
    vm.page-cluster = 3
    vm.panic_on_oom = 0
    vm.percpu_pagelist_fraction = 0
    vm.stat_interval = 1
    vm.swappiness = 0
    vm.user_reserve_kbytes = 131072
    vm.vfs_cache_pressure = 100
    vm.zone_reclaim_mode = 0

**Services listing**

::

    $ service --status-all
     [ + ]  apparmor
     [ - ]  bootmisc.sh
     [ - ]  checkfs.sh
     [ - ]  checkroot-bootclean.sh
     [ - ]  checkroot.sh
     [ + ]  console-setup
     [ + ]  cpufrequtils
     [ + ]  cron
     [ + ]  dbus
     [ + ]  grub-common
     [ - ]  hostname.sh
     [ - ]  hwclock.sh
     [ + ]  keyboard-setup
     [ - ]  killprocs
     [ + ]  kmod
     [ + ]  loadcpufreq
     [ + ]  lxcfs
     [ - ]  mountall-bootclean.sh
     [ - ]  mountall.sh
     [ - ]  mountdevsubfs.sh
     [ - ]  mountkernfs.sh
     [ - ]  mountnfs-bootclean.sh
     [ - ]  mountnfs.sh
     [ + ]  networking
     [ - ]  ondemand
     [ - ]  plymouth
     [ - ]  plymouth-log
     [ + ]  procps
     [ + ]  qemu-kvm
     [ + ]  rc.local
     [ + ]  resolvconf
     [ - ]  rsync
     [ + ]  rsyslog
     [ - ]  screen-cleanup
     [ - ]  sendsigs
     [ + ]  ssh
     [ + ]  udev
     [ - ]  umountfs
     [ - ]  umountnfs.sh
     [ - ]  umountroot
     [ + ]  urandom
     [ + ]  uuidd
     [ - ]  x11-common

**Host CFS optimizations (QEMU+VPP)**

Applying CFS scheduler tuning on all Qemu vcpu worker threads (those are
handling testpmd - pmd threads) and VPP PMD worker threads. List of VPP PMD
threads can be obtained e.g. from:

::

    $ for psid in $(pgrep vpp)
    $ do
    $     for tid in $(ps -Lo tid --pid $psid | grep -v TID)
    $     do
    $         echo $tid
    $     done
    $ done

Or:

::

    $ cat /proc/`pidof vpp`/task/*/stat | awk '{print $1" "$2" "$39}'

Applying Round-robin scheduling with highest priority

::

    $ for psid in $(pgrep vpp)
    $ do
    $     for tid in $(ps -Lo tid --pid $psid | grep -v TID)
    $     do
    $         chrt -r -p 1 $tid
    $     done
    $ done

More information about Linux CFS can be found in: `Sched manual pages
<http://man7.org/linux/man-pages/man7/sched.7.html>`_.


**Host IRQ affinity**

Changing the default pinning of every IRQ to core 0. (Same does apply on both
guest VM and host OS)

::

    $ for l in `ls /proc/irq`; do echo 1 | sudo tee /proc/irq/$l/smp_affinity; done

**Host RCU affinity**

Changing the default pinning of RCU to core 0. (Same does apply on both guest VM
and host OS)

::

    $ for i in `pgrep rcu[^c]` ; do sudo taskset -pc 0 $i ; done

**Host Writeback affinity**

Changing the default pinning of writebacks to core 0. (Same does apply on both
guest VM and host OS)

::

    $ echo 1 | sudo tee /sys/bus/workqueue/devices/writeback/cpumask


DUT Configuration - VPP
-----------------------

**VPP Version**

|vpp-release|

**VPP Compile Parameters**

`FD.io VPP compile job`_

**VPP Install Parameters**

::

    $ dpkg -i --force-all vpp*

**VPP Startup Configuration**

VPP startup configuration changes per test case with different settings for CPU
cores, rx-queues and no-multi-seg parameter. Startup config is aligned with
applied test case tag:

Tagged by **1T1C**

::

    unix
    {
        cli-listen localhost:5002
        log /tmp/vpe.log
        nodaemon
    }
    cpu
    {
        corelist-workers 2
        main-core 1
    }
    ip6
    {
        heap-size 3G
        hash-buckets 2000000
    }
    heapsize 3G
    dpdk
    {
        dev default
        {
            num-rx-queues 1
        }
        dev 0000:0a:00.0
        dev 0000:0a:00.1
        socket-mem 1024,1024
        no-multi-seg
    }

Tagged by **2T1C**

::

    unix
    {
        cli-listen localhost:5002
        log /tmp/vpe.log
        nodaemon
    }
    cpu
    {
        corelist-workers 2,3
        main-core 1
    }
    ip6
    {
        heap-size 3G
        hash-buckets 2000000
    }
    heapsize 3G
    dpdk
    {
        dev default
        {
            num-rx-queues 1
        }
        dev 0000:0a:00.0
        dev 0000:0a:00.1
        socket-mem 1024,1024
        no-multi-seg
    }

Tagged by **4T4C**

::

    unix
    {
        cli-listen localhost:5002
        log /tmp/vpe.log
        nodaemon
    }
    cpu
    {
        corelist-workers 2,3,4,5
        main-core 1
    }
    ip6
    {
        heap-size 3G
        hash-buckets 2000000
    }
    heapsize 3G
    dpdk
    {
        dev default
        {
            num-rx-queues 2
        }
        dev 0000:0a:00.0
        dev 0000:0a:00.1
        socket-mem 1024,1024
        no-multi-seg
    }


TG Configuration - TRex
-----------------------

**TG Version**

|trex-release|

**DPDK version**

DPDK v17.05

**TG Build Script used**

`TRex intallation`_

**TG Startup Configuration**

::

    $ cat /etc/trex_cfg.yaml
    - port_limit      : 2
      version         : 2
      interfaces      : ["0000:0d:00.0","0000:0d:00.1"]
      port_info       :
        - dest_mac        :   [0x3c,0xfd,0xfe,0x9c,0xee,0xf5]
          src_mac         :   [0x3c,0xfd,0xfe,0x9c,0xee,0xf4]
        - dest_mac        :   [0x3c,0xfd,0xfe,0x9c,0xee,0xf4]
          src_mac         :   [0x3c,0xfd,0xfe,0x9c,0xee,0xf5]

**TG Startup Command**

::

    $ sh -c 'cd <t-rex-install-dir>/scripts/ && sudo nohup ./t-rex-64 -i -c 7 --iom 0 > /dev/null 2>&1 &'> /dev/null

**TG common API - pointer to driver**

`TRex driver`_
