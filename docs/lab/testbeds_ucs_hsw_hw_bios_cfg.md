# Cisco UCS c240m4 Haswell Servers - HW and BIOS Configuration

1. [Linux lscpu](#linux-lscpu)
1. [Linux dmidecode pci](#linux-dmidecode-pci)
1. [Linux dmidecode memory](#linux-dmidecode-memory)
1. [Xeon Hsw Server BIOS Configuration](#xeon-hsw-server-bios-configuration)

## Linux lscpu

```
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
 Flags:                 fpu vme de pse tsc msr pae mce cx8 apic sep mtrr pge mca cmov pat pse36 clflush dts acpi mmx fxsr sse sse2 ss ht tm pbe syscall nx pdpe1gb rdtscp lm constant_tsc arch_perfmon pebs bts rep_good nopl xtopology nonstop_tsc aperfmperf eagerfpu pni pclmulqdq
 dtes64 monitor ds_cpl vmx smx est tm2 ssse3 sdbg fma cx16 xtpr pdcm pcid dca sse4_1 sse4_2 x2apic movbe popcnt tsc_deadline_timer aes xsave avx f16c rdrand lahf_lm abm epb tpr_shadow vnmi flexpriority ept vpid fsgsbase tsc_adjust bmi1 avx2 smep bmi2 erms invpcid cqm xsaveopt
 cqm_llc cqm_occup_llc dtherm arat pln pts
```

## Linux dmidecode pci

```
 $ dmidecode --type 9 | grep 'Handle\|Slot\|Type\|Address'
 Handle 0x0046, DMI type 9, 17 bytes
 System Slot Information
     Designation: SlotID:1
     Type: x8 PCI Express 3 x8
     Bus Address: 0000:0a:02.0
 Handle 0x0047, DMI type 9, 17 bytes
 System Slot Information
     Designation: SlotID:2
     Type: x8 PCI Express 3 x8
     Bus Address: 0000:0e:03.2
 Handle 0x0048, DMI type 9, 17 bytes
 System Slot Information
     Designation: SlotID:3
     Type: x8 PCI Express 3 x8
     Bus Address: 0000:0d:03.0
 Handle 0x0049, DMI type 9, 17 bytes
 System Slot Information
     Designation: SlotID:4
     Type: x8 PCI Express 3 x8
     Bus Address: 0000:85:02.2
 Handle 0x004A, DMI type 9, 17 bytes
 System Slot Information
     Designation: SlotID:5
     Type: x8 PCI Express 3 x16
     Bus Address: 0000:87:03.0
 Handle 0x004B, DMI type 9, 17 bytes
 System Slot Information
     Designation: SlotID:6
     Type: x8 PCI Express 3 x8
     Bus Address: 0000:84:02.0
 Handle 0x004C, DMI type 9, 17 bytes
 System Slot Information
     Designation: SlotID:MLOM
     Type: x8 Other
     Bus Address: 0000:01:01.0
 Handle 0x004D, DMI type 9, 17 bytes
 System Slot Information
     Designation: SlotID:HBA
     Type: x8 Other
     Bus Address: 0000:0c:02.2
 Handle 0x004E, DMI type 9, 17 bytes
 System Slot Information
     Designation: SlotID:NVMe1
     Type: x4 PCI Express 3 x4
     Bus Address: 0000:82:01.0
 Handle 0x004F, DMI type 9, 17 bytes
 System Slot Information
     Designation: SlotID:NVMe2
     Type: x4 PCI Express 3 x4
     Bus Address: 0000:83:01.1
 Handle 0x0050, DMI type 9, 17 bytes
 System Slot Information
     Designation: SlotID:2.1
     Type: x16 PCI Express 3 x16
     Bus Address: 0000:00:1f.7
 Handle 0x0051, DMI type 9, 17 bytes
 System Slot Information
     Designation: SlotID:2.2
     Type: x16 PCI Express 3 x16
     Bus Address: 0000:00:1f.7
 Handle 0x0052, DMI type 9, 17 bytes
 System Slot Information
     Designation: SlotID:2.3
     Type: x16 PCI Express 3 x16
     Bus Address: 0000:00:1f.7
 Handle 0x0053, DMI type 9, 17 bytes
 System Slot Information
     Designation: SlotID:2.4
     Type: x16 PCI Express 3 x16
     Bus Address: 0000:00:1f.7
 Handle 0x0054, DMI type 9, 17 bytes
 System Slot Information
     Designation: SlotID:2.5
     Type: x16 PCI Express 3 x16
     Bus Address: 0000:00:1f.7
 Handle 0x0055, DMI type 9, 17 bytes
 System Slot Information
     Designation: SlotID:5.1
     Type: x8 PCI Express 3 x16
     Bus Address: 0000:00:1f.7
 Handle 0x0056, DMI type 9, 17 bytes
 System Slot Information
     Designation: SlotID:5.2
     Type: x8 PCI Express 3 x16
     Bus Address: 0000:00:1f.7
 Handle 0x0057, DMI type 9, 17 bytes
 System Slot Information
     Designation: SlotID:5.3
     Type: x8 PCI Express 3 x16
     Bus Address: 0000:00:1f.7
 Handle 0x0058, DMI type 9, 17 bytes
 System Slot Information
     Designation: SlotID:5.4
     Type: x8 PCI Express 3 x16
     Bus Address: 0000:00:1f.7
 Handle 0x0059, DMI type 9, 17 bytes
 System Slot Information
     Designation: SlotID:5.5
     Type: x8 PCI Express 3 x16
     Bus Address: 0000:00:1f.7
```

## Linux dmidecode memory

```
 $ dmidecode -t memory
 # dmidecode 2.12
 SMBIOS 2.8 present.

 Handle 0x0022, DMI type 16, 23 bytes
 Physical Memory Array
     Location: System Board Or Motherboard
     Use: System Memory
     Error Correction Type: Multi-bit ECC
     Maximum Capacity: 1536 GB
     Error Information Handle: Not Provided
     Number Of Devices: 24

 Handle 0x0024, DMI type 17, 34 bytes
 Memory Device
     Array Handle: 0x0022
     Error Information Handle: Not Provided
     Total Width: 72 bits
     Data Width: 64 bits
     Size: 32 GB
     Form Factor: DIMM
     Set: None
     Locator: DIMM_A1
     Bank Locator: NODE 0 CHANNEL 0 DIMM 0
     Type: Other
     Type Detail: None
     Speed: 2133 MHz
     Manufacturer: 0xAD00
     Serial Number: 80EC7380
     Asset Tag: DIMM_A1_AssetTag
     Part Number: HMA84GL7MMR4N-TF
     Rank: 4
     Configured Clock Speed: 2133 MHz

 Handle 0x0025, DMI type 17, 34 bytes
 Memory Device
     Array Handle: 0x0022
     Error Information Handle: Not Provided
     Total Width: 72 bits
     Data Width: 64 bits
     Size: 32 GB
     Form Factor: DIMM
     Set: None
     Locator: DIMM_A2
     Bank Locator: NODE 0 CHANNEL 0 DIMM 1
     Type: Other
     Type Detail: None
     Speed: 2133 MHz
     Manufacturer: 0xAD00
     Serial Number: 80EC73D1
     Asset Tag: DIMM_A2_AssetTag
     Part Number: HMA84GL7MMR4N-TF
     Rank: 4
     Configured Clock Speed: 2133 MHz

 Handle 0x0026, DMI type 17, 34 bytes
 Memory Device
     Array Handle: 0x0022
     Error Information Handle: Not Provided
     Total Width: Unknown
     Data Width: Unknown
     Size: No Module Installed
     Form Factor: DIMM
     Set: None
     Locator: DIMM_A3
     Bank Locator: NODE 0 CHANNEL 0 DIMM 2
     Type: Other
     Type Detail: None
     Speed: Unknown
     Manufacturer: NO DIMM
     Serial Number: NO DIMM
     Asset Tag: NO DIMM
     Part Number: NO DIMM
     Rank: Unknown
     Configured Clock Speed: Unknown

 Handle 0x0027, DMI type 17, 34 bytes
 Memory Device
     Array Handle: 0x0022
     Error Information Handle: Not Provided
     Total Width: 72 bits
     Data Width: 64 bits
     Size: 32 GB
     Form Factor: DIMM
     Set: None
     Locator: DIMM_B1
     Bank Locator: NODE 0 CHANNEL 1 DIMM 0
     Type: Other
     Type Detail: None
     Speed: 2133 MHz
     Manufacturer: 0xAD00
     Serial Number: 80EC7325
     Asset Tag: DIMM_B1_AssetTag
     Part Number: HMA84GL7MMR4N-TF
     Rank: 4
     Configured Clock Speed: 2133 MHz

 Handle 0x0028, DMI type 17, 34 bytes
 Memory Device
     Array Handle: 0x0022
     Error Information Handle: Not Provided
     Total Width: 72 bits
     Data Width: 64 bits
     Size: 32 GB
     Form Factor: DIMM
     Set: None
     Locator: DIMM_B2
     Bank Locator: NODE 0 CHANNEL 1 DIMM 1
     Type: Other
     Type Detail: None
     Speed: 2133 MHz
     Manufacturer: 0xAD00
     Serial Number: 80EC7334
     Asset Tag: DIMM_B2_AssetTag
     Part Number: HMA84GL7MMR4N-TF
     Rank: 4
     Configured Clock Speed: 2133 MHz

 Handle 0x0029, DMI type 17, 34 bytes
 Memory Device
     Array Handle: 0x0022
     Error Information Handle: Not Provided
     Total Width: Unknown
     Data Width: Unknown
     Size: No Module Installed
     Form Factor: DIMM
     Set: None
     Locator: DIMM_B3
     Bank Locator: NODE 0 CHANNEL 1 DIMM 2
     Type: Other
     Type Detail: None
     Speed: Unknown
     Manufacturer: NO DIMM
     Serial Number: NO DIMM
     Asset Tag: NO DIMM
     Part Number: NO DIMM
     Rank: Unknown
     Configured Clock Speed: Unknown

 Handle 0x002A, DMI type 17, 34 bytes
 Memory Device
     Array Handle: 0x0022
     Error Information Handle: Not Provided
     Total Width: 72 bits
     Data Width: 64 bits
     Size: 32 GB
     Form Factor: DIMM
     Set: None
     Locator: DIMM_C1
     Bank Locator: NODE 0 CHANNEL 2 DIMM 0
     Type: Other
     Type Detail: None
     Speed: 2133 MHz
     Manufacturer: 0xAD00
     Serial Number: 80EC7329
     Asset Tag: DIMM_C1_AssetTag
     Part Number: HMA84GL7MMR4N-TF
     Rank: 4
     Configured Clock Speed: 2133 MHz

 Handle 0x002B, DMI type 17, 34 bytes
 Memory Device
     Array Handle: 0x0022
     Error Information Handle: Not Provided
     Total Width: 72 bits
     Data Width: 64 bits
     Size: 32 GB
     Form Factor: DIMM
     Set: None
     Locator: DIMM_C2
     Bank Locator: NODE 0 CHANNEL 2 DIMM 1
     Type: Other
     Type Detail: None
     Speed: 2133 MHz
     Manufacturer: 0xAD00
     Serial Number: 80EC732D
     Asset Tag: DIMM_C2_AssetTag
     Part Number: HMA84GL7MMR4N-TF
     Rank: 4
     Configured Clock Speed: 2133 MHz

 Handle 0x002C, DMI type 17, 34 bytes
 Memory Device
     Array Handle: 0x0022
     Error Information Handle: Not Provided
     Total Width: Unknown
     Data Width: Unknown
     Size: No Module Installed
     Form Factor: DIMM
     Set: None
     Locator: DIMM_C3
     Bank Locator: NODE 0 CHANNEL 2 DIMM 2
     Type: Other
     Type Detail: None
     Speed: Unknown
     Manufacturer: NO DIMM
     Serial Number: NO DIMM
     Asset Tag: NO DIMM
     Part Number: NO DIMM
     Rank: Unknown
     Configured Clock Speed: Unknown

 Handle 0x002D, DMI type 17, 34 bytes
 Memory Device
     Array Handle: 0x0022
     Error Information Handle: Not Provided
     Total Width: 72 bits
     Data Width: 64 bits
     Size: 32 GB
     Form Factor: DIMM
     Set: None
     Locator: DIMM_D1
     Bank Locator: NODE 0 CHANNEL 3 DIMM 0
     Type: Other
     Type Detail: None
     Speed: 2133 MHz
     Manufacturer: 0xAD00
     Serial Number: 80EC73D3
     Asset Tag: DIMM_D1_AssetTag
     Part Number: HMA84GL7MMR4N-TF
     Rank: 4
     Configured Clock Speed: 2133 MHz

 Handle 0x002E, DMI type 17, 34 bytes
 Memory Device
     Array Handle: 0x0022
     Error Information Handle: Not Provided
     Total Width: 72 bits
     Data Width: 64 bits
     Size: 32 GB
     Form Factor: DIMM
     Set: None
     Locator: DIMM_D2
     Bank Locator: NODE 0 CHANNEL 3 DIMM 1
     Type: Other
     Type Detail: None
     Speed: 2133 MHz
     Manufacturer: 0xAD00
     Serial Number: 80EC7330
     Asset Tag: DIMM_D2_AssetTag
     Part Number: HMA84GL7MMR4N-TF
     Rank: 4
     Configured Clock Speed: 2133 MHz

 Handle 0x002F, DMI type 17, 34 bytes
 Memory Device
     Array Handle: 0x0022
     Error Information Handle: Not Provided
     Total Width: Unknown
     Data Width: Unknown
     Size: No Module Installed
     Form Factor: DIMM
     Set: None
     Locator: DIMM_D3
     Bank Locator: NODE 0 CHANNEL 3 DIMM 2
     Type: Other
     Type Detail: None
     Speed: Unknown
     Manufacturer: NO DIMM
     Serial Number: NO DIMM
     Asset Tag: NO DIMM
     Part Number: NO DIMM
     Rank: Unknown
     Configured Clock Speed: Unknown

 Handle 0x0030, DMI type 17, 34 bytes
 Memory Device
     Array Handle: 0x0022
     Error Information Handle: Not Provided
     Total Width: 72 bits
     Data Width: 64 bits
     Size: 32 GB
     Form Factor: DIMM
     Set: None
     Locator: DIMM_E1
     Bank Locator: NODE 1 CHANNEL 0 DIMM 0
     Type: Other
     Type Detail: None
     Speed: 2133 MHz
     Manufacturer: 0xAD00
     Serial Number: 80E54252
     Asset Tag: DIMM_E1_AssetTag
     Part Number: HMA84GL7MMR4N-TF
     Rank: 4
     Configured Clock Speed: 2133 MHz

 Handle 0x0031, DMI type 17, 34 bytes
 Memory Device
     Array Handle: 0x0022
     Error Information Handle: Not Provided
     Total Width: 72 bits
     Data Width: 64 bits
     Size: 32 GB
     Form Factor: DIMM
     Set: None
     Locator: DIMM_E2
     Bank Locator: NODE 1 CHANNEL 0 DIMM 1
     Type: Other
     Type Detail: None
     Speed: 2133 MHz
     Manufacturer: 0xAD00
     Serial Number: 80E54235
     Asset Tag: DIMM_E2_AssetTag
     Part Number: HMA84GL7MMR4N-TF
     Rank: 4
     Configured Clock Speed: 2133 MHz

 Handle 0x0032, DMI type 17, 34 bytes
 Memory Device
     Array Handle: 0x0022
     Error Information Handle: Not Provided
     Total Width: Unknown
     Data Width: Unknown
     Size: No Module Installed
     Form Factor: DIMM
     Set: None
     Locator: DIMM_E3
     Bank Locator: NODE 1 CHANNEL 0 DIMM 2
     Type: Other
     Type Detail: None
     Speed: Unknown
     Manufacturer: NO DIMM
     Serial Number: NO DIMM
     Asset Tag: NO DIMM
     Part Number: NO DIMM
     Rank: Unknown
     Configured Clock Speed: Unknown

 Handle 0x0033, DMI type 17, 34 bytes
 Memory Device
     Array Handle: 0x0022
     Error Information Handle: Not Provided
     Total Width: 72 bits
     Data Width: 64 bits
     Size: 32 GB
     Form Factor: DIMM
     Set: None
     Locator: DIMM_F1
     Bank Locator: NODE 1 CHANNEL 1 DIMM 0
     Type: Other
     Type Detail: None
     Speed: 2133 MHz
     Manufacturer: 0xAD00
     Serial Number: 80E54218
     Asset Tag: DIMM_F1_AssetTag
     Part Number: HMA84GL7MMR4N-TF
     Rank: 4
     Configured Clock Speed: 2133 MHz

 Handle 0x0034, DMI type 17, 34 bytes
 Memory Device
     Array Handle: 0x0022
     Error Information Handle: Not Provided
     Total Width: 72 bits
     Data Width: 64 bits
     Size: 32 GB
     Form Factor: DIMM
     Set: None
     Locator: DIMM_F2
     Bank Locator: NODE 1 CHANNEL 1 DIMM 1
     Type: Other
     Type Detail: None
     Speed: 2133 MHz
     Manufacturer: 0xAD00
     Serial Number: 80E54236
     Asset Tag: DIMM_F2_AssetTag
     Part Number: HMA84GL7MMR4N-TF
     Rank: 4
     Configured Clock Speed: 2133 MHz

 Handle 0x0035, DMI type 17, 34 bytes
 Memory Device
     Array Handle: 0x0022
     Error Information Handle: Not Provided
     Total Width: Unknown
     Data Width: Unknown
     Size: No Module Installed
     Form Factor: DIMM
     Set: None
     Locator: DIMM_F3
     Bank Locator: NODE 1 CHANNEL 1 DIMM 2
     Type: Other
     Type Detail: None
     Speed: Unknown
     Manufacturer: NO DIMM
     Serial Number: NO DIMM
     Asset Tag: NO DIMM
     Part Number: NO DIMM
     Rank: Unknown
     Configured Clock Speed: Unknown

 Handle 0x0036, DMI type 17, 34 bytes
 Memory Device
     Array Handle: 0x0022
     Error Information Handle: Not Provided
     Total Width: 72 bits
     Data Width: 64 bits
     Size: 32 GB
     Form Factor: DIMM
     Set: None
     Locator: DIMM_G1
     Bank Locator: NODE 1 CHANNEL 2 DIMM 0
     Type: Other
     Type Detail: None
     Speed: 2133 MHz
     Manufacturer: 0xAD00
     Serial Number: 80E54247
     Asset Tag: DIMM_G1_AssetTag
     Part Number: HMA84GL7MMR4N-TF
     Rank: 4
     Configured Clock Speed: 2133 MHz

 Handle 0x0037, DMI type 17, 34 bytes
 Memory Device
     Array Handle: 0x0022
     Error Information Handle: Not Provided
     Total Width: 72 bits
     Data Width: 64 bits
     Size: 32 GB
     Form Factor: DIMM
     Set: None
     Locator: DIMM_G2
     Bank Locator: NODE 1 CHANNEL 2 DIMM 1
     Type: Other
     Type Detail: None
     Speed: 2133 MHz
     Manufacturer: 0xAD00
     Serial Number: 80E5421E
     Asset Tag: DIMM_G2_AssetTag
     Part Number: HMA84GL7MMR4N-TF
     Rank: 4
     Configured Clock Speed: 2133 MHz

 Handle 0x0038, DMI type 17, 34 bytes
 Memory Device
     Array Handle: 0x0022
     Error Information Handle: Not Provided
     Total Width: Unknown
     Data Width: Unknown
     Size: No Module Installed
     Form Factor: DIMM
     Set: None
     Locator: DIMM_G3
     Bank Locator: NODE 1 CHANNEL 2 DIMM 2
     Type: Other
     Type Detail: None
     Speed: Unknown
     Manufacturer: NO DIMM
     Serial Number: NO DIMM
     Asset Tag: NO DIMM
     Part Number: NO DIMM
     Rank: Unknown
     Configured Clock Speed: Unknown

 Handle 0x0039, DMI type 17, 34 bytes
 Memory Device
     Array Handle: 0x0022
     Error Information Handle: Not Provided
     Total Width: 72 bits
     Data Width: 64 bits
     Size: 32 GB
     Form Factor: DIMM
     Set: None
     Locator: DIMM_H1
     Bank Locator: NODE 1 CHANNEL 3 DIMM 0
     Type: Other
     Type Detail: None
     Speed: 2133 MHz
     Manufacturer: 0xAD00
     Serial Number: 80E5423C
     Asset Tag: DIMM_H1_AssetTag
     Part Number: HMA84GL7MMR4N-TF
     Rank: 4
     Configured Clock Speed: 2133 MHz

 Handle 0x003A, DMI type 17, 34 bytes
 Memory Device
     Array Handle: 0x0022
     Error Information Handle: Not Provided
     Total Width: 72 bits
     Data Width: 64 bits
     Size: 32 GB
     Form Factor: DIMM
     Set: None
     Locator: DIMM_H2
     Bank Locator: NODE 1 CHANNEL 3 DIMM 1
     Type: Other
     Type Detail: None
     Speed: 2133 MHz
     Manufacturer: 0xAD00
     Serial Number: 80E5424D
     Asset Tag: DIMM_H2_AssetTag
     Part Number: HMA84GL7MMR4N-TF
     Rank: 4
     Configured Clock Speed: 2133 MHz

 Handle 0x003B, DMI type 17, 34 bytes
 Memory Device
     Array Handle: 0x0022
     Error Information Handle: Not Provided
     Total Width: Unknown
     Data Width: Unknown
     Size: No Module Installed
     Form Factor: DIMM
     Set: None
     Locator: DIMM_H3
     Bank Locator: NODE 1 CHANNEL 3 DIMM 2
     Type: Other
     Type Detail: None
     Speed: Unknown
     Manufacturer: NO DIMM
     Serial Number: NO DIMM
     Asset Tag: NO DIMM
     Part Number: NO DIMM
     Rank: Unknown
     Configured Clock Speed: Unknown
```

## Xeon Hsw Server BIOS Configuration

```
 C240 / # scope bios
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
 C240-FCH1950V1H5 /bios/advanced #
```
