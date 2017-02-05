Test Environment
================

To execute performance tests, there are three identical testbeds, each testbed
consists of two SUTs and one TG.

SUT Configuration - Host HW
---------------------------
Hardware details (CPU, memory, NIC layout) are described in
`CSIT/CSIT_LF_testbed <https://wiki.fd.io/view/CSIT/CSIT_LF_testbed>`_ in
summary:

- All hosts are Cisco UCS C240-M4 (2x Intel(R) Xeon(R) CPU E5-2699 v3 @ 2.30GHz,
  18c, 512GB RAM),
- BIOS settings are default except for the following:

  - Hyperthreading disabled,
  - SpeedStep disabled
  - TurboBoost disabled
  - Power Technology: Performance

- Hosts run Ubuntu 16.04.1, kernel 4.4.0-42-generic
- Linux kernel boot command line option "intel_pstate=disable" is applied to
  both SUTs and TG. In addition, on SUTs, only cores 0 and 18 (the first core on
  each socket) are available to the Linux operating system and generic tasks,
  all other CPU cores are isolated and reserved for VPP.
- In addition to CIMC and Management, each TG has 4x Intel X710 10GB NIC
  (=8 ports) and 2x Intel XL710 40GB NIC (=4 ports), whereas each SUT has:

  - 1x Intel X520 NIC (10GB, 2 ports),
  - 1x Cisco VIC 1385 (40GB, 2 ports),
  - 1x Intel XL710 NIC (40GB, 2 ports),
  - 1x Intel X710 NIC (10GB, 2 ports),
  - 1x Cisco VIC 1227 (10GB, 2 ports).
  - This allows for a total of five ring topologies, each using ports on
    specific NIC model, enabling per NIC model benchmarking.

**NIC types**

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

Software details (OS, configuration) is described in
`CSIT/CSIT_LF_testbed <https://wiki.fd.io/view/CSIT/CSIT_LF_testbed>`_ in
summary:

.. code-block:: xml

  <stack host="10.30.51.17" script_version="2.1.0">
    <section id="2" name="Compute Hardware">
      <function id="linux_cpupower_frequency_info" significance="1" time="2017-01-27 13:58:10.758131 UTC" version="1.0.0">
        <exec_command><![CDATA[sudo cpupower -c all frequency-info]]></exec_command>
        <exec_return_code>1</exec_return_code>
        <exec_output><![CDATA[sudo: cpupower: command not found
  ]]></exec_output>
      </function>
      <function id="linux_cpupower_idle_info" significance="1" time="2017-01-27 13:58:11.816988 UTC" version="1.0.0">
        <exec_command><![CDATA[sudo cpupower -c all idle-info]]></exec_command>
        <exec_return_code>1</exec_return_code>
        <exec_output><![CDATA[sudo: cpupower: command not found
  ]]></exec_output>
      </function>
      <function id="linux_ethtool" significance="1" time="2017-01-27 13:58:12.508041 UTC" version="1.0.0">
        <exec_command><![CDATA[for x in `ifconfig | grep Ethernet | awk '{print $1}'`; do ethtool -k $x; done]]></exec_command>
        <exec_return_code>0</exec_return_code>
        <exec_output><![CDATA[Features for enp23s0f0:
  rx-checksumming: on
  tx-checksumming: on
  	tx-checksum-ipv4: on
  	tx-checksum-ip-generic: off [fixed]
  	tx-checksum-ipv6: on
  	tx-checksum-fcoe-crc: off [fixed]
  	tx-checksum-sctp: on
  scatter-gather: on
  	tx-scatter-gather: on
  	tx-scatter-gather-fraglist: off [fixed]
  tcp-segmentation-offload: on
  	tx-tcp-segmentation: on
  	tx-tcp-ecn-segmentation: off [fixed]
  	tx-tcp6-segmentation: on
  udp-fragmentation-offload: off [fixed]
  generic-segmentation-offload: on
  generic-receive-offload: on
  large-receive-offload: off [fixed]
  rx-vlan-offload: on
  tx-vlan-offload: on
  ntuple-filters: off [fixed]
  receive-hashing: on
  highdma: on [fixed]
  rx-vlan-filter: on [fixed]
  vlan-challenged: off [fixed]
  tx-lockless: off [fixed]
  netns-local: off [fixed]
  tx-gso-robust: off [fixed]
  tx-fcoe-segmentation: off [fixed]
  tx-gre-segmentation: off [fixed]
  tx-ipip-segmentation: off [fixed]
  tx-sit-segmentation: off [fixed]
  tx-udp_tnl-segmentation: off [fixed]
  fcoe-mtu: off [fixed]
  tx-nocache-copy: off
  loopback: off [fixed]
  rx-fcs: off [fixed]
  rx-all: off
  tx-vlan-stag-hw-insert: off [fixed]
  rx-vlan-stag-hw-parse: off [fixed]
  rx-vlan-stag-filter: off [fixed]
  l2-fwd-offload: off [fixed]
  busy-poll: off [fixed]
  hw-tc-offload: off [fixed]
  ]]></exec_output>
      </function>
      <function id="linux_lscpu" significance="1" time="2017-01-27 13:58:13.481910 UTC" version="1.0.0">
        <exec_command><![CDATA[lscpu]]></exec_command>
        <exec_return_code>0</exec_return_code>
        <exec_output><![CDATA[Architecture:          x86_64
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
  CPU MHz:               2294.513
  BogoMIPS:              4590.41
  Virtualization:        VT-x
  L1d cache:             32K
  L1i cache:             32K
  L2 cache:              256K
  L3 cache:              46080K
  NUMA node0 CPU(s):     0-17
  NUMA node1 CPU(s):     18-35
  Flags:                 fpu vme de pse tsc msr pae mce cx8 apic sep mtrr pge mca cmov pat pse36 clflush dts acpi mmx fxsr sse sse2 ss ht tm pbe syscall nx pdpe1gb rdtscp lm constant_tsc arch_perfmon pebs bts rep_good nopl xtopology nonstop_tsc aperfmperf eagerfpu pni pclmulqdq dtes64 monitor ds_cpl vmx smx est tm2 ssse3 sdbg fma cx16 xtpr pdcm pcid dca sse4_1 sse4_2 x2apic movbe popcnt tsc_deadline_timer aes xsave avx f16c rdrand lahf_lm abm epb tpr_shadow vnmi flexpriority ept vpid fsgsbase tsc_adjust bmi1 avx2 smep bmi2 erms invpcid cqm xsaveopt cqm_llc cqm_occup_llc dtherm arat pln pts
  ]]></exec_output>
      </function>
      <function id="linux_meminfo" significance="1" time="2017-01-27 13:58:15.661517 UTC" version="1.0.0">
        <exec_command><![CDATA[cat /sys/devices/system/node/node*/meminfo]]></exec_command>
        <exec_return_code>0</exec_return_code>
        <exec_output><![CDATA[Node 0 MemTotal:       264048292 kB
  Node 0 MemFree:        258531344 kB
  Node 0 MemUsed:         5516948 kB
  Node 0 Active:           565156 kB
  Node 0 Inactive:         201140 kB
  Node 0 Active(anon):      97256 kB
  Node 0 Inactive(anon):    31188 kB
  Node 0 Active(file):     467900 kB
  Node 0 Inactive(file):   169952 kB
  Node 0 Unevictable:           0 kB
  Node 0 Mlocked:               0 kB
  Node 0 Dirty:                 0 kB
  Node 0 Writeback:             0 kB
  Node 0 FilePages:        749876 kB
  Node 0 Mapped:            15532 kB
  Node 0 AnonPages:         16444 kB
  Node 0 Shmem:            112028 kB
  Node 0 KernelStack:        3664 kB
  Node 0 PageTables:         1184 kB
  Node 0 NFS_Unstable:          0 kB
  Node 0 Bounce:                0 kB
  Node 0 WritebackTmp:          0 kB
  Node 0 Slab:              71912 kB
  Node 0 SReclaimable:      43316 kB
  Node 0 SUnreclaim:        28596 kB
  Node 0 AnonHugePages:      8192 kB
  Node 0 HugePages_Total:  2048
  Node 0 HugePages_Free:   1536
  Node 0 HugePages_Surp:      0
  Node 1 MemTotal:       264237596 kB
  Node 1 MemFree:        254311164 kB
  Node 1 MemUsed:         9926432 kB
  Node 1 Active:          3634328 kB
  Node 1 Inactive:        1564088 kB
  Node 1 Active(anon):    3180500 kB
  Node 1 Inactive(anon):  1461588 kB
  Node 1 Active(file):     453828 kB
  Node 1 Inactive(file):   102500 kB
  Node 1 Unevictable:           0 kB
  Node 1 Mlocked:               0 kB
  Node 1 Dirty:                 8 kB
  Node 1 Writeback:             0 kB
  Node 1 FilePages:       4764096 kB
  Node 1 Mapped:            97676 kB
  Node 1 AnonPages:        434320 kB
  Node 1 Shmem:           4207768 kB
  Node 1 KernelStack:        2432 kB
  Node 1 PageTables:         2076 kB
  Node 1 NFS_Unstable:          0 kB
  Node 1 Bounce:                0 kB
  Node 1 WritebackTmp:          0 kB
  Node 1 Slab:              75920 kB
  Node 1 SReclaimable:      51532 kB
  Node 1 SUnreclaim:        24388 kB
  Node 1 AnonHugePages:    411648 kB
  Node 1 HugePages_Total:  2048
  Node 1 HugePages_Free:   1536
  Node 1 HugePages_Surp:      0
  ]]></exec_output>
      </function>
      <function id="linux_proc_cpuinfo" significance="1" time="2017-01-27 13:58:17.476109 UTC" version="1.0.0">
        <exec_command><![CDATA[cat /proc/cpuinfo]]></exec_command>
        <exec_return_code>0</exec_return_code>
        <exec_output><![CDATA[processor	: 0
  vendor_id	: GenuineIntel
  cpu family	: 6
  model		: 63
  model name	: Intel(R) Xeon(R) CPU E5-2699 v3 @ 2.30GHz
  stepping	: 2
  microcode	: 0x35
  cpu MHz		: 2294.513
  cache size	: 46080 KB
  physical id	: 0
  siblings	: 18
  core id		: 0
  cpu cores	: 18
  apicid		: 0
  initial apicid	: 0
  fpu		: yes
  fpu_exception	: yes
  cpuid level	: 15
  wp		: yes
  flags		: fpu vme de pse tsc msr pae mce cx8 apic sep mtrr pge mca cmov pat pse36 clflush dts acpi mmx fxsr sse sse2 ss ht tm pbe syscall nx pdpe1gb rdtscp lm constant_tsc arch_perfmon pebs bts rep_good nopl xtopology nonstop_tsc aperfmperf eagerfpu pni pclmulqdq dtes64 monitor ds_cpl vmx smx est tm2 ssse3 sdbg fma cx16 xtpr pdcm pcid dca sse4_1 sse4_2 x2apic movbe popcnt tsc_deadline_timer aes xsave avx f16c rdrand lahf_lm abm epb tpr_shadow vnmi flexpriority ept vpid fsgsbase tsc_adjust bmi1 avx2 smep bmi2 erms invpcid cqm xsaveopt cqm_llc cqm_occup_llc dtherm arat pln pts
  bugs		:
  bogomips	: 4589.02
  clflush size	: 64
  cache_alignment	: 64
  address sizes	: 46 bits physical, 48 bits virtual
  power management:

  processor	: 1
  vendor_id	: GenuineIntel
  cpu family	: 6
  model		: 63
  model name	: Intel(R) Xeon(R) CPU E5-2699 v3 @ 2.30GHz
  stepping	: 2
  microcode	: 0x35
  cpu MHz		: 2294.513
  cache size	: 46080 KB
  physical id	: 0
  siblings	: 18
  core id		: 1
  cpu cores	: 18
  apicid		: 2
  initial apicid	: 2
  fpu		: yes
  fpu_exception	: yes
  cpuid level	: 15
  wp		: yes
  flags		: fpu vme de pse tsc msr pae mce cx8 apic sep mtrr pge mca cmov pat pse36 clflush dts acpi mmx fxsr sse sse2 ss ht tm pbe syscall nx pdpe1gb rdtscp lm constant_tsc arch_perfmon pebs bts rep_good nopl xtopology nonstop_tsc aperfmperf eagerfpu pni pclmulqdq dtes64 monitor ds_cpl vmx smx est tm2 ssse3 sdbg fma cx16 xtpr pdcm pcid dca sse4_1 sse4_2 x2apic movbe popcnt tsc_deadline_timer aes xsave avx f16c rdrand lahf_lm abm epb tpr_shadow vnmi flexpriority ept vpid fsgsbase tsc_adjust bmi1 avx2 smep bmi2 erms invpcid cqm xsaveopt cqm_llc cqm_occup_llc dtherm arat pln pts
  bugs		:
  bogomips	: 4589.02
  clflush size	: 64
  cache_alignment	: 64
  address sizes	: 46 bits physical, 48 bits virtual
  power management:

  processor	: 2
  vendor_id	: GenuineIntel
  cpu family	: 6
  model		: 63
  model name	: Intel(R) Xeon(R) CPU E5-2699 v3 @ 2.30GHz
  stepping	: 2
  microcode	: 0x35
  cpu MHz		: 2294.513
  cache size	: 46080 KB
  physical id	: 0
  siblings	: 18
  core id		: 2
  cpu cores	: 18
  apicid		: 4
  initial apicid	: 4
  fpu		: yes
  fpu_exception	: yes
  cpuid level	: 15
  wp		: yes
  flags		: fpu vme de pse tsc msr pae mce cx8 apic sep mtrr pge mca cmov pat pse36 clflush dts acpi mmx fxsr sse sse2 ss ht tm pbe syscall nx pdpe1gb rdtscp lm constant_tsc arch_perfmon pebs bts rep_good nopl xtopology nonstop_tsc aperfmperf eagerfpu pni pclmulqdq dtes64 monitor ds_cpl vmx smx est tm2 ssse3 sdbg fma cx16 xtpr pdcm pcid dca sse4_1 sse4_2 x2apic movbe popcnt tsc_deadline_timer aes xsave avx f16c rdrand lahf_lm abm epb tpr_shadow vnmi flexpriority ept vpid fsgsbase tsc_adjust bmi1 avx2 smep bmi2 erms invpcid cqm xsaveopt cqm_llc cqm_occup_llc dtherm arat pln pts
  bugs		:
  bogomips	: 4589.02
  clflush size	: 64
  cache_alignment	: 64
  address sizes	: 46 bits physical, 48 bits virtual
  power management:

  processor	: 3
  vendor_id	: GenuineIntel
  cpu family	: 6
  model		: 63
  model name	: Intel(R) Xeon(R) CPU E5-2699 v3 @ 2.30GHz
  stepping	: 2
  microcode	: 0x35
  cpu MHz		: 2294.513
  cache size	: 46080 KB
  physical id	: 0
  siblings	: 18
  core id		: 3
  cpu cores	: 18
  apicid		: 6
  initial apicid	: 6
  fpu		: yes
  fpu_exception	: yes
  cpuid level	: 15
  wp		: yes
  flags		: fpu vme de pse tsc msr pae mce cx8 apic sep mtrr pge mca cmov pat pse36 clflush dts acpi mmx fxsr sse sse2 ss ht tm pbe syscall nx pdpe1gb rdtscp lm constant_tsc arch_perfmon pebs bts rep_good nopl xtopology nonstop_tsc aperfmperf eagerfpu pni pclmulqdq dtes64 monitor ds_cpl vmx smx est tm2 ssse3 sdbg fma cx16 xtpr pdcm pcid dca sse4_1 sse4_2 x2apic movbe popcnt tsc_deadline_timer aes xsave avx f16c rdrand lahf_lm abm epb tpr_shadow vnmi flexpriority ept vpid fsgsbase tsc_adjust bmi1 avx2 smep bmi2 erms invpcid cqm xsaveopt cqm_llc cqm_occup_llc dtherm arat pln pts
  bugs		:
  bogomips	: 4589.02
  clflush size	: 64
  cache_alignment	: 64
  address sizes	: 46 bits physical, 48 bits virtual
  power management:

  processor	: 4
  vendor_id	: GenuineIntel
  cpu family	: 6
  model		: 63
  model name	: Intel(R) Xeon(R) CPU E5-2699 v3 @ 2.30GHz
  stepping	: 2
  microcode	: 0x35
  cpu MHz		: 2294.513
  cache size	: 46080 KB
  physical id	: 0
  siblings	: 18
  core id		: 4
  cpu cores	: 18
  apicid		: 8
  initial apicid	: 8
  fpu		: yes
  fpu_exception	: yes
  cpuid level	: 15
  wp		: yes
  flags		: fpu vme de pse tsc msr pae mce cx8 apic sep mtrr pge mca cmov pat pse36 clflush dts acpi mmx fxsr sse sse2 ss ht tm pbe syscall nx pdpe1gb rdtscp lm constant_tsc arch_perfmon pebs bts rep_good nopl xtopology nonstop_tsc aperfmperf eagerfpu pni pclmulqdq dtes64 monitor ds_cpl vmx smx est tm2 ssse3 sdbg fma cx16 xtpr pdcm pcid dca sse4_1 sse4_2 x2apic movbe popcnt tsc_deadline_timer aes xsave avx f16c rdrand lahf_lm abm epb tpr_shadow vnmi flexpriority ept vpid fsgsbase tsc_adjust bmi1 avx2 smep bmi2 erms invpcid cqm xsaveopt cqm_llc cqm_occup_llc dtherm arat pln pts
  bugs		:
  bogomips	: 4589.02
  clflush size	: 64
  cache_alignment	: 64
  address sizes	: 46 bits physical, 48 bits virtual
  power management:

  processor	: 5
  vendor_id	: GenuineIntel
  cpu family	: 6
  model		: 63
  model name	: Intel(R) Xeon(R) CPU E5-2699 v3 @ 2.30GHz
  stepping	: 2
  microcode	: 0x35
  cpu MHz		: 2294.513
  cache size	: 46080 KB
  physical id	: 0
  siblings	: 18
  core id		: 8
  cpu cores	: 18
  apicid		: 16
  initial apicid	: 16
  fpu		: yes
  fpu_exception	: yes
  cpuid level	: 15
  wp		: yes
  flags		: fpu vme de pse tsc msr pae mce cx8 apic sep mtrr pge mca cmov pat pse36 clflush dts acpi mmx fxsr sse sse2 ss ht tm pbe syscall nx pdpe1gb rdtscp lm constant_tsc arch_perfmon pebs bts rep_good nopl xtopology nonstop_tsc aperfmperf eagerfpu pni pclmulqdq dtes64 monitor ds_cpl vmx smx est tm2 ssse3 sdbg fma cx16 xtpr pdcm pcid dca sse4_1 sse4_2 x2apic movbe popcnt tsc_deadline_timer aes xsave avx f16c rdrand lahf_lm abm epb tpr_shadow vnmi flexpriority ept vpid fsgsbase tsc_adjust bmi1 avx2 smep bmi2 erms invpcid cqm xsaveopt cqm_llc cqm_occup_llc dtherm arat pln pts
  bugs		:
  bogomips	: 4589.02
  clflush size	: 64
  cache_alignment	: 64
  address sizes	: 46 bits physical, 48 bits virtual
  power management:

  processor	: 6
  vendor_id	: GenuineIntel
  cpu family	: 6
  model		: 63
  model name	: Intel(R) Xeon(R) CPU E5-2699 v3 @ 2.30GHz
  stepping	: 2
  microcode	: 0x35
  cpu MHz		: 2294.513
  cache size	: 46080 KB
  physical id	: 0
  siblings	: 18
  core id		: 9
  cpu cores	: 18
  apicid		: 18
  initial apicid	: 18
  fpu		: yes
  fpu_exception	: yes
  cpuid level	: 15
  wp		: yes
  flags		: fpu vme de pse tsc msr pae mce cx8 apic sep mtrr pge mca cmov pat pse36 clflush dts acpi mmx fxsr sse sse2 ss ht tm pbe syscall nx pdpe1gb rdtscp lm constant_tsc arch_perfmon pebs bts rep_good nopl xtopology nonstop_tsc aperfmperf eagerfpu pni pclmulqdq dtes64 monitor ds_cpl vmx smx est tm2 ssse3 sdbg fma cx16 xtpr pdcm pcid dca sse4_1 sse4_2 x2apic movbe popcnt tsc_deadline_timer aes xsave avx f16c rdrand lahf_lm abm epb tpr_shadow vnmi flexpriority ept vpid fsgsbase tsc_adjust bmi1 avx2 smep bmi2 erms invpcid cqm xsaveopt cqm_llc cqm_occup_llc dtherm arat pln pts
  bugs		:
  bogomips	: 4589.02
  clflush size	: 64
  cache_alignment	: 64
  address sizes	: 46 bits physical, 48 bits virtual
  power management:

  processor	: 7
  vendor_id	: GenuineIntel
  cpu family	: 6
  model		: 63
  model name	: Intel(R) Xeon(R) CPU E5-2699 v3 @ 2.30GHz
  stepping	: 2
  microcode	: 0x35
  cpu MHz		: 2294.513
  cache size	: 46080 KB
  physical id	: 0
  siblings	: 18
  core id		: 10
  cpu cores	: 18
  apicid		: 20
  initial apicid	: 20
  fpu		: yes
  fpu_exception	: yes
  cpuid level	: 15
  wp		: yes
  flags		: fpu vme de pse tsc msr pae mce cx8 apic sep mtrr pge mca cmov pat pse36 clflush dts acpi mmx fxsr sse sse2 ss ht tm pbe syscall nx pdpe1gb rdtscp lm constant_tsc arch_perfmon pebs bts rep_good nopl xtopology nonstop_tsc aperfmperf eagerfpu pni pclmulqdq dtes64 monitor ds_cpl vmx smx est tm2 ssse3 sdbg fma cx16 xtpr pdcm pcid dca sse4_1 sse4_2 x2apic movbe popcnt tsc_deadline_timer aes xsave avx f16c rdrand lahf_lm abm epb tpr_shadow vnmi flexpriority ept vpid fsgsbase tsc_adjust bmi1 avx2 smep bmi2 erms invpcid cqm xsaveopt cqm_llc cqm_occup_llc dtherm arat pln pts
  bugs		:
  bogomips	: 4589.02
  clflush size	: 64
  cache_alignment	: 64
  address sizes	: 46 bits physical, 48 bits virtual
  power management:

  processor	: 8
  vendor_id	: GenuineIntel
  cpu family	: 6
  model		: 63
  model name	: Intel(R) Xeon(R) CPU E5-2699 v3 @ 2.30GHz
  stepping	: 2
  microcode	: 0x35
  cpu MHz		: 2294.513
  cache size	: 46080 KB
  physical id	: 0
  siblings	: 18
  core id		: 11
  cpu cores	: 18
  apicid		: 22
  initial apicid	: 22
  fpu		: yes
  fpu_exception	: yes
  cpuid level	: 15
  wp		: yes
  flags		: fpu vme de pse tsc msr pae mce cx8 apic sep mtrr pge mca cmov pat pse36 clflush dts acpi mmx fxsr sse sse2 ss ht tm pbe syscall nx pdpe1gb rdtscp lm constant_tsc arch_perfmon pebs bts rep_good nopl xtopology nonstop_tsc aperfmperf eagerfpu pni pclmulqdq dtes64 monitor ds_cpl vmx smx est tm2 ssse3 sdbg fma cx16 xtpr pdcm pcid dca sse4_1 sse4_2 x2apic movbe popcnt tsc_deadline_timer aes xsave avx f16c rdrand lahf_lm abm epb tpr_shadow vnmi flexpriority ept vpid fsgsbase tsc_adjust bmi1 avx2 smep bmi2 erms invpcid cqm xsaveopt cqm_llc cqm_occup_llc dtherm arat pln pts
  bugs		:
  bogomips	: 4589.02
  clflush size	: 64
  cache_alignment	: 64
  address sizes	: 46 bits physical, 48 bits virtual
  power management:

  processor	: 9
  vendor_id	: GenuineIntel
  cpu family	: 6
  model		: 63
  model name	: Intel(R) Xeon(R) CPU E5-2699 v3 @ 2.30GHz
  stepping	: 2
  microcode	: 0x35
  cpu MHz		: 2294.513
  cache size	: 46080 KB
  physical id	: 0
  siblings	: 18
  core id		: 16
  cpu cores	: 18
  apicid		: 32
  initial apicid	: 32
  fpu		: yes
  fpu_exception	: yes
  cpuid level	: 15
  wp		: yes
  flags		: fpu vme de pse tsc msr pae mce cx8 apic sep mtrr pge mca cmov pat pse36 clflush dts acpi mmx fxsr sse sse2 ss ht tm pbe syscall nx pdpe1gb rdtscp lm constant_tsc arch_perfmon pebs bts rep_good nopl xtopology nonstop_tsc aperfmperf eagerfpu pni pclmulqdq dtes64 monitor ds_cpl vmx smx est tm2 ssse3 sdbg fma cx16 xtpr pdcm pcid dca sse4_1 sse4_2 x2apic movbe popcnt tsc_deadline_timer aes xsave avx f16c rdrand lahf_lm abm epb tpr_shadow vnmi flexpriority ept vpid fsgsbase tsc_adjust bmi1 avx2 smep bmi2 erms invpcid cqm xsaveopt cqm_llc cqm_occup_llc dtherm arat pln pts
  bugs		:
  bogomips	: 4589.02
  clflush size	: 64
  cache_alignment	: 64
  address sizes	: 46 bits physical, 48 bits virtual
  power management:

  processor	: 10
  vendor_id	: GenuineIntel
  cpu family	: 6
  model		: 63
  model name	: Intel(R) Xeon(R) CPU E5-2699 v3 @ 2.30GHz
  stepping	: 2
  microcode	: 0x35
  cpu MHz		: 2294.513
  cache size	: 46080 KB
  physical id	: 0
  siblings	: 18
  core id		: 17
  cpu cores	: 18
  apicid		: 34
  initial apicid	: 34
  fpu		: yes
  fpu_exception	: yes
  cpuid level	: 15
  wp		: yes
  flags		: fpu vme de pse tsc msr pae mce cx8 apic sep mtrr pge mca cmov pat pse36 clflush dts acpi mmx fxsr sse sse2 ss ht tm pbe syscall nx pdpe1gb rdtscp lm constant_tsc arch_perfmon pebs bts rep_good nopl xtopology nonstop_tsc aperfmperf eagerfpu pni pclmulqdq dtes64 monitor ds_cpl vmx smx est tm2 ssse3 sdbg fma cx16 xtpr pdcm pcid dca sse4_1 sse4_2 x2apic movbe popcnt tsc_deadline_timer aes xsave avx f16c rdrand lahf_lm abm epb tpr_shadow vnmi flexpriority ept vpid fsgsbase tsc_adjust bmi1 avx2 smep bmi2 erms invpcid cqm xsaveopt cqm_llc cqm_occup_llc dtherm arat pln pts
  bugs		:
  bogomips	: 4589.02
  clflush size	: 64
  cache_alignment	: 64
  address sizes	: 46 bits physical, 48 bits virtual
  power management:

  processor	: 11
  vendor_id	: GenuineIntel
  cpu family	: 6
  model		: 63
  model name	: Intel(R) Xeon(R) CPU E5-2699 v3 @ 2.30GHz
  stepping	: 2
  microcode	: 0x35
  cpu MHz		: 2294.513
  cache size	: 46080 KB
  physical id	: 0
  siblings	: 18
  core id		: 18
  cpu cores	: 18
  apicid		: 36
  initial apicid	: 36
  fpu		: yes
  fpu_exception	: yes
  cpuid level	: 15
  wp		: yes
  flags		: fpu vme de pse tsc msr pae mce cx8 apic sep mtrr pge mca cmov pat pse36 clflush dts acpi mmx fxsr sse sse2 ss ht tm pbe syscall nx pdpe1gb rdtscp lm constant_tsc arch_perfmon pebs bts rep_good nopl xtopology nonstop_tsc aperfmperf eagerfpu pni pclmulqdq dtes64 monitor ds_cpl vmx smx est tm2 ssse3 sdbg fma cx16 xtpr pdcm pcid dca sse4_1 sse4_2 x2apic movbe popcnt tsc_deadline_timer aes xsave avx f16c rdrand lahf_lm abm epb tpr_shadow vnmi flexpriority ept vpid fsgsbase tsc_adjust bmi1 avx2 smep bmi2 erms invpcid cqm xsaveopt cqm_llc cqm_occup_llc dtherm arat pln pts
  bugs		:
  bogomips	: 4589.02
  clflush size	: 64
  cache_alignment	: 64
  address sizes	: 46 bits physical, 48 bits virtual
  power management:

  processor	: 12
  vendor_id	: GenuineIntel
  cpu family	: 6
  model		: 63
  model name	: Intel(R) Xeon(R) CPU E5-2699 v3 @ 2.30GHz
  stepping	: 2
  microcode	: 0x35
  cpu MHz		: 2294.513
  cache size	: 46080 KB
  physical id	: 0
  siblings	: 18
  core id		: 19
  cpu cores	: 18
  apicid		: 38
  initial apicid	: 38
  fpu		: yes
  fpu_exception	: yes
  cpuid level	: 15
  wp		: yes
  flags		: fpu vme de pse tsc msr pae mce cx8 apic sep mtrr pge mca cmov pat pse36 clflush dts acpi mmx fxsr sse sse2 ss ht tm pbe syscall nx pdpe1gb rdtscp lm constant_tsc arch_perfmon pebs bts rep_good nopl xtopology nonstop_tsc aperfmperf eagerfpu pni pclmulqdq dtes64 monitor ds_cpl vmx smx est tm2 ssse3 sdbg fma cx16 xtpr pdcm pcid dca sse4_1 sse4_2 x2apic movbe popcnt tsc_deadline_timer aes xsave avx f16c rdrand lahf_lm abm epb tpr_shadow vnmi flexpriority ept vpid fsgsbase tsc_adjust bmi1 avx2 smep bmi2 erms invpcid cqm xsaveopt cqm_llc cqm_occup_llc dtherm arat pln pts
  bugs		:
  bogomips	: 4589.02
  clflush size	: 64
  cache_alignment	: 64
  address sizes	: 46 bits physical, 48 bits virtual
  power management:

  processor	: 13
  vendor_id	: GenuineIntel
  cpu family	: 6
  model		: 63
  model name	: Intel(R) Xeon(R) CPU E5-2699 v3 @ 2.30GHz
  stepping	: 2
  microcode	: 0x35
  cpu MHz		: 2294.513
  cache size	: 46080 KB
  physical id	: 0
  siblings	: 18
  core id		: 20
  cpu cores	: 18
  apicid		: 40
  initial apicid	: 40
  fpu		: yes
  fpu_exception	: yes
  cpuid level	: 15
  wp		: yes
  flags		: fpu vme de pse tsc msr pae mce cx8 apic sep mtrr pge mca cmov pat pse36 clflush dts acpi mmx fxsr sse sse2 ss ht tm pbe syscall nx pdpe1gb rdtscp lm constant_tsc arch_perfmon pebs bts rep_good nopl xtopology nonstop_tsc aperfmperf eagerfpu pni pclmulqdq dtes64 monitor ds_cpl vmx smx est tm2 ssse3 sdbg fma cx16 xtpr pdcm pcid dca sse4_1 sse4_2 x2apic movbe popcnt tsc_deadline_timer aes xsave avx f16c rdrand lahf_lm abm epb tpr_shadow vnmi flexpriority ept vpid fsgsbase tsc_adjust bmi1 avx2 smep bmi2 erms invpcid cqm xsaveopt cqm_llc cqm_occup_llc dtherm arat pln pts
  bugs		:
  bogomips	: 4589.02
  clflush size	: 64
  cache_alignment	: 64
  address sizes	: 46 bits physical, 48 bits virtual
  power management:

  processor	: 14
  vendor_id	: GenuineIntel
  cpu family	: 6
  model		: 63
  model name	: Intel(R) Xeon(R) CPU E5-2699 v3 @ 2.30GHz
  stepping	: 2
  microcode	: 0x35
  cpu MHz		: 2294.513
  cache size	: 46080 KB
  physical id	: 0
  siblings	: 18
  core id		: 24
  cpu cores	: 18
  apicid		: 48
  initial apicid	: 48
  fpu		: yes
  fpu_exception	: yes
  cpuid level	: 15
  wp		: yes
  flags		: fpu vme de pse tsc msr pae mce cx8 apic sep mtrr pge mca cmov pat pse36 clflush dts acpi mmx fxsr sse sse2 ss ht tm pbe syscall nx pdpe1gb rdtscp lm constant_tsc arch_perfmon pebs bts rep_good nopl xtopology nonstop_tsc aperfmperf eagerfpu pni pclmulqdq dtes64 monitor ds_cpl vmx smx est tm2 ssse3 sdbg fma cx16 xtpr pdcm pcid dca sse4_1 sse4_2 x2apic movbe popcnt tsc_deadline_timer aes xsave avx f16c rdrand lahf_lm abm epb tpr_shadow vnmi flexpriority ept vpid fsgsbase tsc_adjust bmi1 avx2 smep bmi2 erms invpcid cqm xsaveopt cqm_llc cqm_occup_llc dtherm arat pln pts
  bugs		:
  bogomips	: 4589.02
  clflush size	: 64
  cache_alignment	: 64
  address sizes	: 46 bits physical, 48 bits virtual
  power management:

  processor	: 15
  vendor_id	: GenuineIntel
  cpu family	: 6
  model		: 63
  model name	: Intel(R) Xeon(R) CPU E5-2699 v3 @ 2.30GHz
  stepping	: 2
  microcode	: 0x35
  cpu MHz		: 2294.513
  cache size	: 46080 KB
  physical id	: 0
  siblings	: 18
  core id		: 25
  cpu cores	: 18
  apicid		: 50
  initial apicid	: 50
  fpu		: yes
  fpu_exception	: yes
  cpuid level	: 15
  wp		: yes
  flags		: fpu vme de pse tsc msr pae mce cx8 apic sep mtrr pge mca cmov pat pse36 clflush dts acpi mmx fxsr sse sse2 ss ht tm pbe syscall nx pdpe1gb rdtscp lm constant_tsc arch_perfmon pebs bts rep_good nopl xtopology nonstop_tsc aperfmperf eagerfpu pni pclmulqdq dtes64 monitor ds_cpl vmx smx est tm2 ssse3 sdbg fma cx16 xtpr pdcm pcid dca sse4_1 sse4_2 x2apic movbe popcnt tsc_deadline_timer aes xsave avx f16c rdrand lahf_lm abm epb tpr_shadow vnmi flexpriority ept vpid fsgsbase tsc_adjust bmi1 avx2 smep bmi2 erms invpcid cqm xsaveopt cqm_llc cqm_occup_llc dtherm arat pln pts
  bugs		:
  bogomips	: 4589.02
  clflush size	: 64
  cache_alignment	: 64
  address sizes	: 46 bits physical, 48 bits virtual
  power management:

  processor	: 16
  vendor_id	: GenuineIntel
  cpu family	: 6
  model		: 63
  model name	: Intel(R) Xeon(R) CPU E5-2699 v3 @ 2.30GHz
  stepping	: 2
  microcode	: 0x35
  cpu MHz		: 2294.513
  cache size	: 46080 KB
  physical id	: 0
  siblings	: 18
  core id		: 26
  cpu cores	: 18
  apicid		: 52
  initial apicid	: 52
  fpu		: yes
  fpu_exception	: yes
  cpuid level	: 15
  wp		: yes
  flags		: fpu vme de pse tsc msr pae mce cx8 apic sep mtrr pge mca cmov pat pse36 clflush dts acpi mmx fxsr sse sse2 ss ht tm pbe syscall nx pdpe1gb rdtscp lm constant_tsc arch_perfmon pebs bts rep_good nopl xtopology nonstop_tsc aperfmperf eagerfpu pni pclmulqdq dtes64 monitor ds_cpl vmx smx est tm2 ssse3 sdbg fma cx16 xtpr pdcm pcid dca sse4_1 sse4_2 x2apic movbe popcnt tsc_deadline_timer aes xsave avx f16c rdrand lahf_lm abm epb tpr_shadow vnmi flexpriority ept vpid fsgsbase tsc_adjust bmi1 avx2 smep bmi2 erms invpcid cqm xsaveopt cqm_llc cqm_occup_llc dtherm arat pln pts
  bugs		:
  bogomips	: 4589.02
  clflush size	: 64
  cache_alignment	: 64
  address sizes	: 46 bits physical, 48 bits virtual
  power management:

  processor	: 17
  vendor_id	: GenuineIntel
  cpu family	: 6
  model		: 63
  model name	: Intel(R) Xeon(R) CPU E5-2699 v3 @ 2.30GHz
  stepping	: 2
  microcode	: 0x35
  cpu MHz		: 2294.513
  cache size	: 46080 KB
  physical id	: 0
  siblings	: 18
  core id		: 27
  cpu cores	: 18
  apicid		: 54
  initial apicid	: 54
  fpu		: yes
  fpu_exception	: yes
  cpuid level	: 15
  wp		: yes
  flags		: fpu vme de pse tsc msr pae mce cx8 apic sep mtrr pge mca cmov pat pse36 clflush dts acpi mmx fxsr sse sse2 ss ht tm pbe syscall nx pdpe1gb rdtscp lm constant_tsc arch_perfmon pebs bts rep_good nopl xtopology nonstop_tsc aperfmperf eagerfpu pni pclmulqdq dtes64 monitor ds_cpl vmx smx est tm2 ssse3 sdbg fma cx16 xtpr pdcm pcid dca sse4_1 sse4_2 x2apic movbe popcnt tsc_deadline_timer aes xsave avx f16c rdrand lahf_lm abm epb tpr_shadow vnmi flexpriority ept vpid fsgsbase tsc_adjust bmi1 avx2 smep bmi2 erms invpcid cqm xsaveopt cqm_llc cqm_occup_llc dtherm arat pln pts
  bugs		:
  bogomips	: 4589.02
  clflush size	: 64
  cache_alignment	: 64
  address sizes	: 46 bits physical, 48 bits virtual
  power management:

  processor	: 18
  vendor_id	: GenuineIntel
  cpu family	: 6
  model		: 63
  model name	: Intel(R) Xeon(R) CPU E5-2699 v3 @ 2.30GHz
  stepping	: 2
  microcode	: 0x35
  cpu MHz		: 2294.513
  cache size	: 46080 KB
  physical id	: 1
  siblings	: 18
  core id		: 0
  cpu cores	: 18
  apicid		: 64
  initial apicid	: 64
  fpu		: yes
  fpu_exception	: yes
  cpuid level	: 15
  wp		: yes
  flags		: fpu vme de pse tsc msr pae mce cx8 apic sep mtrr pge mca cmov pat pse36 clflush dts acpi mmx fxsr sse sse2 ss ht tm pbe syscall nx pdpe1gb rdtscp lm constant_tsc arch_perfmon pebs bts rep_good nopl xtopology nonstop_tsc aperfmperf eagerfpu pni pclmulqdq dtes64 monitor ds_cpl vmx smx est tm2 ssse3 sdbg fma cx16 xtpr pdcm pcid dca sse4_1 sse4_2 x2apic movbe popcnt tsc_deadline_timer aes xsave avx f16c rdrand lahf_lm abm epb tpr_shadow vnmi flexpriority ept vpid fsgsbase tsc_adjust bmi1 avx2 smep bmi2 erms invpcid cqm xsaveopt cqm_llc cqm_occup_llc dtherm arat pln pts
  bugs		:
  bogomips	: 4590.41
  clflush size	: 64
  cache_alignment	: 64
  address sizes	: 46 bits physical, 48 bits virtual
  power management:

  processor	: 19
  vendor_id	: GenuineIntel
  cpu family	: 6
  model		: 63
  model name	: Intel(R) Xeon(R) CPU E5-2699 v3 @ 2.30GHz
  stepping	: 2
  microcode	: 0x35
  cpu MHz		: 2294.513
  cache size	: 46080 KB
  physical id	: 1
  siblings	: 18
  core id		: 1
  cpu cores	: 18
  apicid		: 66
  initial apicid	: 66
  fpu		: yes
  fpu_exception	: yes
  cpuid level	: 15
  wp		: yes
  flags		: fpu vme de pse tsc msr pae mce cx8 apic sep mtrr pge mca cmov pat pse36 clflush dts acpi mmx fxsr sse sse2 ss ht tm pbe syscall nx pdpe1gb rdtscp lm constant_tsc arch_perfmon pebs bts rep_good nopl xtopology nonstop_tsc aperfmperf eagerfpu pni pclmulqdq dtes64 monitor ds_cpl vmx smx est tm2 ssse3 sdbg fma cx16 xtpr pdcm pcid dca sse4_1 sse4_2 x2apic movbe popcnt tsc_deadline_timer aes xsave avx f16c rdrand lahf_lm abm epb tpr_shadow vnmi flexpriority ept vpid fsgsbase tsc_adjust bmi1 avx2 smep bmi2 erms invpcid cqm xsaveopt cqm_llc cqm_occup_llc dtherm arat pln pts
  bugs		:
  bogomips	: 4590.41
  clflush size	: 64
  cache_alignment	: 64
  address sizes	: 46 bits physical, 48 bits virtual
  power management:

  processor	: 20
  vendor_id	: GenuineIntel
  cpu family	: 6
  model		: 63
  model name	: Intel(R) Xeon(R) CPU E5-2699 v3 @ 2.30GHz
  stepping	: 2
  microcode	: 0x35
  cpu MHz		: 2294.513
  cache size	: 46080 KB
  physical id	: 1
  siblings	: 18
  core id		: 2
  cpu cores	: 18
  apicid		: 68
  initial apicid	: 68
  fpu		: yes
  fpu_exception	: yes
  cpuid level	: 15
  wp		: yes
  flags		: fpu vme de pse tsc msr pae mce cx8 apic sep mtrr pge mca cmov pat pse36 clflush dts acpi mmx fxsr sse sse2 ss ht tm pbe syscall nx pdpe1gb rdtscp lm constant_tsc arch_perfmon pebs bts rep_good nopl xtopology nonstop_tsc aperfmperf eagerfpu pni pclmulqdq dtes64 monitor ds_cpl vmx smx est tm2 ssse3 sdbg fma cx16 xtpr pdcm pcid dca sse4_1 sse4_2 x2apic movbe popcnt tsc_deadline_timer aes xsave avx f16c rdrand lahf_lm abm epb tpr_shadow vnmi flexpriority ept vpid fsgsbase tsc_adjust bmi1 avx2 smep bmi2 erms invpcid cqm xsaveopt cqm_llc cqm_occup_llc dtherm arat pln pts
  bugs		:
  bogomips	: 4590.41
  clflush size	: 64
  cache_alignment	: 64
  address sizes	: 46 bits physical, 48 bits virtual
  power management:

  processor	: 21
  vendor_id	: GenuineIntel
  cpu family	: 6
  model		: 63
  model name	: Intel(R) Xeon(R) CPU E5-2699 v3 @ 2.30GHz
  stepping	: 2
  microcode	: 0x35
  cpu MHz		: 2294.513
  cache size	: 46080 KB
  physical id	: 1
  siblings	: 18
  core id		: 3
  cpu cores	: 18
  apicid		: 70
  initial apicid	: 70
  fpu		: yes
  fpu_exception	: yes
  cpuid level	: 15
  wp		: yes
  flags		: fpu vme de pse tsc msr pae mce cx8 apic sep mtrr pge mca cmov pat pse36 clflush dts acpi mmx fxsr sse sse2 ss ht tm pbe syscall nx pdpe1gb rdtscp lm constant_tsc arch_perfmon pebs bts rep_good nopl xtopology nonstop_tsc aperfmperf eagerfpu pni pclmulqdq dtes64 monitor ds_cpl vmx smx est tm2 ssse3 sdbg fma cx16 xtpr pdcm pcid dca sse4_1 sse4_2 x2apic movbe popcnt tsc_deadline_timer aes xsave avx f16c rdrand lahf_lm abm epb tpr_shadow vnmi flexpriority ept vpid fsgsbase tsc_adjust bmi1 avx2 smep bmi2 erms invpcid cqm xsaveopt cqm_llc cqm_occup_llc dtherm arat pln pts
  bugs		:
  bogomips	: 4590.41
  clflush size	: 64
  cache_alignment	: 64
  address sizes	: 46 bits physical, 48 bits virtual
  power management:

  processor	: 22
  vendor_id	: GenuineIntel
  cpu family	: 6
  model		: 63
  model name	: Intel(R) Xeon(R) CPU E5-2699 v3 @ 2.30GHz
  stepping	: 2
  microcode	: 0x35
  cpu MHz		: 2294.513
  cache size	: 46080 KB
  physical id	: 1
  siblings	: 18
  core id		: 4
  cpu cores	: 18
  apicid		: 72
  initial apicid	: 72
  fpu		: yes
  fpu_exception	: yes
  cpuid level	: 15
  wp		: yes
  flags		: fpu vme de pse tsc msr pae mce cx8 apic sep mtrr pge mca cmov pat pse36 clflush dts acpi mmx fxsr sse sse2 ss ht tm pbe syscall nx pdpe1gb rdtscp lm constant_tsc arch_perfmon pebs bts rep_good nopl xtopology nonstop_tsc aperfmperf eagerfpu pni pclmulqdq dtes64 monitor ds_cpl vmx smx est tm2 ssse3 sdbg fma cx16 xtpr pdcm pcid dca sse4_1 sse4_2 x2apic movbe popcnt tsc_deadline_timer aes xsave avx f16c rdrand lahf_lm abm epb tpr_shadow vnmi flexpriority ept vpid fsgsbase tsc_adjust bmi1 avx2 smep bmi2 erms invpcid cqm xsaveopt cqm_llc cqm_occup_llc dtherm arat pln pts
  bugs		:
  bogomips	: 4590.41
  clflush size	: 64
  cache_alignment	: 64
  address sizes	: 46 bits physical, 48 bits virtual
  power management:

  processor	: 23
  vendor_id	: GenuineIntel
  cpu family	: 6
  model		: 63
  model name	: Intel(R) Xeon(R) CPU E5-2699 v3 @ 2.30GHz
  stepping	: 2
  microcode	: 0x35
  cpu MHz		: 2294.513
  cache size	: 46080 KB
  physical id	: 1
  siblings	: 18
  core id		: 8
  cpu cores	: 18
  apicid		: 80
  initial apicid	: 80
  fpu		: yes
  fpu_exception	: yes
  cpuid level	: 15
  wp		: yes
  flags		: fpu vme de pse tsc msr pae mce cx8 apic sep mtrr pge mca cmov pat pse36 clflush dts acpi mmx fxsr sse sse2 ss ht tm pbe syscall nx pdpe1gb rdtscp lm constant_tsc arch_perfmon pebs bts rep_good nopl xtopology nonstop_tsc aperfmperf eagerfpu pni pclmulqdq dtes64 monitor ds_cpl vmx smx est tm2 ssse3 sdbg fma cx16 xtpr pdcm pcid dca sse4_1 sse4_2 x2apic movbe popcnt tsc_deadline_timer aes xsave avx f16c rdrand lahf_lm abm epb tpr_shadow vnmi flexpriority ept vpid fsgsbase tsc_adjust bmi1 avx2 smep bmi2 erms invpcid cqm xsaveopt cqm_llc cqm_occup_llc dtherm arat pln pts
  bugs		:
  bogomips	: 4590.41
  clflush size	: 64
  cache_alignment	: 64
  address sizes	: 46 bits physical, 48 bits virtual
  power management:

  processor	: 24
  vendor_id	: GenuineIntel
  cpu family	: 6
  model		: 63
  model name	: Intel(R) Xeon(R) CPU E5-2699 v3 @ 2.30GHz
  stepping	: 2
  microcode	: 0x35
  cpu MHz		: 2294.513
  cache size	: 46080 KB
  physical id	: 1
  siblings	: 18
  core id		: 9
  cpu cores	: 18
  apicid		: 82
  initial apicid	: 82
  fpu		: yes
  fpu_exception	: yes
  cpuid level	: 15
  wp		: yes
  flags		: fpu vme de pse tsc msr pae mce cx8 apic sep mtrr pge mca cmov pat pse36 clflush dts acpi mmx fxsr sse sse2 ss ht tm pbe syscall nx pdpe1gb rdtscp lm constant_tsc arch_perfmon pebs bts rep_good nopl xtopology nonstop_tsc aperfmperf eagerfpu pni pclmulqdq dtes64 monitor ds_cpl vmx smx est tm2 ssse3 sdbg fma cx16 xtpr pdcm pcid dca sse4_1 sse4_2 x2apic movbe popcnt tsc_deadline_timer aes xsave avx f16c rdrand lahf_lm abm epb tpr_shadow vnmi flexpriority ept vpid fsgsbase tsc_adjust bmi1 avx2 smep bmi2 erms invpcid cqm xsaveopt cqm_llc cqm_occup_llc dtherm arat pln pts
  bugs		:
  bogomips	: 4590.41
  clflush size	: 64
  cache_alignment	: 64
  address sizes	: 46 bits physical, 48 bits virtual
  power management:

  processor	: 25
  vendor_id	: GenuineIntel
  cpu family	: 6
  model		: 63
  model name	: Intel(R) Xeon(R) CPU E5-2699 v3 @ 2.30GHz
  stepping	: 2
  microcode	: 0x35
  cpu MHz		: 2294.513
  cache size	: 46080 KB
  physical id	: 1
  siblings	: 18
  core id		: 10
  cpu cores	: 18
  apicid		: 84
  initial apicid	: 84
  fpu		: yes
  fpu_exception	: yes
  cpuid level	: 15
  wp		: yes
  flags		: fpu vme de pse tsc msr pae mce cx8 apic sep mtrr pge mca cmov pat pse36 clflush dts acpi mmx fxsr sse sse2 ss ht tm pbe syscall nx pdpe1gb rdtscp lm constant_tsc arch_perfmon pebs bts rep_good nopl xtopology nonstop_tsc aperfmperf eagerfpu pni pclmulqdq dtes64 monitor ds_cpl vmx smx est tm2 ssse3 sdbg fma cx16 xtpr pdcm pcid dca sse4_1 sse4_2 x2apic movbe popcnt tsc_deadline_timer aes xsave avx f16c rdrand lahf_lm abm epb tpr_shadow vnmi flexpriority ept vpid fsgsbase tsc_adjust bmi1 avx2 smep bmi2 erms invpcid cqm xsaveopt cqm_llc cqm_occup_llc dtherm arat pln pts
  bugs		:
  bogomips	: 4590.41
  clflush size	: 64
  cache_alignment	: 64
  address sizes	: 46 bits physical, 48 bits virtual
  power management:

  processor	: 26
  vendor_id	: GenuineIntel
  cpu family	: 6
  model		: 63
  model name	: Intel(R) Xeon(R) CPU E5-2699 v3 @ 2.30GHz
  stepping	: 2
  microcode	: 0x35
  cpu MHz		: 2294.513
  cache size	: 46080 KB
  physical id	: 1
  siblings	: 18
  core id		: 11
  cpu cores	: 18
  apicid		: 86
  initial apicid	: 86
  fpu		: yes
  fpu_exception	: yes
  cpuid level	: 15
  wp		: yes
  flags		: fpu vme de pse tsc msr pae mce cx8 apic sep mtrr pge mca cmov pat pse36 clflush dts acpi mmx fxsr sse sse2 ss ht tm pbe syscall nx pdpe1gb rdtscp lm constant_tsc arch_perfmon pebs bts rep_good nopl xtopology nonstop_tsc aperfmperf eagerfpu pni pclmulqdq dtes64 monitor ds_cpl vmx smx est tm2 ssse3 sdbg fma cx16 xtpr pdcm pcid dca sse4_1 sse4_2 x2apic movbe popcnt tsc_deadline_timer aes xsave avx f16c rdrand lahf_lm abm epb tpr_shadow vnmi flexpriority ept vpid fsgsbase tsc_adjust bmi1 avx2 smep bmi2 erms invpcid cqm xsaveopt cqm_llc cqm_occup_llc dtherm arat pln pts
  bugs		:
  bogomips	: 4590.41
  clflush size	: 64
  cache_alignment	: 64
  address sizes	: 46 bits physical, 48 bits virtual
  power management:

  processor	: 27
  vendor_id	: GenuineIntel
  cpu family	: 6
  model		: 63
  model name	: Intel(R) Xeon(R) CPU E5-2699 v3 @ 2.30GHz
  stepping	: 2
  microcode	: 0x35
  cpu MHz		: 2294.513
  cache size	: 46080 KB
  physical id	: 1
  siblings	: 18
  core id		: 16
  cpu cores	: 18
  apicid		: 96
  initial apicid	: 96
  fpu		: yes
  fpu_exception	: yes
  cpuid level	: 15
  wp		: yes
  flags		: fpu vme de pse tsc msr pae mce cx8 apic sep mtrr pge mca cmov pat pse36 clflush dts acpi mmx fxsr sse sse2 ss ht tm pbe syscall nx pdpe1gb rdtscp lm constant_tsc arch_perfmon pebs bts rep_good nopl xtopology nonstop_tsc aperfmperf eagerfpu pni pclmulqdq dtes64 monitor ds_cpl vmx smx est tm2 ssse3 sdbg fma cx16 xtpr pdcm pcid dca sse4_1 sse4_2 x2apic movbe popcnt tsc_deadline_timer aes xsave avx f16c rdrand lahf_lm abm epb tpr_shadow vnmi flexpriority ept vpid fsgsbase tsc_adjust bmi1 avx2 smep bmi2 erms invpcid cqm xsaveopt cqm_llc cqm_occup_llc dtherm arat pln pts
  bugs		:
  bogomips	: 4590.41
  clflush size	: 64
  cache_alignment	: 64
  address sizes	: 46 bits physical, 48 bits virtual
  power management:

  processor	: 28
  vendor_id	: GenuineIntel
  cpu family	: 6
  model		: 63
  model name	: Intel(R) Xeon(R) CPU E5-2699 v3 @ 2.30GHz
  stepping	: 2
  microcode	: 0x35
  cpu MHz		: 2294.513
  cache size	: 46080 KB
  physical id	: 1
  siblings	: 18
  core id		: 17
  cpu cores	: 18
  apicid		: 98
  initial apicid	: 98
  fpu		: yes
  fpu_exception	: yes
  cpuid level	: 15
  wp		: yes
  flags		: fpu vme de pse tsc msr pae mce cx8 apic sep mtrr pge mca cmov pat pse36 clflush dts acpi mmx fxsr sse sse2 ss ht tm pbe syscall nx pdpe1gb rdtscp lm constant_tsc arch_perfmon pebs bts rep_good nopl xtopology nonstop_tsc aperfmperf eagerfpu pni pclmulqdq dtes64 monitor ds_cpl vmx smx est tm2 ssse3 sdbg fma cx16 xtpr pdcm pcid dca sse4_1 sse4_2 x2apic movbe popcnt tsc_deadline_timer aes xsave avx f16c rdrand lahf_lm abm epb tpr_shadow vnmi flexpriority ept vpid fsgsbase tsc_adjust bmi1 avx2 smep bmi2 erms invpcid cqm xsaveopt cqm_llc cqm_occup_llc dtherm arat pln pts
  bugs		:
  bogomips	: 4590.41
  clflush size	: 64
  cache_alignment	: 64
  address sizes	: 46 bits physical, 48 bits virtual
  power management:

  processor	: 29
  vendor_id	: GenuineIntel
  cpu family	: 6
  model		: 63
  model name	: Intel(R) Xeon(R) CPU E5-2699 v3 @ 2.30GHz
  stepping	: 2
  microcode	: 0x35
  cpu MHz		: 2294.513
  cache size	: 46080 KB
  physical id	: 1
  siblings	: 18
  core id		: 18
  cpu cores	: 18
  apicid		: 100
  initial apicid	: 100
  fpu		: yes
  fpu_exception	: yes
  cpuid level	: 15
  wp		: yes
  flags		: fpu vme de pse tsc msr pae mce cx8 apic sep mtrr pge mca cmov pat pse36 clflush dts acpi mmx fxsr sse sse2 ss ht tm pbe syscall nx pdpe1gb rdtscp lm constant_tsc arch_perfmon pebs bts rep_good nopl xtopology nonstop_tsc aperfmperf eagerfpu pni pclmulqdq dtes64 monitor ds_cpl vmx smx est tm2 ssse3 sdbg fma cx16 xtpr pdcm pcid dca sse4_1 sse4_2 x2apic movbe popcnt tsc_deadline_timer aes xsave avx f16c rdrand lahf_lm abm epb tpr_shadow vnmi flexpriority ept vpid fsgsbase tsc_adjust bmi1 avx2 smep bmi2 erms invpcid cqm xsaveopt cqm_llc cqm_occup_llc dtherm arat pln pts
  bugs		:
  bogomips	: 4590.41
  clflush size	: 64
  cache_alignment	: 64
  address sizes	: 46 bits physical, 48 bits virtual
  power management:

  processor	: 30
  vendor_id	: GenuineIntel
  cpu family	: 6
  model		: 63
  model name	: Intel(R) Xeon(R) CPU E5-2699 v3 @ 2.30GHz
  stepping	: 2
  microcode	: 0x35
  cpu MHz		: 2294.513
  cache size	: 46080 KB
  physical id	: 1
  siblings	: 18
  core id		: 19
  cpu cores	: 18
  apicid		: 102
  initial apicid	: 102
  fpu		: yes
  fpu_exception	: yes
  cpuid level	: 15
  wp		: yes
  flags		: fpu vme de pse tsc msr pae mce cx8 apic sep mtrr pge mca cmov pat pse36 clflush dts acpi mmx fxsr sse sse2 ss ht tm pbe syscall nx pdpe1gb rdtscp lm constant_tsc arch_perfmon pebs bts rep_good nopl xtopology nonstop_tsc aperfmperf eagerfpu pni pclmulqdq dtes64 monitor ds_cpl vmx smx est tm2 ssse3 sdbg fma cx16 xtpr pdcm pcid dca sse4_1 sse4_2 x2apic movbe popcnt tsc_deadline_timer aes xsave avx f16c rdrand lahf_lm abm epb tpr_shadow vnmi flexpriority ept vpid fsgsbase tsc_adjust bmi1 avx2 smep bmi2 erms invpcid cqm xsaveopt cqm_llc cqm_occup_llc dtherm arat pln pts
  bugs		:
  bogomips	: 4590.41
  clflush size	: 64
  cache_alignment	: 64
  address sizes	: 46 bits physical, 48 bits virtual
  power management:

  processor	: 31
  vendor_id	: GenuineIntel
  cpu family	: 6
  model		: 63
  model name	: Intel(R) Xeon(R) CPU E5-2699 v3 @ 2.30GHz
  stepping	: 2
  microcode	: 0x35
  cpu MHz		: 2294.513
  cache size	: 46080 KB
  physical id	: 1
  siblings	: 18
  core id		: 20
  cpu cores	: 18
  apicid		: 104
  initial apicid	: 104
  fpu		: yes
  fpu_exception	: yes
  cpuid level	: 15
  wp		: yes
  flags		: fpu vme de pse tsc msr pae mce cx8 apic sep mtrr pge mca cmov pat pse36 clflush dts acpi mmx fxsr sse sse2 ss ht tm pbe syscall nx pdpe1gb rdtscp lm constant_tsc arch_perfmon pebs bts rep_good nopl xtopology nonstop_tsc aperfmperf eagerfpu pni pclmulqdq dtes64 monitor ds_cpl vmx smx est tm2 ssse3 sdbg fma cx16 xtpr pdcm pcid dca sse4_1 sse4_2 x2apic movbe popcnt tsc_deadline_timer aes xsave avx f16c rdrand lahf_lm abm epb tpr_shadow vnmi flexpriority ept vpid fsgsbase tsc_adjust bmi1 avx2 smep bmi2 erms invpcid cqm xsaveopt cqm_llc cqm_occup_llc dtherm arat pln pts
  bugs		:
  bogomips	: 4590.41
  clflush size	: 64
  cache_alignment	: 64
  address sizes	: 46 bits physical, 48 bits virtual
  power management:

  processor	: 32
  vendor_id	: GenuineIntel
  cpu family	: 6
  model		: 63
  model name	: Intel(R) Xeon(R) CPU E5-2699 v3 @ 2.30GHz
  stepping	: 2
  microcode	: 0x35
  cpu MHz		: 2294.513
  cache size	: 46080 KB
  physical id	: 1
  siblings	: 18
  core id		: 24
  cpu cores	: 18
  apicid		: 112
  initial apicid	: 112
  fpu		: yes
  fpu_exception	: yes
  cpuid level	: 15
  wp		: yes
  flags		: fpu vme de pse tsc msr pae mce cx8 apic sep mtrr pge mca cmov pat pse36 clflush dts acpi mmx fxsr sse sse2 ss ht tm pbe syscall nx pdpe1gb rdtscp lm constant_tsc arch_perfmon pebs bts rep_good nopl xtopology nonstop_tsc aperfmperf eagerfpu pni pclmulqdq dtes64 monitor ds_cpl vmx smx est tm2 ssse3 sdbg fma cx16 xtpr pdcm pcid dca sse4_1 sse4_2 x2apic movbe popcnt tsc_deadline_timer aes xsave avx f16c rdrand lahf_lm abm epb tpr_shadow vnmi flexpriority ept vpid fsgsbase tsc_adjust bmi1 avx2 smep bmi2 erms invpcid cqm xsaveopt cqm_llc cqm_occup_llc dtherm arat pln pts
  bugs		:
  bogomips	: 4590.41
  clflush size	: 64
  cache_alignment	: 64
  address sizes	: 46 bits physical, 48 bits virtual
  power management:

  processor	: 33
  vendor_id	: GenuineIntel
  cpu family	: 6
  model		: 63
  model name	: Intel(R) Xeon(R) CPU E5-2699 v3 @ 2.30GHz
  stepping	: 2
  microcode	: 0x35
  cpu MHz		: 2294.513
  cache size	: 46080 KB
  physical id	: 1
  siblings	: 18
  core id		: 25
  cpu cores	: 18
  apicid		: 114
  initial apicid	: 114
  fpu		: yes
  fpu_exception	: yes
  cpuid level	: 15
  wp		: yes
  flags		: fpu vme de pse tsc msr pae mce cx8 apic sep mtrr pge mca cmov pat pse36 clflush dts acpi mmx fxsr sse sse2 ss ht tm pbe syscall nx pdpe1gb rdtscp lm constant_tsc arch_perfmon pebs bts rep_good nopl xtopology nonstop_tsc aperfmperf eagerfpu pni pclmulqdq dtes64 monitor ds_cpl vmx smx est tm2 ssse3 sdbg fma cx16 xtpr pdcm pcid dca sse4_1 sse4_2 x2apic movbe popcnt tsc_deadline_timer aes xsave avx f16c rdrand lahf_lm abm epb tpr_shadow vnmi flexpriority ept vpid fsgsbase tsc_adjust bmi1 avx2 smep bmi2 erms invpcid cqm xsaveopt cqm_llc cqm_occup_llc dtherm arat pln pts
  bugs		:
  bogomips	: 4590.41
  clflush size	: 64
  cache_alignment	: 64
  address sizes	: 46 bits physical, 48 bits virtual
  power management:

  processor	: 34
  vendor_id	: GenuineIntel
  cpu family	: 6
  model		: 63
  model name	: Intel(R) Xeon(R) CPU E5-2699 v3 @ 2.30GHz
  stepping	: 2
  microcode	: 0x35
  cpu MHz		: 2294.513
  cache size	: 46080 KB
  physical id	: 1
  siblings	: 18
  core id		: 26
  cpu cores	: 18
  apicid		: 116
  initial apicid	: 116
  fpu		: yes
  fpu_exception	: yes
  cpuid level	: 15
  wp		: yes
  flags		: fpu vme de pse tsc msr pae mce cx8 apic sep mtrr pge mca cmov pat pse36 clflush dts acpi mmx fxsr sse sse2 ss ht tm pbe syscall nx pdpe1gb rdtscp lm constant_tsc arch_perfmon pebs bts rep_good nopl xtopology nonstop_tsc aperfmperf eagerfpu pni pclmulqdq dtes64 monitor ds_cpl vmx smx est tm2 ssse3 sdbg fma cx16 xtpr pdcm pcid dca sse4_1 sse4_2 x2apic movbe popcnt tsc_deadline_timer aes xsave avx f16c rdrand lahf_lm abm epb tpr_shadow vnmi flexpriority ept vpid fsgsbase tsc_adjust bmi1 avx2 smep bmi2 erms invpcid cqm xsaveopt cqm_llc cqm_occup_llc dtherm arat pln pts
  bugs		:
  bogomips	: 4590.41
  clflush size	: 64
  cache_alignment	: 64
  address sizes	: 46 bits physical, 48 bits virtual
  power management:

  processor	: 35
  vendor_id	: GenuineIntel
  cpu family	: 6
  model		: 63
  model name	: Intel(R) Xeon(R) CPU E5-2699 v3 @ 2.30GHz
  stepping	: 2
  microcode	: 0x35
  cpu MHz		: 2294.513
  cache size	: 46080 KB
  physical id	: 1
  siblings	: 18
  core id		: 27
  cpu cores	: 18
  apicid		: 118
  initial apicid	: 118
  fpu		: yes
  fpu_exception	: yes
  cpuid level	: 15
  wp		: yes
  flags		: fpu vme de pse tsc msr pae mce cx8 apic sep mtrr pge mca cmov pat pse36 clflush dts acpi mmx fxsr sse sse2 ss ht tm pbe syscall nx pdpe1gb rdtscp lm constant_tsc arch_perfmon pebs bts rep_good nopl xtopology nonstop_tsc aperfmperf eagerfpu pni pclmulqdq dtes64 monitor ds_cpl vmx smx est tm2 ssse3 sdbg fma cx16 xtpr pdcm pcid dca sse4_1 sse4_2 x2apic movbe popcnt tsc_deadline_timer aes xsave avx f16c rdrand lahf_lm abm epb tpr_shadow vnmi flexpriority ept vpid fsgsbase tsc_adjust bmi1 avx2 smep bmi2 erms invpcid cqm xsaveopt cqm_llc cqm_occup_llc dtherm arat pln pts
  bugs		:
  bogomips	: 4590.41
  clflush size	: 64
  cache_alignment	: 64
  address sizes	: 46 bits physical, 48 bits virtual
  power management:

  ]]></exec_output>
      </function>
      <function id="linux_proc_meminfo" significance="1" time="2017-01-27 13:58:18.604298 UTC" version="1.0.0">
        <exec_command><![CDATA[cat /proc/meminfo]]></exec_command>
        <exec_return_code>0</exec_return_code>
        <exec_output><![CDATA[MemTotal:       528285888 kB
  MemFree:        512842508 kB
  MemAvailable:   512796444 kB
  Buffers:          170032 kB
  Cached:          5343940 kB
  SwapCached:            0 kB
  Active:          4199484 kB
  Inactive:        1765228 kB
  Active(anon):    3277756 kB
  Inactive(anon):  1492776 kB
  Active(file):     921728 kB
  Inactive(file):   272452 kB
  Unevictable:           0 kB
  Mlocked:               0 kB
  SwapTotal:        999420 kB
  SwapFree:         999420 kB
  Dirty:                12 kB
  Writeback:             0 kB
  AnonPages:        450820 kB
  Mapped:           113208 kB
  Shmem:           4319796 kB
  Slab:             147836 kB
  SReclaimable:      94848 kB
  SUnreclaim:        52988 kB
  KernelStack:        6096 kB
  PageTables:         3260 kB
  NFS_Unstable:          0 kB
  Bounce:                0 kB
  WritebackTmp:          0 kB
  CommitLimit:    260948060 kB
  Committed_AS:   13186928 kB
  VmallocTotal:   34359738367 kB
  VmallocUsed:           0 kB
  VmallocChunk:          0 kB
  HardwareCorrupted:     0 kB
  AnonHugePages:    419840 kB
  CmaTotal:              0 kB
  CmaFree:               0 kB
  HugePages_Total:    4096
  HugePages_Free:     3072
  HugePages_Rsvd:        0
  HugePages_Surp:        0
  Hugepagesize:       2048 kB
  DirectMap4k:      112156 kB
  DirectMap2M:     5021696 kB
  DirectMap1G:    533725184 kB
  ]]></exec_output>
      </function>
      <function id="linux_lspci" significance="2" time="2017-01-27 13:58:14.667658 UTC" version="1.0.0">
        <exec_command><![CDATA[lspci]]></exec_command>
        <exec_return_code>0</exec_return_code>
        <exec_output><![CDATA[00:00.0 Host bridge: Intel Corporation Xeon E7 v3/Xeon E5 v3/Core i7 DMI2 (rev 02)
  00:01.0 PCI bridge: Intel Corporation Xeon E7 v3/Xeon E5 v3/Core i7 PCI Express Root Port 1 (rev 02)
  00:02.0 PCI bridge: Intel Corporation Xeon E7 v3/Xeon E5 v3/Core i7 PCI Express Root Port 2 (rev 02)
  00:02.2 PCI bridge: Intel Corporation Xeon E7 v3/Xeon E5 v3/Core i7 PCI Express Root Port 2 (rev 02)
  00:03.0 PCI bridge: Intel Corporation Xeon E7 v3/Xeon E5 v3/Core i7 PCI Express Root Port 3 (rev 02)
  00:03.2 PCI bridge: Intel Corporation Xeon E7 v3/Xeon E5 v3/Core i7 PCI Express Root Port 3 (rev 02)
  00:05.0 System peripheral: Intel Corporation Xeon E7 v3/Xeon E5 v3/Core i7 Address Map, VTd_Misc, System Management (rev 02)
  00:05.1 System peripheral: Intel Corporation Xeon E7 v3/Xeon E5 v3/Core i7 Hot Plug (rev 02)
  00:05.2 System peripheral: Intel Corporation Xeon E7 v3/Xeon E5 v3/Core i7 RAS, Control Status and Global Errors (rev 02)
  00:05.4 PIC: Intel Corporation Xeon E7 v3/Xeon E5 v3/Core i7 I/O APIC (rev 02)
  00:11.0 Unassigned class [ff00]: Intel Corporation C610/X99 series chipset SPSR (rev 05)
  00:16.0 Communication controller: Intel Corporation C610/X99 series chipset MEI Controller #1 (rev 05)
  00:16.1 Communication controller: Intel Corporation C610/X99 series chipset MEI Controller #2 (rev 05)
  00:1a.0 USB controller: Intel Corporation C610/X99 series chipset USB Enhanced Host Controller #2 (rev 05)
  00:1c.0 PCI bridge: Intel Corporation C610/X99 series chipset PCI Express Root Port #1 (rev d5)
  00:1c.3 PCI bridge: Intel Corporation C610/X99 series chipset PCI Express Root Port #4 (rev d5)
  00:1c.4 PCI bridge: Intel Corporation C610/X99 series chipset PCI Express Root Port #5 (rev d5)
  00:1d.0 USB controller: Intel Corporation C610/X99 series chipset USB Enhanced Host Controller #1 (rev 05)
  00:1f.0 ISA bridge: Intel Corporation C610/X99 series chipset LPC Controller (rev 05)
  00:1f.2 SATA controller: Intel Corporation C610/X99 series chipset 6-Port SATA Controller [AHCI mode] (rev 05)
  01:00.0 PCI bridge: Cisco Systems Inc VIC 82 PCIe Upstream Port (rev 01)
  02:00.0 PCI bridge: Cisco Systems Inc VIC PCIe Downstream Port (rev a2)
  02:01.0 PCI bridge: Cisco Systems Inc VIC PCIe Downstream Port (rev a2)
  03:00.0 Unclassified device [00ff]: Cisco Systems Inc VIC Management Controller (rev a2)
  04:00.0 PCI bridge: Cisco Systems Inc VIC PCIe Upstream Port (rev a2)
  05:00.0 PCI bridge: Cisco Systems Inc VIC PCIe Downstream Port (rev a2)
  05:01.0 PCI bridge: Cisco Systems Inc VIC PCIe Downstream Port (rev a2)
  05:02.0 PCI bridge: Cisco Systems Inc VIC PCIe Downstream Port (rev a2)
  05:03.0 PCI bridge: Cisco Systems Inc VIC PCIe Downstream Port (rev a2)
  06:00.0 Ethernet controller: Cisco Systems Inc VIC Ethernet NIC (rev a2)
  07:00.0 Ethernet controller: Cisco Systems Inc VIC Ethernet NIC (rev a2)
  08:00.0 Fibre Channel: Cisco Systems Inc VIC FCoE HBA (rev a2)
  09:00.0 Fibre Channel: Cisco Systems Inc VIC FCoE HBA (rev a2)
  0a:00.0 Ethernet controller: Intel Corporation 82599ES 10-Gigabit SFI/SFP+ Network Connection (rev 01)
  0a:00.1 Ethernet controller: Intel Corporation 82599ES 10-Gigabit SFI/SFP+ Network Connection (rev 01)
  0c:00.0 RAID bus controller: LSI Logic / Symbios Logic MegaRAID SAS-3 3108 [Invader] (rev 02)
  0e:00.0 PCI bridge: Cisco Systems Inc VIC 1300 PCIe Upstream Port (rev 01)
  0f:00.0 PCI bridge: Cisco Systems Inc VIC PCIe Downstream Port (rev a2)
  0f:01.0 PCI bridge: Cisco Systems Inc VIC PCIe Downstream Port (rev a2)
  10:00.0 Unclassified device [00ff]: Cisco Systems Inc VIC Management Controller (rev a2)
  11:00.0 PCI bridge: Cisco Systems Inc VIC PCIe Upstream Port (rev a2)
  12:00.0 PCI bridge: Cisco Systems Inc VIC PCIe Downstream Port (rev a2)
  12:01.0 PCI bridge: Cisco Systems Inc VIC PCIe Downstream Port (rev a2)
  13:00.0 Ethernet controller: Cisco Systems Inc VIC Ethernet NIC (rev a2)
  14:00.0 Ethernet controller: Cisco Systems Inc VIC Ethernet NIC (rev a2)
  16:00.0 VGA compatible controller: Matrox Electronics Systems Ltd. MGA G200e [Pilot] ServerEngines (SEP1) (rev 02)
  17:00.0 Ethernet controller: Intel Corporation I350 Gigabit Network Connection (rev 01)
  17:00.1 Ethernet controller: Intel Corporation I350 Gigabit Network Connection (rev 01)
  7f:08.0 System peripheral: Intel Corporation Xeon E7 v3/Xeon E5 v3/Core i7 QPI Link 0 (rev 02)
  7f:08.2 Performance counters: Intel Corporation Xeon E7 v3/Xeon E5 v3/Core i7 QPI Link 0 (rev 02)
  7f:08.3 System peripheral: Intel Corporation Xeon E7 v3/Xeon E5 v3/Core i7 QPI Link 0 (rev 02)
  7f:09.0 System peripheral: Intel Corporation Xeon E7 v3/Xeon E5 v3/Core i7 QPI Link 1 (rev 02)
  7f:09.2 Performance counters: Intel Corporation Xeon E7 v3/Xeon E5 v3/Core i7 QPI Link 1 (rev 02)
  7f:09.3 System peripheral: Intel Corporation Xeon E7 v3/Xeon E5 v3/Core i7 QPI Link 1 (rev 02)
  7f:0b.0 System peripheral: Intel Corporation Xeon E7 v3/Xeon E5 v3/Core i7 R3 QPI Link 0 & 1 Monitoring (rev 02)
  7f:0b.1 Performance counters: Intel Corporation Xeon E7 v3/Xeon E5 v3/Core i7 R3 QPI Link 0 & 1 Monitoring (rev 02)
  7f:0b.2 Performance counters: Intel Corporation Xeon E7 v3/Xeon E5 v3/Core i7 R3 QPI Link 0 & 1 Monitoring (rev 02)
  7f:0c.0 System peripheral: Intel Corporation Xeon E7 v3/Xeon E5 v3/Core i7 Unicast Registers (rev 02)
  7f:0c.1 System peripheral: Intel Corporation Xeon E7 v3/Xeon E5 v3/Core i7 Unicast Registers (rev 02)
  7f:0c.2 System peripheral: Intel Corporation Xeon E7 v3/Xeon E5 v3/Core i7 Unicast Registers (rev 02)
  7f:0c.3 System peripheral: Intel Corporation Xeon E7 v3/Xeon E5 v3/Core i7 Unicast Registers (rev 02)
  7f:0c.4 System peripheral: Intel Corporation Xeon E7 v3/Xeon E5 v3/Core i7 Unicast Registers (rev 02)
  7f:0c.5 System peripheral: Intel Corporation Xeon E7 v3/Xeon E5 v3/Core i7 Unicast Registers (rev 02)
  7f:0c.6 System peripheral: Intel Corporation Xeon E7 v3/Xeon E5 v3/Core i7 Unicast Registers (rev 02)
  7f:0c.7 System peripheral: Intel Corporation Xeon E7 v3/Xeon E5 v3/Core i7 Unicast Registers (rev 02)
  7f:0d.0 System peripheral: Intel Corporation Xeon E7 v3/Xeon E5 v3/Core i7 Unicast Registers (rev 02)
  7f:0d.1 System peripheral: Intel Corporation Xeon E7 v3/Xeon E5 v3/Core i7 Unicast Registers (rev 02)
  7f:0d.2 System peripheral: Intel Corporation Xeon E7 v3/Xeon E5 v3/Core i7 Unicast Registers (rev 02)
  7f:0d.3 System peripheral: Intel Corporation Xeon E7 v3/Xeon E5 v3/Core i7 Unicast Registers (rev 02)
  7f:0d.4 System peripheral: Intel Corporation Xeon E7 v3/Xeon E5 v3/Core i7 Unicast Registers (rev 02)
  7f:0d.5 System peripheral: Intel Corporation Xeon E7 v3/Xeon E5 v3/Core i7 Unicast Registers (rev 02)
  7f:0d.6 System peripheral: Intel Corporation Xeon E7 v3/Xeon E5 v3/Core i7 Unicast Registers (rev 02)
  7f:0d.7 System peripheral: Intel Corporation Xeon E7 v3/Xeon E5 v3/Core i7 Unicast Registers (rev 02)
  7f:0e.0 System peripheral: Intel Corporation Xeon E7 v3/Xeon E5 v3/Core i7 Unicast Registers (rev 02)
  7f:0e.1 System peripheral: Intel Corporation Xeon E7 v3/Xeon E5 v3/Core i7 Unicast Registers (rev 02)
  7f:0f.0 System peripheral: Intel Corporation Xeon E7 v3/Xeon E5 v3/Core i7 Buffered Ring Agent (rev 02)
  7f:0f.1 System peripheral: Intel Corporation Xeon E7 v3/Xeon E5 v3/Core i7 Buffered Ring Agent (rev 02)
  7f:0f.2 System peripheral: Intel Corporation Xeon E7 v3/Xeon E5 v3/Core i7 Buffered Ring Agent (rev 02)
  7f:0f.3 System peripheral: Intel Corporation Xeon E7 v3/Xeon E5 v3/Core i7 Buffered Ring Agent (rev 02)
  7f:0f.4 System peripheral: Intel Corporation Xeon E7 v3/Xeon E5 v3/Core i7 System Address Decoder & Broadcast Registers (rev 02)
  7f:0f.5 System peripheral: Intel Corporation Xeon E7 v3/Xeon E5 v3/Core i7 System Address Decoder & Broadcast Registers (rev 02)
  7f:0f.6 System peripheral: Intel Corporation Xeon E7 v3/Xeon E5 v3/Core i7 System Address Decoder & Broadcast Registers (rev 02)
  7f:10.0 System peripheral: Intel Corporation Xeon E7 v3/Xeon E5 v3/Core i7 PCIe Ring Interface (rev 02)
  7f:10.1 Performance counters: Intel Corporation Xeon E7 v3/Xeon E5 v3/Core i7 PCIe Ring Interface (rev 02)
  7f:10.5 System peripheral: Intel Corporation Xeon E7 v3/Xeon E5 v3/Core i7 Scratchpad & Semaphore Registers (rev 02)
  7f:10.6 Performance counters: Intel Corporation Xeon E7 v3/Xeon E5 v3/Core i7 Scratchpad & Semaphore Registers (rev 02)
  7f:10.7 System peripheral: Intel Corporation Xeon E7 v3/Xeon E5 v3/Core i7 Scratchpad & Semaphore Registers (rev 02)
  7f:12.0 System peripheral: Intel Corporation Xeon E7 v3/Xeon E5 v3/Core i7 Home Agent 0 (rev 02)
  7f:12.1 Performance counters: Intel Corporation Xeon E7 v3/Xeon E5 v3/Core i7 Home Agent 0 (rev 02)
  7f:12.4 System peripheral: Intel Corporation Xeon E7 v3/Xeon E5 v3/Core i7 Home Agent 1 (rev 02)
  7f:12.5 Performance counters: Intel Corporation Xeon E7 v3/Xeon E5 v3/Core i7 Home Agent 1 (rev 02)
  7f:13.0 System peripheral: Intel Corporation Xeon E7 v3/Xeon E5 v3/Core i7 Integrated Memory Controller 0 Target Address, Thermal & RAS Registers (rev 02)
  7f:13.1 System peripheral: Intel Corporation Xeon E7 v3/Xeon E5 v3/Core i7 Integrated Memory Controller 0 Target Address, Thermal & RAS Registers (rev 02)
  7f:13.2 System peripheral: Intel Corporation Xeon E7 v3/Xeon E5 v3/Core i7 Integrated Memory Controller 0 Channel Target Address Decoder (rev 02)
  7f:13.3 System peripheral: Intel Corporation Xeon E7 v3/Xeon E5 v3/Core i7 Integrated Memory Controller 0 Channel Target Address Decoder (rev 02)
  7f:13.6 System peripheral: Intel Corporation Xeon E7 v3/Xeon E5 v3/Core i7 DDRIO Channel 0/1 Broadcast (rev 02)
  7f:13.7 System peripheral: Intel Corporation Xeon E7 v3/Xeon E5 v3/Core i7 DDRIO Global Broadcast (rev 02)
  7f:14.0 System peripheral: Intel Corporation Xeon E7 v3/Xeon E5 v3/Core i7 Integrated Memory Controller 0 Channel 0 Thermal Control (rev 02)
  7f:14.1 System peripheral: Intel Corporation Xeon E7 v3/Xeon E5 v3/Core i7 Integrated Memory Controller 0 Channel 1 Thermal Control (rev 02)
  7f:14.2 System peripheral: Intel Corporation Xeon E7 v3/Xeon E5 v3/Core i7 Integrated Memory Controller 0 Channel 0 ERROR Registers (rev 02)
  7f:14.3 System peripheral: Intel Corporation Xeon E7 v3/Xeon E5 v3/Core i7 Integrated Memory Controller 0 Channel 1 ERROR Registers (rev 02)
  7f:14.4 System peripheral: Intel Corporation Xeon E7 v3/Xeon E5 v3/Core i7 DDRIO (VMSE) 0 & 1 (rev 02)
  7f:14.5 System peripheral: Intel Corporation Xeon E7 v3/Xeon E5 v3/Core i7 DDRIO (VMSE) 0 & 1 (rev 02)
  7f:14.6 System peripheral: Intel Corporation Xeon E7 v3/Xeon E5 v3/Core i7 DDRIO (VMSE) 0 & 1 (rev 02)
  7f:14.7 System peripheral: Intel Corporation Xeon E7 v3/Xeon E5 v3/Core i7 DDRIO (VMSE) 0 & 1 (rev 02)
  7f:16.0 System peripheral: Intel Corporation Xeon E7 v3/Xeon E5 v3/Core i7 Integrated Memory Controller 1 Target Address, Thermal & RAS Registers (rev 02)
  7f:16.1 System peripheral: Intel Corporation Xeon E7 v3/Xeon E5 v3/Core i7 Integrated Memory Controller 1 Target Address, Thermal & RAS Registers (rev 02)
  7f:16.2 System peripheral: Intel Corporation Xeon E7 v3/Xeon E5 v3/Core i7 Integrated Memory Controller 1 Channel Target Address Decoder (rev 02)
  7f:16.3 System peripheral: Intel Corporation Xeon E7 v3/Xeon E5 v3/Core i7 Integrated Memory Controller 1 Channel Target Address Decoder (rev 02)
  7f:16.6 System peripheral: Intel Corporation Xeon E7 v3/Xeon E5 v3/Core i7 DDRIO Channel 2/3 Broadcast (rev 02)
  7f:16.7 System peripheral: Intel Corporation Xeon E7 v3/Xeon E5 v3/Core i7 DDRIO Global Broadcast (rev 02)
  7f:17.0 System peripheral: Intel Corporation Xeon E7 v3/Xeon E5 v3/Core i7 Integrated Memory Controller 1 Channel 0 Thermal Control (rev 02)
  7f:17.1 System peripheral: Intel Corporation Xeon E7 v3/Xeon E5 v3/Core i7 Integrated Memory Controller 1 Channel 1 Thermal Control (rev 02)
  7f:17.2 System peripheral: Intel Corporation Xeon E7 v3/Xeon E5 v3/Core i7 Integrated Memory Controller 1 Channel 0 ERROR Registers (rev 02)
  7f:17.3 System peripheral: Intel Corporation Xeon E7 v3/Xeon E5 v3/Core i7 Integrated Memory Controller 1 Channel 1 ERROR Registers (rev 02)
  7f:17.4 System peripheral: Intel Corporation Xeon E7 v3/Xeon E5 v3/Core i7 DDRIO (VMSE) 2 & 3 (rev 02)
  7f:17.5 System peripheral: Intel Corporation Xeon E7 v3/Xeon E5 v3/Core i7 DDRIO (VMSE) 2 & 3 (rev 02)
  7f:17.6 System peripheral: Intel Corporation Xeon E7 v3/Xeon E5 v3/Core i7 DDRIO (VMSE) 2 & 3 (rev 02)
  7f:17.7 System peripheral: Intel Corporation Xeon E7 v3/Xeon E5 v3/Core i7 DDRIO (VMSE) 2 & 3 (rev 02)
  7f:1e.0 System peripheral: Intel Corporation Xeon E7 v3/Xeon E5 v3/Core i7 Power Control Unit (rev 02)
  7f:1e.1 System peripheral: Intel Corporation Xeon E7 v3/Xeon E5 v3/Core i7 Power Control Unit (rev 02)
  7f:1e.2 System peripheral: Intel Corporation Xeon E7 v3/Xeon E5 v3/Core i7 Power Control Unit (rev 02)
  7f:1e.3 System peripheral: Intel Corporation Xeon E7 v3/Xeon E5 v3/Core i7 Power Control Unit (rev 02)
  7f:1e.4 System peripheral: Intel Corporation Xeon E7 v3/Xeon E5 v3/Core i7 Power Control Unit (rev 02)
  7f:1f.0 System peripheral: Intel Corporation Xeon E7 v3/Xeon E5 v3/Core i7 VCU (rev 02)
  7f:1f.2 System peripheral: Intel Corporation Xeon E7 v3/Xeon E5 v3/Core i7 VCU (rev 02)
  80:00.0 PCI bridge: Intel Corporation Xeon E7 v3/Xeon E5 v3/Core i7 PCI Express Root Port 0 (rev 02)
  80:01.0 PCI bridge: Intel Corporation Xeon E7 v3/Xeon E5 v3/Core i7 PCI Express Root Port 1 (rev 02)
  80:01.1 PCI bridge: Intel Corporation Xeon E7 v3/Xeon E5 v3/Core i7 PCI Express Root Port 1 (rev 02)
  80:02.0 PCI bridge: Intel Corporation Xeon E7 v3/Xeon E5 v3/Core i7 PCI Express Root Port 2 (rev 02)
  80:02.2 PCI bridge: Intel Corporation Xeon E7 v3/Xeon E5 v3/Core i7 PCI Express Root Port 2 (rev 02)
  80:03.0 PCI bridge: Intel Corporation Xeon E7 v3/Xeon E5 v3/Core i7 PCI Express Root Port 3 (rev 02)
  80:05.0 System peripheral: Intel Corporation Xeon E7 v3/Xeon E5 v3/Core i7 Address Map, VTd_Misc, System Management (rev 02)
  80:05.1 System peripheral: Intel Corporation Xeon E7 v3/Xeon E5 v3/Core i7 Hot Plug (rev 02)
  80:05.2 System peripheral: Intel Corporation Xeon E7 v3/Xeon E5 v3/Core i7 RAS, Control Status and Global Errors (rev 02)
  80:05.4 PIC: Intel Corporation Xeon E7 v3/Xeon E5 v3/Core i7 I/O APIC (rev 02)
  85:00.0 Ethernet controller: Intel Corporation Ethernet Controller XL710 for 40GbE QSFP+ (rev 01)
  85:00.1 Ethernet controller: Intel Corporation Ethernet Controller XL710 for 40GbE QSFP+ (rev 01)
  87:00.0 Ethernet controller: Intel Corporation Ethernet Controller X710 for 10GbE SFP+ (rev 01)
  87:00.1 Ethernet controller: Intel Corporation Ethernet Controller X710 for 10GbE SFP+ (rev 01)
  ff:08.0 System peripheral: Intel Corporation Xeon E7 v3/Xeon E5 v3/Core i7 QPI Link 0 (rev 02)
  ff:08.2 Performance counters: Intel Corporation Xeon E7 v3/Xeon E5 v3/Core i7 QPI Link 0 (rev 02)
  ff:08.3 System peripheral: Intel Corporation Xeon E7 v3/Xeon E5 v3/Core i7 QPI Link 0 (rev 02)
  ff:09.0 System peripheral: Intel Corporation Xeon E7 v3/Xeon E5 v3/Core i7 QPI Link 1 (rev 02)
  ff:09.2 Performance counters: Intel Corporation Xeon E7 v3/Xeon E5 v3/Core i7 QPI Link 1 (rev 02)
  ff:09.3 System peripheral: Intel Corporation Xeon E7 v3/Xeon E5 v3/Core i7 QPI Link 1 (rev 02)
  ff:0b.0 System peripheral: Intel Corporation Xeon E7 v3/Xeon E5 v3/Core i7 R3 QPI Link 0 & 1 Monitoring (rev 02)
  ff:0b.1 Performance counters: Intel Corporation Xeon E7 v3/Xeon E5 v3/Core i7 R3 QPI Link 0 & 1 Monitoring (rev 02)
  ff:0b.2 Performance counters: Intel Corporation Xeon E7 v3/Xeon E5 v3/Core i7 R3 QPI Link 0 & 1 Monitoring (rev 02)
  ff:0c.0 System peripheral: Intel Corporation Xeon E7 v3/Xeon E5 v3/Core i7 Unicast Registers (rev 02)
  ff:0c.1 System peripheral: Intel Corporation Xeon E7 v3/Xeon E5 v3/Core i7 Unicast Registers (rev 02)
  ff:0c.2 System peripheral: Intel Corporation Xeon E7 v3/Xeon E5 v3/Core i7 Unicast Registers (rev 02)
  ff:0c.3 System peripheral: Intel Corporation Xeon E7 v3/Xeon E5 v3/Core i7 Unicast Registers (rev 02)
  ff:0c.4 System peripheral: Intel Corporation Xeon E7 v3/Xeon E5 v3/Core i7 Unicast Registers (rev 02)
  ff:0c.5 System peripheral: Intel Corporation Xeon E7 v3/Xeon E5 v3/Core i7 Unicast Registers (rev 02)
  ff:0c.6 System peripheral: Intel Corporation Xeon E7 v3/Xeon E5 v3/Core i7 Unicast Registers (rev 02)
  ff:0c.7 System peripheral: Intel Corporation Xeon E7 v3/Xeon E5 v3/Core i7 Unicast Registers (rev 02)
  ff:0d.0 System peripheral: Intel Corporation Xeon E7 v3/Xeon E5 v3/Core i7 Unicast Registers (rev 02)
  ff:0d.1 System peripheral: Intel Corporation Xeon E7 v3/Xeon E5 v3/Core i7 Unicast Registers (rev 02)
  ff:0d.2 System peripheral: Intel Corporation Xeon E7 v3/Xeon E5 v3/Core i7 Unicast Registers (rev 02)
  ff:0d.3 System peripheral: Intel Corporation Xeon E7 v3/Xeon E5 v3/Core i7 Unicast Registers (rev 02)
  ff:0d.4 System peripheral: Intel Corporation Xeon E7 v3/Xeon E5 v3/Core i7 Unicast Registers (rev 02)
  ff:0d.5 System peripheral: Intel Corporation Xeon E7 v3/Xeon E5 v3/Core i7 Unicast Registers (rev 02)
  ff:0d.6 System peripheral: Intel Corporation Xeon E7 v3/Xeon E5 v3/Core i7 Unicast Registers (rev 02)
  ff:0d.7 System peripheral: Intel Corporation Xeon E7 v3/Xeon E5 v3/Core i7 Unicast Registers (rev 02)
  ff:0e.0 System peripheral: Intel Corporation Xeon E7 v3/Xeon E5 v3/Core i7 Unicast Registers (rev 02)
  ff:0e.1 System peripheral: Intel Corporation Xeon E7 v3/Xeon E5 v3/Core i7 Unicast Registers (rev 02)
  ff:0f.0 System peripheral: Intel Corporation Xeon E7 v3/Xeon E5 v3/Core i7 Buffered Ring Agent (rev 02)
  ff:0f.1 System peripheral: Intel Corporation Xeon E7 v3/Xeon E5 v3/Core i7 Buffered Ring Agent (rev 02)
  ff:0f.2 System peripheral: Intel Corporation Xeon E7 v3/Xeon E5 v3/Core i7 Buffered Ring Agent (rev 02)
  ff:0f.3 System peripheral: Intel Corporation Xeon E7 v3/Xeon E5 v3/Core i7 Buffered Ring Agent (rev 02)
  ff:0f.4 System peripheral: Intel Corporation Xeon E7 v3/Xeon E5 v3/Core i7 System Address Decoder & Broadcast Registers (rev 02)
  ff:0f.5 System peripheral: Intel Corporation Xeon E7 v3/Xeon E5 v3/Core i7 System Address Decoder & Broadcast Registers (rev 02)
  ff:0f.6 System peripheral: Intel Corporation Xeon E7 v3/Xeon E5 v3/Core i7 System Address Decoder & Broadcast Registers (rev 02)
  ff:10.0 System peripheral: Intel Corporation Xeon E7 v3/Xeon E5 v3/Core i7 PCIe Ring Interface (rev 02)
  ff:10.1 Performance counters: Intel Corporation Xeon E7 v3/Xeon E5 v3/Core i7 PCIe Ring Interface (rev 02)
  ff:10.5 System peripheral: Intel Corporation Xeon E7 v3/Xeon E5 v3/Core i7 Scratchpad & Semaphore Registers (rev 02)
  ff:10.6 Performance counters: Intel Corporation Xeon E7 v3/Xeon E5 v3/Core i7 Scratchpad & Semaphore Registers (rev 02)
  ff:10.7 System peripheral: Intel Corporation Xeon E7 v3/Xeon E5 v3/Core i7 Scratchpad & Semaphore Registers (rev 02)
  ff:12.0 System peripheral: Intel Corporation Xeon E7 v3/Xeon E5 v3/Core i7 Home Agent 0 (rev 02)
  ff:12.1 Performance counters: Intel Corporation Xeon E7 v3/Xeon E5 v3/Core i7 Home Agent 0 (rev 02)
  ff:12.4 System peripheral: Intel Corporation Xeon E7 v3/Xeon E5 v3/Core i7 Home Agent 1 (rev 02)
  ff:12.5 Performance counters: Intel Corporation Xeon E7 v3/Xeon E5 v3/Core i7 Home Agent 1 (rev 02)
  ff:13.0 System peripheral: Intel Corporation Xeon E7 v3/Xeon E5 v3/Core i7 Integrated Memory Controller 0 Target Address, Thermal & RAS Registers (rev 02)
  ff:13.1 System peripheral: Intel Corporation Xeon E7 v3/Xeon E5 v3/Core i7 Integrated Memory Controller 0 Target Address, Thermal & RAS Registers (rev 02)
  ff:13.2 System peripheral: Intel Corporation Xeon E7 v3/Xeon E5 v3/Core i7 Integrated Memory Controller 0 Channel Target Address Decoder (rev 02)
  ff:13.3 System peripheral: Intel Corporation Xeon E7 v3/Xeon E5 v3/Core i7 Integrated Memory Controller 0 Channel Target Address Decoder (rev 02)
  ff:13.6 System peripheral: Intel Corporation Xeon E7 v3/Xeon E5 v3/Core i7 DDRIO Channel 0/1 Broadcast (rev 02)
  ff:13.7 System peripheral: Intel Corporation Xeon E7 v3/Xeon E5 v3/Core i7 DDRIO Global Broadcast (rev 02)
  ff:14.0 System peripheral: Intel Corporation Xeon E7 v3/Xeon E5 v3/Core i7 Integrated Memory Controller 0 Channel 0 Thermal Control (rev 02)
  ff:14.1 System peripheral: Intel Corporation Xeon E7 v3/Xeon E5 v3/Core i7 Integrated Memory Controller 0 Channel 1 Thermal Control (rev 02)
  ff:14.2 System peripheral: Intel Corporation Xeon E7 v3/Xeon E5 v3/Core i7 Integrated Memory Controller 0 Channel 0 ERROR Registers (rev 02)
  ff:14.3 System peripheral: Intel Corporation Xeon E7 v3/Xeon E5 v3/Core i7 Integrated Memory Controller 0 Channel 1 ERROR Registers (rev 02)
  ff:14.4 System peripheral: Intel Corporation Xeon E7 v3/Xeon E5 v3/Core i7 DDRIO (VMSE) 0 & 1 (rev 02)
  ff:14.5 System peripheral: Intel Corporation Xeon E7 v3/Xeon E5 v3/Core i7 DDRIO (VMSE) 0 & 1 (rev 02)
  ff:14.6 System peripheral: Intel Corporation Xeon E7 v3/Xeon E5 v3/Core i7 DDRIO (VMSE) 0 & 1 (rev 02)
  ff:14.7 System peripheral: Intel Corporation Xeon E7 v3/Xeon E5 v3/Core i7 DDRIO (VMSE) 0 & 1 (rev 02)
  ff:16.0 System peripheral: Intel Corporation Xeon E7 v3/Xeon E5 v3/Core i7 Integrated Memory Controller 1 Target Address, Thermal & RAS Registers (rev 02)
  ff:16.1 System peripheral: Intel Corporation Xeon E7 v3/Xeon E5 v3/Core i7 Integrated Memory Controller 1 Target Address, Thermal & RAS Registers (rev 02)
  ff:16.2 System peripheral: Intel Corporation Xeon E7 v3/Xeon E5 v3/Core i7 Integrated Memory Controller 1 Channel Target Address Decoder (rev 02)
  ff:16.3 System peripheral: Intel Corporation Xeon E7 v3/Xeon E5 v3/Core i7 Integrated Memory Controller 1 Channel Target Address Decoder (rev 02)
  ff:16.6 System peripheral: Intel Corporation Xeon E7 v3/Xeon E5 v3/Core i7 DDRIO Channel 2/3 Broadcast (rev 02)
  ff:16.7 System peripheral: Intel Corporation Xeon E7 v3/Xeon E5 v3/Core i7 DDRIO Global Broadcast (rev 02)
  ff:17.0 System peripheral: Intel Corporation Xeon E7 v3/Xeon E5 v3/Core i7 Integrated Memory Controller 1 Channel 0 Thermal Control (rev 02)
  ff:17.1 System peripheral: Intel Corporation Xeon E7 v3/Xeon E5 v3/Core i7 Integrated Memory Controller 1 Channel 1 Thermal Control (rev 02)
  ff:17.2 System peripheral: Intel Corporation Xeon E7 v3/Xeon E5 v3/Core i7 Integrated Memory Controller 1 Channel 0 ERROR Registers (rev 02)
  ff:17.3 System peripheral: Intel Corporation Xeon E7 v3/Xeon E5 v3/Core i7 Integrated Memory Controller 1 Channel 1 ERROR Registers (rev 02)
  ff:17.4 System peripheral: Intel Corporation Xeon E7 v3/Xeon E5 v3/Core i7 DDRIO (VMSE) 2 & 3 (rev 02)
  ff:17.5 System peripheral: Intel Corporation Xeon E7 v3/Xeon E5 v3/Core i7 DDRIO (VMSE) 2 & 3 (rev 02)
  ff:17.6 System peripheral: Intel Corporation Xeon E7 v3/Xeon E5 v3/Core i7 DDRIO (VMSE) 2 & 3 (rev 02)
  ff:17.7 System peripheral: Intel Corporation Xeon E7 v3/Xeon E5 v3/Core i7 DDRIO (VMSE) 2 & 3 (rev 02)
  ff:1e.0 System peripheral: Intel Corporation Xeon E7 v3/Xeon E5 v3/Core i7 Power Control Unit (rev 02)
  ff:1e.1 System peripheral: Intel Corporation Xeon E7 v3/Xeon E5 v3/Core i7 Power Control Unit (rev 02)
  ff:1e.2 System peripheral: Intel Corporation Xeon E7 v3/Xeon E5 v3/Core i7 Power Control Unit (rev 02)
  ff:1e.3 System peripheral: Intel Corporation Xeon E7 v3/Xeon E5 v3/Core i7 Power Control Unit (rev 02)
  ff:1e.4 System peripheral: Intel Corporation Xeon E7 v3/Xeon E5 v3/Core i7 Power Control Unit (rev 02)
  ff:1f.0 System peripheral: Intel Corporation Xeon E7 v3/Xeon E5 v3/Core i7 VCU (rev 02)
  ff:1f.2 System peripheral: Intel Corporation Xeon E7 v3/Xeon E5 v3/Core i7 VCU (rev 02)
  ]]></exec_output>
      </function>
      <function id="linux_cgroup_cpuset" significance="2" time="2017-01-27 13:58:21.596662 UTC" version="1.0.0">
        <exec_command><![CDATA[for a in $(find /sys/fs/cgroup/cpuset -type d) ; do echo $a ; echo -n "CPUs = " ; cat $a/cpuset.cpus ; echo -n "MEMs = " ; cat $a/cpuset.mems ; echo -n "PIDs/TIDs = " ; cat $a/tasks | tr '\012' ',' ; echo ; echo ; done]]></exec_command>
        <exec_return_code>0</exec_return_code>
        <exec_output><![CDATA[/sys/fs/cgroup/cpuset
  CPUs = 0-35
  MEMs = 0-1
  PIDs/TIDs = 1,2,3,5,8,9,10,11,12,13,14,16,17,18,19,21,22,23,24,26,27,28,29,31,32,33,34,35,36,37,38,39,40,41,42,43,44,45,46,47,48,49,50,51,52,53,54,55,56,57,58,59,60,61,62,63,64,65,66,67,68,69,70,71,72,73,74,75,76,77,78,79,80,81,82,83,84,85,86,87,88,89,90,91,92,93,94,95,96,97,98,99,101,103,104,105,107,108,109,110,111,112,113,114,115,117,118,119,120,122,123,124,125,126,127,128,129,130,131,132,133,134,135,136,137,138,139,140,141,142,143,144,145,146,147,148,149,150,151,152,153,154,155,156,157,158,159,160,161,162,163,164,165,166,167,168,169,170,171,172,173,174,175,176,177,178,179,180,181,182,183,184,185,186,187,188,189,190,191,192,193,194,195,196,197,198,199,200,201,205,206,207,208,209,225,228,229,230,231,232,233,234,235,236,237,238,239,240,241,242,243,244,245,246,247,248,249,250,251,252,255,261,274,276,312,313,314,315,324,329,333,334,335,337,340,341,343,344,345,352,353,355,356,360,361,363,364,371,372,373,374,404,405,461,601,879,880,912,917,921,935,936,937,938,939,940,941,942,944,945,947,948,949,950,951,952,953,954,955,956,957,959,960,961,962,963,1011,1038,1061,1110,1135,1136,1144,1169,1220,1333,1347,1352,1354,1355,1356,1359,1362,1415,1421,1432,1459,1461,3657,5907,6236,6830,7418,7423,7509,7981,8669,8676,9387,9481,9486,9487,9495,10069,10078,10111,10116,10117,12758,14060,14061,14108,16956,17226,17518,20356,20710,24548,24550,25286,26127,26136,27016,27890,29718,32537,35499,35974,

  ]]></exec_output>
      </function>
    </section>
    <section id="3" name="Compute Operating System">
      <function id="linux_centos_release" significance="1" time="2017-01-27 13:58:20.299730 UTC" version="1.0.0">
        <exec_command><![CDATA[rpm -q centos-release]]></exec_command>
        <exec_return_code>127</exec_return_code>
        <exec_output><![CDATA[bash: rpm: command not found
  ]]></exec_output>
      </function>
      <function id="linux_kernel_version" significance="1" time="2017-01-27 13:58:26.139348 UTC" version="1.0.0">
        <exec_command><![CDATA[uname -a]]></exec_command>
        <exec_return_code>0</exec_return_code>
        <exec_output><![CDATA[Linux t1-sut1 4.4.0-42-generic #62-Ubuntu SMP Fri Oct 7 23:11:45 UTC 2016 x86_64 x86_64 x86_64 GNU/Linux
  ]]></exec_output>
      </function>
      <function id="linux_linux_version" significance="1" time="2017-01-27 13:58:27.949997 UTC" version="1.0.0">
        <exec_command><![CDATA[lsb_release -a]]></exec_command>
        <exec_return_code>0</exec_return_code>
        <exec_output><![CDATA[Distributor ID:	Ubuntu
  Description:	Ubuntu 16.04.1 LTS
  Release:	16.04
  Codename:	xenial
  ]]></exec_output>
      </function>
      <function id="linux_os_release" significance="1" time="2017-01-27 13:58:30.993370 UTC" version="1.0.0">
        <exec_command><![CDATA[cat /etc/os-release]]></exec_command>
        <exec_return_code>0</exec_return_code>
        <exec_output><![CDATA[NAME="Ubuntu"
  VERSION="16.04.1 LTS (Xenial Xerus)"
  ID=ubuntu
  ID_LIKE=debian
  PRETTY_NAME="Ubuntu 16.04.1 LTS"
  VERSION_ID="16.04"
  HOME_URL="http://www.ubuntu.com/"
  SUPPORT_URL="http://help.ubuntu.com/"
  BUG_REPORT_URL="http://bugs.launchpad.net/ubuntu/"
  UBUNTU_CODENAME=xenial
  ]]></exec_output>
      </function>
      <function id="linux_proc_cmdline" significance="1" time="2017-01-27 13:58:32.089255 UTC" version="1.0.0">
        <exec_command><![CDATA[cat /proc/cmdline]]></exec_command>
        <exec_return_code>0</exec_return_code>
        <exec_output><![CDATA[BOOT_IMAGE=/vmlinuz-4.4.0-42-generic root=UUID=efb7e8b3-3548-4440-98f6-6ebe102e9ec6 ro isolcpus=1-17,19-35 nohz_full=1-17,19-35 rcu_nocbs=1-17,19-35 intel_pstate=disable console=tty0 console=ttyS0,115200n8
  ]]></exec_output>
      </function>
      <function id="linux_proc_mounts" significance="1" time="2017-01-27 13:58:33.115767 UTC" version="1.0.0">
        <exec_command><![CDATA[cat /proc/mounts]]></exec_command>
        <exec_return_code>0</exec_return_code>
        <exec_output><![CDATA[sysfs /sys sysfs rw,nosuid,nodev,noexec,relatime 0 0
  proc /proc proc rw,nosuid,nodev,noexec,relatime 0 0
  udev /dev devtmpfs rw,nosuid,relatime,size=264125516k,nr_inodes=66031379,mode=755 0 0
  devpts /dev/pts devpts rw,nosuid,noexec,relatime,gid=5,mode=620,ptmxmode=000 0 0
  tmpfs /run tmpfs rw,nosuid,noexec,relatime,size=52828592k,mode=755 0 0
  /dev/sda2 / ext4 rw,relatime,errors=remount-ro,data=ordered 0 0
  securityfs /sys/kernel/security securityfs rw,nosuid,nodev,noexec,relatime 0 0
  tmpfs /dev/shm tmpfs rw,nosuid,nodev 0 0
  tmpfs /run/lock tmpfs rw,nosuid,nodev,noexec,relatime,size=5120k 0 0
  tmpfs /sys/fs/cgroup tmpfs ro,nosuid,nodev,noexec,mode=755 0 0
  cgroup /sys/fs/cgroup/systemd cgroup rw,nosuid,nodev,noexec,relatime,xattr,release_agent=/lib/systemd/systemd-cgroups-agent,name=systemd 0 0
  pstore /sys/fs/pstore pstore rw,nosuid,nodev,noexec,relatime 0 0
  cgroup /sys/fs/cgroup/blkio cgroup rw,nosuid,nodev,noexec,relatime,blkio 0 0
  cgroup /sys/fs/cgroup/perf_event cgroup rw,nosuid,nodev,noexec,relatime,perf_event 0 0
  cgroup /sys/fs/cgroup/pids cgroup rw,nosuid,nodev,noexec,relatime,pids 0 0
  cgroup /sys/fs/cgroup/net_cls,net_prio cgroup rw,nosuid,nodev,noexec,relatime,net_cls,net_prio 0 0
  cgroup /sys/fs/cgroup/freezer cgroup rw,nosuid,nodev,noexec,relatime,freezer 0 0
  cgroup /sys/fs/cgroup/memory cgroup rw,nosuid,nodev,noexec,relatime,memory 0 0
  cgroup /sys/fs/cgroup/cpu,cpuacct cgroup rw,nosuid,nodev,noexec,relatime,cpu,cpuacct 0 0
  cgroup /sys/fs/cgroup/hugetlb cgroup rw,nosuid,nodev,noexec,relatime,hugetlb 0 0
  cgroup /sys/fs/cgroup/devices cgroup rw,nosuid,nodev,noexec,relatime,devices 0 0
  cgroup /sys/fs/cgroup/cpuset cgroup rw,nosuid,nodev,noexec,relatime,cpuset 0 0
  systemd-1 /proc/sys/fs/binfmt_misc autofs rw,relatime,fd=32,pgrp=1,timeout=0,minproto=5,maxproto=5,direct 0 0
  mqueue /dev/mqueue mqueue rw,relatime 0 0
  debugfs /sys/kernel/debug debugfs rw,relatime 0 0
  hugetlbfs /dev/hugepages hugetlbfs rw,relatime 0 0
  tracefs /sys/kernel/debug/tracing tracefs rw,relatime 0 0
  fusectl /sys/fs/fuse/connections fusectl rw,relatime 0 0
  /dev/sda1 /boot ext4 rw,relatime,data=ordered 0 0
  none /mnt/huge hugetlbfs rw,relatime,pagesize=2048k 0 0
  none /mnt/huge hugetlbfs rw,relatime,pagesize=2048k 0 0
  none /mnt/huge hugetlbfs rw,relatime,pagesize=2048k 0 0
  none /mnt/huge hugetlbfs rw,relatime,pagesize=2048k 0 0
  none /mnt/huge hugetlbfs rw,relatime,pagesize=2048k 0 0
  none /mnt/huge hugetlbfs rw,relatime,pagesize=2048k 0 0
  binfmt_misc /proc/sys/fs/binfmt_misc binfmt_misc rw,relatime 0 0
  ]]></exec_output>
      </function>
      <function id="linux_rhel_release" significance="1" time="2017-01-27 13:58:34.546507 UTC" version="1.0.0">
        <exec_command><![CDATA[cat /etc/redhat-release]]></exec_command>
        <exec_return_code>1</exec_return_code>
        <exec_output><![CDATA[cat: /etc/redhat-release: No such file or directory
  ]]></exec_output>
      </function>
      <function id="linux_dtime" significance="1" time="2017-01-27 13:58:39.106331 UTC" version="1.0.0">
        <exec_command><![CDATA[date +'%b %d %Y %H:%M:%S %Z']]></exec_command>
        <exec_return_code>0</exec_return_code>
        <exec_output>
          <time>Jan 27 2017 05:58:38 PST</time>
        </exec_output>
      </function>
      <function id="linux_installed_packages_dpkg" significance="2" time="2017-01-27 13:58:24.251357 UTC" version="1.0.0">
        <exec_command><![CDATA[dpkg -l]]></exec_command>
        <exec_return_code>0</exec_return_code>
        <exec_output><![CDATA[Desired=Unknown/Install/Remove/Purge/Hold
  | Status=Not/Inst/Conf-files/Unpacked/halF-conf/Half-inst/trig-aWait/Trig-pend
  |/ Err?=(none)/Reinst-required (Status,Err: uppercase=bad)
  ||/ Name                               Version                             Architecture Description
  +++-==================================-===================================-============-===============================================================================
  ii  accountsservice                    0.6.40-2ubuntu11.1                  amd64        query and manipulate user account information
  ii  acl                                2.2.52-3                            amd64        Access control list utilities
  ii  adduser                            3.113+nmu3ubuntu4                   all          add and remove users and groups
  ii  apt                                1.2.12~ubuntu16.04.1                amd64        commandline package manager
  ii  apt-utils                          1.2.12~ubuntu16.04.1                amd64        package management related utility programs
  ii  autoconf                           2.69-9                              all          automatic configure script builder
  ii  automake                           1:1.15-4ubuntu1                     all          Tool for generating GNU Standards-compliant Makefiles
  ii  autotools-dev                      20150820.1                          all          Update infrastructure for config.{guess,sub} files
  ii  base-files                         9.4ubuntu4.2                        amd64        Debian base system miscellaneous files
  ii  base-passwd                        3.5.39                              amd64        Debian base system master password and group files
  ii  bash                               4.3-14ubuntu1.1                     amd64        GNU Bourne Again SHell
  ii  binutils                           2.26.1-1ubuntu1~16.04.3             amd64        GNU assembler, linker and binary utilities
  ii  bsdutils                           1:2.27.1-6ubuntu3.1                 amd64        basic utilities from 4.4BSD-Lite
  ii  build-essential                    12.1ubuntu2                         amd64        Informational list of build-essential packages
  ii  busybox-initramfs                  1:1.22.0-15ubuntu1                  amd64        Standalone shell setup for initramfs
  ii  bzip2                              1.0.6-8                             amd64        high-quality block-sorting file compressor - utilities
  ii  ca-certificates                    20160104ubuntu1                     all          Common CA certificates
  ii  cgroup-bin                         0.41-7ubuntu1                       all          control and monitor control groups (transitional package)
  ii  cgroup-lite                        1.11                                all          Light-weight package to set up cgroups at system boot
  ii  cgroup-tools                       0.41-7ubuntu1                       amd64        control and monitor control groups (tools)
  ii  console-setup                      1.108ubuntu15.2                     all          console font and keymap setup program
  ii  console-setup-linux                1.108ubuntu15.2                     all          Linux specific part of console-setup
  ii  coreutils                          8.25-2ubuntu2                       amd64        GNU core utilities
  ii  cpio                               2.11+dfsg-5ubuntu1                  amd64        GNU cpio -- a program to manage archives of files
  ii  cpp                                4:5.3.1-1ubuntu1                    amd64        GNU C preprocessor (cpp)
  ii  cpp-5                              5.4.0-6ubuntu1~16.04.2              amd64        GNU C preprocessor
  ii  cpu-checker                        0.7-0ubuntu7                        amd64        tools to help evaluate certain CPU (or BIOS) features
  ii  cpufrequtils                       008-1                               amd64        utilities to deal with the cpufreq Linux kernel feature
  ii  crda                               3.13-1                              amd64        wireless Central Regulatory Domain Agent
  ii  cron                               3.0pl1-128ubuntu2                   amd64        process scheduling daemon
  ii  crudini                            0.7-1                               amd64        utility for manipulating ini files
  ii  dash                               0.5.8-2.1ubuntu2                    amd64        POSIX-compliant shell
  ii  dbus                               1.10.6-1ubuntu3                     amd64        simple interprocess messaging system (daemon and utilities)
  ii  debconf                            1.5.58ubuntu1                       all          Debian configuration management system
  ii  debconf-i18n                       1.5.58ubuntu1                       all          full internationalization support for debconf
  ii  debianutils                        4.7                                 amd64        Miscellaneous utilities specific to Debian
  ii  dh-python                          2.20151103ubuntu1.1                 all          Debian helper tools for packaging Python libraries and applications
  ii  diffutils                          1:3.3-3                             amd64        File comparison utilities
  ii  distro-info-data                   0.28ubuntu0.1                       all          information about the distributions' releases (data files)
  ii  dkms                               2.2.0.3-2ubuntu11.2                 all          Dynamic Kernel Module Support Framework
  ii  dmidecode                          3.0-2ubuntu0.1                      amd64        SMBIOS/DMI table decoder
  ii  dpkg                               1.18.4ubuntu1.1                     amd64        Debian package management system
  ii  dpkg-dev                           1.18.4ubuntu1.1                     all          Debian package development tools
  ii  e2fslibs:amd64                     1.42.13-1ubuntu1                    amd64        ext2/ext3/ext4 file system libraries
  ii  e2fsprogs                          1.42.13-1ubuntu1                    amd64        ext2/ext3/ext4 file system utilities
  ii  eject                              2.1.5+deb1+cvs20081104-13.1         amd64        ejects CDs and operates CD-Changers under Linux
  ii  ethtool                            1:4.5-1                             amd64        display or change Ethernet device settings
  ii  expect                             5.45-7                              amd64        Automates interactive applications
  ii  fakeroot                           1.20.2-1ubuntu1                     amd64        tool for simulating superuser privileges
  ii  file                               1:5.25-2ubuntu1                     amd64        Determines file type using "magic" numbers
  ii  findutils                          4.6.0+git+20160126-2                amd64        utilities for finding files--find, xargs
  ii  fontconfig-config                  2.11.94-0ubuntu1.1                  all          generic font configuration library - configuration
  ii  fonts-dejavu-core                  2.35-1                              all          Vera font family derivate with additional characters
  ii  g++                                4:5.3.1-1ubuntu1                    amd64        GNU C++ compiler
  ii  g++-5                              5.4.0-6ubuntu1~16.04.2              amd64        GNU C++ compiler
  ii  gcc                                4:5.3.1-1ubuntu1                    amd64        GNU C compiler
  ii  gcc-5                              5.4.0-6ubuntu1~16.04.2              amd64        GNU C compiler
  ii  gcc-5-base:amd64                   5.4.0-6ubuntu1~16.04.2              amd64        GCC, the GNU Compiler Collection (base package)
  ii  gcc-6-base:amd64                   6.0.1-0ubuntu1                      amd64        GCC, the GNU Compiler Collection (base package)
  ii  gettext-base                       0.19.7-2ubuntu3                     amd64        GNU Internationalization utilities for the base system
  ii  gir1.2-glib-2.0:amd64              1.46.0-3ubuntu1                     amd64        Introspection data for GLib, GObject, Gio and GModule
  ii  git                                1:2.7.4-0ubuntu1                    amd64        fast, scalable, distributed revision control system
  ii  git-man                            1:2.7.4-0ubuntu1                    all          fast, scalable, distributed revision control system (manual pages)
  ii  gnupg                              1.4.20-1ubuntu3.1                   amd64        GNU privacy guard - a free PGP replacement
  ii  gpgv                               1.4.20-1ubuntu3.1                   amd64        GNU privacy guard - signature verification tool
  ii  grep                               2.25-1~16.04.1                      amd64        GNU grep, egrep and fgrep
  ii  grub-common                        2.02~beta2-36ubuntu3.1              amd64        GRand Unified Bootloader (common files)
  ii  grub-gfxpayload-lists              0.7                                 amd64        GRUB gfxpayload blacklist
  ii  grub-pc                            2.02~beta2-36ubuntu3.1              amd64        GRand Unified Bootloader, version 2 (PC/BIOS version)
  ii  grub-pc-bin                        2.02~beta2-36ubuntu3.1              amd64        GRand Unified Bootloader, version 2 (PC/BIOS binaries)
  ii  grub2-common                       2.02~beta2-36ubuntu3.1              amd64        GRand Unified Bootloader (common files for version 2)
  ii  gzip                               1.6-4ubuntu1                        amd64        GNU compression utilities
  ii  hostname                           3.16ubuntu2                         amd64        utility to set/show the host name or domain name
  ii  htop                               2.0.1-1ubuntu1                      amd64        interactive processes viewer
  ii  ifupdown                           0.8.10ubuntu1                       amd64        high level tools to configure network interfaces
  ii  init                               1.29ubuntu2                         amd64        System-V-like init utilities - metapackage
  ii  init-system-helpers                1.29ubuntu2                         all          helper tools for all init systems
  ii  initramfs-tools                    0.122ubuntu8.1                      all          generic modular initramfs generator (automation)
  ii  initramfs-tools-bin                0.122ubuntu8.1                      amd64        binaries used by initramfs-tools
  ii  initramfs-tools-core               0.122ubuntu8.1                      all          generic modular initramfs generator (core tools)
  ii  initscripts                        2.88dsf-59.3ubuntu2                 amd64        scripts for initializing and shutting down the system
  ii  insserv                            1.14.0-5ubuntu3                     amd64        boot sequence organizer using LSB init.d script dependency information
  ii  installation-report                2.60ubuntu1                         all          system installation report
  ii  iproute2                           4.3.0-1ubuntu3                      amd64        networking and traffic control tools
  ii  iputils-ping                       3:20121221-5ubuntu2                 amd64        Tools to test the reachability of network hosts
  ii  ipxe-qemu                          1.0.0+git-20150424.a25a16d-1ubuntu1 all          PXE boot firmware - ROM images for qemu
  ii  isc-dhcp-client                    4.3.3-5ubuntu12.1                   amd64        DHCP client for automatically obtaining an IP address
  ii  isc-dhcp-common                    4.3.3-5ubuntu12.1                   amd64        common files used by all of the isc-dhcp packages
  ii  iso-codes                          3.65-1                              all          ISO language, territory, currency, script codes and their translations
  ii  iw                                 3.17-1                              amd64        tool for configuring Linux wireless devices
  ii  kbd                                1.15.5-1ubuntu4                     amd64        Linux console font and keytable utilities
  ii  keyboard-configuration             1.108ubuntu15.2                     all          system-wide keyboard preferences
  ii  klibc-utils                        2.0.4-8ubuntu1.16.04.1              amd64        small utilities built with klibc for early boot
  ii  kmod                               22-1ubuntu4                         amd64        tools for managing Linux kernel modules
  ii  krb5-locales                       1.13.2+dfsg-5                       all          Internationalization support for MIT Kerberos
  ii  language-selector-common           0.165.3                             all          Language selector for Ubuntu
  ii  laptop-detect                      0.13.7ubuntu2                       amd64        attempt to detect a laptop
  ii  less                               481-2.1                             amd64        pager program similar to more
  ii  libaccountsservice0:amd64          0.6.40-2ubuntu11.1                  amd64        query and manipulate user account information - shared libraries
  ii  libacl1:amd64                      2.2.52-3                            amd64        Access control list shared library
  ii  libaio1:amd64                      0.3.110-2                           amd64        Linux kernel AIO access library - shared library
  ii  libalgorithm-diff-perl             1.19.03-1                           all          module to find differences between files
  ii  libalgorithm-diff-xs-perl          0.04-4build1                        amd64        module to find differences between files (XS accelerated)
  ii  libalgorithm-merge-perl            0.08-3                              all          Perl module for three-way merge of textual data
  ii  libapparmor1:amd64                 2.10.95-0ubuntu2                    amd64        changehat AppArmor library
  ii  libapt-inst2.0:amd64               1.2.12~ubuntu16.04.1                amd64        deb package format runtime library
  ii  libapt-pkg5.0:amd64                1.2.12~ubuntu16.04.1                amd64        package management runtime library
  ii  libasan2:amd64                     5.4.0-6ubuntu1~16.04.2              amd64        AddressSanitizer -- a fast memory error detector
  ii  libasn1-8-heimdal:amd64            1.7~git20150920+dfsg-4ubuntu1       amd64        Heimdal Kerberos - ASN.1 library
  ii  libasound2:amd64                   1.1.0-0ubuntu1                      amd64        shared library for ALSA applications
  ii  libasound2-data                    1.1.0-0ubuntu1                      all          Configuration files and profiles for ALSA drivers
  ii  libasprintf0v5:amd64               0.19.7-2ubuntu3                     amd64        GNU library to use fprintf and friends in C++
  ii  libasyncns0:amd64                  0.8-5build1                         amd64        Asynchronous name service query library
  ii  libatm1:amd64                      1:2.5.1-1.5                         amd64        shared library for ATM (Asynchronous Transfer Mode)
  ii  libatomic1:amd64                   5.4.0-6ubuntu1~16.04.2              amd64        support library providing __atomic built-in functions
  ii  libattr1:amd64                     1:2.4.47-2                          amd64        Extended attribute shared library
  ii  libaudit-common                    1:2.4.5-1ubuntu2                    all          Dynamic library for security auditing - common files
  ii  libaudit1:amd64                    1:2.4.5-1ubuntu2                    amd64        Dynamic library for security auditing
  ii  libblkid1:amd64                    2.27.1-6ubuntu3.1                   amd64        block device ID library
  ii  libbluetooth3:amd64                5.37-0ubuntu5                       amd64        Library to use the BlueZ Linux Bluetooth stack
  ii  libboost-iostreams1.58.0:amd64     1.58.0+dfsg-5ubuntu3.1              amd64        Boost.Iostreams Library
  ii  libboost-random1.58.0:amd64        1.58.0+dfsg-5ubuntu3.1              amd64        Boost Random Number Library
  ii  libboost-system1.58.0:amd64        1.58.0+dfsg-5ubuntu3.1              amd64        Operating system (e.g. diagnostics support) library
  ii  libboost-thread1.58.0:amd64        1.58.0+dfsg-5ubuntu3.1              amd64        portable C++ multi-threading
  ii  libbrlapi0.6:amd64                 5.3.1-2ubuntu2.1                    amd64        braille display access via BRLTTY - shared library
  ii  libbsd0:amd64                      0.8.2-1                             amd64        utility functions from BSD systems - shared library
  ii  libbz2-1.0:amd64                   1.0.6-8                             amd64        high-quality block-sorting file compressor library - runtime
  ii  libc-bin                           2.23-0ubuntu3                       amd64        GNU C Library: Binaries
  ii  libc-dev-bin                       2.23-0ubuntu3                       amd64        GNU C Library: Development binaries
  ii  libc6:amd64                        2.23-0ubuntu3                       amd64        GNU C Library: Shared libraries
  ii  libc6-dev:amd64                    2.23-0ubuntu3                       amd64        GNU C Library: Development Libraries and Header Files
  ii  libcaca0:amd64                     0.99.beta19-2build2~gcc5.2          amd64        colour ASCII art library
  ii  libcacard0:amd64                   1:2.5.0-2                           amd64        Virtual Common Access Card (CAC) Emulator (runtime library)
  ii  libcap-ng0:amd64                   0.7.7-1                             amd64        An alternate POSIX capabilities library
  ii  libcap2:amd64                      1:2.24-12                           amd64        POSIX 1003.1e capabilities (library)
  ii  libcap2-bin                        1:2.24-12                           amd64        POSIX 1003.1e capabilities (utilities)
  ii  libcc1-0:amd64                     5.4.0-6ubuntu1~16.04.2              amd64        GCC cc1 plugin for GDB
  ii  libcgroup1:amd64                   0.41-7ubuntu1                       amd64        control and monitor control groups (library)
  ii  libcilkrts5:amd64                  5.4.0-6ubuntu1~16.04.2              amd64        Intel Cilk Plus language extensions (runtime)
  ii  libcomerr2:amd64                   1.42.13-1ubuntu1                    amd64        common error description library
  ii  libcpufreq0                        008-1                               amd64        shared library to deal with the cpufreq Linux kernel feature
  ii  libcryptsetup4:amd64               2:1.6.6-5ubuntu2                    amd64        disk encryption support - shared library
  ii  libcurl3-gnutls:amd64              7.47.0-1ubuntu2.1                   amd64        easy-to-use client-side URL transfer library (GnuTLS flavour)
  ii  libdb5.3:amd64                     5.3.28-11                           amd64        Berkeley v5.3 Database Libraries [runtime]
  ii  libdbus-1-3:amd64                  1.10.6-1ubuntu3                     amd64        simple interprocess messaging system (library)
  ii  libdbus-glib-1-2:amd64             0.106-1                             amd64        simple interprocess messaging system (GLib-based shared library)
  ii  libdebconfclient0:amd64            0.198ubuntu1                        amd64        Debian Configuration Management System (C-implementation library)
  ii  libdevmapper1.02.1:amd64           2:1.02.110-1ubuntu10                amd64        Linux Kernel Device Mapper userspace library
  ii  libdns-export162                   1:9.10.3.dfsg.P4-8ubuntu1.1         amd64        Exported DNS Shared Library
  ii  libdpkg-perl                       1.18.4ubuntu1.1                     all          Dpkg perl modules
  ii  libdrm-amdgpu1:amd64               2.4.67-1ubuntu0.16.04.2             amd64        Userspace interface to amdgpu-specific kernel DRM services -- runtime
  ii  libdrm-intel1:amd64                2.4.67-1ubuntu0.16.04.2             amd64        Userspace interface to intel-specific kernel DRM services -- runtime
  ii  libdrm-nouveau2:amd64              2.4.67-1ubuntu0.16.04.2             amd64        Userspace interface to nouveau-specific kernel DRM services -- runtime
  ii  libdrm-radeon1:amd64               2.4.67-1ubuntu0.16.04.2             amd64        Userspace interface to radeon-specific kernel DRM services -- runtime
  ii  libdrm2:amd64                      2.4.67-1ubuntu0.16.04.2             amd64        Userspace interface to kernel DRM services -- runtime
  ii  libedit2:amd64                     3.1-20150325-1ubuntu2               amd64        BSD editline and history libraries
  ii  libelf1:amd64                      0.165-3ubuntu1                      amd64        library to read and write ELF files
  ii  liberror-perl                      0.17-1.2                            all          Perl module for error/exception handling in an OO-ish way
  ii  libestr0                           0.1.10-1                            amd64        Helper functions for handling strings (lib)
  ii  libexpat1:amd64                    2.1.0-7ubuntu0.16.04.2              amd64        XML parsing C library - runtime library
  ii  libexpat1-dev:amd64                2.1.0-7ubuntu0.16.04.2              amd64        XML parsing C library - development kit
  ii  libfakeroot:amd64                  1.20.2-1ubuntu1                     amd64        tool for simulating superuser privileges - shared libraries
  ii  libfdisk1:amd64                    2.27.1-6ubuntu3.1                   amd64        fdisk partitioning library
  ii  libfdt1:amd64                      1.4.0+dfsg-2                        amd64        Flat Device Trees manipulation library
  ii  libffi6:amd64                      3.2.1-4                             amd64        Foreign Function Interface library runtime
  ii  libfile-fcntllock-perl             0.22-3                              amd64        Perl module for file locking with fcntl(2)
  ii  libflac8:amd64                     1.3.1-4                             amd64        Free Lossless Audio Codec - runtime C library
  ii  libfontconfig1:amd64               2.11.94-0ubuntu1.1                  amd64        generic font configuration library - runtime
  ii  libfontenc1:amd64                  1:1.1.3-1                           amd64        X11 font encoding library
  ii  libfreetype6:amd64                 2.6.1-0.1ubuntu2                    amd64        FreeType 2 font engine, shared library files
  ii  libfribidi0:amd64                  0.19.7-1                            amd64        Free Implementation of the Unicode BiDi algorithm
  ii  libfuse2:amd64                     2.9.4-1ubuntu3                      amd64        Filesystem in Userspace (library)
  ii  libgcc-5-dev:amd64                 5.4.0-6ubuntu1~16.04.2              amd64        GCC support library (development files)
  ii  libgcc1:amd64                      1:6.0.1-0ubuntu1                    amd64        GCC support library
  ii  libgcrypt20:amd64                  1.6.5-2ubuntu0.2                    amd64        LGPL Crypto library - runtime library
  ii  libgdbm3:amd64                     1.8.3-13.1                          amd64        GNU dbm database routines (runtime version)
  ii  libgirepository-1.0-1:amd64        1.46.0-3ubuntu1                     amd64        Library for handling GObject introspection data (runtime library)
  ii  libgl1-mesa-dri:amd64              11.2.0-1ubuntu2.2                   amd64        free implementation of the OpenGL API -- DRI modules
  ii  libgl1-mesa-glx:amd64              11.2.0-1ubuntu2.2                   amd64        free implementation of the OpenGL API -- GLX runtime
  ii  libglapi-mesa:amd64                11.2.0-1ubuntu2.2                   amd64        free implementation of the GL API -- shared library
  ii  libglib2.0-0:amd64                 2.48.1-1~ubuntu16.04.1              amd64        GLib library of C routines
  ii  libglib2.0-bin                     2.48.1-1~ubuntu16.04.1              amd64        Programs for the GLib library
  ii  libglib2.0-data                    2.48.1-1~ubuntu16.04.1              all          Common files for GLib library
  ii  libglib2.0-dev                     2.48.1-1~ubuntu16.04.1              amd64        Development files for the GLib library
  ii  libgmp10:amd64                     2:6.1.0+dfsg-2                      amd64        Multiprecision arithmetic library
  ii  libgnutls-openssl27:amd64          3.4.10-4ubuntu1.1                   amd64        GNU TLS library - OpenSSL wrapper
  ii  libgnutls30:amd64                  3.4.10-4ubuntu1.1                   amd64        GNU TLS library - main runtime library
  ii  libgomp1:amd64                     5.4.0-6ubuntu1~16.04.2              amd64        GCC OpenMP (GOMP) support library
  ii  libgpg-error0:amd64                1.21-2ubuntu1                       amd64        library for common error values and messages in GnuPG components
  ii  libgssapi-krb5-2:amd64             1.13.2+dfsg-5                       amd64        MIT Kerberos runtime libraries - krb5 GSS-API Mechanism
  ii  libgssapi3-heimdal:amd64           1.7~git20150920+dfsg-4ubuntu1       amd64        Heimdal Kerberos - GSSAPI support library
  ii  libhcrypto4-heimdal:amd64          1.7~git20150920+dfsg-4ubuntu1       amd64        Heimdal Kerberos - crypto library
  ii  libheimbase1-heimdal:amd64         1.7~git20150920+dfsg-4ubuntu1       amd64        Heimdal Kerberos - Base library
  ii  libheimntlm0-heimdal:amd64         1.7~git20150920+dfsg-4ubuntu1       amd64        Heimdal Kerberos - NTLM support library
  ii  libhogweed4:amd64                  3.2-1                               amd64        low level cryptographic library (public-key cryptos)
  ii  libhx509-5-heimdal:amd64           1.7~git20150920+dfsg-4ubuntu1       amd64        Heimdal Kerberos - X509 support library
  ii  libice6:amd64                      2:1.0.9-1                           amd64        X11 Inter-Client Exchange library
  ii  libicu55:amd64                     55.1-7                              amd64        International Components for Unicode
  ii  libidn11:amd64                     1.32-3ubuntu1.1                     amd64        GNU Libidn library, implementation of IETF IDN specifications
  ii  libisc-export160                   1:9.10.3.dfsg.P4-8ubuntu1.1         amd64        Exported ISC Shared Library
  ii  libiscsi2:amd64                    1.12.0-2                            amd64        iSCSI client shared library
  ii  libisl15:amd64                     0.16.1-1                            amd64        manipulating sets and relations of integer points bounded by linear constraints
  ii  libitm1:amd64                      5.4.0-6ubuntu1~16.04.2              amd64        GNU Transactional Memory Library
  ii  libjpeg-turbo8:amd64               1.4.2-0ubuntu3                      amd64        IJG JPEG compliant runtime library.
  ii  libjpeg8:amd64                     8c-2ubuntu8                         amd64        Independent JPEG Group's JPEG runtime library (dependency package)
  ii  libjson-c2:amd64                   0.11-4ubuntu2                       amd64        JSON manipulation library - shared library
  ii  libk5crypto3:amd64                 1.13.2+dfsg-5                       amd64        MIT Kerberos runtime libraries - Crypto Library
  ii  libkeyutils1:amd64                 1.5.9-8ubuntu1                      amd64        Linux Key Management Utilities (library)
  ii  libklibc                           2.0.4-8ubuntu1.16.04.1              amd64        minimal libc subset for use with initramfs
  ii  libkmod2:amd64                     22-1ubuntu4                         amd64        libkmod shared library
  ii  libkrb5-26-heimdal:amd64           1.7~git20150920+dfsg-4ubuntu1       amd64        Heimdal Kerberos - libraries
  ii  libkrb5-3:amd64                    1.13.2+dfsg-5                       amd64        MIT Kerberos runtime libraries
  ii  libkrb5support0:amd64              1.13.2+dfsg-5                       amd64        MIT Kerberos runtime libraries - Support library
  ii  libldap-2.4-2:amd64                2.4.42+dfsg-2ubuntu3.1              amd64        OpenLDAP libraries
  ii  libllvm3.8:amd64                   1:3.8-2ubuntu4                      amd64        Modular compiler and toolchain technologies, runtime library
  ii  liblocale-gettext-perl             1.07-1build1                        amd64        module using libc functions for internationalization in Perl
  ii  liblsan0:amd64                     5.4.0-6ubuntu1~16.04.2              amd64        LeakSanitizer -- a memory leak detector (runtime)
  ii  libltdl-dev:amd64                  2.4.6-0.1                           amd64        System independent dlopen wrapper for GNU libtool
  ii  libltdl7:amd64                     2.4.6-0.1                           amd64        System independent dlopen wrapper for GNU libtool
  ii  liblz4-1:amd64                     0.0~r131-2ubuntu2                   amd64        Fast LZ compression algorithm library - runtime
  ii  liblzma5:amd64                     5.1.1alpha+20120614-2ubuntu2        amd64        XZ-format compression library
  ii  libmagic1:amd64                    1:5.25-2ubuntu1                     amd64        File type determination library using "magic" numbers
  ii  libmnl0:amd64                      1.0.3-5                             amd64        minimalistic Netlink communication library
  ii  libmount1:amd64                    2.27.1-6ubuntu3.1                   amd64        device mounting library
  ii  libmpc3:amd64                      1.0.3-1                             amd64        multiple precision complex floating-point library
  ii  libmpdec2:amd64                    2.4.2-1                             amd64        library for decimal floating point arithmetic (runtime library)
  ii  libmpfr4:amd64                     3.1.4-1                             amd64        multiple precision floating-point computation
  ii  libmpx0:amd64                      5.4.0-6ubuntu1~16.04.2              amd64        Intel memory protection extensions (runtime)
  ii  libncurses5:amd64                  6.0+20160213-1ubuntu1               amd64        shared libraries for terminal handling
  ii  libncursesw5:amd64                 6.0+20160213-1ubuntu1               amd64        shared libraries for terminal handling (wide character support)
  ii  libnettle6:amd64                   3.2-1                               amd64        low level cryptographic library (symmetric and one-way cryptos)
  ii  libnewt0.52:amd64                  0.52.18-1ubuntu2                    amd64        Not Erik's Windowing Toolkit - text mode windowing with slang
  ii  libnih-dbus1:amd64                 1.0.3-4.3ubuntu1                    amd64        NIH D-Bus Bindings Library
  ii  libnih1:amd64                      1.0.3-4.3ubuntu1                    amd64        NIH Utility Library
  ii  libnl-3-200:amd64                  3.2.27-1                            amd64        library for dealing with netlink sockets
  ii  libnl-genl-3-200:amd64             3.2.27-1                            amd64        library for dealing with netlink sockets - generic netlink
  ii  libnspr4:amd64                     2:4.12-0ubuntu0.16.04.1             amd64        NetScape Portable Runtime Library
  ii  libnss3:amd64                      2:3.23-0ubuntu0.16.04.1             amd64        Network Security Service libraries
  ii  libnss3-nssdb                      2:3.23-0ubuntu0.16.04.1             all          Network Security Security libraries - shared databases
  ii  libnuma1:amd64                     2.0.11-1ubuntu1                     amd64        Libraries for controlling NUMA policy
  ii  libogg0:amd64                      1.3.2-1                             amd64        Ogg bitstream library
  ii  libopus0:amd64                     1.1.2-1ubuntu1                      amd64        Opus codec runtime library
  ii  libp11-kit0:amd64                  0.23.2-3                            amd64        Library for loading and coordinating access to PKCS#11 modules - runtime
  ii  libpam-modules:amd64               1.1.8-3.2ubuntu2                    amd64        Pluggable Authentication Modules for PAM
  ii  libpam-modules-bin                 1.1.8-3.2ubuntu2                    amd64        Pluggable Authentication Modules for PAM - helper binaries
  ii  libpam-runtime                     1.1.8-3.2ubuntu2                    all          Runtime support for the PAM library
  ii  libpam0g:amd64                     1.1.8-3.2ubuntu2                    amd64        Pluggable Authentication Modules library
  ii  libpci3:amd64                      1:3.3.1-1.1ubuntu1                  amd64        Linux PCI Utilities (shared library)
  ii  libpciaccess0:amd64                0.13.4-1                            amd64        Generic PCI access library for X
  ii  libpcre16-3:amd64                  2:8.38-3.1                          amd64        Perl 5 Compatible Regular Expression Library - 16 bit runtime files
  ii  libpcre3:amd64                     2:8.38-3.1                          amd64        Perl 5 Compatible Regular Expression Library - runtime files
  ii  libpcre3-dev:amd64                 2:8.38-3.1                          amd64        Perl 5 Compatible Regular Expression Library - development files
  ii  libpcre32-3:amd64                  2:8.38-3.1                          amd64        Perl 5 Compatible Regular Expression Library - 32 bit runtime files
  ii  libpcrecpp0v5:amd64                2:8.38-3.1                          amd64        Perl 5 Compatible Regular Expression Library - C++ runtime files
  ii  libperl5.22:amd64                  5.22.1-9                            amd64        shared Perl library
  ii  libpixman-1-0:amd64                0.33.6-1                            amd64        pixel-manipulation library for X and cairo
  ii  libplymouth4:amd64                 0.9.2-3ubuntu13.1                   amd64        graphical boot animation and logger - shared libraries
  ii  libpng12-0:amd64                   1.2.54-1ubuntu1                     amd64        PNG library - runtime
  ii  libpolkit-gobject-1-0:amd64        0.105-14.1                          amd64        PolicyKit Authorization API
  ii  libpopt0:amd64                     1.16-10                             amd64        lib for parsing cmdline parameters
  ii  libprocps4:amd64                   2:3.3.10-4ubuntu2                   amd64        library for accessing process information from /proc
  ii  libpulse0:amd64                    1:8.0-0ubuntu3                      amd64        PulseAudio client libraries
  ii  libpython-all-dev:amd64            2.7.11-1                            amd64        package depending on all supported Python development packages
  ii  libpython-dev:amd64                2.7.11-1                            amd64        header files and a static library for Python (default)
  ii  libpython-stdlib:amd64             2.7.11-1                            amd64        interactive high-level object-oriented language (default python version)
  ii  libpython2.7:amd64                 2.7.12-1~16.04                      amd64        Shared Python runtime library (version 2.7)
  ii  libpython2.7-dev:amd64             2.7.12-1~16.04                      amd64        Header files and a static library for Python (v2.7)
  ii  libpython2.7-minimal:amd64         2.7.12-1~16.04                      amd64        Minimal subset of the Python language (version 2.7)
  ii  libpython2.7-stdlib:amd64          2.7.12-1~16.04                      amd64        Interactive high-level object-oriented language (standard library, version 2.7)
  ii  libpython3-stdlib:amd64            3.5.1-3                             amd64        interactive high-level object-oriented language (default python3 version)
  ii  libpython3.5-minimal:amd64         3.5.2-2~16.01                       amd64        Minimal subset of the Python language (version 3.5)
  ii  libpython3.5-stdlib:amd64          3.5.2-2~16.01                       amd64        Interactive high-level object-oriented language (standard library, version 3.5)
  ii  libquadmath0:amd64                 5.4.0-6ubuntu1~16.04.2              amd64        GCC Quad-Precision Math Library
  ii  librados2                          10.2.2-0ubuntu0.16.04.2             amd64        RADOS distributed object store client library
  ii  librbd1                            10.2.2-0ubuntu0.16.04.2             amd64        RADOS block device client library
  ii  libreadline6:amd64                 6.3-8ubuntu2                        amd64        GNU readline and history libraries, run-time libraries
  ii  libroken18-heimdal:amd64           1.7~git20150920+dfsg-4ubuntu1       amd64        Heimdal Kerberos - roken support library
  ii  librtmp1:amd64                     2.4+20151223.gitfa8646d-1build1     amd64        toolkit for RTMP streams (shared library)
  ii  libsasl2-2:amd64                   2.1.26.dfsg1-14build1               amd64        Cyrus SASL - authentication abstraction library
  ii  libsasl2-modules:amd64             2.1.26.dfsg1-14build1               amd64        Cyrus SASL - pluggable authentication modules
  ii  libsasl2-modules-db:amd64          2.1.26.dfsg1-14build1               amd64        Cyrus SASL - pluggable authentication modules (DB)
  ii  libsdl1.2debian:amd64              1.2.15+dfsg1-3                      amd64        Simple DirectMedia Layer
  ii  libseccomp2:amd64                  2.2.3-3ubuntu3                      amd64        high level interface to Linux seccomp filter
  ii  libselinux1:amd64                  2.4-3build2                         amd64        SELinux runtime shared libraries
  ii  libsemanage-common                 2.3-1build3                         all          Common files for SELinux policy management libraries
  ii  libsemanage1:amd64                 2.3-1build3                         amd64        SELinux policy management library
  ii  libsepol1:amd64                    2.4-2                               amd64        SELinux library for manipulating binary security policies
  ii  libsigsegv2:amd64                  2.10-4                              amd64        Library for handling page faults in a portable way
  ii  libslang2:amd64                    2.3.0-2ubuntu1                      amd64        S-Lang programming library - runtime version
  ii  libsm6:amd64                       2:1.2.2-1                           amd64        X11 Session Management library
  ii  libsmartcols1:amd64                2.27.1-6ubuntu3.1                   amd64        smart column output alignment library
  ii  libsndfile1:amd64                  1.0.25-10                           amd64        Library for reading/writing audio files
  ii  libspice-server1:amd64             0.12.6-4ubuntu0.1                   amd64        Implements the server side of the SPICE protocol
  ii  libsqlite3-0:amd64                 3.11.0-1ubuntu1                     amd64        SQLite 3 shared library
  ii  libss2:amd64                       1.42.13-1ubuntu1                    amd64        command-line interface parsing library
  ii  libssl1.0.0:amd64                  1.0.2g-1ubuntu4.5                   amd64        Secure Sockets Layer toolkit - shared libraries
  ii  libstdc++-5-dev:amd64              5.4.0-6ubuntu1~16.04.2              amd64        GNU Standard C++ Library v3 (development files)
  ii  libstdc++6:amd64                   5.4.0-6ubuntu1~16.04.2              amd64        GNU Standard C++ Library v3
  ii  libsystemd0:amd64                  229-4ubuntu10                       amd64        systemd utility library
  ii  libtasn1-6:amd64                   4.7-3ubuntu0.16.04.1                amd64        Manage ASN.1 structures (runtime)
  ii  libtcl8.6:amd64                    8.6.5+dfsg-2                        amd64        Tcl (the Tool Command Language) v8.6 - run-time library files
  ii  libtext-charwidth-perl             0.04-7build5                        amd64        get display widths of characters on the terminal
  ii  libtext-iconv-perl                 1.7-5build4                         amd64        converts between character sets in Perl
  ii  libtext-wrapi18n-perl              0.06-7.1                            all          internationalized substitute of Text::Wrap
  ii  libtinfo5:amd64                    6.0+20160213-1ubuntu1               amd64        shared low-level terminfo library for terminal handling
  ii  libtk8.6:amd64                     8.6.5-1                             amd64        Tk toolkit for Tcl and X11 v8.6 - run-time files
  ii  libtool                            2.4.6-0.1                           all          Generic library support script
  ii  libtsan0:amd64                     5.4.0-6ubuntu1~16.04.2              amd64        ThreadSanitizer -- a Valgrind-based detector of data races (runtime)
  ii  libtxc-dxtn-s2tc0:amd64            0~git20131104-1.1                   amd64        Texture compression library for Mesa
  ii  libubsan0:amd64                    5.4.0-6ubuntu1~16.04.2              amd64        UBSan -- undefined behaviour sanitizer (runtime)
  ii  libudev1:amd64                     229-4ubuntu10                       amd64        libudev shared library
  ii  libusb-0.1-4:amd64                 2:0.1.12-28                         amd64        userspace USB programming library
  ii  libusb-1.0-0:amd64                 2:1.0.20-1                          amd64        userspace USB programming library
  ii  libusbredirparser1:amd64           0.7.1-1                             amd64        Parser for the usbredir protocol (runtime)
  ii  libustr-1.0-1:amd64                1.0.4-5                             amd64        Micro string library: shared library
  ii  libutempter0:amd64                 1.1.6-3                             amd64        privileged helper for utmp/wtmp updates (runtime)
  ii  libuuid1:amd64                     2.27.1-6ubuntu3.1                   amd64        Universally Unique ID library
  ii  libvorbis0a:amd64                  1.3.5-3                             amd64        decoder library for Vorbis General Audio Compression Codec
  ii  libvorbisenc2:amd64                1.3.5-3                             amd64        encoder library for Vorbis General Audio Compression Codec
  ii  libwind0-heimdal:amd64             1.7~git20150920+dfsg-4ubuntu1       amd64        Heimdal Kerberos - stringprep implementation
  ii  libwrap0:amd64                     7.6.q-25                            amd64        Wietse Venema's TCP wrappers library
  ii  libx11-6:amd64                     2:1.6.3-1ubuntu2                    amd64        X11 client-side library
  ii  libx11-data                        2:1.6.3-1ubuntu2                    all          X11 client-side library
  ii  libx11-xcb1:amd64                  2:1.6.3-1ubuntu2                    amd64        Xlib/XCB interface library
  ii  libxau6:amd64                      1:1.0.8-1                           amd64        X11 authorisation library
  ii  libxaw7:amd64                      2:1.0.13-1                          amd64        X11 Athena Widget library
  ii  libxcb-dri2-0:amd64                1.11.1-1ubuntu1                     amd64        X C Binding, dri2 extension
  ii  libxcb-dri3-0:amd64                1.11.1-1ubuntu1                     amd64        X C Binding, dri3 extension
  ii  libxcb-glx0:amd64                  1.11.1-1ubuntu1                     amd64        X C Binding, glx extension
  ii  libxcb-present0:amd64              1.11.1-1ubuntu1                     amd64        X C Binding, present extension
  ii  libxcb-shape0:amd64                1.11.1-1ubuntu1                     amd64        X C Binding, shape extension
  ii  libxcb-sync1:amd64                 1.11.1-1ubuntu1                     amd64        X C Binding, sync extension
  ii  libxcb1:amd64                      1.11.1-1ubuntu1                     amd64        X C Binding
  ii  libxcomposite1:amd64               1:0.4.4-1                           amd64        X11 Composite extension library
  ii  libxdamage1:amd64                  1:1.1.4-2                           amd64        X11 damaged region extension library
  ii  libxdmcp6:amd64                    1:1.1.2-1.1                         amd64        X11 Display Manager Control Protocol library
  ii  libxen-4.6:amd64                   4.6.0-1ubuntu4.2                    amd64        Public libs for Xen
  ii  libxenstore3.0:amd64               4.6.0-1ubuntu4.2                    amd64        Xenstore communications library for Xen
  ii  libxext6:amd64                     2:1.3.3-1                           amd64        X11 miscellaneous extension library
  ii  libxfixes3:amd64                   1:5.0.1-2                           amd64        X11 miscellaneous 'fixes' extension library
  ii  libxft2:amd64                      2.3.2-1                             amd64        FreeType-based font drawing library for X
  ii  libxi6:amd64                       2:1.7.6-1                           amd64        X11 Input extension library
  ii  libxinerama1:amd64                 2:1.1.3-1                           amd64        X11 Xinerama extension library
  ii  libxml2:amd64                      2.9.3+dfsg1-1ubuntu0.1              amd64        GNOME XML library
  ii  libxmu6:amd64                      2:1.1.2-2                           amd64        X11 miscellaneous utility library
  ii  libxmuu1:amd64                     2:1.1.2-2                           amd64        X11 miscellaneous micro-utility library
  ii  libxpm4:amd64                      1:3.5.11-1                          amd64        X11 pixmap library
  ii  libxrandr2:amd64                   2:1.5.0-1                           amd64        X11 RandR extension library
  ii  libxrender1:amd64                  1:0.9.9-0ubuntu1                    amd64        X Rendering Extension client library
  ii  libxshmfence1:amd64                1.2-1                               amd64        X shared memory fences - shared library
  ii  libxss1:amd64                      1:1.2.2-1                           amd64        X11 Screen Saver extension library
  ii  libxt6:amd64                       1:1.1.5-0ubuntu1                    amd64        X11 toolkit intrinsics library
  ii  libxtables11:amd64                 1.6.0-2ubuntu3                      amd64        netfilter xtables library
  ii  libxtst6:amd64                     2:1.2.2-1                           amd64        X11 Testing -- Record extension library
  ii  libxv1:amd64                       2:1.0.10-1                          amd64        X11 Video extension library
  ii  libxxf86dga1:amd64                 2:1.1.4-1                           amd64        X11 Direct Graphics Access extension library
  ii  libxxf86vm1:amd64                  1:1.1.4-1                           amd64        X11 XFree86 video mode extension library
  ii  libyajl2:amd64                     2.1.0-2                             amd64        Yet Another JSON Library
  ii  linux-base                         4.0ubuntu1                          all          Linux image base package
  ii  linux-firmware                     1.157.2                             all          Firmware for Linux kernel drivers
  ii  linux-generic                      4.4.0.42.44                         amd64        Complete Generic Linux kernel and headers
  ii  linux-headers-4.4.0-42             4.4.0-42.62                         all          Header files related to Linux kernel version 4.4.0
  ii  linux-headers-4.4.0-42-generic     4.4.0-42.62                         amd64        Linux kernel headers for version 4.4.0 on 64 bit x86 SMP
  ii  linux-headers-generic              4.4.0.42.44                         amd64        Generic Linux kernel headers
  ii  linux-image-4.4.0-42-generic       4.4.0-42.62                         amd64        Linux kernel image for version 4.4.0 on 64 bit x86 SMP
  ii  linux-image-extra-4.4.0-42-generic 4.4.0-42.62                         amd64        Linux kernel extra modules for version 4.4.0 on 64 bit x86 SMP
  ii  linux-image-generic                4.4.0.42.44                         amd64        Generic Linux kernel image
  ii  linux-libc-dev:amd64               4.4.0-43.63                         amd64        Linux Kernel Headers for development
  ii  locales                            2.23-0ubuntu3                       all          GNU C Library: National Language (locale) data [support]
  ii  login                              1:4.2-3.1ubuntu5                    amd64        system login tools
  ii  logrotate                          3.8.7-2ubuntu2                      amd64        Log rotation utility
  ii  lsb-base                           9.20160110ubuntu0.2                 all          Linux Standard Base init script functionality
  ii  lsb-release                        9.20160110ubuntu0.2                 all          Linux Standard Base version reporting utility
  ii  lshw                               02.17-1.1ubuntu3.2                  amd64        information about hardware configuration
  ii  m4                                 1.4.17-5                            amd64        macro processing language
  ii  make                               4.1-6                               amd64        utility for directing compilation
  ii  makedev                            2.3.1-93ubuntu1                     all          creates device files in /dev
  ii  manpages                           4.04-2                              all          Manual pages about using a GNU/Linux system
  ii  manpages-dev                       4.04-2                              all          Manual pages about using GNU/Linux for development
  ii  mawk                               1.3.3-17ubuntu2                     amd64        a pattern scanning and text processing language
  ii  mime-support                       3.59ubuntu1                         all          MIME files 'mime.types' & 'mailcap', and support programs
  ii  mount                              2.27.1-6ubuntu3.1                   amd64        tools for mounting and manipulating filesystems
  ii  mountall                           2.54ubuntu1                         amd64        filesystem mounting tool
  ii  msr-tools                          1.3-2                               amd64        Utilities for modifying MSRs from userspace
  ii  multiarch-support                  2.23-0ubuntu3                       amd64        Transitional package to ensure multiarch compatibility
  ii  ncurses-base                       6.0+20160213-1ubuntu1               all          basic terminal type definitions
  ii  ncurses-bin                        6.0+20160213-1ubuntu1               amd64        terminal-related programs and man pages
  ii  ncurses-term                       6.0+20160213-1ubuntu1               all          additional terminal type definitions
  ii  net-tools                          1.60-26ubuntu1                      amd64        NET-3 networking toolkit
  ii  netbase                            5.3                                 all          Basic TCP/IP networking system
  ii  netcat-openbsd                     1.105-7ubuntu1                      amd64        TCP/IP swiss army knife
  ii  openssh-client                     1:7.2p2-4ubuntu2.1                  amd64        secure shell (SSH) client, for secure access to remote machines
  ii  openssh-server                     1:7.2p2-4ubuntu2.1                  amd64        secure shell (SSH) server, for secure access from remote machines
  ii  openssh-sftp-server                1:7.2p2-4ubuntu2.1                  amd64        secure shell (SSH) sftp server module, for SFTP access from remote machines
  ii  openssl                            1.0.2g-1ubuntu4.5                   amd64        Secure Sockets Layer toolkit - cryptographic utility
  ii  os-prober                          1.70ubuntu3                         amd64        utility to detect other OSes on a set of drives
  ii  passwd                             1:4.2-3.1ubuntu5                    amd64        change and administer password and group data
  ii  patch                              2.7.5-1                             amd64        Apply a diff file to an original
  ii  pciutils                           1:3.3.1-1.1ubuntu1                  amd64        Linux PCI Utilities
  ii  perl                               5.22.1-9                            amd64        Larry Wall's Practical Extraction and Report Language
  ii  perl-base                          5.22.1-9                            amd64        minimal Perl system
  ii  perl-modules-5.22                  5.22.1-9                            all          Core Perl modules
  ii  pkg-config                         0.29.1-0ubuntu1                     amd64        manage compile and link flags for libraries
  ii  plymouth                           0.9.2-3ubuntu13.1                   amd64        boot animation, logger and I/O multiplexer
  ii  plymouth-theme-ubuntu-text         0.9.2-3ubuntu13.1                   amd64        boot animation, logger and I/O multiplexer - ubuntu text theme
  ii  procps                             2:3.3.10-4ubuntu2                   amd64        /proc file system utilities
  ii  python                             2.7.11-1                            amd64        interactive high-level object-oriented language (default version)
  ii  python-all                         2.7.11-1                            amd64        package depending on all supported Python runtime versions
  ii  python-all-dev                     2.7.11-1                            amd64        package depending on all supported Python development packages
  ii  python-apt                         1.1.0~beta1build1                   amd64        Python interface to libapt-pkg
  ii  python-apt-common                  1.1.0~beta1build1                   all          Python interface to libapt-pkg (locales)
  ii  python-dev                         2.7.11-1                            amd64        header files and a static library for Python (default)
  ii  python-iniparse                    0.4-2.2                             all          access and modify configuration data in INI files (Python 2)
  ii  python-minimal                     2.7.11-1                            amd64        minimal subset of the Python language (default version)
  ii  python-pip                         8.1.1-2ubuntu0.2                    all          alternative Python package installer
  ii  python-pip-whl                     8.1.1-2ubuntu0.2                    all          alternative Python package installer
  ii  python-pkg-resources               20.7.0-1                            all          Package Discovery and Resource Access using pkg_resources
  ii  python-setuptools                  20.7.0-1                            all          Python Distutils Enhancements
  ii  python-six                         1.10.0-3                            all          Python 2 and 3 compatibility library (Python 2 interface)
  ii  python-virtualenv                  15.0.1+ds-3                         all          Python virtual environment creator
  ii  python-wheel                       0.29.0-1                            all          built-package format for Python
  ii  python2.7                          2.7.12-1~16.04                      amd64        Interactive high-level object-oriented language (version 2.7)
  ii  python2.7-dev                      2.7.12-1~16.04                      amd64        Header files and a static library for Python (v2.7)
  ii  python2.7-minimal                  2.7.12-1~16.04                      amd64        Minimal subset of the Python language (version 2.7)
  ii  python3                            3.5.1-3                             amd64        interactive high-level object-oriented language (default python3 version)
  ii  python3-apt                        1.1.0~beta1build1                   amd64        Python 3 interface to libapt-pkg
  ii  python3-chardet                    2.3.0-2                             all          universal character encoding detector for Python3
  ii  python3-dbus                       1.2.0-3                             amd64        simple interprocess messaging system (Python 3 interface)
  ii  python3-gi                         3.20.0-0ubuntu1                     amd64        Python 3 bindings for gobject-introspection libraries
  ii  python3-minimal                    3.5.1-3                             amd64        minimal subset of the Python language (default python3 version)
  ii  python3-pkg-resources              20.7.0-1                            all          Package Discovery and Resource Access using pkg_resources
  ii  python3-requests                   2.9.1-3                             all          elegant and simple HTTP library for Python3, built for human beings
  ii  python3-six                        1.10.0-3                            all          Python 2 and 3 compatibility library (Python 3 interface)
  ii  python3-urllib3                    1.13.1-2ubuntu0.16.04.1             all          HTTP library with thread-safe connection pooling for Python3
  ii  python3-virtualenv                 15.0.1+ds-3                         all          Python virtual environment creator
  ii  python3.5                          3.5.2-2~16.01                       amd64        Interactive high-level object-oriented language (version 3.5)
  ii  python3.5-minimal                  3.5.2-2~16.01                       amd64        Minimal subset of the Python language (version 3.5)
  ii  qemu-block-extra:amd64             1:2.5+dfsg-5ubuntu10.5              amd64        extra block backend modules for qemu-system and qemu-utils
  ii  qemu-system-common                 1:2.5+dfsg-5ubuntu10.5              amd64        QEMU full system emulation binaries (common files)
  ii  qemu-system-x86                    1:2.5+dfsg-5ubuntu10.5              amd64        QEMU full system emulation binaries (x86)
  ii  qemu-utils                         1:2.5+dfsg-5ubuntu10.5              amd64        QEMU utilities
  ii  readline-common                    6.3-8ubuntu2                        all          GNU readline and history libraries, common files
  ii  rename                             0.20-4                              all          Perl extension for renaming multiple files
  ii  resolvconf                         1.78ubuntu2                         all          name server information handler
  ii  rsync                              3.1.1-3ubuntu1                      amd64        fast, versatile, remote (and local) file-copying tool
  ii  rsyslog                            8.16.0-1ubuntu3                     amd64        reliable system and kernel logging daemon
  ii  seabios                            1.8.2-1ubuntu1                      all          Legacy BIOS implementation
  ii  sed                                4.2.2-7                             amd64        The GNU sed stream editor
  ii  sensible-utils                     0.0.9                               all          Utilities for sensible alternative selection
  ii  sgml-base                          1.26+nmu4ubuntu1                    all          SGML infrastructure and SGML catalog file support
  ii  shared-mime-info                   1.5-2ubuntu0.1                      amd64        FreeDesktop.org shared MIME database and spec
  ii  sharutils                          1:4.15.2-1                          amd64        shar, unshar, uuencode, uudecode
  ii  ssh-import-id                      5.5-0ubuntu1                        all          securely retrieve an SSH public key and install it locally
  ii  sudo                               1.8.16-0ubuntu1.1                   amd64        Provide limited super user privileges to specific users
  ii  systemd                            229-4ubuntu10                       amd64        system and service manager
  ii  systemd-sysv                       229-4ubuntu10                       amd64        system and service manager - SysV links
  ii  sysv-rc                            2.88dsf-59.3ubuntu2                 all          System-V-like runlevel change mechanism
  ii  sysvinit-utils                     2.88dsf-59.3ubuntu2                 amd64        System-V-like utilities
  ii  tar                                1.28-2.1                            amd64        GNU version of the tar archiving utility
  ii  tasksel                            3.34ubuntu3                         all          tool for selecting tasks for installation on Debian systems
  ii  tasksel-data                       3.34ubuntu3                         all          official tasks used for installation of Debian systems
  ii  tcl-expect:amd64                   5.45-7                              amd64        Automates interactive applications (Tcl package)
  ii  tcl8.6                             8.6.5+dfsg-2                        amd64        Tcl (the Tool Command Language) v8.6 - shell
  ii  tcpd                               7.6.q-25                            amd64        Wietse Venema's TCP wrapper utilities
  ii  telnet                             0.17-40                             amd64        basic telnet client
  ii  tk8.6                              8.6.5-1                             amd64        Tk toolkit for Tcl and X11 v8.6 - windowing shell
  ii  tzdata                             2016g-0ubuntu0.16.04                all          time zone and daylight-saving time data
  ii  ubuntu-keyring                     2012.05.19                          all          GnuPG keys of the Ubuntu archive
  ii  ubuntu-minimal                     1.361                               amd64        Minimal core of Ubuntu
  ii  ucf                                3.0036                              all          Update Configuration File(s): preserve user changes to config files
  ii  udev                               229-4ubuntu10                       amd64        /dev/ and hotplug management daemon
  ii  ureadahead                         0.100.0-19                          amd64        Read required files in advance
  ii  usbutils                           1:007-4                             amd64        Linux USB utilities
  ii  util-linux                         2.27.1-6ubuntu3.1                   amd64        miscellaneous system utilities
  ii  vim-common                         2:7.4.1689-3ubuntu1.1               amd64        Vi IMproved - Common files
  ii  vim-tiny                           2:7.4.1689-3ubuntu1.1               amd64        Vi IMproved - enhanced vi editor - compact version
  ii  virtualenv                         15.0.1+ds-3                         all          Python virtual environment creator
  ii  vpp                                17.01-release                       amd64        Vector Packet Processing--executables
  ii  vpp-dbg                            17.01-release                       amd64        Vector Packet Processing--debug symbols
  ii  vpp-dev                            17.01-release                       amd64        Vector Packet Processing--development support
  ii  vpp-dpdk-dev                       17.01-release                       amd64        Vector Packet Processing--development support
  ii  vpp-dpdk-dkms                      17.01-release                       amd64        DPDK 2.1 igb_uio_driver
  ii  vpp-lib                            17.01-release                       amd64        Vector Packet Processing--runtime libraries
  ii  vpp-plugins                        17.01-release                       amd64        Vector Packet Processing--runtime plugins
  ii  wamerican                          7.1-1                               all          American English dictionary words for /usr/share/dict
  ii  wget                               1.17.1-1ubuntu1.1                   amd64        retrieves files from the web
  ii  whiptail                           0.52.18-1ubuntu2                    amd64        Displays user-friendly dialog boxes from shell scripts
  ii  wireless-regdb                     2015.07.20-1ubuntu1                 all          wireless regulatory database
  ii  x11-common                         1:7.7+13ubuntu3                     all          X Window System (X.Org) infrastructure
  ii  x11-utils                          7.7+3                               amd64        X11 utilities
  ii  xauth                              1:1.0.9-1ubuntu2                    amd64        X authentication utility
  ii  xbitmaps                           1.1.1-2                             all          Base X bitmaps
  ii  xdg-user-dirs                      0.15-2ubuntu6                       amd64        tool to manage well known user directories
  ii  xkb-data                           2.16-1ubuntu1                       all          X Keyboard Extension (XKB) configuration data
  ii  xml-core                           0.13+nmu2                           all          XML infrastructure and XML catalog file support
  ii  xterm                              322-1ubuntu1                        amd64        X terminal emulator
  ii  xz-utils                           5.1.1alpha+20120614-2ubuntu2        amd64        XZ-format compression utilities
  ii  zlib1g:amd64                       1:1.2.8.dfsg-2ubuntu4               amd64        compression library - runtime
  ii  zlib1g-dev:amd64                   1:1.2.8.dfsg-2ubuntu4               amd64        compression library - development
  ]]></exec_output>
      </function>
      <function id="linux_installed_packages_yum" significance="2" time="2017-01-27 13:58:25.244400 UTC" version="1.0.0">
        <exec_command><![CDATA[yum list installed]]></exec_command>
        <exec_return_code>127</exec_return_code>
        <exec_output><![CDATA[bash: yum: command not found
  ]]></exec_output>
      </function>
      <function id="linux_lsblk" significance="2" time="2017-01-27 13:58:29.023708 UTC" version="1.0.1">
        <exec_command><![CDATA[lsblk -l]]></exec_command>
        <exec_return_code>0</exec_return_code>
        <exec_output><![CDATA[NAME MAJ:MIN RM  SIZE RO TYPE MOUNTPOINT
  sda    8:0    0  1.8T  0 disk 
  sda1   8:1    0  243M  0 part /boot
  sda2   8:2    0  1.8T  0 part /
  sda3   8:3    0    1K  0 part 
  sda5   8:5    0  976M  0 part [SWAP]
  ]]></exec_output>
      </function>
      <function id="linux_lsmod" significance="2" time="2017-01-27 13:58:30.057597 UTC" version="1.0.0">
        <exec_command><![CDATA[lsmod | sort]]></exec_command>
        <exec_return_code>0</exec_return_code>
        <exec_output><![CDATA[8250_fintek            16384  0
  ablk_helper            16384  1 aesni_intel
  acpi_pad               20480  0
  acpi_power_meter       20480  0
  aesni_intel           167936  0
  aes_x86_64             20480  1 aesni_intel
  ahci                   36864  0
  autofs4                40960  2
  binfmt_misc            20480  1
  coretemp               16384  0
  crc32_pclmul           16384  0
  crct10dif_pclmul       16384  0
  cryptd                 20480  2 aesni_intel,ablk_helper
  dca                    16384  2 igb,ixgbe
  edac_core              53248  1 sb_edac
  enclosure              16384  1 ses
  enic                   81920  0
  fjes                   28672  0
  fnic                  106496  0
  gf128mul               16384  1 lrw
  glue_helper            16384  1 aesni_intel
  hid                   118784  2 hid_generic,usbhid
  hid_generic            16384  0
  i2c_algo_bit           16384  1 igb
  i40e                  286720  0
  igb                   196608  0
  igb_uio                16384  2
  input_leds             16384  0
  intel_powerclamp       16384  0
  intel_rapl             20480  0
  ip6_udp_tunnel         16384  1 vxlan
  ipmi_msghandler        49152  2 ipmi_ssif,ipmi_si
  ipmi_si                57344  0
  ipmi_ssif              24576  0
  irqbypass              16384  1 kvm
  ixgbe                 290816  0
  joydev                 20480  0
  kvm                   540672  1 kvm_intel
  kvm_intel             172032  0
  libahci                32768  1 ahci
  libfc                 114688  2 fnic,libfcoe
  libfcoe                65536  1 fnic
  lpc_ich                24576  0
  lrw                    16384  1 aesni_intel
  mac_hid                16384  0
  mdio                   16384  1 ixgbe
  megaraid_sas          135168  3
  mei                    98304  1 mei_me
  mei_me                 36864  0
  Module                  Size  Used by
  pps_core               20480  1 ptp
  ptp                    20480  3 igb,i40e,ixgbe
  sb_edac                32768  0
  scsi_transport_fc      61440  2 fnic,libfc
  ses                    20480  0
  shpchp                 36864  0
  udp_tunnel             16384  1 vxlan
  uio                    20480  5 igb_uio
  usbhid                 49152  0
  vxlan                  49152  2 i40e,ixgbe
  wmi                    20480  0
  x86_pkg_temp_thermal    16384  0
  ]]></exec_output>
      </function>
      <function id="linux_sysctl" significance="2" time="2017-01-27 13:58:37.035813 UTC" version="1.0.0">
        <exec_command><![CDATA[sysctl -a]]></exec_command>
        <exec_return_code>0</exec_return_code>
        <exec_output><![CDATA[abi.vsyscall32 = 1
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
  fs.dentry-state = 72838	55555	45	0	0	0
  fs.dir-notify-enable = 1
  fs.epoll.max_user_watches = 108185804
  fs.file-max = 52706320
  fs.file-nr = 1800	0	52706320
  fs.inode-nr = 50289	367
  fs.inode-state = 50289	367	0	0	0	0	0
  fs.inotify.max_queued_events = 16384
  fs.inotify.max_user_instances = 128
  fs.inotify.max_user_watches = 8192
  fs.lease-break-time = 45
  fs.leases-enable = 1
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
  kernel.hostname = t1-sut1
  kernel.hotplug = 
  kernel.hung_task_check_count = 4194304
  kernel.hung_task_panic = 0
  kernel.hung_task_timeout_secs = 120
  kernel.hung_task_warnings = 2
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
  kernel.ns_last_pid = 10478
  kernel.numa_balancing = 1
  kernel.numa_balancing_scan_delay_ms = 1000
  kernel.numa_balancing_scan_period_max_ms = 60000
  kernel.numa_balancing_scan_period_min_ms = 1000
  kernel.numa_balancing_scan_size_mb = 256
  kernel.osrelease = 4.4.0-42-generic
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
  kernel.pty.nr = 0
  kernel.pty.reserve = 1024
  kernel.random.boot_id = 5d158e9a-7591-4d6b-82b6-066ca2d8b0ad
  kernel.random.entropy_avail = 427
  kernel.random.poolsize = 4096
  kernel.random.read_wakeup_threshold = 64
  kernel.random.urandom_min_reseed_secs = 60
  kernel.random.uuid = f281780a-3f18-4304-81f8-0a377e82ff6b
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
  kernel.sched_domain.cpu0.domain0.max_newidle_lb_cost = 2985
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
  kernel.sched_domain.cpu18.domain0.max_newidle_lb_cost = 14184
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
  kernel.unprivileged_userns_clone = 1
  kernel.version = #62-Ubuntu SMP Fri Oct 7 23:11:45 UTC 2016
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
  net.core.netdev_rss_key = d3:11:03:c5:ec:2b:4c:6c:9a:cf:77:78:bd:f3:48:ce:66:56:8d:83:30:85:80:8b:78:ca:e1:59:7d:89:c3:f5:2e:a9:87:67:9f:90:82:43:23:80:9e:5d:18:91:cd:9f:f7:67:7d:a5
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
  net.ipv4.conf.all.accept_redirects = 1
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
  net.ipv4.conf.all.forwarding = 0
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
  net.ipv4.conf.default.forwarding = 0
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
  net.ipv4.conf.enp23s0f0.accept_local = 0
  net.ipv4.conf.enp23s0f0.accept_redirects = 1
  net.ipv4.conf.enp23s0f0.accept_source_route = 1
  net.ipv4.conf.enp23s0f0.arp_accept = 0
  net.ipv4.conf.enp23s0f0.arp_announce = 0
  net.ipv4.conf.enp23s0f0.arp_filter = 0
  net.ipv4.conf.enp23s0f0.arp_ignore = 0
  net.ipv4.conf.enp23s0f0.arp_notify = 0
  net.ipv4.conf.enp23s0f0.bootp_relay = 0
  net.ipv4.conf.enp23s0f0.disable_policy = 0
  net.ipv4.conf.enp23s0f0.disable_xfrm = 0
  net.ipv4.conf.enp23s0f0.force_igmp_version = 0
  net.ipv4.conf.enp23s0f0.forwarding = 0
  net.ipv4.conf.enp23s0f0.igmpv2_unsolicited_report_interval = 10000
  net.ipv4.conf.enp23s0f0.igmpv3_unsolicited_report_interval = 1000
  net.ipv4.conf.enp23s0f0.ignore_routes_with_linkdown = 0
  net.ipv4.conf.enp23s0f0.log_martians = 0
  net.ipv4.conf.enp23s0f0.mc_forwarding = 0
  net.ipv4.conf.enp23s0f0.medium_id = 0
  net.ipv4.conf.enp23s0f0.promote_secondaries = 0
  net.ipv4.conf.enp23s0f0.proxy_arp = 0
  net.ipv4.conf.enp23s0f0.proxy_arp_pvlan = 0
  net.ipv4.conf.enp23s0f0.route_localnet = 0
  net.ipv4.conf.enp23s0f0.rp_filter = 1
  net.ipv4.conf.enp23s0f0.secure_redirects = 1
  net.ipv4.conf.enp23s0f0.send_redirects = 1
  net.ipv4.conf.enp23s0f0.shared_media = 1
  net.ipv4.conf.enp23s0f0.src_valid_mark = 0
  net.ipv4.conf.enp23s0f0.tag = 0
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
  net.ipv4.conf.lo.forwarding = 0
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
  net.ipv4.ip_forward = 0
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
  net.ipv4.neigh.enp23s0f0.anycast_delay = 100
  net.ipv4.neigh.enp23s0f0.app_solicit = 0
  net.ipv4.neigh.enp23s0f0.base_reachable_time_ms = 30000
  net.ipv4.neigh.enp23s0f0.delay_first_probe_time = 5
  net.ipv4.neigh.enp23s0f0.gc_stale_time = 60
  net.ipv4.neigh.enp23s0f0.locktime = 100
  net.ipv4.neigh.enp23s0f0.mcast_resolicit = 0
  net.ipv4.neigh.enp23s0f0.mcast_solicit = 3
  net.ipv4.neigh.enp23s0f0.proxy_delay = 80
  net.ipv4.neigh.enp23s0f0.proxy_qlen = 64
  net.ipv4.neigh.enp23s0f0.retrans_time_ms = 1000
  net.ipv4.neigh.enp23s0f0.ucast_solicit = 3
  net.ipv4.neigh.enp23s0f0.unres_qlen = 31
  net.ipv4.neigh.enp23s0f0.unres_qlen_bytes = 65536
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
  net.ipv4.tcp_mem = 6188856	8251810	12377712
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
  net.ipv4.udp_mem = 12377715	16503621	24755430
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
  net.ipv6.conf.default.suppress_frag_ndisc = 1
  net.ipv6.conf.default.temp_prefered_lft = 86400
  net.ipv6.conf.default.temp_valid_lft = 604800
  net.ipv6.conf.default.use_oif_addrs_only = 0
  net.ipv6.conf.default.use_tempaddr = 2
  net.ipv6.conf.enp23s0f0.accept_dad = 1
  net.ipv6.conf.enp23s0f0.accept_ra = 1
  net.ipv6.conf.enp23s0f0.accept_ra_defrtr = 1
  net.ipv6.conf.enp23s0f0.accept_ra_from_local = 0
  net.ipv6.conf.enp23s0f0.accept_ra_min_hop_limit = 1
  net.ipv6.conf.enp23s0f0.accept_ra_mtu = 1
  net.ipv6.conf.enp23s0f0.accept_ra_pinfo = 1
  net.ipv6.conf.enp23s0f0.accept_ra_rt_info_max_plen = 0
  net.ipv6.conf.enp23s0f0.accept_ra_rtr_pref = 1
  net.ipv6.conf.enp23s0f0.accept_redirects = 1
  net.ipv6.conf.enp23s0f0.accept_source_route = 0
  net.ipv6.conf.enp23s0f0.autoconf = 1
  net.ipv6.conf.enp23s0f0.dad_transmits = 1
  net.ipv6.conf.enp23s0f0.disable_ipv6 = 0
  net.ipv6.conf.enp23s0f0.force_mld_version = 0
  net.ipv6.conf.enp23s0f0.force_tllao = 0
  net.ipv6.conf.enp23s0f0.forwarding = 0
  net.ipv6.conf.enp23s0f0.hop_limit = 64
  net.ipv6.conf.enp23s0f0.ignore_routes_with_linkdown = 0
  net.ipv6.conf.enp23s0f0.max_addresses = 16
  net.ipv6.conf.enp23s0f0.max_desync_factor = 600
  net.ipv6.conf.enp23s0f0.mc_forwarding = 0
  net.ipv6.conf.enp23s0f0.mldv1_unsolicited_report_interval = 10000
  net.ipv6.conf.enp23s0f0.mldv2_unsolicited_report_interval = 1000
  net.ipv6.conf.enp23s0f0.mtu = 1500
  net.ipv6.conf.enp23s0f0.ndisc_notify = 0
  net.ipv6.conf.enp23s0f0.proxy_ndp = 0
  net.ipv6.conf.enp23s0f0.regen_max_retry = 3
  net.ipv6.conf.enp23s0f0.router_probe_interval = 60
  net.ipv6.conf.enp23s0f0.router_solicitation_delay = 1
  net.ipv6.conf.enp23s0f0.router_solicitation_interval = 4
  net.ipv6.conf.enp23s0f0.router_solicitations = 3
  net.ipv6.conf.enp23s0f0.suppress_frag_ndisc = 1
  net.ipv6.conf.enp23s0f0.temp_prefered_lft = 86400
  net.ipv6.conf.enp23s0f0.temp_valid_lft = 604800
  net.ipv6.conf.enp23s0f0.use_oif_addrs_only = 0
  net.ipv6.conf.enp23s0f0.use_tempaddr = 0
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
  net.ipv6.conf.lo.suppress_frag_ndisc = 1
  net.ipv6.conf.lo.temp_prefered_lft = 86400
  net.ipv6.conf.lo.temp_valid_lft = 604800
  net.ipv6.conf.lo.use_oif_addrs_only = 0
  net.ipv6.conf.lo.use_tempaddr = -1
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
  net.ipv6.neigh.enp23s0f0.anycast_delay = 100
  net.ipv6.neigh.enp23s0f0.app_solicit = 0
  net.ipv6.neigh.enp23s0f0.base_reachable_time_ms = 30000
  net.ipv6.neigh.enp23s0f0.delay_first_probe_time = 5
  net.ipv6.neigh.enp23s0f0.gc_stale_time = 60
  net.ipv6.neigh.enp23s0f0.locktime = 0
  net.ipv6.neigh.enp23s0f0.mcast_resolicit = 0
  net.ipv6.neigh.enp23s0f0.mcast_solicit = 3
  net.ipv6.neigh.enp23s0f0.proxy_delay = 80
  net.ipv6.neigh.enp23s0f0.proxy_qlen = 64
  net.ipv6.neigh.enp23s0f0.retrans_time_ms = 1000
  net.ipv6.neigh.enp23s0f0.ucast_solicit = 3
  net.ipv6.neigh.enp23s0f0.unres_qlen = 31
  net.ipv6.neigh.enp23s0f0.unres_qlen_bytes = 65536
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
  ]]></exec_output>
      </function>
      <function id="linux_sched_features" significance="2" time="2017-01-27 13:58:38.037485 UTC" version="1.0.0">
        <exec_command><![CDATA[cat /sys/kernel/debug/sched_features]]></exec_command>
        <exec_return_code>1</exec_return_code>
        <exec_output><![CDATA[cat: /sys/kernel/debug/sched_features: Permission denied
  ]]></exec_output>
      </function>
      <function id="linux_bridges_status" significance="3" time="2017-01-27 13:58:19.413900 UTC" version="1.0.0">
        <exec_command><![CDATA[brctl show]]></exec_command>
        <exec_return_code>127</exec_return_code>
        <exec_output><![CDATA[bash: brctl: command not found
  ]]></exec_output>
      </function>
      <function id="linux_grub" significance="3" time="2017-01-27 13:58:20.989306 UTC" version="1.0.0">
        <exec_command><![CDATA[cat /etc/default/grub]]></exec_command>
        <exec_return_code>0</exec_return_code>
        <exec_output><![CDATA[# If you change this file, run 'update-grub' afterwards to update
  # /boot/grub/grub.cfg.
  # For full documentation of the options in this file, see:
  #   info -f grub -n 'Simple configuration'

  GRUB_DEFAULT=0
  GRUB_TIMEOUT=10
  GRUB_DISTRIBUTOR=`lsb_release -i -s 2> /dev/null || echo Debian`
  GRUB_CMDLINE_LINUX_DEFAULT="console=tty0 console=ttyS0,115200n8"
  GRUB_CMDLINE_LINUX="isolcpus=1-17,19-35 nohz_full=1-17,19-35 rcu_nocbs=1-17,19-35 intel_pstate=disable"

  # Uncomment to enable BadRAM filtering, modify to suit your needs
  # This works with Linux (no patch required) and with any kernel that obtains
  # the memory map information from GRUB (GNU Mach, kernel of FreeBSD ...)
  #GRUB_BADRAM="0x01234567,0xfefefefe,0x89abcdef,0xefefefef"

  # Uncomment to disable graphical terminal (grub-pc only)
  #GRUB_TERMINAL=console
  GRUB_TERMINAL=serial
  GRUB_SERIAL_COMMAND="serial --speed=115200 --unit=0 --word=8 --parity=no --stop=1"

  # The resolution used on graphical terminal
  # note that you can use only modes which your graphic card supports via VBE
  # you can see them in real GRUB with the command `vbeinfo'
  #GRUB_GFXMODE=640x480

  # Uncomment if you don't want GRUB to pass "root=UUID=xxx" parameter to Linux
  #GRUB_DISABLE_LINUX_UUID=true

  # Uncomment to disable generation of recovery mode menu entries
  #GRUB_DISABLE_RECOVERY="true"

  # Uncomment to get a beep at grub start
  #GRUB_INIT_TUNE="480 440 1"
  ]]></exec_output>
      </function>
      <function id="linux_grub_alt" significance="3" time="2017-01-27 13:58:22.366564 UTC" version="1.0.0">
        <exec_command><![CDATA[sudo cat /boot/grub/grub.conf]]></exec_command>
        <exec_return_code>1</exec_return_code>
        <exec_output><![CDATA[cat: /boot/grub/grub.conf: No such file or directory
  ]]></exec_output>
      </function>
      <function id="linux_links_status" significance="3" time="2017-01-27 13:58:26.878837 UTC" version="1.0.0">
        <exec_command><![CDATA[ip link list]]></exec_command>
        <exec_return_code>0</exec_return_code>
        <exec_output><![CDATA[1: lo: <LOOPBACK,UP,LOWER_UP> mtu 65536 qdisc noqueue state UNKNOWN mode DEFAULT group default qlen 1
      link/loopback 00:00:00:00:00:00 brd 00:00:00:00:00:00
  6: enp23s0f0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 qdisc mq state UP mode DEFAULT group default qlen 1000
      link/ether 00:fe:c8:e5:68:32 brd ff:ff:ff:ff:ff:ff
  ]]></exec_output>
      </function>
      <function id="linux_ps" significance="3" time="2017-01-27 13:58:33.808821 UTC" version="1.0.0">
        <exec_command><![CDATA[ps -ef]]></exec_command>
        <exec_return_code>0</exec_return_code>
        <exec_output><![CDATA[UID        PID  PPID  C STIME TTY          TIME CMD
  root         1     0  0  2016 ?        01:27:39 /sbin/init
  root         2     0  0  2016 ?        00:00:00 [kthreadd]
  root         3     2  0  2016 ?        00:05:30 [ksoftirqd/0]
  root         5     2  0  2016 ?        00:00:00 [kworker/0:0H]
  root         8     2  0  2016 ?        00:08:31 [rcu_sched]
  root         9     2  0  2016 ?        00:00:00 [rcu_bh]
  root        10     2  0  2016 ?        00:00:23 [migration/0]
  root        11     2  0  2016 ?        00:00:13 [watchdog/0]
  root        12     2  0  2016 ?        00:00:03 [watchdog/1]
  root        13     2  0  2016 ?        00:00:00 [migration/1]
  root        14     2  0  2016 ?        00:00:00 [ksoftirqd/1]
  root        16     2  0  2016 ?        00:00:00 [kworker/1:0H]
  root        17     2  0  2016 ?        00:00:04 [watchdog/2]
  root        18     2  0  2016 ?        00:00:00 [migration/2]
  root        19     2  0  2016 ?        00:00:00 [ksoftirqd/2]
  root        21     2  0  2016 ?        00:00:00 [kworker/2:0H]
  root        22     2  0  2016 ?        00:00:06 [watchdog/3]
  root        23     2  0  2016 ?        00:00:00 [migration/3]
  root        24     2  0  2016 ?        00:00:00 [ksoftirqd/3]
  root        26     2  0  2016 ?        00:00:00 [kworker/3:0H]
  root        27     2  0  2016 ?        00:00:06 [watchdog/4]
  root        28     2  0  2016 ?        00:00:00 [migration/4]
  root        29     2  0  2016 ?        00:00:00 [ksoftirqd/4]
  root        31     2  0  2016 ?        00:00:00 [kworker/4:0H]
  root        32     2  0  2016 ?        00:00:09 [watchdog/5]
  root        33     2  0  2016 ?        00:00:00 [migration/5]
  root        34     2  0  2016 ?        00:00:00 [ksoftirqd/5]
  root        35     2  0  2016 ?        00:00:00 [kworker/5:0]
  root        36     2  0  2016 ?        00:00:00 [kworker/5:0H]
  root        37     2  0  2016 ?        00:00:08 [watchdog/6]
  root        38     2  0  2016 ?        00:00:00 [migration/6]
  root        39     2  0  2016 ?        00:00:00 [ksoftirqd/6]
  root        40     2  0  2016 ?        00:00:00 [kworker/6:0]
  root        41     2  0  2016 ?        00:00:00 [kworker/6:0H]
  root        42     2  0  2016 ?        00:00:09 [watchdog/7]
  root        43     2  0  2016 ?        00:00:00 [migration/7]
  root        44     2  0  2016 ?        00:00:00 [ksoftirqd/7]
  root        45     2  0  2016 ?        00:00:00 [kworker/7:0]
  root        46     2  0  2016 ?        00:00:00 [kworker/7:0H]
  root        47     2  0  2016 ?        00:00:09 [watchdog/8]
  root        48     2  0  2016 ?        00:00:00 [migration/8]
  root        49     2  0  2016 ?        00:00:00 [ksoftirqd/8]
  root        50     2  0  2016 ?        00:00:00 [kworker/8:0]
  root        51     2  0  2016 ?        00:00:00 [kworker/8:0H]
  root        52     2  0  2016 ?        00:00:09 [watchdog/9]
  root        53     2  0  2016 ?        00:00:00 [migration/9]
  root        54     2  0  2016 ?        00:00:00 [ksoftirqd/9]
  root        55     2  0  2016 ?        00:00:00 [kworker/9:0]
  root        56     2  0  2016 ?        00:00:00 [kworker/9:0H]
  root        57     2  0  2016 ?        00:00:09 [watchdog/10]
  root        58     2  0  2016 ?        00:00:00 [migration/10]
  root        59     2  0  2016 ?        00:00:00 [ksoftirqd/10]
  root        60     2  0  2016 ?        00:00:00 [kworker/10:0]
  root        61     2  0  2016 ?        00:00:00 [kworker/10:0H]
  root        62     2  0  2016 ?        00:00:10 [watchdog/11]
  root        63     2  0  2016 ?        00:00:00 [migration/11]
  root        64     2  0  2016 ?        00:00:00 [ksoftirqd/11]
  root        65     2  0  2016 ?        00:00:00 [kworker/11:0]
  root        66     2  0  2016 ?        00:00:00 [kworker/11:0H]
  root        67     2  0  2016 ?        00:00:10 [watchdog/12]
  root        68     2  0  2016 ?        00:00:00 [migration/12]
  root        69     2  0  2016 ?        00:00:00 [ksoftirqd/12]
  root        70     2  0  2016 ?        00:00:00 [kworker/12:0]
  root        71     2  0  2016 ?        00:00:00 [kworker/12:0H]
  root        72     2  0  2016 ?        00:00:10 [watchdog/13]
  root        73     2  0  2016 ?        00:00:00 [migration/13]
  root        74     2  0  2016 ?        00:00:00 [ksoftirqd/13]
  root        75     2  0  2016 ?        00:00:00 [kworker/13:0]
  root        76     2  0  2016 ?        00:00:00 [kworker/13:0H]
  root        77     2  0  2016 ?        00:00:09 [watchdog/14]
  root        78     2  0  2016 ?        00:00:00 [migration/14]
  root        79     2  0  2016 ?        00:00:00 [ksoftirqd/14]
  root        80     2  0  2016 ?        00:00:00 [kworker/14:0]
  root        81     2  0  2016 ?        00:00:00 [kworker/14:0H]
  root        82     2  0  2016 ?        00:00:09 [watchdog/15]
  root        83     2  0  2016 ?        00:00:00 [migration/15]
  root        84     2  0  2016 ?        00:00:00 [ksoftirqd/15]
  root        85     2  0  2016 ?        00:00:00 [kworker/15:0]
  root        86     2  0  2016 ?        00:00:00 [kworker/15:0H]
  root        87     2  0  2016 ?        00:00:10 [watchdog/16]
  root        88     2  0  2016 ?        00:00:00 [migration/16]
  root        89     2  0  2016 ?        00:00:00 [ksoftirqd/16]
  root        90     2  0  2016 ?        00:00:00 [kworker/16:0]
  root        91     2  0  2016 ?        00:00:00 [kworker/16:0H]
  root        92     2  0  2016 ?        00:00:10 [watchdog/17]
  root        93     2  0  2016 ?        00:00:00 [migration/17]
  root        94     2  0  2016 ?        00:00:00 [ksoftirqd/17]
  root        95     2  0  2016 ?        00:00:00 [kworker/17:0]
  root        96     2  0  2016 ?        00:00:00 [kworker/17:0H]
  root        97     2  0  2016 ?        00:00:18 [watchdog/18]
  root        98     2  0  2016 ?        00:00:26 [migration/18]
  root        99     2  0  2016 ?        00:13:29 [ksoftirqd/18]
  root       101     2  0  2016 ?        00:00:00 [kworker/18:0H]
  root       103     2  0  2016 ?        00:00:11 [watchdog/19]
  root       104     2  0  2016 ?        00:00:00 [migration/19]
  root       105     2  0  2016 ?        00:00:00 [ksoftirqd/19]
  root       107     2  0  2016 ?        00:00:00 [kworker/19:0H]
  root       108     2  0  2016 ?        00:00:11 [watchdog/20]
  root       109     2  0  2016 ?        00:00:00 [migration/20]
  root       110     2  0  2016 ?        00:00:00 [ksoftirqd/20]
  root       111     2  0  2016 ?        00:00:00 [kworker/20:0]
  root       112     2  0  2016 ?        00:00:00 [kworker/20:0H]
  root       113     2  0  2016 ?        00:00:11 [watchdog/21]
  root       114     2  0  2016 ?        00:00:00 [migration/21]
  root       115     2  0  2016 ?        00:00:00 [ksoftirqd/21]
  root       117     2  0  2016 ?        00:00:00 [kworker/21:0H]
  root       118     2  0  2016 ?        00:00:11 [watchdog/22]
  root       119     2  0  2016 ?        00:00:00 [migration/22]
  root       120     2  0  2016 ?        00:00:00 [ksoftirqd/22]
  root       122     2  0  2016 ?        00:00:00 [kworker/22:0H]
  root       123     2  0  2016 ?        00:00:11 [watchdog/23]
  root       124     2  0  2016 ?        00:00:00 [migration/23]
  root       125     2  0  2016 ?        00:00:00 [ksoftirqd/23]
  root       126     2  0  2016 ?        00:00:00 [kworker/23:0]
  root       127     2  0  2016 ?        00:00:00 [kworker/23:0H]
  root       128     2  0  2016 ?        00:00:11 [watchdog/24]
  root       129     2  0  2016 ?        00:00:00 [migration/24]
  root       130     2  0  2016 ?        00:00:00 [ksoftirqd/24]
  root       131     2  0  2016 ?        00:00:00 [kworker/24:0]
  root       132     2  0  2016 ?        00:00:00 [kworker/24:0H]
  root       133     2  0  2016 ?        00:00:11 [watchdog/25]
  root       134     2  0  2016 ?        00:00:00 [migration/25]
  root       135     2  0  2016 ?        00:00:00 [ksoftirqd/25]
  root       136     2  0  2016 ?        00:00:00 [kworker/25:0]
  root       137     2  0  2016 ?        00:00:00 [kworker/25:0H]
  root       138     2  0  2016 ?        00:00:11 [watchdog/26]
  root       139     2  0  2016 ?        00:00:00 [migration/26]
  root       140     2  0  2016 ?        00:00:00 [ksoftirqd/26]
  root       141     2  0  2016 ?        00:00:00 [kworker/26:0]
  root       142     2  0  2016 ?        00:00:00 [kworker/26:0H]
  root       143     2  0  2016 ?        00:00:11 [watchdog/27]
  root       144     2  0  2016 ?        00:00:00 [migration/27]
  root       145     2  0  2016 ?        00:00:00 [ksoftirqd/27]
  root       146     2  0  2016 ?        00:00:00 [kworker/27:0]
  root       147     2  0  2016 ?        00:00:00 [kworker/27:0H]
  root       148     2  0  2016 ?        00:00:11 [watchdog/28]
  root       149     2  0  2016 ?        00:00:00 [migration/28]
  root       150     2  0  2016 ?        00:00:00 [ksoftirqd/28]
  root       151     2  0  2016 ?        00:00:00 [kworker/28:0]
  root       152     2  0  2016 ?        00:00:00 [kworker/28:0H]
  root       153     2  0  2016 ?        00:00:12 [watchdog/29]
  root       154     2  0  2016 ?        00:00:00 [migration/29]
  root       155     2  0  2016 ?        00:00:00 [ksoftirqd/29]
  root       156     2  0  2016 ?        00:00:00 [kworker/29:0]
  root       157     2  0  2016 ?        00:00:00 [kworker/29:0H]
  root       158     2  0  2016 ?        00:00:12 [watchdog/30]
  root       159     2  0  2016 ?        00:00:00 [migration/30]
  root       160     2  0  2016 ?        00:00:00 [ksoftirqd/30]
  root       161     2  0  2016 ?        00:00:00 [kworker/30:0]
  root       162     2  0  2016 ?        00:00:00 [kworker/30:0H]
  root       163     2  0  2016 ?        00:00:12 [watchdog/31]
  root       164     2  0  2016 ?        00:00:00 [migration/31]
  root       165     2  0  2016 ?        00:00:00 [ksoftirqd/31]
  root       166     2  0  2016 ?        00:00:00 [kworker/31:0]
  root       167     2  0  2016 ?        00:00:00 [kworker/31:0H]
  root       168     2  0  2016 ?        00:00:11 [watchdog/32]
  root       169     2  0  2016 ?        00:00:00 [migration/32]
  root       170     2  0  2016 ?        00:00:00 [ksoftirqd/32]
  root       171     2  0  2016 ?        00:00:00 [kworker/32:0]
  root       172     2  0  2016 ?        00:00:00 [kworker/32:0H]
  root       173     2  0  2016 ?        00:00:12 [watchdog/33]
  root       174     2  0  2016 ?        00:00:00 [migration/33]
  root       175     2  0  2016 ?        00:00:00 [ksoftirqd/33]
  root       176     2  0  2016 ?        00:00:00 [kworker/33:0]
  root       177     2  0  2016 ?        00:00:00 [kworker/33:0H]
  root       178     2  0  2016 ?        00:00:11 [watchdog/34]
  root       179     2  0  2016 ?        00:00:00 [migration/34]
  root       180     2  0  2016 ?        00:00:00 [ksoftirqd/34]
  root       181     2  0  2016 ?        00:00:00 [kworker/34:0]
  root       182     2  0  2016 ?        00:00:00 [kworker/34:0H]
  root       183     2  0  2016 ?        00:00:12 [watchdog/35]
  root       184     2  0  2016 ?        00:00:00 [migration/35]
  root       185     2  0  2016 ?        00:00:00 [ksoftirqd/35]
  root       186     2  0  2016 ?        00:00:00 [kworker/35:0]
  root       187     2  0  2016 ?        00:00:00 [kworker/35:0H]
  root       188     2  0  2016 ?        00:00:00 [kdevtmpfs]
  root       189     2  0  2016 ?        00:00:00 [netns]
  root       190     2  0  2016 ?        00:00:00 [perf]
  root       191     2  0  2016 ?        00:00:03 [khungtaskd]
  root       192     2  0  2016 ?        00:00:00 [writeback]
  root       193     2  0  2016 ?        00:00:00 [ksmd]
  root       194     2  0  2016 ?        00:01:18 [khugepaged]
  root       195     2  0  2016 ?        00:00:00 [crypto]
  root       196     2  0  2016 ?        00:00:00 [kintegrityd]
  root       197     2  0  2016 ?        00:00:00 [bioset]
  root       198     2  0  2016 ?        00:00:00 [kblockd]
  root       199     2  0  2016 ?        00:00:00 [ata_sff]
  root       200     2  0  2016 ?        00:00:00 [md]
  root       201     2  0  2016 ?        00:00:00 [devfreq_wq]
  root       205     2  0  2016 ?        00:00:00 [kswapd0]
  root       206     2  0  2016 ?        00:00:00 [kswapd1]
  root       207     2  0  2016 ?        00:00:00 [vmstat]
  root       208     2  0  2016 ?        00:00:00 [fsnotify_mark]
  root       209     2  0  2016 ?        00:00:00 [ecryptfs-kthrea]
  root       225     2  0  2016 ?        00:00:00 [kthrotld]
  root       228     2  0  2016 ?        00:00:00 [acpi_thermal_pm]
  root       229     2  0  2016 ?        00:00:00 [bioset]
  root       230     2  0  2016 ?        00:00:00 [bioset]
  root       231     2  0  2016 ?        00:00:00 [bioset]
  root       232     2  0  2016 ?        00:00:00 [bioset]
  root       233     2  0  2016 ?        00:00:00 [bioset]
  root       234     2  0  2016 ?        00:00:00 [bioset]
  root       235     2  0  2016 ?        00:00:00 [bioset]
  root       236     2  0  2016 ?        00:00:00 [bioset]
  root       237     2  0  2016 ?        00:00:00 [bioset]
  root       238     2  0  2016 ?        00:00:00 [bioset]
  root       239     2  0  2016 ?        00:00:00 [bioset]
  root       240     2  0  2016 ?        00:00:00 [bioset]
  root       241     2  0  2016 ?        00:00:00 [bioset]
  root       242     2  0  2016 ?        00:00:00 [bioset]
  root       243     2  0  2016 ?        00:00:00 [bioset]
  root       244     2  0  2016 ?        00:00:00 [bioset]
  root       245     2  0  2016 ?        00:00:00 [bioset]
  root       246     2  0  2016 ?        00:00:00 [bioset]
  root       247     2  0  2016 ?        00:00:00 [bioset]
  root       248     2  0  2016 ?        00:00:00 [bioset]
  root       249     2  0  2016 ?        00:00:00 [bioset]
  root       250     2  0  2016 ?        00:00:00 [bioset]
  root       251     2  0  2016 ?        00:00:00 [bioset]
  root       252     2  0  2016 ?        00:00:00 [bioset]
  root       255     2  0  2016 ?        00:00:00 [kworker/35:1]
  root       261     2  0  2016 ?        00:00:00 [ipv6_addrconf]
  root       274     2  0  2016 ?        00:00:00 [deferwq]
  root       276     2  0  2016 ?        00:00:00 [charger_manager]
  root       312     2  0  2016 ?        00:00:00 [fc_exch_workque]
  root       313     2  0  2016 ?        00:00:00 [fc_rport_eq]
  root       314     2  0  2016 ?        00:00:00 [scsi_eh_0]
  root       315     2  0  2016 ?        00:00:00 [scsi_tmf_0]
  root       324     2  0  2016 ?        00:00:00 [bioset]
  root       329     2  0  2016 ?        00:00:00 [ixgbe]
  root       333     2  0  2016 ?        00:00:00 [scsi_eh_1]
  root       334     2  0  2016 ?        00:00:00 [fnic_event_wq]
  root       335     2  0  2016 ?        00:00:00 [scsi_tmf_1]
  root       337     2  0  2016 ?        00:00:00 [scsi_eh_2]
  root       340     2  0  2016 ?        00:00:00 [scsi_tmf_2]
  root       341     2  0  2016 ?        00:00:00 [fnic_fip_q]
  root       343     2  0  2016 ?        00:00:00 [scsi_eh_3]
  root       344     2  0  2016 ?        00:00:00 [scsi_eh_4]
  root       345     2  0  2016 ?        00:00:00 [scsi_tmf_3]
  root       352     2  0  2016 ?        00:00:00 [scsi_eh_5]
  root       353     2  0  2016 ?        00:00:00 [scsi_tmf_5]
  root       355     2  0  2016 ?        00:00:00 [scsi_tmf_4]
  root       356     2  0  2016 ?        00:00:00 [i40e]
  root       360     2  0  2016 ?        00:00:00 [scsi_eh_6]
  root       361     2  0  2016 ?        00:00:00 [scsi_tmf_6]
  root       363     2  0  2016 ?        00:00:00 [scsi_eh_7]
  root       364     2  0  2016 ?        00:00:00 [scsi_tmf_7]
  root       371     2  0  2016 ?        00:00:00 [scsi_wq_4]
  root       372     2  0  2016 ?        00:00:00 [bioset]
  root       373     2  0  2016 ?        00:00:00 [scsi_eh_8]
  root       374     2  0  2016 ?        00:00:00 [scsi_tmf_8]
  root       404     2  0  2016 ?        00:00:00 [scsi_wq_8]
  root       405     2  0  2016 ?        00:00:00 [bioset]
  root       461     2  0 Jan19 ?        00:00:00 [kworker/19:1]
  root       601     2  0  2016 ?        00:00:00 [bioset]
  root       879     2  0  2016 ?        00:00:42 [jbd2/sda2-8]
  root       880     2  0  2016 ?        00:00:00 [ext4-rsv-conver]
  root       912     2  0  2016 ?        00:00:02 [kworker/18:1H]
  root       917     1  0  2016 ?        00:23:57 /lib/systemd/systemd-journald
  root       921     2  0  2016 ?        00:00:00 [kauditd]
  root       935     2  0  2016 ?        00:00:00 [kworker/5:1]
  root       936     2  0  2016 ?        00:00:00 [kworker/6:1]
  root       937     2  0  2016 ?        00:00:00 [kworker/7:1]
  root       938     2  0  2016 ?        00:00:00 [kworker/8:1]
  root       939     2  0  2016 ?        00:00:00 [kworker/9:1]
  root       940     2  0  2016 ?        00:00:00 [kworker/10:1]
  root       941     2  0  2016 ?        00:00:00 [kworker/20:1]
  root       942     2  0  2016 ?        00:00:00 [kworker/12:1]
  root       944     2  0  2016 ?        00:00:00 [kworker/13:1]
  root       945     2  0  2016 ?        00:00:00 [kworker/14:1]
  root       947     2  0  2016 ?        00:00:00 [kworker/15:1]
  root       948     2  0  2016 ?        00:00:00 [kworker/23:1]
  root       949     2  0  2016 ?        00:00:00 [kworker/16:1]
  root       950     2  0  2016 ?        00:00:00 [kworker/24:1]
  root       951     2  0  2016 ?        00:00:00 [kworker/17:1]
  root       952     2  0  2016 ?        00:00:00 [kworker/25:1]
  root       953     2  0  2016 ?        00:00:00 [kworker/11:1]
  root       954     2  0  2016 ?        00:00:00 [kworker/26:1]
  root       955     2  0  2016 ?        00:00:00 [kworker/27:1]
  root       956     2  0  2016 ?        00:00:00 [kworker/28:1]
  root       957     2  0  2016 ?        00:00:00 [kworker/29:1]
  root       959     2  0  2016 ?        00:00:00 [kworker/30:1]
  root       960     2  0  2016 ?        00:00:00 [kworker/31:1]
  root       961     2  0  2016 ?        00:00:00 [kworker/32:1]
  root       962     2  0  2016 ?        00:00:00 [kworker/33:1]
  root       963     2  0  2016 ?        00:00:00 [kworker/34:1]
  root      1011     1  0  2016 ?        00:00:27 /lib/systemd/systemd-udevd
  root      1038     2  0  2016 ?        00:00:00 [kvm-irqfd-clean]
  root      1061     2  0  2016 ?        00:00:00 [kipmi0]
  root      1110     2  0  2016 ?        00:00:00 [edac-poller]
  root      1135     2  0  2016 ?        00:00:00 [jbd2/sda1-8]
  root      1136     2  0  2016 ?        00:00:00 [ext4-rsv-conver]
  root      1144     2  0  2016 ?        00:00:01 [kworker/0:1H]
  systemd+  1169     1  0  2016 ?        00:00:05 /lib/systemd/systemd-timesyncd
  syslog    1333     1  0  2016 ?        00:05:01 /usr/sbin/rsyslogd -n
  root      1347     1  0  2016 ?        00:00:05 /usr/sbin/cron -f
  message+  1352     1  0  2016 ?        00:03:05 /usr/bin/dbus-daemon --system --address=systemd: --nofork --nopidfile --systemd-activation
  root      1359     1  0  2016 ?        00:00:47 /lib/systemd/systemd-logind
  root      1362     1  2  2016 ?        2-22:13:18 /usr/lib/accountsservice/accounts-daemon
  root      1432     1  0  2016 ?        00:00:00 /usr/sbin/sshd -D
  root      1459     1  0  2016 tty1     00:00:00 /sbin/agetty --noclear tty1 linux
  root      1461     1  0  2016 ttyS0    00:00:00 /sbin/agetty --keep-baud 115200 38400 9600 ttyS0 vt220
  root      3657     2  0 Jan21 ?        00:00:00 [kworker/21:1]
  root      5907     2  0 Jan26 ?        00:00:00 [kworker/4:2]
  root      6236     2  0  2016 ?        00:00:08 [kworker/u73:2]
  root      6830     2  0 01:06 ?        00:00:00 [kworker/4:0]
  root      7418     2  0 05:42 ?        00:00:00 [kworker/18:0]
  root      7423     2  0 05:42 ?        00:00:00 [kworker/18:3]
  root      7509     2  0 05:42 ?        00:00:00 [kworker/0:2]
  root      7981     2  0 05:46 ?        00:00:00 [kworker/0:3]
  root      8669     2  0 05:53 ?        00:00:00 [kworker/0:1]
  root      8676     2  0 05:53 ?        00:00:00 [kworker/0:4]
  root      9387     2  0 05:56 ?        00:00:00 [kworker/18:1]
  root      9481     1 99 05:56 ?        00:03:22 /usr/bin/vpp -c /etc/vpp/startup.conf
  root     10069  1432  0 05:58 ?        00:00:00 sshd: testuser [priv]
  testuser 10078 10069  0 05:58 ?        00:00:00 sshd: testuser@notty
  testuser 10153 10078  0 05:58 ?        00:00:00 ps -ef
  root     12758     2  0 Jan26 ?        00:00:00 [kworker/22:1]
  root     14060     2  0  2016 ?        00:00:00 [kworker/u75:0]
  root     14061     2  0  2016 ?        00:00:16 [kworker/u75:1]
  root     14108     2  0  2016 ?        00:00:00 [kworker/5:1H]
  root     16956     2  0 Jan16 ?        00:00:00 [kworker/19:2]
  root     17226     2  0 02:29 ?        00:00:00 [kworker/3:1]
  root     17518     2  0  2016 ?        00:00:11 [kworker/u74:0]
  root     20356     2  0  2016 ?        00:00:00 [kworker/21:2]
  root     20710     2  0 Jan10 ?        00:00:00 [kworker/22:0]
  root     24548     2  0 Jan26 ?        00:00:00 [kworker/u72:2]
  root     24550     2  0 Jan26 ?        00:00:01 [kworker/u72:0]
  root     25286     2  0 Jan24 ?        00:00:00 [kworker/u74:2]
  root     26127  1432  0 Jan26 ?        00:00:02 sshd: testuser [priv]
  testuser 26136 26127  0 Jan26 ?        00:00:19 sshd: testuser@notty
  root     27016     2  0 Jan26 ?        00:00:00 [kworker/1:1]
  root     27890     2  0 Jan26 ?        00:00:00 [kworker/3:0]
  root     29718     2  0 Jan08 ?        00:00:00 [kworker/2:0]
  root     32537     2  0 Jan09 ?        00:00:00 [kworker/2:1]
  root     35499     2  0 00:14 ?        00:00:00 [kworker/1:0]
  root     35974     2  0 00:16 ?        00:00:00 [kworker/u73:1]
  ]]></exec_output>
      </function>
      <function id="linux_service" significance="3" time="2017-01-27 13:58:35.659825 UTC" version="1.0.0">
        <exec_command><![CDATA[service --status-all]]></exec_command>
        <exec_return_code>0</exec_return_code>
        <exec_output><![CDATA[ [ - ]  bootmisc.sh
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
   [ - ]  sendsigs
   [ + ]  ssh
   [ + ]  udev
   [ - ]  umountfs
   [ - ]  umountnfs.sh
   [ - ]  umountroot
   [ + ]  urandom
   [ - ]  x11-common
  ]]></exec_output>
      </function>
    </section>
    <section id="4" name="Compute Virtualization Infrastructure / Hypervisor">
      <function id="linux_virsh_capabilities" significance="1" time="2017-01-27 13:58:39.999871 UTC" version="1.0.0">
        <exec_command><![CDATA[virsh capabilities]]></exec_command>
        <exec_return_code>127</exec_return_code>
        <exec_output><![CDATA[bash: virsh: command not found
  ]]></exec_output>
      </function>
      <function id="linux_virsh_domains" significance="2" time="2017-01-27 13:58:41.069921 UTC" version="1.0.0">
        <exec_command><![CDATA[virsh list | grep -E -v "Id.*Name.*State" | grep "^ " | awk '{print $2}']]></exec_command>
        <exec_return_code>0</exec_return_code>
        <exec_output><![CDATA[]]></exec_output>
      </function>
    </section>
    <section id="5" name="Compute Virtualization Functions / VMs">
      <function id="linux_virsh_domains_xml" significance="1" time="2017-01-27 13:58:42.147566 UTC" version="1.0.0">
        <exec_command><![CDATA[virsh dumpxml]]></exec_command>
        <exec_return_code>0</exec_return_code>
        <exec_output>
          <virsh_domains/>
        </exec_output>
      </function>
    </section>
    <section id="6" name="Network Virtualization Infastructure / vSwitch">
      <function id="linux_ovs_bridges_status" significance="1" time="2017-01-27 13:58:43.371611 UTC" version="1.0.0">
        <exec_command><![CDATA[sudo ovs-vsctl show]]></exec_command>
        <exec_return_code>1</exec_return_code>
        <exec_output><![CDATA[sudo: ovs-vsctl: command not found
  ]]></exec_output>
      </function>
      <function id="linux_ovs_version" significance="1" time="2017-01-27 13:58:44.255264 UTC" version="1.0.0">
        <exec_command><![CDATA[ovs-vsctl --version]]></exec_command>
        <exec_return_code>127</exec_return_code>
        <exec_output><![CDATA[bash: ovs-vsctl: command not found
  ]]></exec_output>
      </function>
      <function id="linux_vpp_conf" significance="1" time="2017-01-27 13:58:45.319272 UTC" version="1.0.0">
        <exec_command><![CDATA[cat /opt/cisco/vpe/etc/qn.conf]]></exec_command>
        <exec_return_code>1</exec_return_code>
        <exec_output><![CDATA[cat: /opt/cisco/vpe/etc/qn.conf: No such file or directory
  ]]></exec_output>
      </function>
    </section>
  </stack>


DUT Configuration - DPDK
------------------------

**DPDK Version**

16.09

**DPDK Compile Parameters**

.. code-block:: bash

    make install T=x86_64-native-linuxapp-gcc -j

**DPDK Startup Configuration**

DPDK startup configuration changes per test case with different settings for CPU
cores, rx-queues. Startup config is aligned with applied test case tag:

Tagged by **1T1C**

.. code-block:: bash

    testpmd -c 0x3 -n 4 -- --nb-ports=2 --portmask=0x3 --nb-cores=1 --max-pkt-len=9000 --txqflags=0 --forward-mode=io --rxq=1 --txq=1 --auto-start

Tagged by **2T2C**

.. code-block:: bash

    testpmd -c 0x403 -n 4 -- --nb-ports=2 --portmask=0x3 --nb-cores=2 --max-pkt-len=9000 --txqflags=0 --forward-mode=io --rxq=1 --txq=1 --auto-start

Tagged by **4T4C**

.. code-block:: bash

    testpmd -c 0xc07 -n 4 -- --nb-ports=2 --portmask=0x3 --nb-cores=4 --max-pkt-len=9000 --txqflags=0 --forward-mode=io --rxq=2 --txq=2 --auto-start


TG Configuration - TRex
-----------------------

**TG Version**

TRex v2.09

**DPDK version**

DPDK v16.07 (20e2b6eba13d9eb61b23ea75f09f2aa966fa6325 - in DPDK repo)

**TG Build Script used**

https://gerrit.fd.io/r/gitweb?p=csit.git;a=blob;f=resources/tools/t-rex/t-rex-installer.sh;h=e89b06f9b12499996df18e5e3399fcd660ebc017;hb=refs/heads/rls1701

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

**TG common API - pointer to driver**

https://gerrit.fd.io/r/gitweb?p=csit.git;a=blob;f=resources/tools/t-rex/t-rex-stateless.py;h=24f4a997389ba3f10ad42e1f9564ef915fd58b44;hb=refs/heads/rls1701

