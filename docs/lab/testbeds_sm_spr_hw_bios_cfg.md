# SuperMicro SapphireRapids Servers - HW and BIOS Configuration

1. [Linux lscpu](#linux-lscpu)
1. [Linux dmidecode](#dmidecode)
1. [Linux dmidecode memory](#linux-dmidecode-memory)
1. [Xeon SPR Server Firmware Inventory](#xeon-spr-server-firmware-inventory)

## Linux lscpu

```
Architecture:            x86_64
  CPU op-mode(s):        32-bit, 64-bit
  Address sizes:         46 bits physical, 57 bits virtual
  Byte Order:            Little Endian
CPU(s):                  128
  On-line CPU(s) list:   0-127
Vendor ID:               GenuineIntel
  Model name:            Intel(R) Xeon(R) Platinum 8462Y+
    CPU family:          6
    Model:               143
    Thread(s) per core:  2
    Core(s) per socket:  32
    Socket(s):           2
    Stepping:            8
    BogoMIPS:            5600.00
    Flags:               fpu vme de pse tsc msr pae mce cx8 apic sep mtrr pge mca cmov pat pse36 clflush dts acpi mmx fxsr sse sse2 ss ht tm pbe syscall nx pdpe1
                         gb rdtscp lm constant_tsc art arch_perfmon pebs bts rep_good nopl xtopology nonstop_tsc cpuid aperfmperf tsc_known_freq pni pclmulqdq dt
                         es64 monitor ds_cpl vmx smx est tm2 ssse3 sdbg fma cx16 xtpr pdcm pcid dca sse4_1 sse4_2 x2apic movbe popcnt tsc_deadline_timer aes xsav
                         e avx f16c rdrand lahf_lm abm 3dnowprefetch cpuid_fault epb cat_l3 cat_l2 cdp_l3 invpcid_single cdp_l2 ssbd mba ibrs ibpb stibp ibrs_enh
                         anced tpr_shadow vnmi flexpriority ept vpid ept_ad fsgsbase tsc_adjust bmi1 avx2 smep bmi2 erms invpcid cqm rdt_a avx512f avx512dq rdsee
                         d adx smap avx512ifma clflushopt clwb intel_pt avx512cd sha_ni avx512bw avx512vl xsaveopt xsavec xgetbv1 xsaves cqm_llc cqm_occup_llc cq
                         m_mbm_total cqm_mbm_local split_lock_detect avx_vnni avx512_bf16 wbnoinvd dtherm arat pln pts hwp hwp_act_window hwp_epp hwp_pkg_req avx
                         512vbmi umip pku ospke waitpkg avx512_vbmi2 gfni vaes vpclmulqdq avx512_vnni avx512_bitalg tme avx512_vpopcntdq la57 rdpid bus_lock_dete
                         ct cldemote movdiri movdir64b enqcmd fsrm md_clear serialize tsxldtrk pconfig arch_lbr amx_bf16 avx512_fp16 amx_tile amx_int8 flush_l1d
                         arch_capabilities
Virtualization features:
  Virtualization:        VT-x
Caches (sum of all):
  L1d:                   3 MiB (64 instances)
  L1i:                   2 MiB (64 instances)
  L2:                    128 MiB (64 instances)
  L3:                    120 MiB (2 instances)
NUMA:
  NUMA node(s):          2
  NUMA node0 CPU(s):     0-31,64-95
  NUMA node1 CPU(s):     32-63,96-127
Vulnerabilities:
  Itlb multihit:         Not affected
  L1tf:                  Not affected
  Mds:                   Not affected
  Meltdown:              Not affected
  Mmio stale data:       Not affected
  Retbleed:              Not affected
  Spec store bypass:     Mitigation; Speculative Store Bypass disabled via prctl and seccomp
  Spectre v1:            Mitigation; usercopy/swapgs barriers and __user pointer sanitization
  Spectre v2:            Mitigation; Enhanced IBRS, IBPB conditional, RSB filling
  Srbds:                 Not affected
  Tsx async abort:       Not affected
```

## Linux dmidecode

```
# dmidecode 3.3
Getting SMBIOS data from sysfs.
SMBIOS 3.5.0 present.
Table at 0x000E6E00.

Handle 0x0000, DMI type 0, 26 bytes
BIOS Information
        Vendor: American Megatrends International, LLC.
        Version: 1.0
        Release Date: 11/16/2022
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
                ACPI is supported
                USB legacy is supported
                BIOS boot specification is supported
                Targeted content distribution is supported
                UEFI is supported
        BIOS Revision: 5.29

Handle 0x0001, DMI type 1, 27 bytes
System Information
        Manufacturer: Supermicro
        Product Name: SYS-741GE-TNRT
        Version: 0123456789
        Serial Number: S512539X3109946
        UUID: 00000000-0000-0000-0000-7cc255275836
        Wake-up Type: Power Switch
        SKU Number: To be filled by O.E.M.
        Family: Family

Handle 0x0002, DMI type 2, 15 bytes
Base Board Information
        Manufacturer: Supermicro
        Product Name: X13DEG-QT
        Version: 1.10
        Serial Number: OM22CS039806
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
        Serial Number: C7490FL36A40118
        Asset Tag: Chassis Asset Tag
        Boot-up State: Safe
        Power Supply State: Safe
        Thermal State: Safe
        Security Status: None
        OEM Information: 0x00000000
        Height: Unspecified
        Number Of Power Cords: 1
        Contained Elements: 0
        SKU Number: 0123456789

Handle 0x0032, DMI type 4, 50 bytes
Processor Information
        Socket Designation: CPU1
        Type: Central Processor
        Family: Xeon
        Manufacturer: Intel(R) Corporation
        ID: F8 06 08 00 FF FB EB BF
        Signature: Type 0, Family 6, Model 143, Stepping 8
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
        Version: Intel(R) Xeon(R) Platinum 8462Y+
        Voltage: 1.6 V
        External Clock: 100 MHz
        Max Speed: 4000 MHz
        Current Speed: 2800 MHz
        Status: Populated, Enabled
        Upgrade: Socket LGA4677
        L1 Cache Handle: 0x002F
        L2 Cache Handle: 0x0030
        L3 Cache Handle: 0x0031
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

Handle 0x0036, DMI type 4, 50 bytes
Processor Information
        Socket Designation: CPU2
        Type: Central Processor
        Family: Xeon
        Manufacturer: Intel(R) Corporation
        ID: F8 06 08 00 FF FB EB BF
        Signature: Type 0, Family 6, Model 143, Stepping 8
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
        Version: Intel(R) Xeon(R) Platinum 8462Y+
        Voltage: 1.6 V
        External Clock: 100 MHz
        Max Speed: 4000 MHz
        Current Speed: 2800 MHz
        Status: Populated, Enabled
        Upgrade: Socket LGA4677
        L1 Cache Handle: 0x0033
        L2 Cache Handle: 0x0034
        L3 Cache Handle: 0x0035
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

## Linux dmidecode memory

```
Handle 0x003D, DMI type 17, 92 bytes
Memory Device
        Array Handle: 0x003C
        Error Information Handle: Not Provided
        Total Width: 80 bits
        Data Width: 64 bits
        Size: 32 GB
        Form Factor: DIMM
        Set: None
        Locator: P1-DIMMA1
        Bank Locator: P0_Node0_Channel0_Dimm0
        Type: DDR5
        Type Detail: Synchronous Registered (Buffered)
        Speed: 4800 MT/s
        Manufacturer: SK Hynix
        Serial Number: 80AD0122149612A27F
        Asset Tag: P1-DIMMA1_AssetTag (date:22/14)
        Part Number: HMCG88MEBRA107N
        Rank: 2
        Configured Memory Speed: 4800 MT/s
        Minimum Voltage: 1.1 V
        Maximum Voltage: 1.1 V
        Configured Voltage: 1.1 V
        Memory Technology: DRAM
        Memory Operating Mode Capability: Volatile memory
        Firmware Version: 0000
        Module Manufacturer ID: Bank 1, Hex 0xAD
        Module Product ID: 0xAD00
        Memory Subsystem Controller Manufacturer ID: Unknown
        Memory Subsystem Controller Product ID: Unknown
        Non-Volatile Size: None
        Volatile Size: 32 GB
        Cache Size: None
        Logical Size: None

Handle 0x003E, DMI type 17, 92 bytes
Memory Device
        Array Handle: 0x003C
        Error Information Handle: Not Provided
        Total Width: 80 bits
        Data Width: 64 bits
        Size: 32 GB
        Form Factor: DIMM
        Set: None
        Locator: P1-DIMMB1
        Bank Locator: P0_Node0_Channel1_Dimm0
        Type: DDR5
        Type Detail: Synchronous Registered (Buffered)
        Speed: 4800 MT/s
        Manufacturer: SK Hynix
        Serial Number: 80AD0122149612A1CC
        Asset Tag: P1-DIMMB1_AssetTag (date:22/14)
        Part Number: HMCG88MEBRA107N
        Rank: 2
        Configured Memory Speed: 4800 MT/s
        Minimum Voltage: 1.1 V
        Maximum Voltage: 1.1 V
        Configured Voltage: 1.1 V
        Memory Technology: DRAM
        Memory Operating Mode Capability: Volatile memory
        Firmware Version: 0000
        Module Manufacturer ID: Bank 1, Hex 0xAD
        Module Product ID: 0xAD00
        Memory Subsystem Controller Manufacturer ID: Unknown
        Memory Subsystem Controller Product ID: Unknown
        Non-Volatile Size: None
        Volatile Size: 32 GB
        Cache Size: None
        Logical Size: None

Handle 0x003F, DMI type 17, 92 bytes
Memory Device
        Array Handle: 0x003C
        Error Information Handle: Not Provided
        Total Width: 80 bits
        Data Width: 64 bits
        Size: 32 GB
        Form Factor: DIMM
        Set: None
        Locator: P1-DIMMC1
        Bank Locator: P0_Node0_Channel2_Dimm0
        Type: DDR5
        Type Detail: Synchronous Registered (Buffered)
        Speed: 4800 MT/s
        Manufacturer: SK Hynix
        Serial Number: 80AD0122149612A1B7
        Asset Tag: P1-DIMMC1_AssetTag (date:22/14)
        Part Number: HMCG88MEBRA107N
        Rank: 2
        Configured Memory Speed: 4800 MT/s
        Minimum Voltage: 1.1 V
        Maximum Voltage: 1.1 V
        Configured Voltage: 1.1 V
        Memory Technology: DRAM
        Memory Operating Mode Capability: Volatile memory
        Firmware Version: 0000
        Module Manufacturer ID: Bank 1, Hex 0xAD
        Module Product ID: 0xAD00
        Memory Subsystem Controller Manufacturer ID: Unknown
        Memory Subsystem Controller Product ID: Unknown
        Non-Volatile Size: None
        Volatile Size: 32 GB
        Cache Size: None
        Logical Size: None

Handle 0x0040, DMI type 17, 92 bytes
Memory Device
        Array Handle: 0x003C
        Error Information Handle: Not Provided
        Total Width: 80 bits
        Data Width: 64 bits
        Size: 32 GB
        Form Factor: DIMM
        Set: None
        Locator: P1-DIMMD1
        Bank Locator: P0_Node0_Channel3_Dimm0
        Type: DDR5
        Type Detail: Synchronous Registered (Buffered)
        Speed: 4800 MT/s
        Manufacturer: SK Hynix
        Serial Number: 80AD0122149612927A
        Asset Tag: P1-DIMMD1_AssetTag (date:22/14)
        Part Number: HMCG88MEBRA107N
        Rank: 2
        Configured Memory Speed: 4800 MT/s
        Minimum Voltage: 1.1 V
        Maximum Voltage: 1.1 V
        Configured Voltage: 1.1 V
        Memory Technology: DRAM
        Memory Operating Mode Capability: Volatile memory
        Firmware Version: 0000
        Module Manufacturer ID: Bank 1, Hex 0xAD
        Module Product ID: 0xAD00
        Memory Subsystem Controller Manufacturer ID: Unknown
        Memory Subsystem Controller Product ID: Unknown
        Non-Volatile Size: None
        Volatile Size: 32 GB
        Cache Size: None
        Logical Size: None

Handle 0x0041, DMI type 17, 92 bytes
Memory Device
        Array Handle: 0x003C
        Error Information Handle: Not Provided
        Total Width: 80 bits
        Data Width: 64 bits
        Size: 32 GB
        Form Factor: DIMM
        Set: None
        Locator: P1-DIMME1
        Bank Locator: P0_Node1_Channel0_Dimm0
        Type: DDR5
        Type Detail: Synchronous Registered (Buffered)
        Speed: 4800 MT/s
        Manufacturer: SK Hynix
        Serial Number: 80AD0122149612A2B2
        Asset Tag: P1-DIMME1_AssetTag (date:22/14)
        Part Number: HMCG88MEBRA107N
        Rank: 2
        Configured Memory Speed: 4800 MT/s
        Minimum Voltage: 1.1 V
        Maximum Voltage: 1.1 V
        Configured Voltage: 1.1 V
        Memory Technology: DRAM
        Memory Operating Mode Capability: Volatile memory
        Firmware Version: 0000
        Module Manufacturer ID: Bank 1, Hex 0xAD
        Module Product ID: 0xAD00
        Memory Subsystem Controller Manufacturer ID: Unknown
        Memory Subsystem Controller Product ID: Unknown
        Non-Volatile Size: None
        Volatile Size: 32 GB
        Cache Size: None
        Logical Size: None

Handle 0x0042, DMI type 17, 92 bytes
Memory Device
        Array Handle: 0x003C
        Error Information Handle: Not Provided
        Total Width: 80 bits
        Data Width: 64 bits
        Size: 32 GB
        Form Factor: DIMM
        Set: None
        Locator: P1-DIMMF1
        Bank Locator: P0_Node1_Channel1_Dimm0
        Type: DDR5
        Type Detail: Synchronous Registered (Buffered)
        Speed: 4800 MT/s
        Manufacturer: SK Hynix
        Serial Number: 80AD0122149612A7F0
        Asset Tag: P1-DIMMF1_AssetTag (date:22/14)
        Part Number: HMCG88MEBRA107N
        Rank: 2
        Configured Memory Speed: 4800 MT/s
        Minimum Voltage: 1.1 V
        Maximum Voltage: 1.1 V
        Configured Voltage: 1.1 V
        Memory Technology: DRAM
        Memory Operating Mode Capability: Volatile memory
        Firmware Version: 0000
        Module Manufacturer ID: Bank 1, Hex 0xAD
        Module Product ID: 0xAD00
        Memory Subsystem Controller Manufacturer ID: Unknown
        Memory Subsystem Controller Product ID: Unknown
        Non-Volatile Size: None
        Volatile Size: 32 GB
        Cache Size: None
        Logical Size: None

Handle 0x0043, DMI type 17, 92 bytes
Memory Device
        Array Handle: 0x003C
        Error Information Handle: Not Provided
        Total Width: 80 bits
        Data Width: 64 bits
        Size: 32 GB
        Form Factor: DIMM
        Set: None
        Locator: P1-DIMMG1
        Bank Locator: P0_Node1_Channel2_Dimm0
        Type: DDR5
        Type Detail: Synchronous Registered (Buffered)
        Speed: 4800 MT/s
        Manufacturer: SK Hynix
        Serial Number: 80AD0122149612A1B0
        Asset Tag: P1-DIMMG1_AssetTag (date:22/14)
        Part Number: HMCG88MEBRA107N
        Rank: 2
        Configured Memory Speed: 4800 MT/s
        Minimum Voltage: 1.1 V
        Maximum Voltage: 1.1 V
        Configured Voltage: 1.1 V
        Memory Technology: DRAM
        Memory Operating Mode Capability: Volatile memory
        Firmware Version: 0000
        Module Manufacturer ID: Bank 1, Hex 0xAD
        Module Product ID: 0xAD00
        Memory Subsystem Controller Manufacturer ID: Unknown
        Memory Subsystem Controller Product ID: Unknown
        Non-Volatile Size: None
        Volatile Size: 32 GB
        Cache Size: None
        Logical Size: None

Handle 0x0044, DMI type 17, 92 bytes
Memory Device
        Array Handle: 0x003C
        Error Information Handle: Not Provided
        Total Width: 80 bits
        Data Width: 64 bits
        Size: 32 GB
        Form Factor: DIMM
        Set: None
        Locator: P1-DIMMH1
        Bank Locator: P0_Node1_Channel3_Dimm0
        Type: DDR5
        Type Detail: Synchronous Registered (Buffered)
        Speed: 4800 MT/s
        Manufacturer: SK Hynix
        Serial Number: 80AD012214961292F4
        Asset Tag: P1-DIMMH1_AssetTag (date:22/14)
        Part Number: HMCG88MEBRA107N
        Rank: 2
        Configured Memory Speed: 4800 MT/s
        Minimum Voltage: 1.1 V
        Maximum Voltage: 1.1 V
        Configured Voltage: 1.1 V
        Memory Technology: DRAM
        Memory Operating Mode Capability: Volatile memory
        Firmware Version: 0000
        Module Manufacturer ID: Bank 1, Hex 0xAD
        Module Product ID: 0xAD00
        Memory Subsystem Controller Manufacturer ID: Unknown
        Memory Subsystem Controller Product ID: Unknown
        Non-Volatile Size: None
        Volatile Size: 32 GB
        Cache Size: None
        Logical Size: None

Handle 0x0045, DMI type 17, 92 bytes
Memory Device
        Array Handle: 0x003C
        Error Information Handle: Not Provided
        Total Width: 80 bits
        Data Width: 64 bits
        Size: 32 GB
        Form Factor: DIMM
        Set: None
        Locator: P2-DIMMA1
        Bank Locator: P1_Node0_Channel0_Dimm0
        Type: DDR5
        Type Detail: Synchronous Registered (Buffered)
        Speed: 4800 MT/s
        Manufacturer: SK Hynix
        Serial Number: 80AD01221496129322
        Asset Tag: P2-DIMMA1_AssetTag (date:22/14)
        Part Number: HMCG88MEBRA107N
        Rank: 2
        Configured Memory Speed: 4800 MT/s
        Minimum Voltage: 1.1 V
        Maximum Voltage: 1.1 V
        Configured Voltage: 1.1 V
        Memory Technology: DRAM
        Memory Operating Mode Capability: Volatile memory
        Firmware Version: 0000
        Module Manufacturer ID: Bank 1, Hex 0xAD
        Module Product ID: 0xAD00
        Memory Subsystem Controller Manufacturer ID: Unknown
        Memory Subsystem Controller Product ID: Unknown
        Non-Volatile Size: None
        Volatile Size: 32 GB
        Cache Size: None
        Logical Size: None

Handle 0x0046, DMI type 17, 92 bytes
Memory Device
        Array Handle: 0x003C
        Error Information Handle: Not Provided
        Total Width: 80 bits
        Data Width: 64 bits
        Size: 32 GB
        Form Factor: DIMM
        Set: None
        Locator: P2-DIMMB1
        Bank Locator: P1_Node0_Channel1_Dimm0
        Type: DDR5
        Type Detail: Synchronous Registered (Buffered)
        Speed: 4800 MT/s
        Manufacturer: SK Hynix
        Serial Number: 80AD0122149612A282
        Asset Tag: P2-DIMMB1_AssetTag (date:22/14)
        Part Number: HMCG88MEBRA107N
        Rank: 2
        Configured Memory Speed: 4800 MT/s
        Minimum Voltage: 1.1 V
        Maximum Voltage: 1.1 V
        Configured Voltage: 1.1 V
        Memory Technology: DRAM
        Memory Operating Mode Capability: Volatile memory
        Firmware Version: 0000
        Module Manufacturer ID: Bank 1, Hex 0xAD
        Module Product ID: 0xAD00
        Memory Subsystem Controller Manufacturer ID: Unknown
        Memory Subsystem Controller Product ID: Unknown
        Non-Volatile Size: None
        Volatile Size: 32 GB
        Cache Size: None
        Logical Size: None

Handle 0x0047, DMI type 17, 92 bytes
Memory Device
        Array Handle: 0x003C
        Error Information Handle: Not Provided
        Total Width: 80 bits
        Data Width: 64 bits
        Size: 32 GB
        Form Factor: DIMM
        Set: None
        Locator: P2-DIMMC1
        Bank Locator: P1_Node0_Channel2_Dimm0
        Type: DDR5
        Type Detail: Synchronous Registered (Buffered)
        Speed: 4800 MT/s
        Manufacturer: SK Hynix
        Serial Number: 80AD0122149612936B
        Asset Tag: P2-DIMMC1_AssetTag (date:22/14)
        Part Number: HMCG88MEBRA107N
        Rank: 2
        Configured Memory Speed: 4800 MT/s
        Minimum Voltage: 1.1 V
        Maximum Voltage: 1.1 V
        Configured Voltage: 1.1 V
        Memory Technology: DRAM
        Memory Operating Mode Capability: Volatile memory
        Firmware Version: 0000
        Module Manufacturer ID: Bank 1, Hex 0xAD
        Module Product ID: 0xAD00
        Memory Subsystem Controller Manufacturer ID: Unknown
        Memory Subsystem Controller Product ID: Unknown
        Non-Volatile Size: None
        Volatile Size: 32 GB
        Cache Size: None
        Logical Size: None

Handle 0x0048, DMI type 17, 92 bytes
Memory Device
        Array Handle: 0x003C
        Error Information Handle: Not Provided
        Total Width: 80 bits
        Data Width: 64 bits
        Size: 32 GB
        Form Factor: DIMM
        Set: None
        Locator: P2-DIMMD1
        Bank Locator: P1_Node0_Channel3_Dimm0
        Type: DDR5
        Type Detail: Synchronous Registered (Buffered)
        Speed: 4800 MT/s
        Manufacturer: SK Hynix
        Serial Number: 80AD012214961292FA
        Asset Tag: P2-DIMMD1_AssetTag (date:22/14)
        Part Number: HMCG88MEBRA107N
        Rank: 2
        Configured Memory Speed: 4800 MT/s
        Minimum Voltage: 1.1 V
        Maximum Voltage: 1.1 V
        Configured Voltage: 1.1 V
        Memory Technology: DRAM
        Memory Operating Mode Capability: Volatile memory
        Firmware Version: 0000
        Module Manufacturer ID: Bank 1, Hex 0xAD
        Module Product ID: 0xAD00
        Memory Subsystem Controller Manufacturer ID: Unknown
        Memory Subsystem Controller Product ID: Unknown
        Non-Volatile Size: None
        Volatile Size: 32 GB
        Cache Size: None
        Logical Size: None

Handle 0x0049, DMI type 17, 92 bytes
Memory Device
        Array Handle: 0x003C
        Error Information Handle: Not Provided
        Total Width: 80 bits
        Data Width: 64 bits
        Size: 32 GB
        Form Factor: DIMM
        Set: None
        Locator: P2-DIMME1
        Bank Locator: P1_Node1_Channel0_Dimm0
        Type: DDR5
        Type Detail: Synchronous Registered (Buffered)
        Speed: 4800 MT/s
        Manufacturer: SK Hynix
        Serial Number: 80AD012214961292ED
        Asset Tag: P2-DIMME1_AssetTag (date:22/14)
        Part Number: HMCG88MEBRA107N
        Rank: 2
        Configured Memory Speed: 4800 MT/s
        Minimum Voltage: 1.1 V
        Maximum Voltage: 1.1 V
        Configured Voltage: 1.1 V
        Memory Technology: DRAM
        Memory Operating Mode Capability: Volatile memory
        Firmware Version: 0000
        Module Manufacturer ID: Bank 1, Hex 0xAD
        Module Product ID: 0xAD00
        Memory Subsystem Controller Manufacturer ID: Unknown
        Memory Subsystem Controller Product ID: Unknown
        Non-Volatile Size: None
        Volatile Size: 32 GB
        Cache Size: None
        Logical Size: None

Handle 0x004A, DMI type 17, 92 bytes
Memory Device
        Array Handle: 0x003C
        Error Information Handle: Not Provided
        Total Width: 80 bits
        Data Width: 64 bits
        Size: 32 GB
        Form Factor: DIMM
        Set: None
        Locator: P2-DIMMF1
        Bank Locator: P1_Node1_Channel1_Dimm0
        Type: DDR5
        Type Detail: Synchronous Registered (Buffered)
        Speed: 4800 MT/s
        Manufacturer: SK Hynix
        Serial Number: 80AD0122149612A888
        Asset Tag: P2-DIMMF1_AssetTag (date:22/14)
        Part Number: HMCG88MEBRA107N
        Rank: 2
        Configured Memory Speed: 4800 MT/s
        Minimum Voltage: 1.1 V
        Maximum Voltage: 1.1 V
        Configured Voltage: 1.1 V
        Memory Technology: DRAM
        Memory Operating Mode Capability: Volatile memory
        Firmware Version: 0000
        Module Manufacturer ID: Bank 1, Hex 0xAD
        Module Product ID: 0xAD00
        Memory Subsystem Controller Manufacturer ID: Unknown
        Memory Subsystem Controller Product ID: Unknown
        Non-Volatile Size: None
        Volatile Size: 32 GB
        Cache Size: None
        Logical Size: None

Handle 0x004B, DMI type 17, 92 bytes
Memory Device
        Array Handle: 0x003C
        Error Information Handle: Not Provided
        Total Width: 80 bits
        Data Width: 64 bits
        Size: 32 GB
        Form Factor: DIMM
        Set: None
        Locator: P2-DIMMG1
        Bank Locator: P1_Node1_Channel2_Dimm0
        Type: DDR5
        Type Detail: Synchronous Registered (Buffered)
        Speed: 4800 MT/s
        Manufacturer: SK Hynix
        Serial Number: 80AD0122149612A299
        Asset Tag: P2-DIMMG1_AssetTag (date:22/14)
        Part Number: HMCG88MEBRA107N
        Rank: 2
        Configured Memory Speed: 4800 MT/s
        Minimum Voltage: 1.1 V
        Maximum Voltage: 1.1 V
        Configured Voltage: 1.1 V
        Memory Technology: DRAM
        Memory Operating Mode Capability: Volatile memory
        Firmware Version: 0000
        Module Manufacturer ID: Bank 1, Hex 0xAD
        Module Product ID: 0xAD00
        Memory Subsystem Controller Manufacturer ID: Unknown
        Memory Subsystem Controller Product ID: Unknown
        Non-Volatile Size: None
        Volatile Size: 32 GB
        Cache Size: None
        Logical Size: None

Handle 0x004C, DMI type 17, 92 bytes
Memory Device
        Array Handle: 0x003C
        Error Information Handle: Not Provided
        Total Width: 80 bits
        Data Width: 64 bits
        Size: 32 GB
        Form Factor: DIMM
        Set: None
        Locator: P2-DIMMH1
        Bank Locator: P1_Node1_Channel3_Dimm0
        Type: DDR5
        Type Detail: Synchronous Registered (Buffered)
        Speed: 4800 MT/s
        Manufacturer: SK Hynix
        Serial Number: 80AD0122149612A195
        Asset Tag: P2-DIMMH1_AssetTag (date:22/14)
        Part Number: HMCG88MEBRA107N
        Rank: 2
        Configured Memory Speed: 4800 MT/s
        Minimum Voltage: 1.1 V
        Maximum Voltage: 1.1 V
        Configured Voltage: 1.1 V
        Memory Technology: DRAM
        Memory Operating Mode Capability: Volatile memory
        Firmware Version: 0000
        Module Manufacturer ID: Bank 1, Hex 0xAD
        Module Product ID: 0xAD00
        Memory Subsystem Controller Manufacturer ID: Unknown
        Memory Subsystem Controller Product ID: Unknown
        Non-Volatile Size: None
        Volatile Size: 32 GB
        Cache Size: None
        Logical Size: None
```

## Xeon ICX Server Firmware Inventory

```
Host.           IPMI IP.      BMC.      BIOS. CPLD.     CPU Microcode.  Cx-7 Firmware.  mlx5.         E810 Firmware.  ice.
s52-t21-sut1.   10.30.50.52.  1.00.2.   1.0.  F2.43.09. 0x2b0000c0.     28.34.1002.     5.9-0.5.6.0.  -.              -.
s53-t21-tg1.    10.30.50.53.  1.00.2.   1.0.  F2.43.09. 0x2b0000c0.     28.34.1002.     5.9-0.5.6.0.  -.              -.
s54-t22-sut1.   10.30.50.54.  1.00.2.   1.0.  F2.43.09. 0x2b0000c0.     -.              -.            4.00.           1.9.7.
s55-t22-tg1.    10.30.50.55.  1.00.2.   1.0.  F2.43.09. 0x2b0000c0.     -.              -.            3.20.           1.9.7.
s56-t23-sut1.   10.30.50.56.  1.00.2.   1.0.  F2.43.09. 0x2b0000c0.     28.34.1002.     5.9-0.5.6.0.  4.00.           1.9.7.
s57-t23-tg1.    10.30.50.57.  1.00.2.   1.0.  F2.43.09. 0x2b0000c0.     28.34.1002.     5.9-0.5.6.0.  3.20.           1.9.7.
s58-t24-sut1.   10.30.50.58.  1.00.2.   1.0.  F2.43.09. 0x2b0000c0.     28.34.1002.     5.9-0.5.6.0.  4.00.           1.9.7.
s59-t24-tg1.    10.30.50.59.  1.00.2.   1.0.  F2.43.09. 0x2b0000c0.     28.34.1002.     5.9-0.5.6.0.  3.20.           1.9.7.
```
