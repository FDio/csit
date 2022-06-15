# SuperMicro Icelake Servers - HW and BIOS Configuration

1. [Linux lscpu](#linux-lscpu)
1. [Linux dmidecode](#dmidecode)
1. [Linux dmidecode pci](#linux-dmidecode-pci)
1. [Linux dmidecode memory](#linux-dmidecode-memory)
1. [Xeon ICX Server BIOS Configuration](#xeon-icx-server-bios-configuration)
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
1. [Xeon ICX Server Firmware Inventory](#xeon-icx-server-firmware-inventory)

## Linux lscpu

```
$ lscpu
Architecture:                    x86_64
CPU op-mode(s):                  32-bit, 64-bit
Byte Order:                      Little Endian
Address sizes:                   46 bits physical, 57 bits virtual
CPU(s):                          128
On-line CPU(s) list:             0-127
Thread(s) per core:              2
Core(s) per socket:              32
Socket(s):                       2
NUMA node(s):                    2
Vendor ID:                       GenuineIntel
CPU family:                      6
Model:                           106
Model name:                      Intel(R) Xeon(R) Platinum 8358 CPU @ 2.60GHz
Stepping:                        6
CPU MHz:                         3283.980
BogoMIPS:                        5200.00
Virtualization:                  VT-x
L1d cache:                       3 MiB
L1i cache:                       2 MiB
L2 cache:                        80 MiB
L3 cache:                        96 MiB
NUMA node0 CPU(s):               0-31,64-95
NUMA node1 CPU(s):               32-63,96-127
Vulnerability Itlb multihit:     Not affected
Vulnerability L1tf:              Not affected
Vulnerability Mds:               Not affected
Vulnerability Meltdown:          Not affected
Vulnerability Spec store bypass: Mitigation; Speculative Store Bypass disabled via prctl and seccomp
Vulnerability Spectre v1:        Mitigation; usercopy/swapgs barriers and __user pointer sanitization
Vulnerability Spectre v2:        Mitigation; Enhanced IBRS, IBPB conditional, RSB filling
Vulnerability Srbds:             Not affected
Vulnerability Tsx async abort:   Not affected
Flags:                           fpu vme de pse tsc msr pae mce cx8 apic sep mtrr pge mca cmov pat pse36 clflush dts acpi mmx fxsr sse sse2 ss ht tm pbe sysca
                                 ll nx pdpe1gb rdtscp lm constant_tsc art arch_perfmon pebs bts rep_good nopl xtopology nonstop_tsc cpuid aperfmperf pni pclmu
                                 lqdq dtes64 monitor ds_cpl vmx smx est tm2 ssse3 sdbg fma cx16 xtpr pdcm pcid dca sse4_1 sse4_2 x2apic movbe popcnt tsc_deadl
                                 ine_timer aes xsave avx f16c rdrand lahf_lm abm 3dnowprefetch cpuid_fault epb cat_l3 invpcid_single ssbd mba ibrs ibpb stibp
                                 ibrs_enhanced tpr_shadow vnmi flexpriority ept vpid ept_ad fsgsbase tsc_adjust bmi1 avx2 smep bmi2 erms invpcid cqm rdt_a avx
                                 512f avx512dq rdseed adx smap avx512ifma clflushopt clwb intel_pt avx512cd sha_ni avx512bw avx512vl xsaveopt xsavec xgetbv1 x
                                 saves cqm_llc cqm_occup_llc cqm_mbm_total cqm_mbm_local wbnoinvd dtherm ida arat pln pts avx512vbmi umip pku ospke avx512_vbm
                                 i2 gfni vaes vpclmulqdq avx512_vnni avx512_bitalg tme avx512_vpopcntdq rdpid md_clear pconfig flush_l1d arch_capabilities
```

## Linux dmidecode

```
# dmidecode 3.2
Getting SMBIOS data from sysfs.
SMBIOS 3.3.0 present.
# SMBIOS implementations newer than version 3.2.0 are not
# fully supported by this version of dmidecode.
Table at 0x6BAEE000.

Handle 0x0000, DMI type 0, 26 bytes
BIOS Information
        Vendor: American Megatrends International, LLC.
        Version: 1.1
        Release Date: 04/09/2021
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
                Japanese floppy for NEC 9800 1.2 MB is supported (int 13h)
                Japanese floppy for Toshiba 1.2 MB is supported (int 13h)
                5.25"/360 kB floppy services are supported (int 13h)
                5.25"/1.2 MB floppy services are supported (int 13h)
                3.5"/720 kB floppy services are supported (int 13h)
                3.5"/2.88 MB floppy services are supported (int 13h)
                Print screen service is supported (int 5h)
                Serial services are supported (int 14h)
                Printer services are supported (int 17h)
                CGA/mono video services are supported (int 10h)
                USB legacy is supported
                BIOS boot specification is supported
                Targeted content distribution is supported
                UEFI is supported
        BIOS Revision: 5.22

Handle 0x0001, DMI type 1, 27 bytes
System Information
        Manufacturer: Supermicro
        Product Name: SYS-740GP-TNRT
        Version: 0123456789
        Serial Number: S424016X1B00510
        UUID: 0698ae00-2383-11ec-8000-3cecefb9a6ba
        Wake-up Type: Power Switch
        SKU Number: To be filled by O.E.M.
        Family: Family

Handle 0x0002, DMI type 2, 15 bytes
Base Board Information
        Manufacturer: Supermicro
        Product Name: X12DPG-QT6
        Version: 1.00
        Serial Number: UM219S003392
        Asset Tag: Base Board Asset Tag
        Features:
                Board is a hosting board
                Board is replaceable
        Location In Chassis: Part Component
        Chassis Handle: 0x0003
        Type: Motherboard
        Contained Object Handles: 0

Handle 0x0003, DMI type 3, 22 bytes
Chassis Information
        Manufacturer: Supermicro
        Type: Other
        Lock: Not Present
        Version: 0123456789
        Serial Number: C7470KK25P50098
        Asset Tag: Chassis Asset Tag
        Boot-up State: Safe
        Power Supply State: Safe
        Thermal State: Safe
        Security Status: None
        OEM Information: 0x00000000
        Height: Unspecified
        Number Of Power Cords: 1
        Contained Elements: 0
        SKU Number: To be filled by O.E.M.

Handle 0x001B, DMI type 38, 18 bytes
IPMI Device Information
        Interface Type: KCS (Keyboard Control Style)
        Specification Version: 2.0
        I2C Slave Address: 0x10
        NV Storage Device: Not Present
        Base Address: 0x0000000000000CA2 (I/O)
        Register Spacing: Successive Byte Boundaries

Handle 0x002A, DMI type 4, 48 bytes
Processor Information
        Socket Designation: CPU1
        Type: Central Processor
        Family: Xeon
        Manufacturer: Intel(R) Corporation
        ID: A6 06 06 00 FF FB EB BF
        Signature: Type 0, Family 6, Model 106, Stepping 6
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
        Version: Intel(R) Xeon(R) Platinum 8358 CPU @ 2.60GHz
        Voltage: 1.6 V
        External Clock: 100 MHz
        Max Speed: 4500 MHz
        Current Speed: 2600 MHz
        Status: Populated, Enabled
        Upgrade: <OUT OF SPEC>
        L1 Cache Handle: 0x0027
        L2 Cache Handle: 0x0028
        L3 Cache Handle: 0x0029
        Serial Number: Not Specified
        Asset Tag: UNKNOWN
        Part Number: Not Specified
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

Handle 0x002E, DMI type 4, 48 bytes
Processor Information
        Socket Designation: CPU2
        Type: Central Processor
        Family: Xeon
        Manufacturer: Intel(R) Corporation
        ID: A6 06 06 00 FF FB EB BF
        Signature: Type 0, Family 6, Model 106, Stepping 6
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
        Version: Intel(R) Xeon(R) Platinum 8358 CPU @ 2.60GHz
        Voltage: 1.6 V
        External Clock: 100 MHz
        Max Speed: 4500 MHz
        Current Speed: 2600 MHz
        Status: Populated, Enabled
        Upgrade: <OUT OF SPEC>
        L1 Cache Handle: 0x002B
        L2 Cache Handle: 0x002C
        L3 Cache Handle: 0x002D
        Serial Number: Not Specified
        Asset Tag: UNKNOWN
        Part Number: Not Specified
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
Handle 0x000A, DMI type 9, 17 bytes
System Slot Information
        Designation: CPU1 SLOT2 PCI-E 4.0 X16
        Type: x16 <OUT OF SPEC>
        Current Usage: In Use
        Length: Short
        Characteristics:
                3.3 V is provided
                Opening is shared
                PME signal is supported
        Bus Address: 0000:4b:00.0

Handle 0x000B, DMI type 9, 17 bytes
System Slot Information
        Designation: CPU1 SlOT4 PCI-E 4.0 X16
        Type: x16 <OUT OF SPEC>
        Current Usage: In Use
        Length: Short
        Characteristics:
                3.3 V is provided
                Opening is shared
                PME signal is supported
        Bus Address: 0000:31:00.0

Handle 0x000C, DMI type 9, 17 bytes
System Slot Information
        Designation: CPU2 SLOT6 PCI-E 4.0 X16
        Type: x16 <OUT OF SPEC>
        Current Usage: Available
        Length: Short
        Characteristics:
                3.3 V is provided
                Opening is shared
                PME signal is supported
        Bus Address: 0000:ff:00.0

Handle 0x000D, DMI type 9, 17 bytes
System Slot Information
        Designation: CPU2 SLOT8 PCI-E 4.0 X16
        Type: x16 <OUT OF SPEC>
        Current Usage: Available
        Length: Short
        Characteristics:
                3.3 V is provided
                Opening is shared
                PME signal is supported
        Bus Address: 0000:ff:00.0

Handle 0x000E, DMI type 9, 17 bytes
System Slot Information
        Designation: CPU1 SLOT9 PCI-E 4.0 X16
        Type: x16 <OUT OF SPEC>
        Current Usage: In Use
        Length: Short
        Characteristics:
                3.3 V is provided
                Opening is shared
                PME signal is supported
        Bus Address: 0000:17:00.0

Handle 0x000F, DMI type 9, 17 bytes
System Slot Information
        Designation: CPU2 SLOT10 PCI-E 4.0 X16
        Type: x16 <OUT OF SPEC>
        Current Usage: Available
        Length: Short
        Characteristics:
                3.3 V is provided
                Opening is shared
                PME signal is supported
        Bus Address: 0000:ff:00.0

Handle 0x0010, DMI type 9, 17 bytes
System Slot Information
        Designation: CPU2 SLOT11 PCI-E 4.0 X8
        Type: x8 <OUT OF SPEC>
        Current Usage: Available
        Length: Short
        Characteristics:
                3.3 V is provided
                Opening is shared
                PME signal is supported
        Bus Address: 0000:ff:00.0

Handle 0x0011, DMI type 9, 17 bytes
System Slot Information
        Designation: M.2-HC1
        Type: x4 M.2 Socket 2
        Current Usage: Available
        Length: Short
        Characteristics:
                3.3 V is provided
                Opening is shared
                PME signal is supported
        Bus Address: 0000:ff:00.0

Handle 0x0012, DMI type 9, 17 bytes
System Slot Information
        Designation: M.2-HC2
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
Handle 0x0033, DMI type 16, 23 bytes
Physical Memory Array
        Location: System Board Or Motherboard
        Use: System Memory
        Error Correction Type: Single-bit ECC
        Maximum Capacity: 12 TB
        Error Information Handle: Not Provided
        Number Of Devices: 16

Handle 0x0034, DMI type 17, 92 bytes
Memory Device
        Array Handle: 0x0033
        Error Information Handle: Not Provided
        Total Width: 72 bits
        Data Width: 64 bits
        Size: 16384 MB
        Form Factor: DIMM
        Set: None
        Locator: P1-DIMMA1
        Bank Locator: P0_Node0_Channel0_Dimm0
        Type: DDR4
        Type Detail: Synchronous Registered (Buffered)
        Speed: 3200 MT/s
        Manufacturer: Samsung
        Serial Number: H0MK0001304705C2E3
        Asset Tag: P1-DIMMA1_AssetTag (date:21/30)
        Part Number: M393A2K43DB3-CWE
        Rank: 2
        Configured Memory Speed: 3200 MT/s
        Minimum Voltage: 1.2 V
        Maximum Voltage: 1.2 V
        Configured Voltage: 1.2 V
        Memory Technology: DRAM
        Memory Operating Mode Capability: Volatile memory
        Firmware Version: 0000
        Module Manufacturer ID: Bank 1, Hex 0xCE
        Module Product ID: Unknown
        Memory Subsystem Controller Manufacturer ID: Unknown
        Memory Subsystem Controller Product ID: Unknown
        Non-Volatile Size: None
        Volatile Size: 16 GB
        Cache Size: None
        Logical Size: None

Handle 0x0036, DMI type 17, 92 bytes
Memory Device
        Array Handle: 0x0033
        Error Information Handle: Not Provided
        Total Width: 72 bits
        Data Width: 64 bits
        Size: 16384 MB
        Form Factor: DIMM
        Set: None
        Locator: P1-DIMMB1
        Bank Locator: P0_Node0_Channel1_Dimm0
        Type: DDR4
        Type Detail: Synchronous Registered (Buffered)
        Speed: 3200 MT/s
        Manufacturer: Samsung
        Serial Number: H0MK0001304705CE60
        Asset Tag: P1-DIMMB1_AssetTag (date:21/30)
        Part Number: M393A2K43DB3-CWE
        Rank: 2
        Configured Memory Speed: 3200 MT/s
        Minimum Voltage: 1.2 V
        Maximum Voltage: 1.2 V
        Configured Voltage: 1.2 V
        Memory Technology: DRAM
        Memory Operating Mode Capability: Volatile memory
        Firmware Version: 0000
        Module Manufacturer ID: Bank 1, Hex 0xCE
        Module Product ID: Unknown
        Memory Subsystem Controller Manufacturer ID: Unknown
        Memory Subsystem Controller Product ID: Unknown
        Non-Volatile Size: None
        Volatile Size: 16 GB
        Cache Size: None
        Logical Size: None

Handle 0x0038, DMI type 17, 92 bytes
Memory Device
        Array Handle: 0x0033
        Error Information Handle: Not Provided
        Total Width: 72 bits
        Data Width: 64 bits
        Size: 16384 MB
        Form Factor: DIMM
        Set: None
        Locator: P1-DIMMC1
        Bank Locator: P0_Node0_Channel2_Dimm0
        Type: DDR4
        Type Detail: Synchronous Registered (Buffered)
        Speed: 3200 MT/s
        Manufacturer: Samsung
        Serial Number: H0MK0001304705C59E
        Asset Tag: P1-DIMMC1_AssetTag (date:21/30)
        Part Number: M393A2K43DB3-CWE
        Rank: 2
        Configured Memory Speed: 3200 MT/s
        Minimum Voltage: 1.2 V
        Maximum Voltage: 1.2 V
        Configured Voltage: 1.2 V
        Memory Technology: DRAM
        Memory Operating Mode Capability: Volatile memory
        Firmware Version: 0000
        Module Manufacturer ID: Bank 1, Hex 0xCE
        Module Product ID: Unknown
        Memory Subsystem Controller Manufacturer ID: Unknown
        Memory Subsystem Controller Product ID: Unknown
        Non-Volatile Size: None
        Volatile Size: 16 GB
        Cache Size: None
        Logical Size: None

Handle 0x003A, DMI type 17, 92 bytes
Memory Device
        Array Handle: 0x0033
        Error Information Handle: Not Provided
        Total Width: 72 bits
        Data Width: 64 bits
        Size: 16384 MB
        Form Factor: DIMM
        Set: None
        Locator: P1-DIMMD1
        Bank Locator: P0_Node0_Channel3_Dimm0
        Type: DDR4
        Type Detail: Synchronous Registered (Buffered)
        Speed: 3200 MT/s
        Manufacturer: Samsung
        Serial Number: H0MK0001304705D12D
        Asset Tag: P1-DIMMD1_AssetTag (date:21/30)
        Part Number: M393A2K43DB3-CWE
        Rank: 2
        Configured Memory Speed: 3200 MT/s
        Minimum Voltage: 1.2 V
        Maximum Voltage: 1.2 V
        Configured Voltage: 1.2 V
        Memory Technology: DRAM
        Memory Operating Mode Capability: Volatile memory
        Firmware Version: 0000
        Module Manufacturer ID: Bank 1, Hex 0xCE
        Module Product ID: Unknown
        Memory Subsystem Controller Manufacturer ID: Unknown
        Memory Subsystem Controller Product ID: Unknown
        Non-Volatile Size: None
        Volatile Size: 16 GB
        Cache Size: None
        Logical Size: None

Handle 0x003C, DMI type 17, 92 bytes
Memory Device
        Array Handle: 0x0033
        Error Information Handle: Not Provided
        Total Width: 72 bits
        Data Width: 64 bits
        Size: 16384 MB
        Form Factor: DIMM
        Set: None
        Locator: P1-DIMME1
        Bank Locator: P0_Node1_Channel0_Dimm0
        Type: DDR4
        Type Detail: Synchronous Registered (Buffered)
        Speed: 3200 MT/s
        Manufacturer: Samsung
        Serial Number: H0MK0001304705C69C
        Asset Tag: P1-DIMME1_AssetTag (date:21/30)
        Part Number: M393A2K43DB3-CWE
        Rank: 2
        Configured Memory Speed: 3200 MT/s
        Minimum Voltage: 1.2 V
        Maximum Voltage: 1.2 V
        Configured Voltage: 1.2 V
        Memory Technology: DRAM
        Memory Operating Mode Capability: Volatile memory
        Firmware Version: 0000
        Module Manufacturer ID: Bank 1, Hex 0xCE
        Module Product ID: Unknown
        Memory Subsystem Controller Manufacturer ID: Unknown
        Memory Subsystem Controller Product ID: Unknown
        Non-Volatile Size: None
        Volatile Size: 16 GB
        Cache Size: None
        Logical Size: None

Handle 0x003E, DMI type 17, 92 bytes
Memory Device
        Array Handle: 0x0033
        Error Information Handle: Not Provided
        Total Width: 72 bits
        Data Width: 64 bits
        Size: 16384 MB
        Form Factor: DIMM
        Set: None
        Locator: P1-DIMMF1
        Bank Locator: P0_Node1_Channel1_Dimm0
        Type: DDR4
        Type Detail: Synchronous Registered (Buffered)
        Speed: 3200 MT/s
        Manufacturer: Samsung
        Serial Number: H0MK0001304705C33A
        Asset Tag: P1-DIMMF1_AssetTag (date:21/30)
        Part Number: M393A2K43DB3-CWE
        Rank: 2
        Configured Memory Speed: 3200 MT/s
        Minimum Voltage: 1.2 V
        Maximum Voltage: 1.2 V
        Configured Voltage: 1.2 V
        Memory Technology: DRAM
        Memory Operating Mode Capability: Volatile memory
        Firmware Version: 0000
        Module Manufacturer ID: Bank 1, Hex 0xCE
        Module Product ID: Unknown
        Memory Subsystem Controller Manufacturer ID: Unknown
        Memory Subsystem Controller Product ID: Unknown
        Non-Volatile Size: None
        Volatile Size: 16 GB
        Cache Size: None
        Logical Size: None

Handle 0x0040, DMI type 17, 92 bytes
Memory Device
        Array Handle: 0x0033
        Error Information Handle: Not Provided
        Total Width: 72 bits
        Data Width: 64 bits
        Size: 16384 MB
        Form Factor: DIMM
        Set: None
        Locator: P1-DIMMG1
        Bank Locator: P0_Node1_Channel2_Dimm0
        Type: DDR4
        Type Detail: Synchronous Registered (Buffered)
        Speed: 3200 MT/s
        Manufacturer: Samsung
        Serial Number: H0MK0001304705C59F
        Asset Tag: P1-DIMMG1_AssetTag (date:21/30)
        Part Number: M393A2K43DB3-CWE
        Rank: 2
        Configured Memory Speed: 3200 MT/s
        Minimum Voltage: 1.2 V
        Maximum Voltage: 1.2 V
        Configured Voltage: 1.2 V
        Memory Technology: DRAM
        Memory Operating Mode Capability: Volatile memory
        Firmware Version: 0000
        Module Manufacturer ID: Bank 1, Hex 0xCE
        Module Product ID: Unknown
        Memory Subsystem Controller Manufacturer ID: Unknown
        Memory Subsystem Controller Product ID: Unknown
        Non-Volatile Size: None
        Volatile Size: 16 GB
        Cache Size: None
        Logical Size: None

Handle 0x0042, DMI type 17, 92 bytes
Memory Device
        Array Handle: 0x0033
        Error Information Handle: Not Provided
        Total Width: 72 bits
        Data Width: 64 bits
        Size: 16384 MB
        Form Factor: DIMM
        Set: None
        Locator: P1-DIMMH1
        Bank Locator: P0_Node1_Channel3_Dimm0
        Type: DDR4
        Type Detail: Synchronous Registered (Buffered)
        Speed: 3200 MT/s
        Manufacturer: Samsung
        Serial Number: H0MK0001304705CA16
        Asset Tag: P1-DIMMH1_AssetTag (date:21/30)
        Part Number: M393A2K43DB3-CWE
        Rank: 2
        Configured Memory Speed: 3200 MT/s
        Minimum Voltage: 1.2 V
        Maximum Voltage: 1.2 V
        Configured Voltage: 1.2 V
        Memory Technology: DRAM
        Memory Operating Mode Capability: Volatile memory
        Firmware Version: 0000
        Module Manufacturer ID: Bank 1, Hex 0xCE
        Module Product ID: Unknown
        Memory Subsystem Controller Manufacturer ID: Unknown
        Memory Subsystem Controller Product ID: Unknown
        Non-Volatile Size: None
        Volatile Size: 16 GB
        Cache Size: None
        Logical Size: None

Handle 0x0044, DMI type 17, 92 bytes
Memory Device
        Array Handle: 0x0033
        Error Information Handle: Not Provided
        Total Width: 72 bits
        Data Width: 64 bits
        Size: 16384 MB
        Form Factor: DIMM
        Set: None
        Locator: P2-DIMMA1
        Bank Locator: P1_Node0_Channel0_Dimm0
        Type: DDR4
        Type Detail: Synchronous Registered (Buffered)
        Speed: 3200 MT/s
        Manufacturer: Samsung
        Serial Number: H0MK0001304705CBFE
        Asset Tag: P2-DIMMA1_AssetTag (date:21/30)
        Part Number: M393A2K43DB3-CWE
        Rank: 2
        Configured Memory Speed: 3200 MT/s
        Minimum Voltage: 1.2 V
        Maximum Voltage: 1.2 V
        Configured Voltage: 1.2 V
        Memory Technology: DRAM
        Memory Operating Mode Capability: Volatile memory
        Firmware Version: 0000
        Module Manufacturer ID: Bank 1, Hex 0xCE
        Module Product ID: Unknown
        Memory Subsystem Controller Manufacturer ID: Unknown
        Memory Subsystem Controller Product ID: Unknown
        Non-Volatile Size: None
        Volatile Size: 16 GB
        Cache Size: None
        Logical Size: None

Handle 0x0046, DMI type 17, 92 bytes
Memory Device
        Array Handle: 0x0033
        Error Information Handle: Not Provided
        Total Width: 72 bits
        Data Width: 64 bits
        Size: 16384 MB
        Form Factor: DIMM
        Set: None
        Locator: P2-DIMMB1
        Bank Locator: P1_Node0_Channel1_Dimm0
        Type: DDR4
        Type Detail: Synchronous Registered (Buffered)
        Speed: 3200 MT/s
        Manufacturer: Samsung
        Serial Number: H0MK0001304705CFC8
        Asset Tag: P2-DIMMB1_AssetTag (date:21/30)
        Part Number: M393A2K43DB3-CWE
        Rank: 2
        Configured Memory Speed: 3200 MT/s
        Minimum Voltage: 1.2 V
        Maximum Voltage: 1.2 V
        Configured Voltage: 1.2 V
        Memory Technology: DRAM
        Memory Operating Mode Capability: Volatile memory
        Firmware Version: 0000
        Module Manufacturer ID: Bank 1, Hex 0xCE
        Module Product ID: Unknown
        Memory Subsystem Controller Manufacturer ID: Unknown
        Memory Subsystem Controller Product ID: Unknown
        Non-Volatile Size: None
        Volatile Size: 16 GB
        Cache Size: None
        Logical Size: None

Handle 0x0048, DMI type 17, 92 bytes
Memory Device
        Array Handle: 0x0033
        Error Information Handle: Not Provided
        Total Width: 72 bits
        Data Width: 64 bits
        Size: 16384 MB
        Form Factor: DIMM
        Set: None
        Locator: P2-DIMMC1
        Bank Locator: P1_Node0_Channel2_Dimm0
        Type: DDR4
        Type Detail: Synchronous Registered (Buffered)
        Speed: 3200 MT/s
        Manufacturer: Samsung
        Serial Number: H0MK0001304705CC02
        Asset Tag: P2-DIMMC1_AssetTag (date:21/30)
        Part Number: M393A2K43DB3-CWE
        Rank: 2
        Configured Memory Speed: 3200 MT/s
        Minimum Voltage: 1.2 V
        Maximum Voltage: 1.2 V
        Configured Voltage: 1.2 V
        Memory Technology: DRAM
        Memory Operating Mode Capability: Volatile memory
        Firmware Version: 0000
        Module Manufacturer ID: Bank 1, Hex 0xCE
        Module Product ID: Unknown
        Memory Subsystem Controller Manufacturer ID: Unknown
        Memory Subsystem Controller Product ID: Unknown
        Non-Volatile Size: None
        Volatile Size: 16 GB
        Cache Size: None
        Logical Size: None

Handle 0x004A, DMI type 17, 92 bytes
Memory Device
        Array Handle: 0x0033
        Error Information Handle: Not Provided
        Total Width: 72 bits
        Data Width: 64 bits
        Size: 16384 MB
        Form Factor: DIMM
        Set: None
        Locator: P2-DIMMD1
        Bank Locator: P1_Node0_Channel3_Dimm0
        Type: DDR4
        Type Detail: Synchronous Registered (Buffered)
        Speed: 3200 MT/s
        Manufacturer: Samsung
        Serial Number: H0MK0001304705CB5A
        Asset Tag: P2-DIMMD1_AssetTag (date:21/30)
        Part Number: M393A2K43DB3-CWE
        Rank: 2
        Configured Memory Speed: 3200 MT/s
        Minimum Voltage: 1.2 V
        Maximum Voltage: 1.2 V
        Configured Voltage: 1.2 V
        Memory Technology: DRAM
        Memory Operating Mode Capability: Volatile memory
        Firmware Version: 0000
        Module Manufacturer ID: Bank 1, Hex 0xCE
        Module Product ID: Unknown
        Memory Subsystem Controller Manufacturer ID: Unknown
        Memory Subsystem Controller Product ID: Unknown
        Non-Volatile Size: None
        Volatile Size: 16 GB
        Cache Size: None
        Logical Size: None

Handle 0x004C, DMI type 17, 92 bytes
Memory Device
        Array Handle: 0x0033
        Error Information Handle: Not Provided
        Total Width: 72 bits
        Data Width: 64 bits
        Size: 16384 MB
        Form Factor: DIMM
        Set: None
        Locator: P2-DIMME1
        Bank Locator: P1_Node1_Channel0_Dimm0
        Type: DDR4
        Type Detail: Synchronous Registered (Buffered)
        Speed: 3200 MT/s
        Manufacturer: Samsung
        Serial Number: H0MK0001304705CB30
        Asset Tag: P2-DIMME1_AssetTag (date:21/30)
        Part Number: M393A2K43DB3-CWE
        Rank: 2
        Configured Memory Speed: 3200 MT/s
        Minimum Voltage: 1.2 V
        Maximum Voltage: 1.2 V
        Configured Voltage: 1.2 V
        Memory Technology: DRAM
        Memory Operating Mode Capability: Volatile memory
        Firmware Version: 0000
        Module Manufacturer ID: Bank 1, Hex 0xCE
        Module Product ID: Unknown
        Memory Subsystem Controller Manufacturer ID: Unknown
        Memory Subsystem Controller Product ID: Unknown
        Non-Volatile Size: None
        Volatile Size: 16 GB
        Cache Size: None
        Logical Size: None

Handle 0x004E, DMI type 17, 92 bytes
Memory Device
        Array Handle: 0x0033
        Error Information Handle: Not Provided
        Total Width: 72 bits
        Data Width: 64 bits
        Size: 16384 MB
        Form Factor: DIMM
        Set: None
        Locator: P2-DIMMF1
        Bank Locator: P1_Node1_Channel1_Dimm0
        Type: DDR4
        Type Detail: Synchronous Registered (Buffered)
        Speed: 3200 MT/s
        Manufacturer: Samsung
        Serial Number: H0MK0001304705CB87
        Asset Tag: P2-DIMMF1_AssetTag (date:21/30)
        Part Number: M393A2K43DB3-CWE
        Rank: 2
        Configured Memory Speed: 3200 MT/s
        Minimum Voltage: 1.2 V
        Maximum Voltage: 1.2 V
        Configured Voltage: 1.2 V
        Memory Technology: DRAM
        Memory Operating Mode Capability: Volatile memory
        Firmware Version: 0000
        Module Manufacturer ID: Bank 1, Hex 0xCE
        Module Product ID: Unknown
        Memory Subsystem Controller Manufacturer ID: Unknown
        Memory Subsystem Controller Product ID: Unknown
        Non-Volatile Size: None
        Volatile Size: 16 GB
        Cache Size: None
        Logical Size: None

Handle 0x0050, DMI type 17, 92 bytes
Memory Device
        Array Handle: 0x0033
        Error Information Handle: Not Provided
        Total Width: 72 bits
        Data Width: 64 bits
        Size: 16384 MB
        Form Factor: DIMM
        Set: None
        Locator: P2-DIMMG1
        Bank Locator: P1_Node1_Channel2_Dimm0
        Type: DDR4
        Type Detail: Synchronous Registered (Buffered)
        Speed: 3200 MT/s
        Manufacturer: Samsung
        Serial Number: H0MK0001304705CB08
        Asset Tag: P2-DIMMG1_AssetTag (date:21/30)
        Part Number: M393A2K43DB3-CWE
        Rank: 2
        Configured Memory Speed: 3200 MT/s
        Minimum Voltage: 1.2 V
        Maximum Voltage: 1.2 V
        Configured Voltage: 1.2 V
        Memory Technology: DRAM
        Memory Operating Mode Capability: Volatile memory
        Firmware Version: 0000
        Module Manufacturer ID: Bank 1, Hex 0xCE
        Module Product ID: Unknown
        Memory Subsystem Controller Manufacturer ID: Unknown
        Memory Subsystem Controller Product ID: Unknown
        Non-Volatile Size: None
        Volatile Size: 16 GB
        Cache Size: None
        Logical Size: None

Handle 0x0052, DMI type 17, 92 bytes
Memory Device
        Array Handle: 0x0033
        Error Information Handle: Not Provided
        Total Width: 72 bits
        Data Width: 64 bits
        Size: 16384 MB
        Form Factor: DIMM
        Set: None
        Locator: P2-DIMMH1
        Bank Locator: P1_Node1_Channel3_Dimm0
        Type: DDR4
        Type Detail: Synchronous Registered (Buffered)
        Speed: 3200 MT/s
        Manufacturer: Samsung
        Serial Number: H0MK0001304705CC01
        Asset Tag: P2-DIMMH1_AssetTag (date:21/30)
        Part Number: M393A2K43DB3-CWE
        Rank: 2
        Configured Memory Speed: 3200 MT/s
        Minimum Voltage: 1.2 V
        Maximum Voltage: 1.2 V
        Configured Voltage: 1.2 V
        Memory Technology: DRAM
        Memory Operating Mode Capability: Volatile memory
        Firmware Version: 0000
        Module Manufacturer ID: Bank 1, Hex 0xCE
        Module Product ID: Unknown
        Memory Subsystem Controller Manufacturer ID: Unknown
        Memory Subsystem Controller Product ID: Unknown
        Non-Volatile Size: None
        Volatile Size: 16 GB
        Cache Size: None
        Logical Size: None
```

## Xeon ICX Server BIOS Configuration

### Boot Feature

```
  |                                                                    |Enables or disables Quiet    |
  |  Quiet Boot                                [Enabled]               |Boot option                  |
  |                                                                    |                             |
  |  Option ROM Messages                       [Force BIOS]            |                             |
  |  Bootup NumLock State                      [On]                    |                             |
  |  Wait For "F1" If Error                    [Disabled]              |                             |
  |  INT19 Trap Response                       [Immediate]             |                             |
  |  Re-try Boot                               [Disabled]              |                             |
  |                                                                    |                             |
  |  Power Configuration                                               |                             |
  |                                                                    |                             |
  |  Watch Dog Function                        [Disabled]              |                             |
  |  Restore on AC Power Loss                  [Last State]            |                             |
  |  Power Button Function                     [Instant Off]           |                             |
  |  Deep Sleep Mode                           [Disabled]              |                             |
```

### CPU Configuration

```
  |  Processor Configuration                                          ^|Enables Hyper Threading      |
  |  --------------------------------------------------               *|(Software Method to          |
  |  Processor BSP Revision                    606A6 - ICX D2         *|Enable/Disable Logical       |
  |  Processor Socket                          CPU1         CPU2      *|Processor threads.           |
  |  Processor ID                              000606A6* |  000606A6  *|                             |
  |  Processor Frequency                       2.600GHz  |  2.600GHz  *|                             |
  |  Processor Max Ratio                            1AH  |       1AH  *|                             |
  |  Processor Min Ratio                            08H  |       08H  *|                             |
  |  Microcode Revision                        0D000280  |  0D000280  *|                             |
  |  L1 Cache RAM(Per Core)                        80KB  |      80KB  *|                             |
  |  L2 Cache RAM(Per Core)                      1280KB  |    1280KB  *|                             |
  |  L3 Cache RAM(Per Package)                  49152KB  |   49152KB  *|                             |
  |  Processor 0 Version                       Intel(R) Xeon(R)       *|                             |
  |                                            Platinum 8358 CPU @    *|                             |
  |                                            2.60GHz                *|                             |
  |  Processor 1 Version                       Intel(R) Xeon(R)       *|                             |
  |                                            Platinum 8358 CPU @    *|                             |
  |                                            2.60GHz                *|                             |
  |                                                                   +|                             |
  |> CPU1 Core Disable Bitmap                                         +|                             |
  |> CPU2 Core Disable Bitmap                                         +|-----------------------------|
  |  Hyper-Threading [ALL]                     [Enable]               +|><: Select Screen            |
  |  Hardware Prefetcher                       [Enable]               +|^v: Select Item              |
  |  Adjacent Cache Prefetch                   [Enable]               +|Enter: Select                |
  |  DCU Streamer Prefetcher                   [Enable]               +|+/-: Change Opt.             |
  |  DCU IP Prefetcher                         [Enable]               +|F1: General Help             |
  |  LLC Prefetch                              [Enable]               +|F2: Previous Values          |
  |  Extended APIC                             [Disable]              +|F3: Optimized Defaults       |
  |  VMX                                       [Enable]               v|F4: Save & Exit              |
  |  Enable SMX                                [Disable]              +|                             |
  |  PPIN Control                              [Unlock/Enable]        *|                             |
  |  AES-NI                                    [Enable]               *|                             |
  |  --------------------------------------------------               *|                             |
  |  TME, TME-MT, TDX                                                 *|                             |
  |  --------------------------------------------------               *|                             |
  |  Total Memory Encryption (TME)             [Disabled]             *|                             |
  |  --------------------------------------------------               *|-----------------------------|
  |  Software Guard Extension (SGX)                                   *|><: Select Screen            |
  |  --------------------------------------------------               *|^v: Select Item              |
  |  SGX Factory Reset                         [Disabled]             *|Enter: Select                |
  |  SW Guard Extensions (SGX)                 [Disabled]             *|+/-: Change Opt.             |
  |  SGX Package Info In-Band Access           [Disabled]             *|F1: General Help             |
  |  --------------------------------------------------               *|F2: Previous Values          |
  |  Limit CPU PA to 46 Bits                   [Enable]               *|F3: Optimized Defaults       |
  |> Advanced Power Management Configuration                          v|F4: Save & Exit              |
```

#### Advanced Power Management Configuration

```
  |  Advanced Power Management Configuration                           |Enable processor power       |
  |  --------------------------------------------------                |management features.         |
  |  Power Technology                          [Custom]                |                             |
  |  Power Performance Tuning                  [BIOS Controls EPB]     |                             |
  |  ENERGY_PERF_BIAS_CFG Mode                 [Maximum Performance]   |                             |
```

##### CPU P State Control

```
  |  CPU P State Control                                               |EIST allows the processor    |
  |                                                                    |to dynamically adjust        |
  |  SpeedStep (P-States)                      [Disable]               |frequency and voltage based  |
  |  Activate SST-BF                           [Disable]               |on power versus performance  |
  |  Configure SST-BF                          [Enable]                |needs.                       |
  |  EIST PSD Function                         [HW_ALL]                |                             |
```

##### Hardware PM State Control

```
  |  Hardware PM State Control                                         |If set to Disable, hardware ^|
  |                                                                    |will choose a P-state       *|
  |  Hardware P-States                         [Disable]               |setting for the system      *|
  |                                                                    |based on an OS request.     *|

  |  Frequency Prioritization                                          |This knob controls whether   |
  |                                                                    |RAPL balancer is enabled.    |
  |  RAPL Prioritization                       [Disable]               |When enabled it activates    |
```

##### CPU C State Control

```
  |  CPU C State Control                                               |Allows Monitor and MWAIT     |
  |                                                                    |instructions.                |
  |  Enable Monitor MWAIT                      [Enable]                |                             |
  |  CPU C6 Report                             [Disable]               |                             |
  |  Enhanced Halt State (C1E)                 [Disable]               |                             |
```

##### Package C State Control

```
  |  Package C State Control                                           |Limit the lowest package     |
  |                                                                    |level C-State to             |
  |  Package C State                           [C0/C1 state]           |processors. Lower package    |
```

##### CPU T State Control

```
  |  CPU T State Control                                               |Enable/Disable CPU           |
  |                                                                    |throttling by OS.            |
  |  Software Controlled T-States              [Disable]               |Throttling reduces power     |
```

##### UPI Configuration

```
  |  Uncore Configuration                                              |Choose Topology Precedence   |
  |  --------------------------------------------------                |to degrade features if       |
  |  Number of CPU                             2                       |system options are in        |
  |  Number of IIO                             2                       |conflict or choose Feature   |
  |  Current UPI Link Speed                    Fast                    |Precedence to degrade        |
  |  Current UPI Link Frequency                11.2 GT/s               |topology if system options   |
  |  Global MMIO Low Base / Limit              90000000 / FBFFFFFF     |are in conflict.             |
  |  Global MMIO High Base / Limit             0000200000000000 /      |                             |
  |                                            0000204FFFFFFFFF        |                             |
  |  Pci-e Configuration Base / Size           80000000 / 10000000     |                             |
  |  Degrade Precedence                        [Topology Precedence]   |                             |
  |  Link L0p Enable                           [Disable]               |                             |
  |  Link L1 Enable                            [Disable]               |                             |
  |  XPT Remote Prefetch                       [Auto]                  |                             |
  |  KTI Prefetch                              [Auto]                  |-----------------------------|
  |  Local/Remote Threshold                    [Auto]                  |><: Select Screen            |
  |  IO Directory Cache (IODC)                 [Auto]                  |^v: Select Item              |
  |  SNC (Sub NUMA)                            [Disable]               |Enter: Select                |
  |  XPT Prefetch                              [Auto]                  |+/-: Change Opt.             |
  |  Snoop Throttle Configuration              [Auto]                  |F1: General Help             |
  |  PCIe Remote P2P Relaxed Ordering          [Disable]               |F2: Previous Values          |
  |  Stale AtoS                                [Auto]                  |F3: Optimized Defaults       |
  |  LLC Dead Line Alloc                       [Enable]                |F4: Save & Exit              |
```

##### Memory Configuration

```
  |                                                                    |Set Enable or Disable        |
  |  --------------------------------------------------                |STEP(Samsung TestBIOS &      |
  |  Integrated Memory Controller (iMC)                                |Enhanced PPR)function        |
  |  --------------------------------------------------                |                             |
  |                                                                    |                             |
  |  STEP DRAM Test                            [Disable]               |                             |
  |   Operation Mode                           [Test and Repair]       |                             |
  |  Enforce POR                               [POR]                   |                             |
  |  PPR Type                                  [Hard PPR]              |                             |
  |  Memory Frequency                          [Auto]                  |                             |
  |  Data Scrambling for DDR4                  [Enable]                |                             |
  |  2x Refresh Enable                         [Auto]                  |                             |
```

##### IIO Configuration

```
  |  IIO Configuration                                                 |Press <Enter> to bring up    |
  |  --------------------------------------------------                |the Intel. Virtualization    |
  |                                                                    |for Directed I/O (VT-d)      |
  |> CPU1 Configuration                                                |Configuration menu.          |
  |> CPU2 Configuration                                                |                             |
  |> IOAT Configuration                                                |                             |
  |> Intel. VT for Directed I/O (VT-d)                                 |                             |
  |> Intel. VMD Technology                                             |                             |
  |  PCI-E ASPM Support (Global)               [Disable]               |                             |
  |  IIO eDPC Support                          [Disable]               |                             |
```

##### CPU1 Configuration

```
  |  IOU0 (IIO PCIe Port 1)                    [Auto]                  |Selects PCIe port            |
  |  IOU1 (IIO PCIe Port 2)                    [Auto]                  |Bifurcation for selected     |
  |  IOU3 (IIO PCIe Port 4)                    [Auto]                  |slot(s)                      |
  |  IOU4 (IIO PCIe Port 5)                    [Auto]                  |                             |
```

##### CPU2 Configuration

```
  |  IOU0 (IIO PCIe Port 1)                    [Auto]                  |Selects PCIe port            |
  |  IOU1 (IIO PCIe Port 2)                    [Auto]                  |Bifurcation for selected     |
  |  IOU3 (IIO PCIe Port 4)                    [Auto]                  |slot(s)                      |
  |  IOU4 (IIO PCIe Port 5)                    [Auto]                  |                             |
```

#### South Bridge

```
  |  USB Module Version                        26                      |AUTO option disables legacy  |
  |                                                                    |support if no USB devices    |
  |  USB Devices:                                                      |are connected. DISABLE       |
  |        1 Drive, 2 Keyboards, 2 Mice, 1 Hub                         |option will keep USB         |
  |                                                                    |devices available only for   |
  |  Legacy USB Support                        [Enabled]               |EFI applications.            |
  |  XHCI Hand-off                             [Enabled]               |                             |
  |  Port 60/64 Emulation                      [Disabled]              |                             |
  |  PCIe PLL SSC                              [Disabled]              |                             |
  |  Port 61h Bit-4 Emulation                  [Disabled]              |                             |
```

### PCIe/PCI/PnP Configuration

```
  |  PCI Bus Driver Version                    A5.01.24               ^|Enables or Disables 64bit    |
  |                                                                   *|capable Devices to be        |
  |  PCI Devices Common Settings:                                     *|Decoded in Above 4G Address  |
  |  Above 4G Decoding                         [Enabled]              *|Space (Only if System        |
  |  SR-IOV Support                            [Enabled]              *|Supports 64 bit PCI          |
  |  ARI Support                               [Enabled]              *|Decoding).                   |
  |  Bus Master Enable                         [Enabled]              *|                             |
  |  Consistent Device Name Support            [Disabled]             *|                             |
  |  MMIO High Base                            [32T]                  *|                             |
  |  MMIO High Granularity Size                [64G]                  *|                             |
  |  Maximum Read Request                      [Auto]                 *|                             |
  |  MMCFG Base                                [Auto]                 *|                             |
  |  NVMe Firmware Source                      [Vendor Defined        *|                             |
  |                                            Firmware]              *|                             |
  |  VGA Priority                              [Onboard]              *|                             |
  |  CPU1 SLOT2 PCI-E 3.0 X16 OPROM            [EFI]                  *|                             |
  |  CPU1 SLOT4 PCI-E 3.0 X16 OPROM            [EFI]                  *|                             |
  |  CPU2 SLOT6 PCI-E 3.0 X16 OPROM            [EFI]                  *|                             |
  |  CPU2 SLOT8 PCI-E 3.0 X16 OPROM            [EFI]                  *|-----------------------------|
  |  CPU1 SLOT9 PCI-E 3.0 X16 OPROM            [EFI]                  *|><: Select Screen            |
  |  CPU2 SLOT10 PCI-E 3.0 X16 OPROM           [EFI]                  *|^v: Select Item              |
  |  CPU2 SLOT11 PCI-E 3.0 X4(IN X8) OPROM     [EFI]                  *|Enter: Select                |
  |  M.2 CONNECTOR OPROM                       [EFI]                  *|+/-: Change Opt.             |
  |  Bus Master Enable                         [Enabled]              +|F1: General Help             |
  |  Onboard LAN1 Option ROM                   [EFI]                  +|F2: Previous Values          |
  |  Onboard LAN2 Option ROM                   [Disabled]             +|F3: Optimized Defaults       |
  |  Onboard Video Option ROM                  [EFI]                  v|F4: Save & Exit              |
  |> Network Stack Configuration                                       |                             |
```

## Xeon ICX Server Firmware Inventory

```
Host.           IPMI IP.      BMC.      BIOS. CPLD.     CPU Microcode.  PCI Bus.   X710 Firmware.            i40e.    E810 Firmware.            ice.
s65-t37-sut1.   10.30.50.75.  1.00.21.  1.1.  F1.00.07. 0D000280.       A5.01.24.  8.30 0x8000a49d 1.2926.0. 2.17.15. 3.20 0x8000d83e 1.3146.0. 1.8.3.
s66-t37-sut2.   10.30.50.76.  1.00.21.  1.1.  F1.00.07. 0D000280.       A5.01.24.  8.30 0x8000a49d 1.2926.0. 2.14.15. 3.20 0x8000d83e 1.3146.0. 1.8.3.
s67-t37-tg1.    10.30.50.77.  1.00.21.  1.1.  F1.00.07. 0D000280.       A5.01.24.  8.30 0x8000a49d 1.2926.0. 2.14.13. 3.20 0x8000d83e 1.3146.0. 1.8.3.
s71-t212-sut1.  10.30.50.81.  1.00.21.  1.1.  F1.00.07. 0D000280.       A5.01.24.  8.30 0x8000a49d 1.2926.0. 2.17.15. 3.20 0x8000d83e 1.3146.0. 1.8.3.
s72-t212-tg1.   10.30.50.82.  1.00.21.  1.1.  F1.00.07. 0D000280.       A5.01.24.  8.30 0x8000a49d 1.2926.0. 2.14.13. 3.20 0x8000d83e 1.3146.0. 1.8.3.
s83-t213-sut1.  10.30.50.83.  1.00.21.  1.1.  F1.00.07. 0D000280.       A5.01.24.  8.30 0x8000a49d 1.2926.0. 2.17.15. 3.20 0x8000d83e 1.3146.0. 1.8.3.
s84-t213-tg1.   10.30.50.84.  1.00.21.  1.1.  F1.00.07. 0D000280.       A5.01.24.  8.30 0x8000a49d 1.2926.0. 2.14.13. 3.20 0x8000d83e 1.3146.0. 1.8.3.
s85-t214-sut1.  10.30.50.85.  1.00.21.  1.1.  F1.00.07. 0D000280.       A5.01.24.  8.30 0x8000a49d 1.2926.0. 2.17.15. 3.20 0x8000d83e 1.3146.0. 1.8.3.
s86-t214-tg1.   10.30.50.86.  1.00.21.  1.1.  F1.00.07. 0D000280.       A5.01.24.  8.30 0x8000a49d 1.2926.0. 2.14.13. 3.20 0x8000d83e 1.3146.0. 1.8.3.
s87-t215-sut1.  10.30.50.87.  1.00.21.  1.1.  F1.00.07. 0D000280.       A5.01.24.  8.30 0x8000a49d 1.2926.0. 2.17.15. 3.20 0x8000d83e 1.3146.0. 1.8.3.
s88-t215-tg1.   10.30.50.88.  1.00.21.  1.1.  F1.00.07. 0D000280.       A5.01.24.  8.30 0x8000a49d 1.2926.0. 2.14.13. 3.20 0x8000d83e 1.3146.0. 1.8.3.
```
