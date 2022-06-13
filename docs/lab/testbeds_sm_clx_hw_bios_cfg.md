# SuperMicro Cascadelake Servers - HW and BIOS Configuration

1. [Linux lscpu](#linux-lscpu)
1. [Linux dmidecode](#dmidecode)
1. [Linux dmidecode pci](#linux-dmidecode-pci)
1. [Linux dmidecode memory](#linux-dmidecode-memory)
1. [Xeon Clx Server BIOS Configuration](#xeon-clx-server-bios-configuration)
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
1. [Xeon Clx Server Firmware Inventory](#xeon-clx-server-firmware-inventory)

## Linux lscpu

```
$ lscpu
Architecture:        x86_64
CPU op-mode(s):      32-bit, 64-bit
Byte Order:          Little Endian
CPU(s):              112
On-line CPU(s) list: 0-111
Thread(s) per core:  2
Core(s) per socket:  28
Socket(s):           2
NUMA node(s):        2
Vendor ID:           GenuineIntel
CPU family:          6
Model:               85
Model name:          Intel(R) Xeon(R) Platinum 8280 CPU @ 2.70GHz
Stepping:            7
CPU MHz:             3299.609
BogoMIPS:            5400.00
Virtualization:      VT-x
L1d cache:           32K
L1i cache:           32K
L2 cache:            1024K
L3 cache:            39424K
NUMA node0 CPU(s):   0-27,56-83
NUMA node1 CPU(s):   28-55,84-111
Flags:               fpu vme de pse tsc msr pae mce cx8 apic sep mtrr pge mca
cmov pat pse36 clflush dts acpi mmx fxsr sse sse2 ss ht tm pbe syscall nx
pdpe1gb rdtscp lm constant_tsc art arch_perfmon pebs bts rep_good nopl xtopology
nonstop_tsc cpuid aperfmperf pni pclmulqdq dtes64 monitor ds_cpl vmx smx est
tm2 ssse3 sdbg fma cx16 xtpr pdcm pcid dca sse4_1 sse4_2 x2apic movbe popcnt
tsc_deadline_timer aes xsave avx f16c rdrand lahf_lm abm 3dnowprefetch
cpuid_fault epb cat_l3 cdp_l3 invpcid_single ssbd mba ibrs ibpb stibp
ibrs_enhanced tpr_shadow vnmi flexpriority ept vpid fsgsbase tsc_adjust bmi1
hle avx2 smep bmi2 erms invpcid rtm cqm mpx rdt_a avx512f avx512dq rdseed adx
smap clflushopt clwb intel_pt avx512cd avx512bw avx512vl xsaveopt xsavec xgetbv1
xsaves cqm_llc cqm_occup_llc cqm_mbm_total cqm_mbm_local dtherm ida arat pln pts
pku ospke avx512_vnni md_clear flush_l1d arch_capabilities
```

```
$ lscpu
Architecture:        x86_64
CPU op-mode(s):      32-bit, 64-bit
Byte Order:          Little Endian
CPU(s):              96
On-line CPU(s) list: 0-95
Thread(s) per core:  2
Core(s) per socket:  24
Socket(s):           2
NUMA node(s):        2
Vendor ID:           GenuineIntel
CPU family:          6
Model:               85
Model name:          Intel(R) Xeon(R) Gold 6252N CPU @ 2.30GHz
Stepping:            7
CPU MHz:             3000.989
BogoMIPS:            4600.00
Virtualization:      VT-x
L1d cache:           32K
L1i cache:           32K
L2 cache:            1024K
L3 cache:            36608K
NUMA node0 CPU(s):   0-23,48-71
NUMA node1 CPU(s):   24-47,72-95
Flags:               fpu vme de pse tsc msr pae mce cx8 apic sep mtrr pge mca
cmov pat pse36 clflush dts acpi mmx fxsr sse sse2 ss ht tm pbe syscall nx
pdpe1gb rdtscp lm constant_tsc art arch_perfmon pebs bts rep_good nopl xtopology
nonstop_tsc cpuid aperfmperf pni pclmulqdq dtes64 monitor ds_cpl vmx smx est tm2
ssse3 sdbg fma cx16 xtpr pdcm pcid dca sse4_1 sse4_2 x2apic movbe popcnt
tsc_deadline_timer aes xsave avx f16c rdrand lahf_lm abm 3dnowprefetch
cpuid_fault epb cat_l3 cdp_l3 invpcid_single ssbd mba ibrs ibpb stibp
ibrs_enhanced tpr_shadow vnmi flexpriority ept vpid fsgsbase tsc_adjust bmi1 hle
avx2 smep bmi2 erms invpcid rtm cqm mpx rdt_a avx512f avx512dq rdseed adx smap
clflushopt clwb intel_pt avx512cd avx512bw avx512vl xsaveopt xsavec xgetbv1
xsaves cqm_llc cqm_occup_llc cqm_mbm_total cqm_mbm_local dtherm ida arat pln pts
pku ospke avx512_vnni md_clear flush_l1d arch_capabilities
```

## Linux dmidecode

```
  # dmidecode 3.1
  Getting SMBIOS data from sysfs.
  SMBIOS 3.1.2 present.
  Table at 0x6EB92000.

  Handle 0x0000, DMI type 0, 26 bytes
  BIOS Information
          Vendor: American Megatrends Inc.
          Version: 3.0c
          Release Date: 03/27/2019
          Address: 0xF0000
          Runtime Size: 64 kB
          ROM Size: 32 MB
          Characteristics:
                  PCI is supported
                  BIOS is upgradeable
                  BIOS shadowing is allowed
                  Boot from CD is supported
                  Selectable boot is supported
                  BIOS ROM is socketed
                  EDD is supported
                  5.25"/1.2 MB floppy services are supported (int 13h)
                  3.5"/720 kB floppy services are supported (int 13h)
                  3.5"/2.88 MB floppy services are supported (int 13h)
                  Print screen service is supported (int 5h)
                  Serial services are supported (int 14h)
                  Printer services are supported (int 17h)
                  ACPI is supported
                  USB legacy is supported
                  BIOS boot specification is supported
                  Targeted content distribution is supported
                  UEFI is supported
          BIOS Revision: 5.14

  Handle 0x0001, DMI type 1, 27 bytes
  System Information
          Manufacturer: Supermicro
          Product Name: SYS-7049GP-TRT
          Version: 0123456789
          Serial Number: S291427X9525476
          UUID: 00000000-0000-0000-0000-AC1F6BACD7BA
          Wake-up Type: Power Switch
          SKU Number: To be filled by O.E.M.
          Family: To be filled by O.E.M.

  Handle 0x0002, DMI type 2, 15 bytes
  Base Board Information
          Manufacturer: Supermicro
          Product Name: X11DPG-QT
          Version: 1.10A
          Serial Number: VM189S007860
          Asset Tag: To be filled by O.E.M.
          Features:
                  Board is a hosting board
                  Board is replaceable
          Location In Chassis: To be filled by O.E.M.
          Chassis Handle: 0x0003
          Type: Motherboard
          Contained Object Handles: 0

  Handle 0x0003, DMI type 3, 22 bytes
  Chassis Information
          Manufacturer: Supermicro
          Type: Other
          Lock: Not Present
          Version: 0123456789
          Serial Number: C7470KH37A30566
          Asset Tag: To be filled by O.E.M.
          Boot-up State: Safe
          Power Supply State: Safe
          Thermal State: Safe
          Security Status: None
          OEM Information: 0x00000000
          Height: Unspecified
          Number Of Power Cords: 1
          Contained Elements: 0
          SKU Number: To be filled by O.E.M.

  Handle 0x0055, DMI type 4, 48 bytes
  Processor Information
          Socket Designation: CPU1
          Type: Central Processor
          Family: Xeon
          Manufacturer: Intel(R) Corporation
          ID: 57 06 05 00 FF FB EB BF
          Signature: Type 0, Family 6, Model 85, Stepping 7
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
                  DS (Debug store)
                  ACPI (ACPI supported)
                  MMX (MMX technology supported)
                  FXSR (FXSAVE and FXSTOR instructions supported)
                  SSE (Streaming SIMD extensions)
                  SSE2 (Streaming SIMD extensions 2)
                  SS (Self-snoop)
                  HTT (Multi-threading)
                  TM (Thermal monitor supported)
                  PBE (Pending break enabled)
          Version: Intel(R) Xeon(R) Gold 6252N CPU @ 2.30GHz
          Voltage: 1.6 V
          External Clock: 100 MHz
          Max Speed: 4500 MHz
          Current Speed: 2300 MHz
          Status: Populated, Enabled
          Upgrade: Socket LGA3647-1
          L1 Cache Handle: 0x0052
          L2 Cache Handle: 0x0053
          L3 Cache Handle: 0x0054
          Serial Number: Not Specified
          Asset Tag: UNKNOWN
          Part Number: Not Specified
          Core Count: 24
          Core Enabled: 24
          Thread Count: 48
          Characteristics:
                  64-bit capable
                  Multi-Core
                  Hardware Thread
                  Execute Protection
                  Enhanced Virtualization
                  Power/Performance Control

  Handle 0x0059, DMI type 4, 48 bytes
  Processor Information
          Socket Designation: CPU2
          Type: Central Processor
          Family: Xeon
          Manufacturer: Intel(R) Corporation
          ID: 57 06 05 00 FF FB EB BF
          Signature: Type 0, Family 6, Model 85, Stepping 7
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
                  DS (Debug store)
                  ACPI (ACPI supported)
                  MMX (MMX technology supported)
                  FXSR (FXSAVE and FXSTOR instructions supported)
                  SSE (Streaming SIMD extensions)
                  SSE2 (Streaming SIMD extensions 2)
                  SS (Self-snoop)
                  HTT (Multi-threading)
                  TM (Thermal monitor supported)
                  PBE (Pending break enabled)
          Version: Intel(R) Xeon(R) Gold 6252N CPU @ 2.30GHz
          Voltage: 1.6 V
          External Clock: 100 MHz
          Max Speed: 4500 MHz
          Current Speed: 2300 MHz
          Status: Populated, Enabled
          Upgrade: Socket LGA3647-1
          L1 Cache Handle: 0x0056
          L2 Cache Handle: 0x0057
          L3 Cache Handle: 0x0058
          Serial Number: Not Specified
          Asset Tag: UNKNOWN
          Part Number: Not Specified
          Core Count: 24
          Core Enabled: 24
          Thread Count: 48
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
  Handle 0x000B, DMI type 9, 17 bytes
  System Slot Information
        Designation: CPU1 SLOT2 PCI-E 3.0 X16
        Type: x16 PCI Express 3 x16
        Current Usage: In Use
        Length: Long
        ID: 2
        Characteristics:
                3.3 V is provided
                Opening is shared
                PME signal is supported
        Bus Address: 0000:18:00.0

  Handle 0x000C, DMI type 9, 17 bytes
  System Slot Information
        Designation: CPU1 SLOT4 PCI-E 3.0 X16
        Type: x16 PCI Express 3 x16
        Current Usage: In Use
        Length: Short
        ID: 4
        Characteristics:
                3.3 V is provided
                Opening is shared
                PME signal is supported
        Bus Address: 0000:3b:00.0

  Handle 0x000D, DMI type 9, 17 bytes
  System Slot Information
        Designation: CPU2 SLOT6 PCI-E 3.0 X16
        Type: x16 PCI Express 3 x16
        Current Usage: Available
        Length: Short
        ID: 6
        Characteristics:
                3.3 V is provided
                Opening is shared
                PME signal is supported
        Bus Address: 0000:ff:00.0

  Handle 0x000E, DMI type 9, 17 bytes
  System Slot Information
        Designation: CPU2 SLOT8 PCI-E 3.0 X16
        Type: x16 PCI Express 3 x16
        Current Usage: Available
        Length: Short
        ID: 8
        Characteristics:
                3.3 V is provided
                Opening is shared
                PME signal is supported
        Bus Address: 0000:ff:00.0

  Handle 0x000F, DMI type 9, 17 bytes
  System Slot Information
        Designation: CPU1 SLOT9 PCI-E 3.0 X16
        Type: x16 PCI Express 3 x16
        Current Usage: Available
        Length: Short
        ID: 9
        Characteristics:
                3.3 V is provided
                Opening is shared
                PME signal is supported
        Bus Address: 0000:ff:00.0

  Handle 0x0010, DMI type 9, 17 bytes
  System Slot Information
        Designation: CPU2 SLOT10 PCI-E 3.0 X16
        Type: x16 PCI Express 3 x16
        Current Usage: Available
        Length: Short
        ID: 10
        Characteristics:
                3.3 V is provided
                Opening is shared
                PME signal is supported
        Bus Address: 0000:ff:00.0

  Handle 0x0011, DMI type 9, 17 bytes
  System Slot Information
        Designation: CPU2 SLOT11 PCI-E 3.0 X4(IN X8)
        Type: x4 PCI Express 3 x8
        Current Usage: Available
        Length: Short
        ID: 11
        Characteristics:
                3.3 V is provided
                Opening is shared
                PME signal is supported
        Bus Address: 0000:ff:00.0

  Handle 0x0012, DMI type 9, 17 bytes
  System Slot Information
        Designation: M.2 CONNECTOR
        Type: x4 M.2 Socket 2
        Current Usage: Available
        Length: Short
        Characteristics:
                3.3 V is provided
                Opening is shared
                PME signal is supported
        Bus Address: 0000:ff:00.0
```

## Linux dmidecode memory

```
  $ dmidecode -t memory
  Handle 0x0021, DMI type 16, 23 bytes
  Physical Memory Array
	Location: System Board Or Motherboard
	Use: System Memory
	Error Correction Type: Single-bit ECC
	Maximum Capacity: 2304 GB
	Error Information Handle: Not Provided
	Number Of Devices: 4

  Handle 0x0023, DMI type 17, 84 bytes
  Memory Device
	Array Handle: 0x0021
	Error Information Handle: Not Provided
	Total Width: 72 bits
	Data Width: 64 bits
	Size: 16384 MB
	Form Factor: DIMM
	Set: None
	Locator: P1-DIMMA1
	Bank Locator: P0_Node0_Channel0_Dimm0
	Type: DDR4
	Type Detail: Synchronous
	Speed: 2933 MT/s
	Manufacturer: SK Hynix
	Serial Number: 93275F0E
	Asset Tag: P1-DIMMA1_AssetTag (date:19/22)
	Part Number: HMA82GR7CJR8N-WM
	Rank: 2
	Configured Clock Speed: 2934 MT/s
	Minimum Voltage: 1.2 V
	Maximum Voltage: 1.2 V
	Configured Voltage: 1.2 V

  Handle 0x0024, DMI type 17, 84 bytes
  Memory Device
	Array Handle: 0x0021
	Error Information Handle: Not Provided
	Total Width: Unknown
	Data Width: Unknown
	Size: No Module Installed
	Form Factor: DIMM
	Set: None
	Locator: P1-DIMMA2
	Bank Locator: P0_Node0_Channel0_Dimm1
	Type: Unknown
	Type Detail: Unknown
	Speed: Unknown
	Manufacturer: NO DIMM
	Serial Number: NO DIMM
	Asset Tag: NO DIMM
	Part Number: NO DIMM
	Rank: Unknown
	Configured Clock Speed: Unknown
	Minimum Voltage: 1.2 V
	Maximum Voltage: 1.2 V
	Configured Voltage: 1.2 V

  Handle 0x0025, DMI type 17, 84 bytes
  Memory Device
	Array Handle: 0x0021
	Error Information Handle: Not Provided
	Total Width: 72 bits
	Data Width: 64 bits
	Size: 16384 MB
	Form Factor: DIMM
	Set: None
	Locator: P1-DIMMB1
	Bank Locator: P0_Node0_Channel1_Dimm0
	Type: DDR4
	Type Detail: Synchronous
	Speed: 2933 MT/s
	Manufacturer: SK Hynix
	Serial Number: 93275F1F
	Asset Tag: P1-DIMMB1_AssetTag (date:19/22)
	Part Number: HMA82GR7CJR8N-WM
	Rank: 2
	Configured Clock Speed: 2934 MT/s
	Minimum Voltage: 1.2 V
	Maximum Voltage: 1.2 V
	Configured Voltage: 1.2 V

  Handle 0x0027, DMI type 17, 84 bytes
  Memory Device
	Array Handle: 0x0021
	Error Information Handle: Not Provided
	Total Width: 72 bits
	Data Width: 64 bits
	Size: 16384 MB
	Form Factor: DIMM
	Set: None
	Locator: P1-DIMMC1
	Bank Locator: P0_Node0_Channel2_Dimm0
	Type: DDR4
	Type Detail: Synchronous
	Speed: 2933 MT/s
	Manufacturer: SK Hynix
	Serial Number: 93275F07
	Asset Tag: P1-DIMMC1_AssetTag (date:19/22)
	Part Number: HMA82GR7CJR8N-WM
	Rank: 2
	Configured Clock Speed: 2934 MT/s
	Minimum Voltage: 1.2 V
	Maximum Voltage: 1.2 V
	Configured Voltage: 1.2 V

  Handle 0x002B, DMI type 17, 84 bytes
  Memory Device
	Array Handle: 0x0029
	Error Information Handle: Not Provided
	Total Width: 72 bits
	Data Width: 64 bits
	Size: 16384 MB
	Form Factor: DIMM
	Set: None
	Locator: P1-DIMMD1
	Bank Locator: P0_Node1_Channel0_Dimm0
	Type: DDR4
	Type Detail: Synchronous
	Speed: 2933 MT/s
	Manufacturer: SK Hynix
	Serial Number: 93275F02
	Asset Tag: P1-DIMMD1_AssetTag (date:19/22)
	Part Number: HMA82GR7CJR8N-WM
	Rank: 2
	Configured Clock Speed: 2934 MT/s
	Minimum Voltage: 1.2 V
	Maximum Voltage: 1.2 V
	Configured Voltage: 1.2 V

  Handle 0x002C, DMI type 17, 84 bytes
  Memory Device
	Array Handle: 0x0029
	Error Information Handle: Not Provided
	Total Width: Unknown
	Data Width: Unknown
	Size: No Module Installed
	Form Factor: DIMM
	Set: None
	Locator: P1-DIMMD2
	Bank Locator: P0_Node1_Channel0_Dimm1
	Type: Unknown
	Type Detail: Unknown
	Speed: Unknown
	Manufacturer: NO DIMM
	Serial Number: NO DIMM
	Asset Tag: NO DIMM
	Part Number: NO DIMM
	Rank: Unknown
	Configured Clock Speed: Unknown
	Minimum Voltage: 1.2 V
	Maximum Voltage: 1.2 V
	Configured Voltage: 1.2 V

  Handle 0x002D, DMI type 17, 84 bytes
  Memory Device
	Array Handle: 0x0029
	Error Information Handle: Not Provided
	Total Width: 72 bits
	Data Width: 64 bits
	Size: 16384 MB
	Form Factor: DIMM
	Set: None
	Locator: P1-DIMME1
	Bank Locator: P0_Node1_Channel1_Dimm0
	Type: DDR4
	Type Detail: Synchronous
	Speed: 2933 MT/s
	Manufacturer: SK Hynix
	Serial Number: 93275F19
	Asset Tag: P1-DIMME1_AssetTag (date:19/22)
	Part Number: HMA82GR7CJR8N-WM
	Rank: 2
	Configured Clock Speed: 2934 MT/s
	Minimum Voltage: 1.2 V
	Maximum Voltage: 1.2 V
	Configured Voltage: 1.2 V

  Handle 0x002F, DMI type 17, 84 bytes
  Memory Device
	Array Handle: 0x0029
	Error Information Handle: Not Provided
	Total Width: 72 bits
	Data Width: 64 bits
	Size: 16384 MB
	Form Factor: DIMM
	Set: None
	Locator: P1-DIMMF1
	Bank Locator: P0_Node1_Channel2_Dimm0
	Type: DDR4
	Type Detail: Synchronous
	Speed: 2933 MT/s
	Manufacturer: SK Hynix
	Serial Number: 93275FD3
	Asset Tag: P1-DIMMF1_AssetTag (date:19/22)
	Part Number: HMA82GR7CJR8N-WM
	Rank: 2
	Configured Clock Speed: 2934 MT/s
	Minimum Voltage: 1.2 V
	Maximum Voltage: 1.2 V
	Configured Voltage: 1.2 V

  Handle 0x0031, DMI type 16, 23 bytes
  Physical Memory Array
	Location: System Board Or Motherboard
	Use: System Memory
	Error Correction Type: Single-bit ECC
	Maximum Capacity: 2304 GB
	Error Information Handle: Not Provided
	Number Of Devices: 4

  Handle 0x0033, DMI type 17, 84 bytes
  Memory Device
	Array Handle: 0x0031
	Error Information Handle: Not Provided
	Total Width: 72 bits
	Data Width: 64 bits
	Size: 16384 MB
	Form Factor: DIMM
	Set: None
	Locator: P2-DIMMA1
	Bank Locator: P1_Node0_Channel0_Dimm0
	Type: DDR4
	Type Detail: Synchronous
	Speed: 2933 MT/s
	Manufacturer: SK Hynix
	Serial Number: 93275FE2
	Asset Tag: P2-DIMMA1_AssetTag (date:19/22)
	Part Number: HMA82GR7CJR8N-WM
	Rank: 2
	Configured Clock Speed: 2934 MT/s
	Minimum Voltage: 1.2 V
	Maximum Voltage: 1.2 V
	Configured Voltage: 1.2 V

  Handle 0x0034, DMI type 17, 84 bytes
  Memory Device
	Array Handle: 0x0031
	Error Information Handle: Not Provided
	Total Width: Unknown
	Data Width: Unknown
	Size: No Module Installed
	Form Factor: DIMM
	Set: None
	Locator: P2-DIMMA2
	Bank Locator: P1_Node0_Channel0_Dimm1
	Type: Unknown
	Type Detail: Unknown
	Speed: Unknown
	Manufacturer: NO DIMM
	Serial Number: NO DIMM
	Asset Tag: NO DIMM
	Part Number: NO DIMM
	Rank: Unknown
	Configured Clock Speed: Unknown
	Minimum Voltage: 1.2 V
	Maximum Voltage: 1.2 V
	Configured Voltage: 1.2 V

  Handle 0x0035, DMI type 17, 84 bytes
  Memory Device
	Array Handle: 0x0031
	Error Information Handle: Not Provided
	Total Width: 72 bits
	Data Width: 64 bits
	Size: 16384 MB
	Form Factor: DIMM
	Set: None
	Locator: P2-DIMMB1
	Bank Locator: P1_Node0_Channel1_Dimm0
	Type: DDR4
	Type Detail: Synchronous
	Speed: 2933 MT/s
	Manufacturer: SK Hynix
	Serial Number: 93276001
	Asset Tag: P2-DIMMB1_AssetTag (date:19/22)
	Part Number: HMA82GR7CJR8N-WM
	Rank: 2
	Configured Clock Speed: 2934 MT/s
	Minimum Voltage: 1.2 V
	Maximum Voltage: 1.2 V
	Configured Voltage: 1.2 V

  Handle 0x0037, DMI type 17, 84 bytes
  Memory Device
	Array Handle: 0x0031
	Error Information Handle: Not Provided
	Total Width: 72 bits
	Data Width: 64 bits
	Size: 16384 MB
	Form Factor: DIMM
	Set: None
	Locator: P2-DIMMC1
	Bank Locator: P1_Node0_Channel2_Dimm0
	Type: DDR4
	Type Detail: Synchronous
	Speed: 2933 MT/s
	Manufacturer: SK Hynix
	Serial Number: 93276005
	Asset Tag: P2-DIMMC1_AssetTag (date:19/22)
	Part Number: HMA82GR7CJR8N-WM
	Rank: 2
	Configured Clock Speed: 2934 MT/s
	Minimum Voltage: 1.2 V
	Maximum Voltage: 1.2 V
	Configured Voltage: 1.2 V

  Handle 0x0039, DMI type 16, 23 bytes
  Physical Memory Array
	Location: System Board Or Motherboard
	Use: System Memory
	Error Correction Type: Single-bit ECC
	Maximum Capacity: 2304 GB
	Error Information Handle: Not Provided
	Number Of Devices: 4

  Handle 0x003B, DMI type 17, 84 bytes
  Memory Device
	Array Handle: 0x0039
	Error Information Handle: Not Provided
	Total Width: 72 bits
	Data Width: 64 bits
	Size: 16384 MB
	Form Factor: DIMM
	Set: None
	Locator: P2-DIMMD1
	Bank Locator: P1_Node1_Channel0_Dimm0
	Type: DDR4
	Type Detail: Synchronous
	Speed: 2933 MT/s
	Manufacturer: SK Hynix
	Serial Number: 93275F44
	Asset Tag: P2-DIMMD1_AssetTag (date:19/22)
	Part Number: HMA82GR7CJR8N-WM
	Rank: 2
	Configured Clock Speed: 2934 MT/s
	Minimum Voltage: 1.2 V
	Maximum Voltage: 1.2 V
	Configured Voltage: 1.2 V

  Handle 0x003C, DMI type 17, 84 bytes
  Memory Device
	Array Handle: 0x0039
	Error Information Handle: Not Provided
	Total Width: Unknown
	Data Width: Unknown
	Size: No Module Installed
	Form Factor: DIMM
	Set: None
	Locator: P2-DIMMD2
	Bank Locator: P1_Node1_Channel0_Dimm1
	Type: Unknown
	Type Detail: Unknown
	Speed: Unknown
	Manufacturer: NO DIMM
	Serial Number: NO DIMM
	Asset Tag: NO DIMM
	Part Number: NO DIMM
	Rank: Unknown
	Configured Clock Speed: Unknown
	Minimum Voltage: 1.2 V
	Maximum Voltage: 1.2 V
	Configured Voltage: 1.2 V

  Handle 0x003D, DMI type 17, 84 bytes
  Memory Device
	Array Handle: 0x0039
	Error Information Handle: Not Provided
	Total Width: 72 bits
	Data Width: 64 bits
	Size: 16384 MB
	Form Factor: DIMM
	Set: None
	Locator: P2-DIMME1
	Bank Locator: P1_Node1_Channel1_Dimm0
	Type: DDR4
	Type Detail: Synchronous
	Speed: 2933 MT/s
	Manufacturer: SK Hynix
	Serial Number: 93275FDF
	Asset Tag: P2-DIMME1_AssetTag (date:19/22)
	Part Number: HMA82GR7CJR8N-WM
	Rank: 2
	Configured Clock Speed: 2934 MT/s
	Minimum Voltage: 1.2 V
	Maximum Voltage: 1.2 V
	Configured Voltage: 1.2 V

  Handle 0x003F, DMI type 17, 84 bytes
  Memory Device
	Array Handle: 0x0039
	Error Information Handle: Not Provided
	Total Width: 72 bits
	Data Width: 64 bits
	Size: 16384 MB
	Form Factor: DIMM
	Set: None
	Locator: P2-DIMMF1
	Bank Locator: P1_Node1_Channel2_Dimm0
	Type: DDR4
	Type Detail: Synchronous
	Speed: 2933 MT/s
	Manufacturer: SK Hynix
	Serial Number: 93275FDD
	Asset Tag: P2-DIMMF1_AssetTag (date:19/22)
	Part Number: HMA82GR7CJR8N-WM
	Rank: 2
	Configured Clock Speed: 2934 MT/s
	Minimum Voltage: 1.2 V
	Maximum Voltage: 1.2 V
	Configured Voltage: 1.2 V
```

## Xeon CLX Server BIOS Configuration - TG

### Boot Feature

```
  |  Quiet Boot                                [Enabled]               |Boot option                  |
  |                                                                    |                             |
  |  Option ROM Messages                       [Force BIOS]            |                             |
  |  Bootup NumLock State                      [On]                    |                             |
  |  Wait For "F1" If Error                    [Enabled]               |                             |
  |  INT19 Trap Response                       [Immediate]             |                             |
  |  Re-try Boot                               [Disabled]              |                             |
  |  Install Windows 7 USB support             [Disabled]              |                             |
  |  Port 61h Bit-4 Emulation                  [Disabled]              |                             |
  |                                                                    |                             |
  |  Power Configuration                                               |                             |
  |  Watch Dog Function                        [Disabled]              |                             |
  |  Restore on AC Power Loss                  [Last State]            |                             |
  |  Power Button Function                     [Instant Off]           |                             |
```

### CPU Configuration

```
  |  Processor Configuration                                          ^|Enables Hyper Threading      |
  |  --------------------------------------------------               *|(Software Method to          |
  |  Processor BSP Revision                    50657 - CLX B1         *|Enable/Disable Logical       |
  |  Processor Socket                          CPU1      |  CPU2      *|Processor threads.           |
  |  Processor ID                              00050657* |  00050657  *|                             |
  |  Processor Frequency                       2.700GHz  |  2.700GHz  *|                             |
  |  Processor Max Ratio                            1BH  |  1BH       *|                             |
  |  Processor Min Ratio                            0AH  |  0AH       *|                             |
  |  Microcode Revision                        0500002C  |  0500002C  *|                             |
  |  L1 Cache RAM                                  64KB  |      64KB  *|                             |
  |  L2 Cache RAM                                1024KB  |    1024KB  *|                             |
  |  L3 Cache RAM                               39424KB  |   39424KB  *|                             |
  |  Processor 0 Version                                              *|                             |
  |  Intel(R) Xeon(R) Platinum 8280 CPU @ 2.70GHz                     *|                             |
  |  Processor 1 Version                                              *|                             |
  |  Intel(R) Xeon(R) Platinum 8280 CPU @ 2.70GHz                     *|                             |
  |                                                                   *|-----------------------------|
  |  Hyper-Threading [ALL]                     [Enable]               *|><: Select Screen            |
  |  Cores Enabled                             0                      *|^v: Select Item              |
  |  Monitor/Mwait                             [Auto]                 *|Enter: Select                |
  |  Execute Disable Bit                       [Enable]               +|+/-: Change Opt.             |
  |  Intel Virtualization Technology           [Enable]               +|F1: General Help             |
  |  PPIN Control                              [Unlock/Enable]        +|F2: Previous Values          |
  |  Hardware Prefetcher                       [Enable]               +|F3: Optimized Defaults       |
  |  Adjacent Cache Prefetch                   [Enable]               v|F4: Save & Exit              |
  |  DCU Streamer Prefetcher                   [Enable]                |                             |
  |  DCU IP Prefetcher                         [Enable]                |                             |
  |  LLC Prefetch                              [Disable]               |                             |
  |  Extended APIC                             [Disable]               |                             |
  |  AES-NI                                    [Enable]                |                             |
  |> Advanced Power Management Configuration                           |                             |
```

#### Advanced Power Management Configuration

```
  |  Advanced Power Management Configuration                           |Switch CPU Power Management  |
  |  --------------------------------------------------                |profile                      |
  |  Power Technology                          [Custom]                |                             |
  |  Power Performance Tuning                  [BIOS Controls EPB]     |                             |
  |  ENERGY_PERF_BIAS_CFG mode                 [Maximum Performance]   |                             |
  |> CPU P State Control                                               |                             |
  |> Hardware PM State Control                                         |                             |
  |> CPU C State Control                                               |                             |
  |> Package C State Control                                           |                             |
  |> CPU T State Control                                               |                             |
```

##### CPU P State Control

```
  |  CPU P State Control                                               |EIST allows the processor    |
  |                                                                    |to dynamically adjust        |
  |  SpeedStep (P-States)                      [Disable]               |frequency and voltage based  |
  |  EIST PSD Function                         [HW_ALL]                |on power versus performance  |
  |                                                                    |needs.                       |
  |                                                                    |                             |
```

##### Hardware PM State Control

```
  |  Hardware PM State Control                                         |If set to Disable, hardware ^|
  |                                                                    |will choose a P-state       *|
  |  Hardware P-States                         [Disable]               |setting for the system      *|
  |                                                                    |based on an OS request.     *|
  |                                                                    |If set to Native Mode,      *|
  |                                                                    |hardware will choose a      *|
  |                                                                    |P-state setting based on OS *|
  |                                                                    |guidance.                   *|
  |                                                                    |If set to Native Mode with  *|
  |                                                                    |No Legacy Support, hardware *|
  |                                                                    |will choose a P-state       *|
  |                                                                    |setting independently       *|
  |                                                                    |without OS guidance.        +|
  |                                                                    |If set to Out of Band Mode, +|
  |                                                                    |hardware autonomously       v|
```

##### CPU C State Control

```
  |  CPU C State Control                                               |Select Enable to support     |
  |                                                                    |Autonomous Core C-State      |
  |  Autonomous Core C-State                   [Disable]               |control which will allow     |
  |  CPU C6 report                             [Disable]               |the processor core to        |
  |  Enhanced Halt State (C1E)                 [Disable]               |control its C-State setting  |
  |                                                                    |automatically and            |
  |                                                                    |independently.               |
```

##### Package C State Control

```
  |  Package C State Control                                           |Limit the lowest package     |
  |                                                                    |level C-State to             |
  |  Package C State                           [C0/C1 state]           |processors. Lower package    |
  |                                                                    |C-State lower processor      |
  |                                                                    |power consumption upon idle. |
```

##### CPU T State Control

```
  |  CPU T State Control                                               |Enable/Disable CPU           |
  |                                                                    |throttling by OS.            |
  |  Software Controlled T-States              [Disable]               |Throttling reduces power     |
  |                                                                    |consumption                  |
```

#### Chipset Configuration

```
  |  WARNING: Setting wrong values in below sections may cause         |North Bridge Parameters      |
  |           system to malfunction.                                   |                             |
  |> North Bridge                                                      |                             |
  |> South Bridge                                                      |                             |
```

##### North Bridge

```
  |> UPI Configuration                                                 |Displays and provides        |
  |> Memory Configuration                                              |option to change the UPI     |
  |> IIO Configuration                                                 |Settings                     |
```

##### UPI Configuration

```
  |  UPI Configuration                                                 |Use this feature to select   |
  |  --------------------------------------------------                |the degrading precedence     |
  |  Number of CPU                             2                       |option for Ultra Path        |
  |  Number of Active UPI Link                 3                       |Interconnect connections.    |
  |  Current UPI Link Speed                    Fast                    |Select Topology Precedent    |
  |  Current UPI Link Frequency                10.4 GT/s               |to degrade UPI features if   |
  |  UPI Global MMIO Low Base / Limit          90000000 / FBFFFFFF     |system options are in        |
  |  UPI Global MMIO High Base / Limit         0000000000000000 /      |conflict. Select Feature     |
  |                                            00000000FFFFFFFF        |Precedent to degrade UPI     |
  |  UPI Pci-e Configuration Base / Size       80000000 / 10000000     |topology if system options   |
  |  Degrade Precedence                        [Topology Precedence]   |are in conflict.             |
  |  Link L0p Enable                           [Disable]               |                             |
  |  Link L1 Enable                            [Disable]               |                             |
  |  IO Directory Cache (IODC)                 [Auto]                  |                             |
  |  SNC                                       [Disable]               |                             |
  |  XPT Prefetch                              [Disable]               |                             |
  |  KTI Prefetch                              [Enable]                |-----------------------------|
  |  Local/Remote Threshold                    [Auto]                  |><: Select Screen            |
  |  Stale AtoS                                [Auto]                  |^v: Select Item              |
  |  LLC Dead Line Alloc                       [Enable]                |Enter: Select                |
  |  Isoc Mode                                 [Auto]                  |+/-: Change Opt.             |
```

##### Memory Configuration

```
  |                                                                    |Select POR to enforce POR    |
  |  --------------------------------------------------                |restrictions for DDR4        |
  |  Integrated Memory Controller (iMC)                                |frequency and voltage        |
  |  --------------------------------------------------                |programming                  |
  |                                                                    |                             |
  |  Enforce POR                               [POR]                   |                             |
  |  PPR Type                                  [Hard PPR]              |                             |
  |  Enhanced PPR                              [Disable]               |                             |
  |   Operation Mode                           [Test and Repair]       |                             |
  |  Memory Frequency                          [2933]                  |                             |
  |  Data Scrambling for DDR4                  [Auto]                  |                             |
  |  tCCD_L Relaxation                         [Auto]                  |                             |
  |  tRWSR Relaxation                          [Disable]               |                             |
  |  tRFC Optimization for 16Gb Based DIMM     [Force 550ns]           |                             |
  |  2x Refresh                                [Auto]                  |                             |
  |  Page Policy                               [Auto]                  |                             |
  |  IMC Interleaving                          [2-way Interleave]      |-----------------------------|
  |> Memory Topology                                                   |><: Select Screen            |
  |> Memory RAS Configuration                                          |^v: Select Item              |
```

##### IIO Configuration

```
  |  IIO Configuration                                                 |Expose IIO DFX devices and   |
  |  --------------------------------------------------                |other CPU devices like PMON  |
  |                                                                    |                             |
  |  EV DFX Features                           [Disable]               |                             |
  |> CPU1 Configuration                                                |                             |
  |> CPU2 Configuration                                                |                             |
  |> IOAT Configuration                                                |                             |
  |> Intel. VT for Directed I/O (VT-d)                                 |                             |
  |> Intel. VMD technology                                             |                             |
  |                                                                    |                             |
  |   IIO-PCIE Express Global Options                                  |                             |
  |  ========================================                          |                             |
  |  PCI-E Completion Timeout Disable          [No]                    |                             |
```

##### CPU1 Configuration

```
  |  IOU0 (IIO PCIe Br1)                       [Auto]                  |Selects PCIe port            |
  |  IOU1 (IIO PCIe Br2)                       [Auto]                  |Bifurcation for selected     |
  |  IOU2 (IIO PCIe Br3)                       [Auto]                  |slot(s)                      |
  |> CPU1 SLOT2 PCI-E 3.0 X16                                          |                             |
  |> CPU1 SLOT4 PCI-E 3.0 X16                                          |                             |
  |> CPU1 SLOT9 PCI-E 3.0 X16                                          |                             |
```

##### CPU2 Configuration

```
  |  IOU0 (IIO PCIe Br1)                       [Auto]                  |Selects PCIe port            |
  |  IOU1 (IIO PCIe Br2)                       [Auto]                  |Bifurcation for selected     |
  |  IOU2 (IIO PCIe Br3)                       [Auto]                  |slot(s)                      |
  |> CPU2 SLOT6 PCI-E 3.0 X16                                          |                             |
  |> CPU2 SLOT8 PCI-E 3.0 X16                                          |                             |
  |> CPU2 SLOT10 PCI-E 3.0 X16                                         |                             |
```

#### South Bridge

```
  |                                                                    |Enables Legacy USB support.  |
  |  USB Module Version                        21                      |AUTO option disables legacy  |
  |                                                                    |support if no USB devices    |
  |  USB Devices:                                                      |are connected. DISABLE       |
  |        1 Keyboard, 1 Mouse, 1 Hub                                  |option will keep USB         |
  |                                                                    |devices available only for   |
  |  Legacy USB Support                        [Enabled]               |EFI applications.            |
  |  XHCI Hand-off                             [Enabled]               |                             |
  |  Port 60/64 Emulation                      [Enabled]               |                             |
  |  PCIe PLL SSC                              [Disable]               |                             |
  |  Real USB Wake Up                          [Enabled]               |                             |
  |  Front USB Wake Up                         [Enabled]               |                             |
  |                                                                    |                             |
  |  Azalia                                    [Auto]                  |                             |
  |    Azalia PME Enable                       [Disabled]              |                             |
```

### PCIe/PCI/PnP Configuration

```
  |  PCI Bus Driver Version                    A5.01.18               ^|Enables or Disables 64bit    |
  |                                                                   *|capable Devices to be        |
  |  PCI Devices Common Settings:                                     *|Decoded in Above 4G Address  |
  |  Above 4G Decoding                         [Enabled]              *|Space (Only if System        |
  |  SR-IOV Support                            [Enabled]              *|Supports 64 bit PCI          |
  |  ARI Support                               [Enabled]              *|Decoding).                   |
  |  MMIO High Base                            [56T]                  *|                             |
  |  MMIO High Granularity Size                [256G]                 *|                             |
  |  Maximum Read Request                      [Auto]                 *|                             |
  |  MMCFG Base                                [2G]                   *|                             |
  |  NVMe Firmware Source                      [Vendor Defined        *|                             |
  |                                            Firmware]              *|                             |
  |  VGA Priority                              [Onboard]              *|                             |
  |  CPU1 SLOT2 PCI-E 3.0 X16 OPROM            [Legacy]               *|                             |
  |  CPU1 SLOT4 PCI-E 3.0 X16 OPROM            [Legacy]               *|                             |
  |  CPU2 SLOT6 PCI-E 3.0 X16 OPROM            [Legacy]               *|                             |
  |  CPU2 SLOT8 PCI-E 3.0 X16 OPROM            [Legacy]               *|-----------------------------|
  |  CPU1 SLOT9 PCI-E 3.0 X16 OPROM            [Legacy]               *|><: Select Screen            |
  |  CPU2 SLOT10 PCI-E 3.0 X16 OPROM           [Legacy]               *|^v: Select Item              |
  |  CPU2 SLOT11 PCI-E 3.0 X4(IN X8) OPROM     [Legacy]               *|Enter: Select                |
  |  M.2 CONNECTOR OPROM                       [Legacy]               *|+/-: Change Opt.             |
  |  Bus Master Enable                         [Enabled]              +|F1: General Help             |
  |  Onboard LAN1 Option ROM                   [Legacy]               +|F2: Previous Values          |
  |  Onboard LAN2 Option ROM                   [Disabled]             +|F3: Optimized Defaults       |
  |  Onboard Video Option ROM                  [Legacy]               v|F4: Save & Exit              |
  |> Network Stack Configuration                                       |                             |
```

### ACPI Settings

```
  |  ACPI Settings                                                     |Enable or Disable Non        |
  |                                                                    |uniform Memory Access        |
  |  NUMA                                      [Enabled]               |(NUMA).                      |
  |  WHEA Support                              [Enabled]               |                             |
  |  High Precision Event Timer                [Enabled]               |                             |
```

## Xeon CLX Server BIOS Configuration - DUT

### Boot Feature

```
  |  Quiet Boot                                [Enabled]               |Boot option                  |
  |                                                                    |                             |
  |  Option ROM Messages                       [Force BIOS]            |                             |
  |  Bootup NumLock State                      [On]                    |                             |
  |  Wait For "F1" If Error                    [Enabled]               |                             |
  |  INT19 Trap Response                       [Immediate]             |                             |
  |  Re-try Boot                               [Disabled]              |                             |
  |  Install Windows 7 USB support             [Disabled]              |                             |
  |  Port 61h Bit-4 Emulation                  [Disabled]              |                             |
  |                                                                    |                             |
  |  Power Configuration                                               |                             |
  |  Watch Dog Function                        [Disabled]              |                             |
  |  Restore on AC Power Loss                  [Last State]            |                             |
  |  Power Button Function                     [Instant Off]           |                             |
```

### CPU Configuration

```
  |--------------------------------------------------------------------+-----------------------------\
  |  Processor Configuration                                          ^|Enables Hyper Threading      |
  |  --------------------------------------------------               *|(Software Method to          |
  |  Processor BSP Revision                    50657 - CLX B1         *|Enable/Disable Logical       |
  |  Processor Socket                          CPU1      |  CPU2      *|Processor threads.           |
  |  Processor ID                              00050657* |  00050657  *|                             |
  |  Processor Frequency                       2.300GHz  |  2.300GHz  *|                             |
  |  Processor Max Ratio                            17H  |  17H       *|                             |
  |  Processor Min Ratio                            0AH  |  0AH       *|                             |
  |  Microcode Revision                        0500002C  |  0500002C  *|                             |
  |  L1 Cache RAM                                  64KB  |      64KB  *|                             |
  |  L2 Cache RAM                                1024KB  |    1024KB  *|                             |
  |  L3 Cache RAM                               36608KB  |   36608KB  *|                             |
  |  Processor 0 Version                                              *|                             |
  |  Intel(R) Xeon(R) Gold 6252N CPU @ 2.30GHz                        *|                             |
  |  Processor 1 Version                                              *|                             |
  |  Intel(R) Xeon(R) Gold 6252N CPU @ 2.30GHz                        *|                             |
  |                                                                   *|-----------------------------|
  |  Hyper-Threading [ALL]                     [Enable]               *|><: Select Screen            |
  |  Cores Enabled                             0                      *|^v: Select Item              |
  |  Monitor/Mwait                             [Auto]                 *|Enter: Select                |
  |  Execute Disable Bit                       [Enable]               +|+/-: Change Opt.             |
  |  Intel Virtualization Technology           [Enable]               +|F1: General Help             |
  |  PPIN Control                              [Unlock/Enable]        +|F2: Previous Values          |
  |  Hardware Prefetcher                       [Enable]               +|F3: Optimized Defaults       |
  |  Adjacent Cache Prefetch                   [Enable]               v|F4: Save & Exit              |
  |  DCU Streamer Prefetcher                   [Enable]                |                             |
  |  DCU IP Prefetcher                         [Enable]                |                             |
  |  LLC Prefetch                              [Disable]               |                             |
  |  Extended APIC                             [Disable]               |                             |
  |  AES-NI                                    [Enable]                |                             |
  |> Advanced Power Management Configuration                           |                             |
```

#### Advanced Power Management Configuration

```
  |  Advanced Power Management Configuration                           |Switch CPU Power Management  |
  |  --------------------------------------------------                |profile                      |
  |  Power Technology                          [Custom]                |                             |
  |  Power Performance Tuning                  [BIOS Controls EPB]     |                             |
  |  ENERGY_PERF_BIAS_CFG mode                 [Maximum Performance]   |                             |
  |> CPU P State Control                                               |                             |
  |> Hardware PM State Control                                         |                             |
  |> CPU C State Control                                               |                             |
  |> Package C State Control                                           |                             |
  |> CPU T State Control                                               |                             |
```

##### CPU P State Control

```
  |  CPU P State Control                                               |EIST allows the processor    |
  |                                                                    |to dynamically adjust        |
  |  SpeedStep (P-States)                      [Disable]               |frequency and voltage based  |
  |  Activate PBF                              [Disable]               |on power versus performance  |
  |  Configure PBF                             [Enable]                |needs.                       |
  |  EIST PSD Function                         [HW_ALL]                |                             |
```

##### Hardware PM State Control

```
  |  Hardware PM State Control                                         |If set to Disable, hardware ^|
  |                                                                    |will choose a P-state       *|
  |  Hardware P-States                         [Disable]               |setting for the system      *|
  |                                                                    |based on an OS request.     *|
  |                                                                    |If set to Native Mode,      *|
  |                                                                    |hardware will choose a      *|
  |                                                                    |P-state setting based on OS *|
  |                                                                    |guidance.                   *|
  |                                                                    |If set to Native Mode with  *|
  |                                                                    |No Legacy Support, hardware *|
  |                                                                    |will choose a P-state       *|
  |                                                                    |setting independently       *|
  |                                                                    |without OS guidance.        +|
  |                                                                    |If set to Out of Band Mode, +|
  |                                                                    |hardware autonomously       v|
```

##### CPU C State Control

```
  |  CPU C State Control                                               |Select Enable to support     |
  |                                                                    |Autonomous Core C-State      |
  |  Autonomous Core C-State                   [Disable]               |control which will allow     |
  |  CPU C6 report                             [Disable]               |the processor core to        |
  |  Enhanced Halt State (C1E)                 [Disable]               |control its C-State setting  |
  |                                                                    |automatically and            |
  |                                                                    |independently.               |
```

##### Package C State Control

```
  |  Package C State Control                                           |Limit the lowest package     |
  |                                                                    |level C-State to             |
  |  Package C State                           [C0/C1 state]           |processors. Lower package    |
  |                                                                    |C-State lower processor      |
  |                                                                    |power consumption upon idle. |
```

##### CPU T State Control

```
  |  CPU T State Control                                               |Enable/Disable CPU           |
  |                                                                    |throttling by OS.            |
  |  Software Controlled T-States              [Disable]               |Throttling reduces power     |
  |                                                                    |consumption                  |
```

#### Chipset Configuration

```
  |  WARNING: Setting wrong values in below sections may cause         |North Bridge Parameters      |
  |           system to malfunction.                                   |                             |
  |> North Bridge                                                      |                             |
  |> South Bridge                                                      |                             |
```

##### North Bridge

```
  |> UPI Configuration                                                 |Displays and provides        |
  |> Memory Configuration                                              |option to change the UPI     |
  |> IIO Configuration                                                 |Settings                     |
```

##### UPI Configuration

```
  |  UPI Configuration                                                 |Use this feature to select   |
  |  --------------------------------------------------                |the degrading precedence     |
  |  Number of CPU                             2                       |option for Ultra Path        |
  |  Number of Active UPI Link                 3                       |Interconnect connections.    |
  |  Current UPI Link Speed                    Fast                    |Select Topology Precedent    |
  |  Current UPI Link Frequency                10.4 GT/s               |to degrade UPI features if   |
  |  UPI Global MMIO Low Base / Limit          90000000 / FBFFFFFF     |system options are in        |
  |  UPI Global MMIO High Base / Limit         0000000000000000 /      |conflict. Select Feature     |
  |                                            00000000FFFFFFFF        |Precedent to degrade UPI     |
  |  UPI Pci-e Configuration Base / Size       80000000 / 10000000     |topology if system options   |
  |  Degrade Precedence                        [Topology Precedence]   |are in conflict.             |
  |  Link L0p Enable                           [Disable]               |                             |
  |  Link L1 Enable                            [Disable]               |                             |
  |  IO Directory Cache (IODC)                 [Auto]                  |                             |
  |  SNC                                       [Disable]               |                             |
  |  XPT Prefetch                              [Disable]               |                             |
  |  KTI Prefetch                              [Enable]                |-----------------------------|
  |  Local/Remote Threshold                    [Auto]                  |><: Select Screen            |
  |  Stale AtoS                                [Auto]                  |^v: Select Item              |
  |  LLC Dead Line Alloc                       [Enable]                |Enter: Select                |
  |  Isoc Mode                                 [Auto]                  |+/-: Change Opt.             |
```

##### Memory Configuration

```
  |                                                                    |Select POR to enforce POR    |
  |  --------------------------------------------------                |restrictions for DDR4        |
  |  Integrated Memory Controller (iMC)                                |frequency and voltage        |
  |  --------------------------------------------------                |programming                  |
  |                                                                    |                             |
  |  Enforce POR                               [POR]                   |                             |
  |  PPR Type                                  [Hard PPR]              |                             |
  |  Enhanced PPR                              [Disable]               |                             |
  |   Operation Mode                           [Test and Repair]       |                             |
  |  Memory Frequency                          [2933]                  |                             |
  |  Data Scrambling for DDR4                  [Auto]                  |                             |
  |  tCCD_L Relaxation                         [Auto]                  |                             |
  |  tRWSR Relaxation                          [Disable]               |                             |
  |  tRFC Optimization for 16Gb Based DIMM     [Force 550ns]           |                             |
  |  2x Refresh                                [Auto]                  |                             |
  |  Page Policy                               [Auto]                  |                             |
  |  IMC Interleaving                          [2-way Interleave]      |-----------------------------|
  |> Memory Topology                                                   |><: Select Screen            |
  |> Memory RAS Configuration                                          |^v: Select Item              |
```

##### IIO Configuration

```
  |  IIO Configuration                                                 |Expose IIO DFX devices and   |
  |  --------------------------------------------------                |other CPU devices like PMON  |
  |                                                                    |                             |
  |  EV DFX Features                           [Disable]               |                             |
  |> CPU1 Configuration                                                |                             |
  |> CPU2 Configuration                                                |                             |
  |> IOAT Configuration                                                |                             |
  |> Intel. VT for Directed I/O (VT-d)                                 |                             |
  |> Intel. VMD technology                                             |                             |
  |                                                                    |                             |
  |   IIO-PCIE Express Global Options                                  |                             |
  |  ========================================                          |                             |
  |  PCI-E Completion Timeout Disable          [No]                    |                             |
```

##### CPU1 Configuration

```
  |  IOU0 (IIO PCIe Br1)                       [Auto]                  |Selects PCIe port            |
  |  IOU1 (IIO PCIe Br2)                       [Auto]                  |Bifurcation for selected     |
  |  IOU2 (IIO PCIe Br3)                       [Auto]                  |slot(s)                      |
  |> CPU1 SLOT2 PCI-E 3.0 X16                                          |                             |
  |> CPU1 SLOT4 PCI-E 3.0 X16                                          |                             |
  |> CPU1 SLOT9 PCI-E 3.0 X16                                          |                             |
```

##### CPU2 Configuration

```
  |  IOU0 (IIO PCIe Br1)                       [Auto]                  |Selects PCIe port            |
  |  IOU1 (IIO PCIe Br2)                       [Auto]                  |Bifurcation for selected     |
  |  IOU2 (IIO PCIe Br3)                       [Auto]                  |slot(s)                      |
  |> CPU2 SLOT6 PCI-E 3.0 X16                                          |                             |
  |> CPU2 SLOT8 PCI-E 3.0 X16                                          |                             |
  |> CPU2 SLOT10 PCI-E 3.0 X16                                         |                             |
```

#### South Bridge

```
  |                                                                    |Enables Legacy USB support.  |
  |  USB Module Version                        21                      |AUTO option disables legacy  |
  |                                                                    |support if no USB devices    |
  |  USB Devices:                                                      |are connected. DISABLE       |
  |        1 Keyboard, 1 Mouse, 1 Hub                                  |option will keep USB         |
  |                                                                    |devices available only for   |
  |  Legacy USB Support                        [Enabled]               |EFI applications.            |
  |  XHCI Hand-off                             [Enabled]               |                             |
  |  Port 60/64 Emulation                      [Enabled]               |                             |
  |  PCIe PLL SSC                              [Disable]               |                             |
  |  Real USB Wake Up                          [Enabled]               |                             |
  |  Front USB Wake Up                         [Enabled]               |                             |
  |                                                                    |                             |
  |  Azalia                                    [Auto]                  |                             |
  |    Azalia PME Enable                       [Disabled]              |                             |
```

### PCIe/PCI/PnP Configuration

```
  |  PCI Bus Driver Version                    A5.01.18               ^|Enables or Disables 64bit    |
  |                                                                   *|capable Devices to be        |
  |  PCI Devices Common Settings:                                     *|Decoded in Above 4G Address  |
  |  Above 4G Decoding                         [Enabled]              *|Space (Only if System        |
  |  SR-IOV Support                            [Enabled]              *|Supports 64 bit PCI          |
  |  ARI Support                               [Enabled]              *|Decoding).                   |
  |  MMIO High Base                            [56T]                  *|                             |
  |  MMIO High Granularity Size                [256G]                 *|                             |
  |  Maximum Read Request                      [Auto]                 *|                             |
  |  MMCFG Base                                [2G]                   *|                             |
  |  NVMe Firmware Source                      [Vendor Defined        *|                             |
  |                                            Firmware]              *|                             |
  |  VGA Priority                              [Onboard]              *|                             |
  |  CPU1 SLOT2 PCI-E 3.0 X16 OPROM            [Legacy]               *|                             |
  |  CPU1 SLOT4 PCI-E 3.0 X16 OPROM            [Legacy]               *|                             |
  |  CPU2 SLOT6 PCI-E 3.0 X16 OPROM            [Legacy]               *|                             |
  |  CPU2 SLOT8 PCI-E 3.0 X16 OPROM            [Legacy]               *|-----------------------------|
  |  CPU1 SLOT9 PCI-E 3.0 X16 OPROM            [Legacy]               *|><: Select Screen            |
  |  CPU2 SLOT10 PCI-E 3.0 X16 OPROM           [Legacy]               *|^v: Select Item              |
  |  CPU2 SLOT11 PCI-E 3.0 X4(IN X8) OPROM     [Legacy]               *|Enter: Select                |
  |  M.2 CONNECTOR OPROM                       [Legacy]               *|+/-: Change Opt.             |
  |  Bus Master Enable                         [Enabled]              +|F1: General Help             |
  |  Onboard LAN1 Option ROM                   [Legacy]               +|F2: Previous Values          |
  |  Onboard LAN2 Option ROM                   [Disabled]             +|F3: Optimized Defaults       |
  |  Onboard Video Option ROM                  [Legacy]               v|F4: Save & Exit              |
  |> Network Stack Configuration                                       |                             |
```

### ACPI Settings

```
  |  ACPI Settings                                                     |Enable or Disable Non        |
  |                                                                    |uniform Memory Access        |
  |  NUMA                                      [Enabled]               |(NUMA).                      |
  |  WHEA Support                              [Enabled]               |                             |
  |  High Precision Event Timer                [Enabled]               |                             |
```


## Xeon Clx Server Firmware Inventory

```
Host.           IPMI IP.      BMC.   BIOS. CPLD.     CPU Microcode.  PCI Bus.   X710 Firmware.            XXV710 Firmware.          i40e.      MLX5 Firmware.    mlx5_core    E810 Firmware.            ice.
s33-t27-sut1.   10.30.55.18.  1.67.  3.2.  03.B1.05. 0500002C.       A5.01.18.  8.30 0x8000a49d 1.2926.0. 8.30 0x8000a485 1.2926.0. 2.17.15.   16.32.1010.       5.3-1.0.5.0. 3.20 0x8000d83e 1.3146.0. 1.8.3.
s34-t27-tg1.    10.30.55.19.  1.67.  3.2.  03.B1.05. 0500002C.       A5.01.18.  8.00 0x80008b82 1.2007.0. 8.00 0x80008c1a 1.2007.0. 2.14.13.   16.32.1010.       5.5-1.0.3.2. N/A.                      N/A.
s35-t28-sut1.   10.30.55.20.  1.67.  3.2.  03.B1.05. 0500002C.       A5.01.18.  8.30 0x8000a49d 1.2926.0. 8.30 0x8000a485 1.2926.0. 2.17.15.   16.32.1010.       5.3-1.0.5.0. 3.20 0x8000d83e 1.3146.0. 1.8.3.
s36-t28-tg1.    10.30.55.21.  1.67.  3.2.  03.B1.05. 0500002C.       A5.01.18.  8.00 0x80008b82 1.2007.0. 8.00 0x80008c1a 1.2007.0. 2.14.13.   16.32.1010.       5.5-1.0.3.2. N/A.                      N/A.
s37-t29-sut1.   10.30.55.22.  1.67.  3.2.  03.B1.05. 0500002C.       A5.01.18.  8.30 0x8000a49d 1.2926.0. 8.30 0x8000a485 1.2926.0. 2.17.15.   16.32.1010.       5.3-1.0.5.0. 3.20 0x8000d83e 1.3146.0. 1.8.3.
s38-t29-tg1.    10.30.55.23.  1.67.  3.2.  03.B1.05. 0500002C.       A5.01.18.  8.00 0x80008b82 1.2007.0. 8.00 0x80008c1a 1.2007.0. 2.14.13.   16.32.1010.       5.5-1.0.3.2. N/A.                      N/A.
```
