Test Environment
================

To execute performance tests, there are three identical testbeds, each testbed
consists of two SUTs and one TG.

Naming Convention
-----------------

Following naming convention is used within this page to specify physical
connectivity and wiring across defined CSIT testbeds:

- testbedname: testbedN.
- hostname:

  - traffic-generator: tN-tgW.
  - system-under-testX: tN-sutX.

- portnames:

  - tN-tgW-cY/pZ.
  - tN-sutX-cY/pZ.

- where:

  - N - testbed number.
  - tgW - server acts as traffic-generator with W index.
  - sutX - server acts as system-under-test with X index.
  - Y - PCIe slot number denoting a NIC card number within the host.

    - Y=1,2,3 - slots in Riser 1, Right PCIe Riser Board, NUMA node 0.
    - Y=4,5,6 - slots in Riser 2, Left PCIe Riser Board, NUMA node 1.
    - Y=m - the MLOM slot.

  - Z - port number on the NIC card.

Server HW Configuration
-----------------------

CSIT testbed contains following three HW configuration types of UCS x86 servers,
across total of ten servers provided:

#. Type-1: Purpose - VPP functional and performance conformance testing.

   - Quantity: 6 computers as SUT hosts (Systems Under Test).
   - Physical connectivity:

     - CIMC and host management ports.
     - NIC ports connected in 3-node topologies.

   - Main HW configuration:

     - Chassis: UCSC-C240-M4SX with 6 PCIe3.0 slots.
     - Processors: 2* E5-2699 2.3 GHz.
     - RAM Memory: 16* 32GB DDR4-2133MHz.
     - Disks: 2* 2TB 12G SAS 7.2K RPM SFF HDD.

   - NICs configuration:

     - Right PCIe Riser Board (Riser 1) (x8, x8, x8 PCIe3.0 lanes)

       - PCIe Slot1: Cisco VIC 1385 2p40GE.

         - PCIe Slot2: Intel NIC x520 2p10GE.
         - PCIe Slot3: empty.

     - Left PCIe Riser Board (Riser 2) (x8, x16, x8 PCIe3.0 lanes)

       - PCIe Slot4: Intel NIC xl710 2p40GE.
       - PCIe Slot5: Intel NIC x710 2p10GE.
       - PCIe Slot6: Intel QAT 8950 50G (Walnut Hill)

     - MLOM slot: Cisco VIC 1227 2p10GE (x8 PCIe2.0 lanes).

#. Type-2: Purpose - VPP functional and performance conformance testing.

   - Quantity: 3 computers as TG hosts (Traffic Generators).
   - Physical connectivity:

     - CIMC and host management ports.
     - NIC ports connected in 3-node topologies.

   - Main HW configuration:

     - Chassis: UCSC-C240-M4SX with 6 PCIe3.0 slots.
     - Processors: 2* E5-2699 2.3 GHz.
     - RAM Memory: 16* 32GB DDR4-2133MHz.
     - Disks: 2* 2TB 12G SAS 7.2K RPM SFF HDD.

   - NICs configuration:

     - Right PCIe Riser Board (Riser 1) (x8, x8, x8 lanes)

       - PCIe Slot1: Intel NIC xl710 2p40GE.
       - PCIe Slot2: Intel NIC x710 2p10GE.
       - PCIe Slot3: Intel NIC x710 2p10GE.

     - Left PCIe Riser Board (Riser 2) (x8, x16, x8 lanes)

       - PCIe Slot4: Intel NIC xl710 2p40GE.
       - PCIe Slot5: Intel NIC x710 2p10GE.
       - PCIe Slot6: Intel NIC x710 2p10GE.

     - MLOM slot: empty.

#. Type-3: Purpose - VIRL functional conformance.

   - Quantity: 3 computers as VIRL hosts.
   - Physical connectivity:

     - CIMC and host management ports.
     - no NIC ports, standalone setup.

   - Main HW configuration:

     - Chassis: UCSC-C240-M4SX with 6 PCIe3.0 slots.
     - Processors: 2* E5-2699 2.3 GHz.
     - RAM Memory: 16* 32GB DDR4-2133MHz.
     - Disks: 2* 480 GB 2.5inch 6G SATA SSD.

   - NICs configuration:

     - Right PCIe Riser Board (Riser 1) (x8, x8, x8 lanes)

       - no cards.

     - Left PCIe Riser Board (Riser 2) (x8, x16, x8 lanes)

       - no cards.

     - MLOM slot: empty.

SUT Configuration - Host HW
---------------------------
Host hardware details (CPU, memory, NIC layout) and physical topology are
described in detail in `LF FDio CSIT testbed wiki page
<https://wiki.fd.io/view/CSIT/CSIT_LF_testbed>`_.

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

This allows for a total of five ring topologies, each using ports on specific
NIC model, enabling per NIC model benchmarking.

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

Software details (OS, configuration) are described in FD.io wiki `LF FDio CSIT
testbed wiki page <https://wiki.fd.io/view/CSIT/CSIT_LF_testbed>`_.

System provisioning is done by combination of PXE boot unattented install and
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

    $ dpkg -l | grep '^ii' | awk '{print $2 ": " $3}'
    accountsservice: 0.6.40-2ubuntu11.1
    acl: 2.2.52-3
    adduser: 3.113+nmu3ubuntu4
    apparmor: 2.10.95-0ubuntu2.6
    apt: 1.2.12~ubuntu16.04.1
    apt-utils: 1.2.12~ubuntu16.04.1
    autoconf: 2.69-9
    automake: 1:1.15-4ubuntu1
    autotools-dev: 20150820.1
    base-files: 9.4ubuntu4.2
    base-passwd: 3.5.39
    bash: 4.3-14ubuntu1.1
    binutils: 2.26.1-1ubuntu1~16.04.3
    bridge-utils: 1.5-9ubuntu1
    bsdutils: 1:2.27.1-6ubuntu3.1
    build-essential: 12.1ubuntu2
    busybox-initramfs: 1:1.22.0-15ubuntu1
    busybox-static: 1:1.22.0-15ubuntu1
    bzip2: 1.0.6-8
    ca-certificates: 20160104ubuntu1
    ca-certificates-java: 20160321
    cgroup-bin: 0.41-7ubuntu1
    cgroup-lite: 1.11
    cgroup-tools: 0.41-7ubuntu1
    cloud-image-utils: 0.27-0ubuntu24
    console-setup: 1.108ubuntu15.2
    console-setup-linux: 1.108ubuntu15.2
    coreutils: 8.25-2ubuntu2
    cpio: 2.11+dfsg-5ubuntu1
    cpp: 4:5.3.1-1ubuntu1
    cpp-5: 5.4.0-6ubuntu1~16.04.2
    cpu-checker: 0.7-0ubuntu7
    cpufrequtils: 008-1
    crda: 3.13-1
    cron: 3.0pl1-128ubuntu2
    crudini: 0.7-1
    dash: 0.5.8-2.1ubuntu2
    dbus: 1.10.6-1ubuntu3
    debconf: 1.5.58ubuntu1
    debconf-i18n: 1.5.58ubuntu1
    debianutils: 4.7
    debootstrap: 1.0.78+nmu1ubuntu1.3
    dh-python: 2.20151103ubuntu1.1
    diffutils: 1:3.3-3
    distro-info: 0.14build1
    distro-info-data: 0.28ubuntu0.1
    dkms: 2.2.0.3-2ubuntu11.2
    dmidecode: 3.0-2ubuntu0.1
    dns-root-data: 2015052300+h+1
    dnsmasq-base: 2.75-1ubuntu0.16.04.2
    dpkg: 1.18.4ubuntu1.1
    dpkg-dev: 1.18.4ubuntu1.1
    e2fslibs:amd64: 1.42.13-1ubuntu1
    e2fsprogs: 1.42.13-1ubuntu1
    eject: 2.1.5+deb1+cvs20081104-13.1
    expect: 5.45-7
    fakeroot: 1.20.2-1ubuntu1
    file: 1:5.25-2ubuntu1
    findutils: 4.6.0+git+20160126-2
    fontconfig-config: 2.11.94-0ubuntu1.1
    fonts-dejavu-core: 2.35-1
    g++: 4:5.3.1-1ubuntu1
    g++-5: 5.4.0-6ubuntu1~16.04.2
    gcc: 4:5.3.1-1ubuntu1
    gcc-5: 5.4.0-6ubuntu1~16.04.2
    gcc-5-base:amd64: 5.4.0-6ubuntu1~16.04.2
    gcc-6-base:amd64: 6.0.1-0ubuntu1
    genisoimage: 9:1.1.11-3ubuntu1
    gettext-base: 0.19.7-2ubuntu3
    gir1.2-glib-2.0:amd64: 1.46.0-3ubuntu1
    git: 1:2.7.4-0ubuntu1
    git-man: 1:2.7.4-0ubuntu1
    gnupg: 1.4.20-1ubuntu3.1
    gpgv: 1.4.20-1ubuntu3.1
    grep: 2.25-1~16.04.1
    grub-common: 2.02~beta2-36ubuntu3.1
    grub-gfxpayload-lists: 0.7
    grub-pc: 2.02~beta2-36ubuntu3.1
    grub-pc-bin: 2.02~beta2-36ubuntu3.1
    grub2-common: 2.02~beta2-36ubuntu3.1
    gzip: 1.6-4ubuntu1
    hostname: 3.16ubuntu2
    ifupdown: 0.8.10ubuntu1
    init: 1.29ubuntu2
    init-system-helpers: 1.29ubuntu2
    initramfs-tools: 0.122ubuntu8.1
    initramfs-tools-bin: 0.122ubuntu8.1
    initramfs-tools-core: 0.122ubuntu8.1
    initscripts: 2.88dsf-59.3ubuntu2
    insserv: 1.14.0-5ubuntu3
    installation-report: 2.60ubuntu1
    iproute2: 4.3.0-1ubuntu3
    iptables: 1.6.0-2ubuntu3
    iputils-ping: 3:20121221-5ubuntu2
    ipxe-qemu: 1.0.0+git-20150424.a25a16d-1ubuntu1
    isc-dhcp-client: 4.3.3-5ubuntu12.1
    isc-dhcp-common: 4.3.3-5ubuntu12.1
    iso-codes: 3.65-1
    iw: 3.17-1
    java-common: 0.56ubuntu2
    kbd: 1.15.5-1ubuntu4
    keyboard-configuration: 1.108ubuntu15.2
    klibc-utils: 2.0.4-8ubuntu1.16.04.1
    kmod: 22-1ubuntu4
    krb5-locales: 1.13.2+dfsg-5
    language-selector-common: 0.165.3
    laptop-detect: 0.13.7ubuntu2
    less: 481-2.1
    libaccountsservice0:amd64: 0.6.40-2ubuntu11.1
    libacl1:amd64: 2.2.52-3
    libaio1:amd64: 0.3.110-2
    libalgorithm-diff-perl: 1.19.03-1
    libalgorithm-diff-xs-perl: 0.04-4build1
    libalgorithm-merge-perl: 0.08-3
    libapparmor-perl: 2.10.95-0ubuntu2.6
    libapparmor1:amd64: 2.10.95-0ubuntu2
    libapr1:amd64: 1.5.2-3
    libapt-inst2.0:amd64: 1.2.12~ubuntu16.04.1
    libapt-pkg5.0:amd64: 1.2.12~ubuntu16.04.1
    libasan2:amd64: 5.4.0-6ubuntu1~16.04.2
    libasn1-8-heimdal:amd64: 1.7~git20150920+dfsg-4ubuntu1
    libasound2:amd64: 1.1.0-0ubuntu1
    libasound2-data: 1.1.0-0ubuntu1
    libasprintf0v5:amd64: 0.19.7-2ubuntu3
    libasyncns0:amd64: 0.8-5build1
    libatm1:amd64: 1:2.5.1-1.5
    libatomic1:amd64: 5.4.0-6ubuntu1~16.04.2
    libattr1:amd64: 1:2.4.47-2
    libaudit-common: 1:2.4.5-1ubuntu2
    libaudit1:amd64: 1:2.4.5-1ubuntu2
    libavahi-client3:amd64: 0.6.32~rc+dfsg-1ubuntu2
    libavahi-common-data:amd64: 0.6.32~rc+dfsg-1ubuntu2
    libavahi-common3:amd64: 0.6.32~rc+dfsg-1ubuntu2
    libblkid1:amd64: 2.27.1-6ubuntu3.1
    libbluetooth3:amd64: 5.37-0ubuntu5
    libboost-iostreams1.58.0:amd64: 1.58.0+dfsg-5ubuntu3.1
    libboost-random1.58.0:amd64: 1.58.0+dfsg-5ubuntu3.1
    libboost-system1.58.0:amd64: 1.58.0+dfsg-5ubuntu3.1
    libboost-thread1.58.0:amd64: 1.58.0+dfsg-5ubuntu3.1
    libbrlapi0.6:amd64: 5.3.1-2ubuntu2.1
    libbsd0:amd64: 0.8.2-1
    libbz2-1.0:amd64: 1.0.6-8
    libc-bin: 2.23-0ubuntu3
    libc-dev-bin: 2.23-0ubuntu3
    libc6:amd64: 2.23-0ubuntu3
    libc6-dev:amd64: 2.23-0ubuntu3
    libcaca0:amd64: 0.99.beta19-2build2~gcc5.2
    libcacard0:amd64: 1:2.5.0-2
    libcap-ng0:amd64: 0.7.7-1
    libcap2:amd64: 1:2.24-12
    libcap2-bin: 1:2.24-12
    libcc1-0:amd64: 5.4.0-6ubuntu1~16.04.2
    libcgroup1:amd64: 0.41-7ubuntu1
    libcilkrts5:amd64: 5.4.0-6ubuntu1~16.04.2
    libcomerr2:amd64: 1.42.13-1ubuntu1
    libcpufreq0: 008-1
    libcryptsetup4:amd64: 2:1.6.6-5ubuntu2
    libcups2:amd64: 2.1.3-4
    libcurl3-gnutls:amd64: 7.47.0-1ubuntu2.1
    libdb5.3:amd64: 5.3.28-11
    libdbus-1-3:amd64: 1.10.6-1ubuntu3
    libdbus-glib-1-2:amd64: 0.106-1
    libdebconfclient0:amd64: 0.198ubuntu1
    libdevmapper1.02.1:amd64: 2:1.02.110-1ubuntu10
    libdns-export162: 1:9.10.3.dfsg.P4-8ubuntu1.1
    libdpkg-perl: 1.18.4ubuntu1.1
    libdrm-amdgpu1:amd64: 2.4.67-1ubuntu0.16.04.2
    libdrm-intel1:amd64: 2.4.67-1ubuntu0.16.04.2
    libdrm-nouveau2:amd64: 2.4.67-1ubuntu0.16.04.2
    libdrm-radeon1:amd64: 2.4.67-1ubuntu0.16.04.2
    libdrm2:amd64: 2.4.67-1ubuntu0.16.04.2
    libedit2:amd64: 3.1-20150325-1ubuntu2
    libelf1:amd64: 0.165-3ubuntu1
    liberror-perl: 0.17-1.2
    libestr0: 0.1.10-1
    libexpat1:amd64: 2.1.0-7ubuntu0.16.04.2
    libexpat1-dev:amd64: 2.1.0-7ubuntu0.16.04.2
    libfakeroot:amd64: 1.20.2-1ubuntu1
    libfdisk1:amd64: 2.27.1-6ubuntu3.1
    libfdt1:amd64: 1.4.0+dfsg-2
    libffi6:amd64: 3.2.1-4
    libfile-fcntllock-perl: 0.22-3
    libflac8:amd64: 1.3.1-4
    libfontconfig1:amd64: 2.11.94-0ubuntu1.1
    libfontenc1:amd64: 1:1.1.3-1
    libfreetype6:amd64: 2.6.1-0.1ubuntu2
    libfribidi0:amd64: 0.19.7-1
    libfuse2:amd64: 2.9.4-1ubuntu3
    libgcc-5-dev:amd64: 5.4.0-6ubuntu1~16.04.2
    libgcc1:amd64: 1:6.0.1-0ubuntu1
    libgcrypt20:amd64: 1.6.5-2ubuntu0.2
    libgdbm3:amd64: 1.8.3-13.1
    libgirepository-1.0-1:amd64: 1.46.0-3ubuntu1
    libgl1-mesa-dri:amd64: 11.2.0-1ubuntu2.2
    libgl1-mesa-glx:amd64: 11.2.0-1ubuntu2.2
    libglapi-mesa:amd64: 11.2.0-1ubuntu2.2
    libglib2.0-0:amd64: 2.48.1-1~ubuntu16.04.1
    libglib2.0-bin: 2.48.1-1~ubuntu16.04.1
    libglib2.0-data: 2.48.1-1~ubuntu16.04.1
    libglib2.0-dev: 2.48.1-1~ubuntu16.04.1
    libgmp10:amd64: 2:6.1.0+dfsg-2
    libgnutls-openssl27:amd64: 3.4.10-4ubuntu1.1
    libgnutls30:amd64: 3.4.10-4ubuntu1.1
    libgomp1:amd64: 5.4.0-6ubuntu1~16.04.2
    libgpg-error0:amd64: 1.21-2ubuntu1
    libgssapi-krb5-2:amd64: 1.13.2+dfsg-5
    libgssapi3-heimdal:amd64: 1.7~git20150920+dfsg-4ubuntu1
    libhcrypto4-heimdal:amd64: 1.7~git20150920+dfsg-4ubuntu1
    libheimbase1-heimdal:amd64: 1.7~git20150920+dfsg-4ubuntu1
    libheimntlm0-heimdal:amd64: 1.7~git20150920+dfsg-4ubuntu1
    libhogweed4:amd64: 3.2-1
    libhx509-5-heimdal:amd64: 1.7~git20150920+dfsg-4ubuntu1
    libice6:amd64: 2:1.0.9-1
    libicu55:amd64: 55.1-7
    libidn11:amd64: 1.32-3ubuntu1.1
    libisc-export160: 1:9.10.3.dfsg.P4-8ubuntu1.1
    libiscsi2:amd64: 1.12.0-2
    libisl15:amd64: 0.16.1-1
    libitm1:amd64: 5.4.0-6ubuntu1~16.04.2
    libjpeg-turbo8:amd64: 1.4.2-0ubuntu3
    libjpeg8:amd64: 8c-2ubuntu8
    libjson-c2:amd64: 0.11-4ubuntu2
    libk5crypto3:amd64: 1.13.2+dfsg-5
    libkeyutils1:amd64: 1.5.9-8ubuntu1
    libklibc: 2.0.4-8ubuntu1.16.04.1
    libkmod2:amd64: 22-1ubuntu4
    libkrb5-26-heimdal:amd64: 1.7~git20150920+dfsg-4ubuntu1
    libkrb5-3:amd64: 1.13.2+dfsg-5
    libkrb5support0:amd64: 1.13.2+dfsg-5
    liblcms2-2:amd64: 2.6-3ubuntu2
    libldap-2.4-2:amd64: 2.4.42+dfsg-2ubuntu3.1
    libllvm3.8:amd64: 1:3.8-2ubuntu4
    liblocale-gettext-perl: 1.07-1build1
    liblsan0:amd64: 5.4.0-6ubuntu1~16.04.2
    libltdl-dev:amd64: 2.4.6-0.1
    libltdl7:amd64: 2.4.6-0.1
    liblxc1: 2.0.7-0ubuntu1~16.04.2
    liblz4-1:amd64: 0.0~r131-2ubuntu2
    liblzma5:amd64: 5.1.1alpha+20120614-2ubuntu2
    libmagic1:amd64: 1:5.25-2ubuntu1
    libmnl0:amd64: 1.0.3-5
    libmount1:amd64: 2.27.1-6ubuntu3.1
    libmpc3:amd64: 1.0.3-1
    libmpdec2:amd64: 2.4.2-1
    libmpfr4:amd64: 3.1.4-1
    libmpx0:amd64: 5.4.0-6ubuntu1~16.04.2
    libncurses5:amd64: 6.0+20160213-1ubuntu1
    libncursesw5:amd64: 6.0+20160213-1ubuntu1
    libnetfilter-conntrack3:amd64: 1.0.5-1
    libnettle6:amd64: 3.2-1
    libnewt0.52:amd64: 0.52.18-1ubuntu2
    libnfnetlink0:amd64: 1.0.1-3
    libnih-dbus1:amd64: 1.0.3-4.3ubuntu1
    libnih1:amd64: 1.0.3-4.3ubuntu1
    libnl-3-200:amd64: 3.2.27-1
    libnl-genl-3-200:amd64: 3.2.27-1
    libnspr4:amd64: 2:4.12-0ubuntu0.16.04.1
    libnss3:amd64: 2:3.23-0ubuntu0.16.04.1
    libnss3-nssdb: 2:3.23-0ubuntu0.16.04.1
    libnuma1:amd64: 2.0.11-1ubuntu1
    libogg0:amd64: 1.3.2-1
    libopus0:amd64: 1.1.2-1ubuntu1
    libp11-kit0:amd64: 0.23.2-3
    libpam-cgfs: 2.0.6-0ubuntu1~16.04.1
    libpam-modules:amd64: 1.1.8-3.2ubuntu2
    libpam-modules-bin: 1.1.8-3.2ubuntu2
    libpam-runtime: 1.1.8-3.2ubuntu2
    libpam0g:amd64: 1.1.8-3.2ubuntu2
    libpcap-dev: 1.7.4-2
    libpcap0.8:amd64: 1.7.4-2
    libpcap0.8-dev: 1.7.4-2
    libpci3:amd64: 1:3.3.1-1.1ubuntu1
    libpciaccess0:amd64: 0.13.4-1
    libpcre16-3:amd64: 2:8.38-3.1
    libpcre3:amd64: 2:8.38-3.1
    libpcre3-dev:amd64: 2:8.38-3.1
    libpcre32-3:amd64: 2:8.38-3.1
    libpcrecpp0v5:amd64: 2:8.38-3.1
    libpcsclite1:amd64: 1.8.14-1ubuntu1.16.04.1
    libperl5.22:amd64: 5.22.1-9
    libpixman-1-0:amd64: 0.33.6-1
    libplymouth4:amd64: 0.9.2-3ubuntu13.1
    libpng12-0:amd64: 1.2.54-1ubuntu1
    libpolkit-gobject-1-0:amd64: 0.105-14.1
    libpopt0:amd64: 1.16-10
    libprocps4:amd64: 2:3.3.10-4ubuntu2
    libpulse0:amd64: 1:8.0-0ubuntu3
    libpython-all-dev:amd64: 2.7.11-1
    libpython-dev:amd64: 2.7.11-1
    libpython-stdlib:amd64: 2.7.11-1
    libpython2.7:amd64: 2.7.12-1~16.04
    libpython2.7-dev:amd64: 2.7.12-1~16.04
    libpython2.7-minimal:amd64: 2.7.12-1~16.04
    libpython2.7-stdlib:amd64: 2.7.12-1~16.04
    libpython3-stdlib:amd64: 3.5.1-3
    libpython3.5-minimal:amd64: 3.5.2-2~16.01
    libpython3.5-stdlib:amd64: 3.5.2-2~16.01
    libquadmath0:amd64: 5.4.0-6ubuntu1~16.04.2
    librados2: 10.2.2-0ubuntu0.16.04.2
    librbd1: 10.2.2-0ubuntu0.16.04.2
    libreadline6:amd64: 6.3-8ubuntu2
    libroken18-heimdal:amd64: 1.7~git20150920+dfsg-4ubuntu1
    librtmp1:amd64: 2.4+20151223.gitfa8646d-1build1
    libsasl2-2:amd64: 2.1.26.dfsg1-14build1
    libsasl2-modules:amd64: 2.1.26.dfsg1-14build1
    libsasl2-modules-db:amd64: 2.1.26.dfsg1-14build1
    libsdl1.2debian:amd64: 1.2.15+dfsg1-3
    libseccomp2:amd64: 2.2.3-3ubuntu3
    libselinux1:amd64: 2.4-3build2
    libsemanage-common: 2.3-1build3
    libsemanage1:amd64: 2.3-1build3
    libsepol1:amd64: 2.4-2
    libsigsegv2:amd64: 2.10-4
    libslang2:amd64: 2.3.0-2ubuntu1
    libsm6:amd64: 2:1.2.2-1
    libsmartcols1:amd64: 2.27.1-6ubuntu3.1
    libsndfile1:amd64: 1.0.25-10
    libspice-server1:amd64: 0.12.6-4ubuntu0.1
    libsqlite3-0:amd64: 3.11.0-1ubuntu1
    libss2:amd64: 1.42.13-1ubuntu1
    libssl1.0.0:amd64: 1.0.2g-1ubuntu4.5
    libstdc++-5-dev:amd64: 5.4.0-6ubuntu1~16.04.2
    libstdc++6:amd64: 5.4.0-6ubuntu1~16.04.2
    libsystemd0:amd64: 229-4ubuntu10
    libtasn1-6:amd64: 4.7-3ubuntu0.16.04.1
    libtcl8.6:amd64: 8.6.5+dfsg-2
    libtext-charwidth-perl: 0.04-7build5
    libtext-iconv-perl: 1.7-5build4
    libtext-wrapi18n-perl: 0.06-7.1
    libtinfo5:amd64: 6.0+20160213-1ubuntu1
    libtk8.6:amd64: 8.6.5-1
    libtool: 2.4.6-0.1
    libtsan0:amd64: 5.4.0-6ubuntu1~16.04.2
    libtxc-dxtn-s2tc0:amd64: 0~git20131104-1.1
    libubsan0:amd64: 5.4.0-6ubuntu1~16.04.2
    libudev1:amd64: 229-4ubuntu10
    libusb-0.1-4:amd64: 2:0.1.12-28
    libusb-1.0-0:amd64: 2:1.0.20-1
    libusbredirparser1:amd64: 0.7.1-1
    libustr-1.0-1:amd64: 1.0.4-5
    libutempter0:amd64: 1.1.6-3
    libuuid1:amd64: 2.27.1-6ubuntu3.1
    libvorbis0a:amd64: 1.3.5-3
    libvorbisenc2:amd64: 1.3.5-3
    libwind0-heimdal:amd64: 1.7~git20150920+dfsg-4ubuntu1
    libwrap0:amd64: 7.6.q-25
    libx11-6:amd64: 2:1.6.3-1ubuntu2
    libx11-data: 2:1.6.3-1ubuntu2
    libx11-xcb1:amd64: 2:1.6.3-1ubuntu2
    libxau6:amd64: 1:1.0.8-1
    libxaw7:amd64: 2:1.0.13-1
    libxcb-dri2-0:amd64: 1.11.1-1ubuntu1
    libxcb-dri3-0:amd64: 1.11.1-1ubuntu1
    libxcb-glx0:amd64: 1.11.1-1ubuntu1
    libxcb-present0:amd64: 1.11.1-1ubuntu1
    libxcb-shape0:amd64: 1.11.1-1ubuntu1
    libxcb-sync1:amd64: 1.11.1-1ubuntu1
    libxcb1:amd64: 1.11.1-1ubuntu1
    libxcomposite1:amd64: 1:0.4.4-1
    libxdamage1:amd64: 1:1.1.4-2
    libxdmcp6:amd64: 1:1.1.2-1.1
    libxen-4.6:amd64: 4.6.0-1ubuntu4.2
    libxenstore3.0:amd64: 4.6.0-1ubuntu4.2
    libxext6:amd64: 2:1.3.3-1
    libxfixes3:amd64: 1:5.0.1-2
    libxft2:amd64: 2.3.2-1
    libxi6:amd64: 2:1.7.6-1
    libxinerama1:amd64: 2:1.1.3-1
    libxml2:amd64: 2.9.3+dfsg1-1ubuntu0.1
    libxmu6:amd64: 2:1.1.2-2
    libxmuu1:amd64: 2:1.1.2-2
    libxpm4:amd64: 1:3.5.11-1
    libxrandr2:amd64: 2:1.5.0-1
    libxrender1:amd64: 1:0.9.9-0ubuntu1
    libxshmfence1:amd64: 1.2-1
    libxss1:amd64: 1:1.2.2-1
    libxt6:amd64: 1:1.1.5-0ubuntu1
    libxtables11:amd64: 1.6.0-2ubuntu3
    libxtst6:amd64: 2:1.2.2-1
    libxv1:amd64: 2:1.0.10-1
    libxxf86dga1:amd64: 2:1.1.4-1
    libxxf86vm1:amd64: 1:1.1.4-1
    libyajl2:amd64: 2.1.0-2
    linux-base: 4.0ubuntu1
    linux-firmware: 1.157.2
    linux-generic: 4.4.0.72.78
    linux-headers-4.4.0-72: 4.4.0-72.93
    linux-headers-4.4.0-72-generic: 4.4.0-72.93
    linux-headers-generic: 4.4.0.72.78
    linux-image-4.4.0-72-generic: 4.4.0-72.93
    linux-image-extra-4.4.0-72-generic: 4.4.0-72.93
    linux-image-generic: 4.4.0.72.78
    linux-libc-dev:amd64: 4.4.0-72.93
    locales: 2.23-0ubuntu3
    login: 1:4.2-3.1ubuntu5
    logrotate: 3.8.7-2ubuntu2
    lsb-base: 9.20160110ubuntu0.2
    lsb-release: 9.20160110ubuntu0.2
    lxc: 2.0.7-0ubuntu1~16.04.2
    lxc-common: 2.0.7-0ubuntu1~16.04.2
    lxc-templates: 2.0.7-0ubuntu1~16.04.2
    lxc1: 2.0.7-0ubuntu1~16.04.2
    lxcfs: 2.0.6-0ubuntu1~16.04.1
    m4: 1.4.17-5
    make: 4.1-6
    makedev: 2.3.1-93ubuntu1
    manpages: 4.04-2
    manpages-dev: 4.04-2
    mawk: 1.3.3-17ubuntu2
    mime-support: 3.59ubuntu1
    mount: 2.27.1-6ubuntu3.1
    mountall: 2.54ubuntu1
    msr-tools: 1.3-2
    multiarch-support: 2.23-0ubuntu3
    ncurses-base: 6.0+20160213-1ubuntu1
    ncurses-bin: 6.0+20160213-1ubuntu1
    ncurses-term: 6.0+20160213-1ubuntu1
    net-tools: 1.60-26ubuntu1
    netbase: 5.3
    netcat-openbsd: 1.105-7ubuntu1
    openjdk-8-jre-headless:amd64: 8u131-b11-0ubuntu1.16.04.2
    openssh-client: 1:7.2p2-4ubuntu2.1
    openssh-server: 1:7.2p2-4ubuntu2.1
    openssh-sftp-server: 1:7.2p2-4ubuntu2.1
    openssl: 1.0.2g-1ubuntu4.5
    os-prober: 1.70ubuntu3
    passwd: 1:4.2-3.1ubuntu5
    patch: 2.7.5-1
    pciutils: 1:3.3.1-1.1ubuntu1
    perl: 5.22.1-9
    perl-base: 5.22.1-9
    perl-modules-5.22: 5.22.1-9
    pkg-config: 0.29.1-0ubuntu1
    plymouth: 0.9.2-3ubuntu13.1
    plymouth-theme-ubuntu-text: 0.9.2-3ubuntu13.1
    procps: 2:3.3.10-4ubuntu2
    python: 2.7.11-1
    python-all: 2.7.11-1
    python-all-dev: 2.7.11-1
    python-apt: 1.1.0~beta1build1
    python-apt-common: 1.1.0~beta1build1
    python-dev: 2.7.11-1
    python-iniparse: 0.4-2.2
    python-minimal: 2.7.11-1
    python-pip: 8.1.1-2ubuntu0.2
    python-pip-whl: 8.1.1-2ubuntu0.2
    python-pkg-resources: 20.7.0-1
    python-setuptools: 20.7.0-1
    python-six: 1.10.0-3
    python-virtualenv: 15.0.1+ds-3
    python-wheel: 0.29.0-1
    python2.7: 2.7.12-1~16.04
    python2.7-dev: 2.7.12-1~16.04
    python2.7-minimal: 2.7.12-1~16.04
    python3: 3.5.1-3
    python3-apt: 1.1.0~beta1build1
    python3-chardet: 2.3.0-2
    python3-dbus: 1.2.0-3
    python3-gi: 3.20.0-0ubuntu1
    python3-lxc: 2.0.7-0ubuntu1~16.04.2
    python3-minimal: 3.5.1-3
    python3-pkg-resources: 20.7.0-1
    python3-requests: 2.9.1-3
    python3-six: 1.10.0-3
    python3-urllib3: 1.13.1-2ubuntu0.16.04.1
    python3-virtualenv: 15.0.1+ds-3
    python3.5: 3.5.2-2~16.01
    python3.5-minimal: 3.5.2-2~16.01
    qemu-block-extra:amd64: 1:2.5+dfsg-5ubuntu10.5
    qemu-system-common: 1:2.5+dfsg-5ubuntu10.5
    qemu-system-x86: 1:2.5+dfsg-5ubuntu10.5
    qemu-utils: 1:2.5+dfsg-5ubuntu10.5
    readline-common: 6.3-8ubuntu2
    rename: 0.20-4
    resolvconf: 1.78ubuntu2
    rsync: 3.1.1-3ubuntu1
    rsyslog: 8.16.0-1ubuntu3
    screen: 4.3.1-2build1
    seabios: 1.8.2-1ubuntu1
    sed: 4.2.2-7
    sensible-utils: 0.0.9
    sgml-base: 1.26+nmu4ubuntu1
    shared-mime-info: 1.5-2ubuntu0.1
    sharutils: 1:4.15.2-1
    socat: 1.7.3.1-1
    ssh-import-id: 5.5-0ubuntu1
    sudo: 1.8.16-0ubuntu1.1
    systemd: 229-4ubuntu10
    systemd-sysv: 229-4ubuntu10
    sysv-rc: 2.88dsf-59.3ubuntu2
    sysvinit-utils: 2.88dsf-59.3ubuntu2
    tar: 1.28-2.1
    tasksel: 3.34ubuntu3
    tasksel-data: 3.34ubuntu3
    tcl-expect:amd64: 5.45-7
    tcl8.6: 8.6.5+dfsg-2
    tcpd: 7.6.q-25
    tk8.6: 8.6.5-1
    tzdata: 2016g-0ubuntu0.16.04
    ubuntu-keyring: 2012.05.19
    ubuntu-minimal: 1.361
    ucf: 3.0036
    udev: 229-4ubuntu10
    uidmap: 1:4.2-3.1ubuntu5.3
    ureadahead: 0.100.0-19
    usbutils: 1:007-4
    util-linux: 2.27.1-6ubuntu3.1
    uuid-runtime: 2.27.1-6ubuntu3.2
    vim-common: 2:7.4.1689-3ubuntu1.1
    vim-tiny: 2:7.4.1689-3ubuntu1.1
    virtualenv: 15.0.1+ds-3
    vpp: 17.10-rc0~89-g7c35f19~b2621
    vpp-dbg: 17.10-rc0~89-g7c35f19~b2621
    vpp-dev: 17.10-rc0~89-g7c35f19~b2621
    vpp-dpdk-dkms: 17.05-vpp6
    vpp-lib: 17.10-rc0~89-g7c35f19~b2621
    vpp-plugins: 17.10-rc0~89-g7c35f19~b2621
    wamerican: 7.1-1
    wget: 1.17.1-1ubuntu1.1
    whiptail: 0.52.18-1ubuntu2
    wireless-regdb: 2015.07.20-1ubuntu1
    x11-common: 1:7.7+13ubuntu3
    x11-utils: 7.7+3
    xauth: 1:1.0.9-1ubuntu2
    xbitmaps: 1.1.1-2
    xdg-user-dirs: 0.15-2ubuntu6
    xkb-data: 2.16-1ubuntu1
    xml-core: 0.13+nmu2
    xterm: 322-1ubuntu1
    xz-utils: 5.1.1alpha+20120614-2ubuntu2
    zlib1g:amd64: 1:1.2.8.dfsg-2ubuntu4
    zlib1g-dev:amd64: 1:1.2.8.dfsg-2ubuntu4

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

DUT Configuration - DPDK
------------------------

**DPDK Version**

|dpdk-release|

**DPDK Compile Parameters**

.. code-block:: bash

    make install T=x86_64-native-linuxapp-gcc -j

**Testpmd Startup Configuration**

Testpmd startup configuration changes per test case with different settings for CPU
cores, rx-queues. Startup config is aligned with applied test case tag:

Tagged by **1T1C**

.. code-block:: bash

    testpmd -c 0x3 -n 4 -- --numa --nb-ports=2 --portmask=0x3 --nb-cores=1 --max-pkt-len=9000 --txqflags=0 --forward-mode=io --rxq=1 --txq=1 --burst=64 --rxd=1024 --txd=1024 --disable-link-check --auto-start

Tagged by **2T2C**

.. code-block:: bash

    testpmd -c 0x403 -n 4 -- --numa --nb-ports=2 --portmask=0x3 --nb-cores=2 --max-pkt-len=9000 --txqflags=0 --forward-mode=io --rxq=1 --txq=1 --burst=64 --rxd=1024 --txd=1024 --disable-link-check --auto-start

Tagged by **4T4C**

.. code-block:: bash

    testpmd -c 0xc07 -n 4 -- --numa --nb-ports=2 --portmask=0x3 --nb-cores=4 --max-pkt-len=9000 --txqflags=0 --forward-mode=io --rxq=2 --txq=2 --burst=64 --rxd=1024 --txd=1024 --disable-link-check --auto-start

**L3FWD Startup Configuration**

L3FWD startup configuration changes per test case with different settings for CPU
cores, rx-queues. Startup config is aligned with applied test case tag:

Tagged by **1T1C**

.. code-block:: bash

    l3fwd -l 1 -n 4 -- -P -L -p 0x3 --config='${port_config}' --enable-jumbo --max-pkt-len=9000 --eth-dest=0,${adj_mac0} --eth-dest=1,${adj_mac1} --parse-ptype

Tagged by **2T2C**

.. code-block:: bash

    l3fwd -l 1,2 -n 4 -- -P -L -p 0x3 --config='${port_config}' --enable-jumbo --max-pkt-len=9000 --eth-dest=0,${adj_mac0} --eth-dest=1,${adj_mac1} --parse-ptype

Tagged by **4T4C**

.. code-block:: bash

    l3fwd -l 1,2,3,4 -n 4 -- -P -L -p 0x3 --config='${port_config}' --enable-jumbo --max-pkt-len=9000 --eth-dest=0,${adj_mac0} --eth-dest=1,${adj_mac1} --parse-ptype

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
