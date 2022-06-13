# SuperMicro Cascadelake Servers - HW and BIOS Configuration

1. [Linux lscpu](#linux-lscpu)
1. [Linux dmidecode](#dmidecode)
1. [Linux dmidecode pci](#linux-dmidecode-pci)
1. [Linux dmidecode memory](#linux-dmidecode-memory)
1. [EPYC zn2 Server BIOS Configuration](#epyc-zn2-server-bios-configuration)
   1. [Boot Feature](#boot-feature)
   1. [CPU Configuration](#cpu-configuration)
      1. [Advanced Power Management Configuration](#advanced-power-management-configuration)
         1. [CPU P State Control](#cpu-p-state-control)
         1. [Hardware PM State Control](#hardware-pm-state-control)
         1. [CPU C State Control](#cpu-c-state-control)
         1. [Package C State Control](#package-c-state-control)
         1. [CPU T State Control](#cpu-t-state-control)
      1. [Chipset Configuration](#chipset-configuration)
         1. [North Bridge](#north-bridge)
         1. [UPI Configuration](#upi-configuration)
         1. [Memory Configuration](#memory-configuration)
         1. [IIO Configuration](#iio-configuration)
         1. [CPU1 Configuration](#cpu1-configuration)
         1. [CPU2 Configuration](#cpu2-configuration)
      1. [South Bridge](#south-bridge)
   1. [PCIe/PCI/PnP Configuration](#pciepcipnp-configuration)
   1. [ACPI Settings](#acpi-settings)
1. [EPYC zn2 Server Firmware Inventory](#epyc-zn2-server-firmware-inventory)

## Linux lscpu

```
$ lscpu
Architecture:        x86_64
CPU op-mode(s):      32-bit, 64-bit
Byte Order:          Little Endian
CPU(s):              64
On-line CPU(s) list: 0-63
Thread(s) per core:  2
Core(s) per socket:  32
Socket(s):           1
NUMA node(s):        2
Vendor ID:           AuthenticAMD
CPU family:          23
Model:               49
Model name:          AMD EPYC 7532 32-Core Processor
Stepping:            0
CPU MHz:             1981.470
CPU max MHz:         2400.0000
CPU min MHz:         1500.0000
BogoMIPS:            4800.05
Virtualization:      AMD-V
L1d cache:           32K
L1i cache:           32K
L2 cache:            512K
L3 cache:            16384K
NUMA node0 CPU(s):   0-15,32-47
NUMA node1 CPU(s):   16-31,48-63
Flags:               fpu vme de pse tsc msr pae mce cx8 apic sep mtrr pge mca cmov pat pse36 clflush mmx fxsr sse sse2 ht syscall nx mmxext fxsr_opt pdpe1gb rdtscp lm constant_tsc rep_good nopl xtopology nonstop_tsc cpuid extd_apicid aperfmperf pni pclmulqdq monitor ssse3 fma cx16 sse4_1 sse4_2 x2apic movbe popcnt aes xsave avx f16c rdrand lahf_lm cmp_legacy svm extapic cr8_legacy abm sse4a misalignsse 3dnowprefetch osvw ibs skinit wdt tce topoext perfctr_core perfctr_nb bpext perfctr_llc mwaitx cpb cat_l3 cdp_l3 hw_pstate sme ssbd ibrs ibpb stibp vmmcall fsgsbase bmi1 avx2 smep bmi2 cqm rdt_a rdseed adx smap clflushopt clwb sha_ni xsaveopt xsavec xgetbv1 xsaves cqm_llc cqm_occup_llc cqm_mbm_total cqm_mbm_local clzero irperf xsaveerptr arat npt lbrv svm_lock nrip_save tsc_scale vmcb_clean flushbyasid decodeassists pausefilter pfthreshold avic v_vmsave_vmload vgif umip rdpid overflow_recov succor smca
```

```
$ lscpu
Architecture:        x86_64
CPU op-mode(s):      32-bit, 64-bit
Byte Order:          Little Endian
CPU(s):              64
On-line CPU(s) list: 0-63
Thread(s) per core:  2
Core(s) per socket:  32
Socket(s):           1
NUMA node(s):        2
Vendor ID:           AuthenticAMD
CPU family:          23
Model:               49
Model name:          AMD EPYC 7532 32-Core Processor
Stepping:            0
CPU MHz:             1981.470
CPU max MHz:         2400.0000
CPU min MHz:         1500.0000
BogoMIPS:            4800.05
Virtualization:      AMD-V
L1d cache:           32K
L1i cache:           32K
L2 cache:            512K
L3 cache:            16384K
NUMA node0 CPU(s):   0-15,32-47
NUMA node1 CPU(s):   16-31,48-63
Flags:               fpu vme de pse tsc msr pae mce cx8 apic sep mtrr pge mca cmov pat pse36 clflush mmx fxsr sse sse2 ht syscall nx mmxext fxsr_opt pdpe1gb rdtscp lm constant_tsc rep_good nopl xtopology nonstop_tsc cpuid extd_apicid aperfmperf pni pclmulqdq monitor ssse3 fma cx16 sse4_1 sse4_2 x2apic movbe popcnt aes xsave avx f16c rdrand lahf_lm cmp_legacy svm extapic cr8_legacy abm sse4a misalignsse 3dnowprefetch osvw ibs skinit wdt tce topoext perfctr_core perfctr_nb bpext perfctr_llc mwaitx cpb cat_l3 cdp_l3 hw_pstate sme ssbd ibrs ibpb stibp vmmcall fsgsbase bmi1 avx2 smep bmi2 cqm rdt_a rdseed adx smap clflushopt clwb sha_ni xsaveopt xsavec xgetbv1 xsaves cqm_llc cqm_occup_llc cqm_mbm_total cqm_mbm_local clzero irperf xsaveerptr arat npt lbrv svm_lock nrip_save tsc_scale vmcb_clean flushbyasid decodeassists pausefilter pfthreshold avic v_vmsave_vmload vgif umip rdpid overflow_recov succor smca
```

## Linux dmidecode

```
  $ dmidecode -t slot
  Handle 0x0026, DMI type 7, 27 bytes
  Cache Information
          Socket Designation: L1 Cache
          Configuration: Enabled, Not Socketed, Level 1
          Operational Mode: Write Back
          Location: Internal
          Installed Size: 2048 kB
          Maximum Size: 2048 kB
          Supported SRAM Types:
                  Pipeline Burst
          Installed SRAM Type: Pipeline Burst
          Speed: 1 ns
          Error Correction Type: Multi-bit ECC
          System Type: Unified
          Associativity: 8-way Set-associative

  Handle 0x0027, DMI type 7, 27 bytes
  Cache Information
          Socket Designation: L2 Cache
          Configuration: Enabled, Not Socketed, Level 2
          Operational Mode: Write Back
          Location: Internal
          Installed Size: 16384 kB
          Maximum Size: 16384 kB
          Supported SRAM Types:
                  Pipeline Burst
          Installed SRAM Type: Pipeline Burst
          Speed: 1 ns
          Error Correction Type: Multi-bit ECC
          System Type: Unified
          Associativity: 8-way Set-associative

  Handle 0x0028, DMI type 7, 27 bytes
  Cache Information
          Socket Designation: L3 Cache
          Configuration: Enabled, Not Socketed, Level 3
          Operational Mode: Write Back
          Location: Internal
          Installed Size: 262144 kB
          Maximum Size: 262144 kB
          Supported SRAM Types:
                  Pipeline Burst
          Installed SRAM Type: Pipeline Burst
          Speed: 1 ns
          Error Correction Type: Multi-bit ECC
          System Type: Unified
          Associativity: 16-way Set-associative

  Handle 0x0029, DMI type 4, 48 bytes
  Processor Information
          Socket Designation: CPU
          Type: Central Processor
          Family: Zen
          Manufacturer: Advanced Micro Devices, Inc.
          ID: 10 0F 83 00 FF FB 8B 17
          Signature: Family 23, Model 49, Stepping 0
          Flags:
                  FPU (Floating-point unit on-chip)
                  VME (Virtual mode extension)
                  DE (Debugging extension)
                  PSE (Page size extension)
                  TSC (Time stamp counter)
                  MSR (Model specific registers)
                  PAE (Physical address extension)
                  MCE (Machine check exception)
                  CX8 (CMPXCHG8 instruction supported)
                  APIC (On-chip APIC hardware supported)
                  SEP (Fast system call)
                  MTRR (Memory type range registers)
                  PGE (Page global enable)
                  MCA (Machine check architecture)
                  CMOV (Conditional move instruction supported)
                  PAT (Page attribute table)
                  PSE-36 (36-bit page size extension)
                  CLFSH (CLFLUSH instruction supported)
                  MMX (MMX technology supported)
                  FXSR (FXSAVE and FXSTOR instructions supported)
                  SSE (Streaming SIMD extensions)
                  SSE2 (Streaming SIMD extensions 2)
                  HTT (Multi-threading)
          Version: AMD EPYC 7532 32-Core Processor
          Voltage: 1.1 V
          External Clock: 100 MHz
          Max Speed: 3300 MHz
          Current Speed: 2400 MHz
          Status: Populated, Enabled
          Upgrade: Socket SP3
          L1 Cache Handle: 0x0026
          L2 Cache Handle: 0x0027
          L3 Cache Handle: 0x0028
          Serial Number: Unknown
          Asset Tag: Unknown
          Part Number: Unknown
          Core Count: 32
          Core Enabled: 32
          Thread Count: 64
          Characteristics:
                  64-bit capable
                  Multi-Core
                  Hardware Thread
                  Execute Protection
                  Enhanced Virtualization
                  Power/Performance Control
```

## Linux dmidecode pci

```
  $ dmidecode -t slot
  Getting SMBIOS data from sysfs.
  SMBIOS 3.2.0 present.
  # SMBIOS implementations newer than version 3.1.1 are not
  # fully supported by this version of dmidecode.

  Handle 0x000A, DMI type 9, 17 bytes
  System Slot Information
          Designation: M.2-HC1 CPU PCI-E 4.0 X4/X2
          Type: x4 PCI Express 3 x4
          Current Usage: Available
          Length: Short
          ID: 1
          Characteristics:
                  3.3 V is provided
                  Opening is shared
                  PME signal is supported
          Bus Address: 0000:ff:00.0

  Handle 0x000B, DMI type 9, 17 bytes
  System Slot Information
          Designation: M.2-HC2 CPU PCI-E 4.0 X2
          Type: x2 PCI Express 3 x2
          Current Usage: Available
          Length: Short
          ID: 2
          Characteristics:
                  3.3 V is provided
                  Opening is shared
                  PME signal is supported
          Bus Address: 0000:ff:00.0

  Handle 0x0042, DMI type 9, 17 bytes
  System Slot Information
          Designation: RSC-W-66G4 SLOT1 PCI-E 4.0 X16
          Type: x16 PCI Express 3 x16
          Current Usage: In Use
          Length: Long
          ID: 1
          Characteristics:
                  3.3 V is provided
                  PME signal is supported
          Bus Address: 0000:41:00.0

  Handle 0x0043, DMI type 9, 17 bytes
  System Slot Information
          Designation: RSC-W-66G4 SLOT2 PCI-E 4.0 X16
          Type: x16 PCI Express 3 x16
          Current Usage: In Use
          Length: Long
          ID: 2
          Characteristics:
                  3.3 V is provided
                  PME signal is supported
          Bus Address: 0000:81:00.0

  Handle 0x0045, DMI type 9, 17 bytes
  System Slot Information
          Designation: RSC-WR-6 SLOT1 PCI-E 4.0 X16
          Type: x16 PCI Express 3 x16
          Current Usage: In Use
          Length: Long
          ID: 1
          Characteristics:
                  3.3 V is provided
                  PME signal is supported
          Bus Address: 0000:01:00.0

```

## Linux dmidecode memory

```
  $ dmidecode -t memory
  # dmidecode 3.1
  Getting SMBIOS data from sysfs.
  SMBIOS 3.2.0 present.
  # SMBIOS implementations newer than version 3.1.1 are not
  # fully supported by this version of dmidecode.

  Handle 0x0023, DMI type 16, 23 bytes
  Physical Memory Array
          Location: System Board Or Motherboard
          Use: System Memory
          Error Correction Type: Multi-bit ECC
          Maximum Capacity: 2 TB
          Error Information Handle: 0x0022
          Number Of Devices: 8

  Handle 0x002B, DMI type 17, 84 bytes
  Memory Device
          Array Handle: 0x0023
          Error Information Handle: 0x002A
          Total Width: 72 bits
          Data Width: 64 bits
          Size: 32 GB
          Form Factor: DIMM
          Set: None
          Locator: DIMMA1
          Bank Locator: P0_Node0_Channel0_Dimm0
          Type: DDR4
          Type Detail: Synchronous Registered (Buffered)
          Speed: 3200 MT/s
          Manufacturer: SK Hynix
          Serial Number: 431E9216
          Asset Tag: P1-DIMMA1_AssetTag (date:19/00)
          Part Number: HMA84GR7CJR4N-XN
          Rank: 2
          Configured Clock Speed: 3200 MT/s
          Minimum Voltage: 1.2 V
          Maximum Voltage: 1.2 V
          Configured Voltage: 1.2 V

  Handle 0x002E, DMI type 17, 84 bytes
  Memory Device
          Array Handle: 0x0023
          Error Information Handle: 0x002D
          Total Width: 72 bits
          Data Width: 64 bits
          Size: 32 GB
          Form Factor: DIMM
          Set: None
          Locator: DIMMB1
          Bank Locator: P0_Node0_Channel1_Dimm0
          Type: DDR4
          Type Detail: Synchronous Registered (Buffered)
          Speed: 3200 MT/s
          Manufacturer: SK Hynix
          Serial Number: 431E91D2
          Asset Tag: P1-DIMMB1_AssetTag (date:19/00)
          Part Number: HMA84GR7CJR4N-XN
          Rank: 2
          Configured Clock Speed: 3200 MT/s
          Minimum Voltage: 1.2 V
          Maximum Voltage: 1.2 V
          Configured Voltage: 1.2 V

  Handle 0x0031, DMI type 17, 84 bytes
  Memory Device
          Array Handle: 0x0023
          Error Information Handle: 0x0030
          Total Width: 72 bits
          Data Width: 64 bits
          Size: 32 GB
          Form Factor: DIMM
          Set: None
          Locator: DIMMC1
          Bank Locator: P0_Node0_Channel2_Dimm0
          Type: DDR4
          Type Detail: Synchronous Registered (Buffered)
          Speed: 3200 MT/s
          Manufacturer: SK Hynix
          Serial Number: 431E918A
          Asset Tag: P1-DIMMC1_AssetTag (date:19/00)
          Part Number: HMA84GR7CJR4N-XN
          Rank: 2
          Configured Clock Speed: 3200 MT/s
          Minimum Voltage: 1.2 V
          Maximum Voltage: 1.2 V
          Configured Voltage: 1.2 V

  Handle 0x0034, DMI type 17, 84 bytes
  Memory Device
          Array Handle: 0x0023
          Error Information Handle: 0x0033
          Total Width: 72 bits
          Data Width: 64 bits
          Size: 32 GB
          Form Factor: DIMM
          Set: None
          Locator: DIMMD1
          Bank Locator: P0_Node0_Channel3_Dimm0
          Type: DDR4
          Type Detail: Synchronous Registered (Buffered)
          Speed: 3200 MT/s
          Manufacturer: SK Hynix
          Serial Number: 431E9187
          Asset Tag: P1-DIMMD1_AssetTag (date:19/00)
          Part Number: HMA84GR7CJR4N-XN
          Rank: 2
          Configured Clock Speed: 3200 MT/s
          Minimum Voltage: 1.2 V
          Maximum Voltage: 1.2 V
          Configured Voltage: 1.2 V

  Handle 0x0037, DMI type 17, 84 bytes
  Memory Device
          Array Handle: 0x0023
          Error Information Handle: 0x0036
          Total Width: 72 bits
          Data Width: 64 bits
          Size: 32 GB
          Form Factor: DIMM
          Set: None
          Locator: DIMME1
          Bank Locator: P0_Node0_Channel4_Dimm0
          Type: DDR4
          Type Detail: Synchronous Registered (Buffered)
          Speed: 3200 MT/s
          Manufacturer: SK Hynix
          Serial Number: 431E9178
          Asset Tag: P1-DIMME1_AssetTag (date:19/00)
          Part Number: HMA84GR7CJR4N-XN
          Rank: 2
          Configured Clock Speed: 3200 MT/s
          Minimum Voltage: 1.2 V
          Maximum Voltage: 1.2 V
          Configured Voltage: 1.2 V

  Handle 0x003A, DMI type 17, 84 bytes
  Memory Device
          Array Handle: 0x0023
          Error Information Handle: 0x0039
          Total Width: 72 bits
          Data Width: 64 bits
          Size: 32 GB
          Form Factor: DIMM
          Set: None
          Locator: DIMMF1
          Bank Locator: P0_Node0_Channel5_Dimm0
          Type: DDR4
          Type Detail: Synchronous Registered (Buffered)
          Speed: 3200 MT/s
          Manufacturer: SK Hynix
          Serial Number: 431E9206
          Asset Tag: P1-DIMMF1_AssetTag (date:19/00)
          Part Number: HMA84GR7CJR4N-XN
          Rank: 2
          Configured Clock Speed: 3200 MT/s
          Minimum Voltage: 1.2 V
          Maximum Voltage: 1.2 V
          Configured Voltage: 1.2 V

  Handle 0x003D, DMI type 17, 84 bytes
  Memory Device
          Array Handle: 0x0023
          Error Information Handle: 0x003C
          Total Width: 72 bits
          Data Width: 64 bits
          Size: 32 GB
          Form Factor: DIMM
          Set: None
          Locator: DIMMG1
          Bank Locator: P0_Node0_Channel6_Dimm0
          Type: DDR4
          Type Detail: Synchronous Registered (Buffered)
          Speed: 3200 MT/s
          Manufacturer: SK Hynix
          Serial Number: 431E9207
          Asset Tag: P1-DIMMG1_AssetTag (date:19/00)
          Part Number: HMA84GR7CJR4N-XN
          Rank: 2
          Configured Clock Speed: 3200 MT/s
          Minimum Voltage: 1.2 V
          Maximum Voltage: 1.2 V
          Configured Voltage: 1.2 V

  Handle 0x0040, DMI type 17, 84 bytes
  Memory Device
          Array Handle: 0x0023
          Error Information Handle: 0x003F
          Total Width: 72 bits
          Data Width: 64 bits
          Size: 32 GB
          Form Factor: DIMM
          Set: None
          Locator: DIMMH1
          Bank Locator: P0_Node0_Channel7_Dimm0
          Type: DDR4
          Type Detail: Synchronous Registered (Buffered)
          Speed: 3200 MT/s
          Manufacturer: SK Hynix
          Serial Number: 431E9209
          Asset Tag: P1-DIMMH1_AssetTag (date:19/00)
          Part Number: HMA84GR7CJR4N-XN
          Rank: 2
          Configured Clock Speed: 3200 MT/s
          Minimum Voltage: 1.2 V
          Maximum Voltage: 1.2 V
          Configured Voltage: 1.2 V
```

## EPYC zn2 Server BIOS Configuration - TG

### Boot Feature

```
  |  Quiet Boot                                [Enabled]               |Boot option                  |
  |                                                                    |                             |
  |  Option ROM Messages                       [Force BIOS]            |                             |
  |  Bootup NumLock State                      [On]                    |                             |
  |  Wait For "F1" If Error                    [Enabled]               |                             |
  |  INT19 Trap Response                       [Immediate]             |                             |
  |  Re-try Boot                               [Disabled]              |                             |
  |                                                                    |                             |
  |  Power Configuration                                               |                             |
  |  Watch Dog Function                        [Disabled]              |                             |
  |  Restore on AC Power Loss                  [Last State]            |                             |
  |  Power Button Function                     [Instant Off]           |                             |
```

### CPU Configuration

```
  |  ACPI Settings                                                    ^|                             |
  |  --------------------------------------------------               *|                             |
  |  PCI AER Support                           [Disabled]             *|                             |
  |  High Precision Event Timer                [Disabled]             *|                             |
  |  NUMA Nodes Per Socket                     [NPS2]                 *|                             |
  |  ACPI SRAT L3 Cache As NUMA Domain         [Auto]                 *|                             |
  |                                                                   *|                             |
  |  CPU Configuration                                                ^|                             |
  |  --------------------------------------------------               *|                             |
  |  SMT Control                               [Auto]                 *|                             |
  |  Core Performance Boost                    [Auto]                 *|                             |
  |  Global C-state control                    [Disabled]             *|                             |
  |  Local APIC Mode                           [Auto]                 *|                             |
  |  CCD Control                               [Auto]                 *|                             |
  |  Core Control                              [Auto]                 *|                             |
  |  Core Control                              [Auto]                 *|                             |
  |  L1 Stream HW Prefetcher                   [Enabled]              *|                             |
  |  L2 Stream HW Prefetcher                   [Enabled]              *|                             |
  |  SVM Mode                                  [Enabled]              *|                             |
  |  SMEE                                      [Disabled]             *|                             |
  |                                                                   *|                             |
  |> CPU1 Information                                                 *|                             |
  |                                                                   *|                             |
  |  NB Configuration                                                 ^|                             |
  |  --------------------------------------------------               *|                             |
  |  Determinism Control                       [Manual]               *|                             |
  |  Determinism Slider                        [Performance]          *|                             |
  |  cTDP Control                              [Disabled]             *|                             |
  |  IOMMU                                     [Disabled]             *|                             |
  |  ACS Enable                                [Auto]                 *|                             |
  |  Package Power Limit Control               [Auto]                 *|                             |
  |  APBDIS                                    [1]                    *|                             |
  |  Fixed SOC Pstate                          [P0]                   *|                             |
  |  DF Cstates                                [Enabled]              *|                             |
  |  Preferred IO                              [Manual]               *|                             |
  |  Preferred IO Bus                          [##]                   *|                             |
  |                                                                   *|                             |
  |                                                                   *|-----------------------------|
  |                                                                   *|><: Select Screen            |
  |                                                                   *|^v: Select Item              |
  |                                                                   *|Enter: Select                |
  |                                                                   +|+/-: Change Opt.             |
  |                                                                   +|F1: General Help             |
  |                                                                   +|F2: Previous Values          |
  |                                                                   +|F3: Optimized Defaults       |
  |                                                                   v|F4: Save & Exit              |
  |                                                                    |                             |
```


## EPYC zn2 Server BIOS Configuration - DUT

### Boot Feature

```
  |  Quiet Boot                                [Enabled]               |Boot option                  |
  |                                                                    |                             |
  |  Option ROM Messages                       [Force BIOS]            |                             |
  |  Bootup NumLock State                      [On]                    |                             |
  |  Wait For "F1" If Error                    [Enabled]               |                             |
  |  INT19 Trap Response                       [Immediate]             |                             |
  |  Re-try Boot                               [Disabled]              |                             |
  |                                                                    |                             |
  |  Power Configuration                                               |                             |
  |  Watch Dog Function                        [Disabled]              |                             |
  |  Restore on AC Power Loss                  [Last State]            |                             |
  |  Power Button Function                     [Instant Off]           |                             |
```

### CPU Configuration

```
  |  ACPI Settings                                                    ^|                             |
  |  --------------------------------------------------               *|                             |
  |  PCI AER Support                           [Disabled]             *|                             |
  |  High Precision Event Timer                [Disabled]             *|                             |
  |  NUMA Nodes Per Socket                     [NPS2]                 *|                             |
  |  ACPI SRAT L3 Cache As NUMA Domain         [Auto]                 *|                             |
  |                                                                   *|                             |
  |  CPU Configuration                                                ^|                             |
  |  --------------------------------------------------               *|                             |
  |  SMT Control                               [Auto]                 *|                             |
  |  Core Performance Boost                    [Auto]                 *|                             |
  |  Global C-state control                    [Disabled]             *|                             |
  |  Local APIC Mode                           [Auto]                 *|                             |
  |  CCD Control                               [Auto]                 *|                             |
  |  Core Control                              [Auto]                 *|                             |
  |  Core Control                              [Auto]                 *|                             |
  |  L1 Stream HW Prefetcher                   [Enabled]              *|                             |
  |  L2 Stream HW Prefetcher                   [Enabled]              *|                             |
  |  SVM Mode                                  [Enabled]              *|                             |
  |  SMEE                                      [Disabled]             *|                             |
  |                                                                   *|                             |
  |> CPU1 Information                                                 *|                             |
  |                                                                   *|                             |
  |  NB Configuration                                                 ^|                             |
  |  --------------------------------------------------               *|                             |
  |  Determinism Control                       [Manual]               *|                             |
  |  Determinism Slider                        [Performance]          *|                             |
  |  cTDP Control                              [Disabled]             *|                             |
  |  IOMMU                                     [Disabled]             *|                             |
  |  ACS Enable                                [Auto]                 *|                             |
  |  Package Power Limit Control               [Auto]                 *|                             |
  |  APBDIS                                    [1]                    *|                             |
  |  Fixed SOC Pstate                          [P0]                   *|                             |
  |  DF Cstates                                [Enabled]              *|                             |
  |  Preferred IO                              [Manual]               *|                             |
  |  Preferred IO Bus                          [##]                   *|                             |
  |                                                                   *|                             |
  |                                                                   *|-----------------------------|
  |                                                                   *|><: Select Screen            |
  |                                                                   *|^v: Select Item              |
  |                                                                   *|Enter: Select                |
  |                                                                   +|+/-: Change Opt.             |
  |                                                                   +|F1: General Help             |
  |                                                                   +|F2: Previous Values          |
  |                                                                   +|F3: Optimized Defaults       |
  |                                                                   v|F4: Save & Exit              |
  |                                                                    |                             |
```


## EPYC zn2 Server Firmware Inventory

```
Host.           IPMI IP.      BMC.       BIOS.  CPLD.      CPU Microcode.  PCI Bus.  X710 Firmware.             XXV710 Firmware.           i40e.      MLX5 Firmware.  mlx5_core
s60-t210-sut1.  10.30.55.24.  03.10.04.  1.1a.  02.c2.00.  0x8301038.      ?.        8.30 0x8000a4c7 1.2074.0.  8.30 0x8000a485 1.2926.0.  2.17.15.   16.32.1010.     5.3-1.0.5.0.
s61-t210-tg1.   10.30.55.25.  03.10.04.  1.1a.  02.c2.00.  0x8301038.      ?.        8.00 0x80008c1a 1.2007.0.  8.00 0x80008ba1 1.2007.0.  2.14.13.   16.32.1010.     5.5-1.0.3.2.
```