---
bookToc: true
title: "MegaRac Altra"
---

# MegaRac Altra

## Linux lscpu

```
Architecture:           aarch64
  CPU op-mode(s):       32-bit, 64-bit
  Byte Order:           Little Endian
CPU(s):                 160
  On-line CPU(s) list:  0-159
Vendor ID:              ARM
  Model name:           Neoverse-N1
    Model:              1
    Thread(s) per core: 1
    Core(s) per socket: 80
    Socket(s):          2
    Stepping:           r3p1
    Frequency boost:    disabled
    CPU max MHz:        3000.0000
    CPU min MHz:        1000.0000
    BogoMIPS:           50.00
    Flags:              fp asimd evtstrm aes pmull sha1 sha2 crc32 atomics fphp asimdhp cpuid asimdrdm lrcpc dcpop asimddp ssbs
Caches (sum of all):
  L1d:                  10 MiB (160 instances)
  L1i:                  10 MiB (160 instances)
  L2:                   160 MiB (160 instances)
NUMA:
  NUMA node(s):         2
  NUMA node0 CPU(s):    0-79
  NUMA node1 CPU(s):    80-159
Vulnerabilities:
  Itlb multihit:        Not affected
  L1tf:                 Not affected
  Mds:                  Not affected
  Meltdown:             Not affected
  Mmio stale data:      Not affected
  Retbleed:             Not affected
  Spec store bypass:    Mitigation; Speculative Store Bypass disabled via prctl
  Spectre v1:           Mitigation; __user pointer sanitization
  Spectre v2:           Mitigation; CSV2, BHB
  Srbds:                Not affected
  Tsx async abort:      Not affected
```

## Linux dmidecode

```
# dmidecode 3.3
Getting SMBIOS data from sysfs.
SMBIOS 3.3.0 present.
Table at 0xB1E10000.

Handle 0x0000, DMI type 0, 26 bytes
BIOS Information
	Vendor: Ampere(R)
	Version: 1.07.20210713 (SCP: 1.07.20210713)
	Release Date: 2021/07/13
	ROM Size: 7680 kB
	Characteristics:
		PCI is supported
		BIOS is upgradeable
		Boot from CD is supported
		Selectable boot is supported
		ACPI is supported
		UEFI is supported
	BIOS Revision: 5.15
	Firmware Revision: 1.7

Handle 0x0001, DMI type 1, 27 bytes
System Information
	Manufacturer: WIWYNN
	Product Name: Mt.Jade Server System B81.030Z1.0007
	Version: DVT
	Serial Number: B81030Z1000704000059N0SC
	UUID: 57c97bbe-008e-368f-19d0-595df92c6de0
	Wake-up Type: Power Switch
	SKU Number: NULL
	Family: Altra

Handle 0x0002, DMI type 2, 15 bytes
Base Board Information
	Manufacturer: WIWYNN
	Product Name: Mt.Jade Motherboard
	Version: B81.03010.0033
	Serial Number: B8103010003303800033J0SA
	Asset Tag: NULL
	Features:
		Board is a hosting board
	Location In Chassis: Part Component
	Chassis Handle: 0x0003
	Type: Motherboard
	Contained Object Handles: 0

Handle 0x0003, DMI type 3, 22 bytes
Chassis Information
	Manufacturer: WIWYNN
	Type: Rack Mount Chassis
	Lock: Present
	Version: B60.03008.0001
	Serial Number: 04000059N0SC
	Asset Tag: NULL
	Boot-up State: Safe
	Power Supply State: Safe
	Thermal State: Safe
	Security Status: None
	OEM Information: 0x00000000
	Height: Unspecified
	Number Of Power Cords: 1
	Contained Elements: 0
	SKU Number: Unknown
```

## Linux dmidecode memory

```
Handle 0x0020, DMI type 16, 23 bytes
Physical Memory Array
	Location: System Board Or Motherboard
	Use: System Memory
	Error Correction Type: Multi-bit ECC
	Maximum Capacity: 4 TB
	Error Information Handle: No Error
	Number Of Devices: 16

Handle 0x0026, DMI type 17, 92 bytes
Memory Device
	Array Handle: 0x0020
	Error Information Handle: No Error
	Total Width: 72 bits
	Data Width: 64 bits
	Size: 8 GB
	Form Factor: DIMM
	Set: None
	Locator: DIMM 1
	Bank Locator: Bank 1
	Type: DDR4
	Type Detail: Registered (Buffered)
	Speed: 3200 MT/s
	Manufacturer: Samsung
	Serial Number: 0197198A
	Asset Tag: Array 1 Asset Tag 1
	Part Number: M393A1K43DB2-CWE
	Rank: 1
	Configured Memory Speed: 3200 MT/s
	Minimum Voltage: 1.14 V
	Maximum Voltage: 1.26 V
	Configured Voltage: 1.2 V
	Memory Technology: DRAM
	Memory Operating Mode Capability: None
	Firmware Version: Not Specified
	Module Manufacturer ID: Bank 1, Hex 0xCE
	Module Product ID: Unknown
	Memory Subsystem Controller Manufacturer ID: Unknown
	Memory Subsystem Controller Product ID: Unknown
	Non-Volatile Size: None
	Volatile Size: 8 GB
	Cache Size: None
	Logical Size: None

Handle 0x0028, DMI type 17, 92 bytes
Memory Device
	Array Handle: 0x0020
	Error Information Handle: 0x0029
	Total Width: Unknown
	Data Width: Unknown
	Size: No Module Installed
	Form Factor: DIMM
	Set: None
	Locator: DIMM 2
	Bank Locator: Bank 2
	Type: Unknown
	Type Detail: Unknown
	Speed: Unknown
	Manufacturer: Array 1 Manufacturer 2
	Serial Number: Array 1 Serial Number 2
	Asset Tag: Array 1 Asset Tag 2
	Part Number: Array 1 Part Number 2
	Rank: Unknown
	Configured Memory Speed: Unknown
	Minimum Voltage: Unknown
	Maximum Voltage: Unknown
	Configured Voltage: Unknown
	Memory Technology: Unknown
	Memory Operating Mode Capability: Unknown
	Firmware Version: Not Specified
	Module Manufacturer ID: Unknown
	Module Product ID: Unknown
	Memory Subsystem Controller Manufacturer ID: Unknown
	Memory Subsystem Controller Product ID: Unknown
	Non-Volatile Size: None
	Volatile Size: None
	Cache Size: None
	Logical Size: None

Handle 0x0030, DMI type 17, 92 bytes
Memory Device
	Array Handle: 0x0020
	Error Information Handle: No Error
	Total Width: 72 bits
	Data Width: 64 bits
	Size: 8 GB
	Form Factor: DIMM
	Set: None
	Locator: DIMM 3
	Bank Locator: Bank 3
	Type: DDR4
	Type Detail: Registered (Buffered)
	Speed: 3200 MT/s
	Manufacturer: Samsung
	Serial Number: 01971992
	Asset Tag: Array 1 Asset Tag 3
	Part Number: M393A1K43DB2-CWE
	Rank: 1
	Configured Memory Speed: 3200 MT/s
	Minimum Voltage: 1.14 V
	Maximum Voltage: 1.26 V
	Configured Voltage: 1.2 V
	Memory Technology: DRAM
	Memory Operating Mode Capability: None
	Firmware Version: Not Specified
	Module Manufacturer ID: Bank 1, Hex 0xCE
	Module Product ID: Unknown
	Memory Subsystem Controller Manufacturer ID: Unknown
	Memory Subsystem Controller Product ID: Unknown
	Non-Volatile Size: None
	Volatile Size: 8 GB
	Cache Size: None
	Logical Size: None

Handle 0x0032, DMI type 17, 92 bytes
Memory Device
	Array Handle: 0x0020
	Error Information Handle: 0x0033
	Total Width: Unknown
	Data Width: Unknown
	Size: No Module Installed
	Form Factor: DIMM
	Set: None
	Locator: DIMM 4
	Bank Locator: Bank 4
	Type: Unknown
	Type Detail: Unknown
	Speed: Unknown
	Manufacturer: Array 1 Manufacturer 4
	Serial Number: Array 1 Serial Number 4
	Asset Tag: Array 1 Asset Tag 4
	Part Number: Array 1 Part Number 4
	Rank: Unknown
	Configured Memory Speed: Unknown
	Minimum Voltage: Unknown
	Maximum Voltage: Unknown
	Configured Voltage: Unknown
	Memory Technology: Unknown
	Memory Operating Mode Capability: Unknown
	Firmware Version: Not Specified
	Module Manufacturer ID: Unknown
	Module Product ID: Unknown
	Memory Subsystem Controller Manufacturer ID: Unknown
	Memory Subsystem Controller Product ID: Unknown
	Non-Volatile Size: None
	Volatile Size: None
	Cache Size: None
	Logical Size: None

Handle 0x0034, DMI type 17, 92 bytes
Memory Device
	Array Handle: 0x0020
	Error Information Handle: No Error
	Total Width: 72 bits
	Data Width: 64 bits
	Size: 8 GB
	Form Factor: DIMM
	Set: None
	Locator: DIMM 5
	Bank Locator: Bank 5
	Type: DDR4
	Type Detail: Registered (Buffered)
	Speed: 3200 MT/s
	Manufacturer: Samsung
	Serial Number: 01971989
	Asset Tag: Array 1 Asset Tag 5
	Part Number: M393A1K43DB2-CWE
	Rank: 1
	Configured Memory Speed: 3200 MT/s
	Minimum Voltage: 1.14 V
	Maximum Voltage: 1.26 V
	Configured Voltage: 1.2 V
	Memory Technology: DRAM
	Memory Operating Mode Capability: None
	Firmware Version: Not Specified
	Module Manufacturer ID: Bank 1, Hex 0xCE
	Module Product ID: Unknown
	Memory Subsystem Controller Manufacturer ID: Unknown
	Memory Subsystem Controller Product ID: Unknown
	Non-Volatile Size: None
	Volatile Size: 8 GB
	Cache Size: None
	Logical Size: None

Handle 0x0036, DMI type 17, 92 bytes
Memory Device
	Array Handle: 0x0020
	Error Information Handle: 0x0037
	Total Width: Unknown
	Data Width: Unknown
	Size: No Module Installed
	Form Factor: DIMM
	Set: None
	Locator: DIMM 6
	Bank Locator: Bank 6
	Type: Unknown
	Type Detail: Unknown
	Speed: Unknown
	Manufacturer: Array 1 Manufacturer 6
	Serial Number: Array 1 Serial Number 6
	Asset Tag: Array 1 Asset Tag 6
	Part Number: Array 1 Part Number 6
	Rank: Unknown
	Configured Memory Speed: Unknown
	Minimum Voltage: Unknown
	Maximum Voltage: Unknown
	Configured Voltage: Unknown
	Memory Technology: Unknown
	Memory Operating Mode Capability: Unknown
	Firmware Version: Not Specified
	Module Manufacturer ID: Unknown
	Module Product ID: Unknown
	Memory Subsystem Controller Manufacturer ID: Unknown
	Memory Subsystem Controller Product ID: Unknown
	Non-Volatile Size: None
	Volatile Size: None
	Cache Size: None
	Logical Size: None

Handle 0x0038, DMI type 17, 92 bytes
Memory Device
	Array Handle: 0x0020
	Error Information Handle: No Error
	Total Width: 72 bits
	Data Width: 64 bits
	Size: 8 GB
	Form Factor: DIMM
	Set: None
	Locator: DIMM 7
	Bank Locator: Bank 7
	Type: DDR4
	Type Detail: Registered (Buffered)
	Speed: 3200 MT/s
	Manufacturer: Samsung
	Serial Number: 01971BA1
	Asset Tag: Array 1 Asset Tag 7
	Part Number: M393A1K43DB2-CWE
	Rank: 1
	Configured Memory Speed: 3200 MT/s
	Minimum Voltage: 1.14 V
	Maximum Voltage: 1.26 V
	Configured Voltage: 1.2 V
	Memory Technology: DRAM
	Memory Operating Mode Capability: None
	Firmware Version: Not Specified
	Module Manufacturer ID: Bank 1, Hex 0xCE
	Module Product ID: Unknown
	Memory Subsystem Controller Manufacturer ID: Unknown
	Memory Subsystem Controller Product ID: Unknown
	Non-Volatile Size: None
	Volatile Size: 8 GB
	Cache Size: None
	Logical Size: None

Handle 0x0040, DMI type 17, 92 bytes
Memory Device
	Array Handle: 0x0020
	Error Information Handle: 0x0041
	Total Width: Unknown
	Data Width: Unknown
	Size: No Module Installed
	Form Factor: DIMM
	Set: None
	Locator: DIMM 8
	Bank Locator: Bank 8
	Type: Unknown
	Type Detail: Unknown
	Speed: Unknown
	Manufacturer: Array 1 Manufacturer 8
	Serial Number: Array 1 Serial Number 8
	Asset Tag: Array 1 Asset Tag 8
	Part Number: Array 1 Part Number 8
	Rank: Unknown
	Configured Memory Speed: Unknown
	Minimum Voltage: Unknown
	Maximum Voltage: Unknown
	Configured Voltage: Unknown
	Memory Technology: Unknown
	Memory Operating Mode Capability: Unknown
	Firmware Version: Not Specified
	Module Manufacturer ID: Unknown
	Module Product ID: Unknown
	Memory Subsystem Controller Manufacturer ID: Unknown
	Memory Subsystem Controller Product ID: Unknown
	Non-Volatile Size: None
	Volatile Size: None
	Cache Size: None
	Logical Size: None

Handle 0x0042, DMI type 17, 92 bytes
Memory Device
	Array Handle: 0x0020
	Error Information Handle: No Error
	Total Width: 72 bits
	Data Width: 64 bits
	Size: 8 GB
	Form Factor: DIMM
	Set: None
	Locator: DIMM 9
	Bank Locator: Bank 9
	Type: DDR4
	Type Detail: Registered (Buffered)
	Speed: 3200 MT/s
	Manufacturer: Samsung
	Serial Number: 01971930
	Asset Tag: Array 1 Asset Tag 9
	Part Number: M393A1K43DB2-CWE
	Rank: 1
	Configured Memory Speed: 3200 MT/s
	Minimum Voltage: 1.14 V
	Maximum Voltage: 1.26 V
	Configured Voltage: 1.2 V
	Memory Technology: DRAM
	Memory Operating Mode Capability: None
	Firmware Version: Not Specified
	Module Manufacturer ID: Bank 1, Hex 0xCE
	Module Product ID: Unknown
	Memory Subsystem Controller Manufacturer ID: Unknown
	Memory Subsystem Controller Product ID: Unknown
	Non-Volatile Size: None
	Volatile Size: 8 GB
	Cache Size: None
	Logical Size: None

Handle 0x0044, DMI type 17, 92 bytes
Memory Device
	Array Handle: 0x0020
	Error Information Handle: 0x0045
	Total Width: Unknown
	Data Width: Unknown
	Size: No Module Installed
	Form Factor: DIMM
	Set: None
	Locator: DIMM 10
	Bank Locator: Bank 10
	Type: Unknown
	Type Detail: Unknown
	Speed: Unknown
	Manufacturer: Array 1 Manufacturer 10
	Serial Number: Array 1 Serial Number 10
	Asset Tag: Array 1 Asset Tag 10
	Part Number: Array 1 Part Number 10
	Rank: Unknown
	Configured Memory Speed: Unknown
	Minimum Voltage: Unknown
	Maximum Voltage: Unknown
	Configured Voltage: Unknown
	Memory Technology: Unknown
	Memory Operating Mode Capability: Unknown
	Firmware Version: Not Specified
	Module Manufacturer ID: Unknown
	Module Product ID: Unknown
	Memory Subsystem Controller Manufacturer ID: Unknown
	Memory Subsystem Controller Product ID: Unknown
	Non-Volatile Size: None
	Volatile Size: None
	Cache Size: None
	Logical Size: None

Handle 0x0046, DMI type 17, 92 bytes
Memory Device
	Array Handle: 0x0020
	Error Information Handle: No Error
	Total Width: 72 bits
	Data Width: 64 bits
	Size: 8 GB
	Form Factor: DIMM
	Set: None
	Locator: DIMM 11
	Bank Locator: Bank 11
	Type: DDR4
	Type Detail: Registered (Buffered)
	Speed: 3200 MT/s
	Manufacturer: Samsung
	Serial Number: 01971BA2
	Asset Tag: Array 1 Asset Tag 11
	Part Number: M393A1K43DB2-CWE
	Rank: 1
	Configured Memory Speed: 3200 MT/s
	Minimum Voltage: 1.14 V
	Maximum Voltage: 1.26 V
	Configured Voltage: 1.2 V
	Memory Technology: DRAM
	Memory Operating Mode Capability: None
	Firmware Version: Not Specified
	Module Manufacturer ID: Bank 1, Hex 0xCE
	Module Product ID: Unknown
	Memory Subsystem Controller Manufacturer ID: Unknown
	Memory Subsystem Controller Product ID: Unknown
	Non-Volatile Size: None
	Volatile Size: 8 GB
	Cache Size: None
	Logical Size: None

Handle 0x0048, DMI type 17, 92 bytes
Memory Device
	Array Handle: 0x0020
	Error Information Handle: 0x0049
	Total Width: Unknown
	Data Width: Unknown
	Size: No Module Installed
	Form Factor: DIMM
	Set: None
	Locator: DIMM 12
	Bank Locator: Bank 12
	Type: Unknown
	Type Detail: Unknown
	Speed: Unknown
	Manufacturer: Array 1 Manufacturer 12
	Serial Number: Array 1 Serial Number 12
	Asset Tag: Array 1 Asset Tag 12
	Part Number: Array 1 Part Number 12
	Rank: Unknown
	Configured Memory Speed: Unknown
	Minimum Voltage: Unknown
	Maximum Voltage: Unknown
	Configured Voltage: Unknown
	Memory Technology: Unknown
	Memory Operating Mode Capability: Unknown
	Firmware Version: Not Specified
	Module Manufacturer ID: Unknown
	Module Product ID: Unknown
	Memory Subsystem Controller Manufacturer ID: Unknown
	Memory Subsystem Controller Product ID: Unknown
	Non-Volatile Size: None
	Volatile Size: None
	Cache Size: None
	Logical Size: None

Handle 0x0050, DMI type 17, 92 bytes
Memory Device
	Array Handle: 0x0020
	Error Information Handle: No Error
	Total Width: 72 bits
	Data Width: 64 bits
	Size: 8 GB
	Form Factor: DIMM
	Set: None
	Locator: DIMM 13
	Bank Locator: Bank 13
	Type: DDR4
	Type Detail: Registered (Buffered)
	Speed: 3200 MT/s
	Manufacturer: Samsung
	Serial Number: 01971957
	Asset Tag: Array 1 Asset Tag 13
	Part Number: M393A1K43DB2-CWE
	Rank: 1
	Configured Memory Speed: 3200 MT/s
	Minimum Voltage: 1.14 V
	Maximum Voltage: 1.26 V
	Configured Voltage: 1.2 V
	Memory Technology: DRAM
	Memory Operating Mode Capability: None
	Firmware Version: Not Specified
	Module Manufacturer ID: Bank 1, Hex 0xCE
	Module Product ID: Unknown
	Memory Subsystem Controller Manufacturer ID: Unknown
	Memory Subsystem Controller Product ID: Unknown
	Non-Volatile Size: None
	Volatile Size: 8 GB
	Cache Size: None
	Logical Size: None

Handle 0x0052, DMI type 17, 92 bytes
Memory Device
	Array Handle: 0x0020
	Error Information Handle: 0x0053
	Total Width: Unknown
	Data Width: Unknown
	Size: No Module Installed
	Form Factor: DIMM
	Set: None
	Locator: DIMM 14
	Bank Locator: Bank 14
	Type: Unknown
	Type Detail: Unknown
	Speed: Unknown
	Manufacturer: Array 1 Manufacturer 14
	Serial Number: Array 1 Serial Number 14
	Asset Tag: Array 1 Asset Tag 14
	Part Number: Array 1 Part Number 14
	Rank: Unknown
	Configured Memory Speed: Unknown
	Minimum Voltage: Unknown
	Maximum Voltage: Unknown
	Configured Voltage: Unknown
	Memory Technology: Unknown
	Memory Operating Mode Capability: Unknown
	Firmware Version: Not Specified
	Module Manufacturer ID: Unknown
	Module Product ID: Unknown
	Memory Subsystem Controller Manufacturer ID: Unknown
	Memory Subsystem Controller Product ID: Unknown
	Non-Volatile Size: None
	Volatile Size: None
	Cache Size: None
	Logical Size: None

Handle 0x0054, DMI type 17, 92 bytes
Memory Device
	Array Handle: 0x0020
	Error Information Handle: No Error
	Total Width: 72 bits
	Data Width: 64 bits
	Size: 8 GB
	Form Factor: DIMM
	Set: None
	Locator: DIMM 15
	Bank Locator: Bank 15
	Type: DDR4
	Type Detail: Registered (Buffered)
	Speed: 3200 MT/s
	Manufacturer: Samsung
	Serial Number: 01971B9E
	Asset Tag: Array 1 Asset Tag 15
	Part Number: M393A1K43DB2-CWE
	Rank: 1
	Configured Memory Speed: 3200 MT/s
	Minimum Voltage: 1.14 V
	Maximum Voltage: 1.26 V
	Configured Voltage: 1.2 V
	Memory Technology: DRAM
	Memory Operating Mode Capability: None
	Firmware Version: Not Specified
	Module Manufacturer ID: Bank 1, Hex 0xCE
	Module Product ID: Unknown
	Memory Subsystem Controller Manufacturer ID: Unknown
	Memory Subsystem Controller Product ID: Unknown
	Non-Volatile Size: None
	Volatile Size: 8 GB
	Cache Size: None
	Logical Size: None

Handle 0x0056, DMI type 17, 92 bytes
Memory Device
	Array Handle: 0x0020
	Error Information Handle: 0x0057
	Total Width: Unknown
	Data Width: Unknown
	Size: No Module Installed
	Form Factor: DIMM
	Set: None
	Locator: DIMM 16
	Bank Locator: Bank 16
	Type: Unknown
	Type Detail: Unknown
	Speed: Unknown
	Manufacturer: Array 1 Manufacturer 16
	Serial Number: Array 1 Serial Number 16
	Asset Tag: Array 1 Asset Tag 16
	Part Number: Array 1 Part Number 16
	Rank: Unknown
	Configured Memory Speed: Unknown
	Minimum Voltage: Unknown
	Maximum Voltage: Unknown
	Configured Voltage: Unknown
	Memory Technology: Unknown
	Memory Operating Mode Capability: Unknown
	Firmware Version: Not Specified
	Module Manufacturer ID: Unknown
	Module Product ID: Unknown
	Memory Subsystem Controller Manufacturer ID: Unknown
	Memory Subsystem Controller Product ID: Unknown
	Non-Volatile Size: None
	Volatile Size: None
	Cache Size: None
	Logical Size: None

Handle 0x0071, DMI type 16, 23 bytes
Physical Memory Array
	Location: System Board Or Motherboard
	Use: System Memory
	Error Correction Type: Multi-bit ECC
	Maximum Capacity: 4 TB
	Error Information Handle: No Error
	Number Of Devices: 16

Handle 0x0077, DMI type 17, 92 bytes
Memory Device
	Array Handle: 0x0071
	Error Information Handle: No Error
	Total Width: 72 bits
	Data Width: 64 bits
	Size: 8 GB
	Form Factor: DIMM
	Set: None
	Locator: Socket 1 DIMM 1
	Bank Locator: Bank 1
	Type: DDR4
	Type Detail: Registered (Buffered)
	Speed: 3200 MT/s
	Manufacturer: Samsung
	Serial Number: 01971918
	Asset Tag: Array 1 Asset Tag 1
	Part Number: M393A1K43DB2-CWE
	Rank: 1
	Configured Memory Speed: 3200 MT/s
	Minimum Voltage: 1.14 V
	Maximum Voltage: 1.26 V
	Configured Voltage: 1.2 V
	Memory Technology: DRAM
	Memory Operating Mode Capability: None
	Firmware Version: Not Specified
	Module Manufacturer ID: Bank 1, Hex 0xCE
	Module Product ID: Unknown
	Memory Subsystem Controller Manufacturer ID: Unknown
	Memory Subsystem Controller Product ID: Unknown
	Non-Volatile Size: None
	Volatile Size: 8 GB
	Cache Size: None
	Logical Size: None

Handle 0x007A, DMI type 17, 92 bytes
Memory Device
	Array Handle: 0x0071
	Error Information Handle: 0x007C
	Total Width: Unknown
	Data Width: Unknown
	Size: No Module Installed
	Form Factor: DIMM
	Set: None
	Locator: Socket 1 DIMM 2
	Bank Locator: Bank 2
	Type: Unknown
	Type Detail: Unknown
	Speed: Unknown
	Manufacturer: Array 1 Manufacturer 2
	Serial Number: Array 1 Serial Number 2
	Asset Tag: Array 1 Asset Tag 2
	Part Number: Array 1 Part Number 2
	Rank: Unknown
	Configured Memory Speed: Unknown
	Minimum Voltage: Unknown
	Maximum Voltage: Unknown
	Configured Voltage: Unknown
	Memory Technology: Unknown
	Memory Operating Mode Capability: Unknown
	Firmware Version: Not Specified
	Module Manufacturer ID: Unknown
	Module Product ID: Unknown
	Memory Subsystem Controller Manufacturer ID: Unknown
	Memory Subsystem Controller Product ID: Unknown
	Non-Volatile Size: None
	Volatile Size: None
	Cache Size: None
	Logical Size: None

Handle 0x007D, DMI type 17, 92 bytes
Memory Device
	Array Handle: 0x0071
	Error Information Handle: No Error
	Total Width: 72 bits
	Data Width: 64 bits
	Size: 8 GB
	Form Factor: DIMM
	Set: None
	Locator: Socket 1 DIMM 3
	Bank Locator: Bank 3
	Type: DDR4
	Type Detail: Registered (Buffered)
	Speed: 3200 MT/s
	Manufacturer: Samsung
	Serial Number: 01971970
	Asset Tag: Array 1 Asset Tag 3
	Part Number: M393A1K43DB2-CWE
	Rank: 1
	Configured Memory Speed: 3200 MT/s
	Minimum Voltage: 1.14 V
	Maximum Voltage: 1.26 V
	Configured Voltage: 1.2 V
	Memory Technology: DRAM
	Memory Operating Mode Capability: None
	Firmware Version: Not Specified
	Module Manufacturer ID: Bank 1, Hex 0xCE
	Module Product ID: Unknown
	Memory Subsystem Controller Manufacturer ID: Unknown
	Memory Subsystem Controller Product ID: Unknown
	Non-Volatile Size: None
	Volatile Size: 8 GB
	Cache Size: None
	Logical Size: None

Handle 0x0080, DMI type 17, 92 bytes
Memory Device
	Array Handle: 0x0071
	Error Information Handle: 0x0082
	Total Width: Unknown
	Data Width: Unknown
	Size: No Module Installed
	Form Factor: DIMM
	Set: None
	Locator: Socket 1 DIMM 4
	Bank Locator: Bank 4
	Type: Unknown
	Type Detail: Unknown
	Speed: Unknown
	Manufacturer: Array 1 Manufacturer 4
	Serial Number: Array 1 Serial Number 4
	Asset Tag: Array 1 Asset Tag 4
	Part Number: Array 1 Part Number 4
	Rank: Unknown
	Configured Memory Speed: Unknown
	Minimum Voltage: Unknown
	Maximum Voltage: Unknown
	Configured Voltage: Unknown
	Memory Technology: Unknown
	Memory Operating Mode Capability: Unknown
	Firmware Version: Not Specified
	Module Manufacturer ID: Unknown
	Module Product ID: Unknown
	Memory Subsystem Controller Manufacturer ID: Unknown
	Memory Subsystem Controller Product ID: Unknown
	Non-Volatile Size: None
	Volatile Size: None
	Cache Size: None
	Logical Size: None

Handle 0x0083, DMI type 17, 92 bytes
Memory Device
	Array Handle: 0x0071
	Error Information Handle: No Error
	Total Width: 72 bits
	Data Width: 64 bits
	Size: 8 GB
	Form Factor: DIMM
	Set: None
	Locator: Socket 1 DIMM 5
	Bank Locator: Bank 5
	Type: DDR4
	Type Detail: Registered (Buffered)
	Speed: 3200 MT/s
	Manufacturer: Samsung
	Serial Number: 01971993
	Asset Tag: Array 1 Asset Tag 5
	Part Number: M393A1K43DB2-CWE
	Rank: 1
	Configured Memory Speed: 3200 MT/s
	Minimum Voltage: 1.14 V
	Maximum Voltage: 1.26 V
	Configured Voltage: 1.2 V
	Memory Technology: DRAM
	Memory Operating Mode Capability: None
	Firmware Version: Not Specified
	Module Manufacturer ID: Bank 1, Hex 0xCE
	Module Product ID: Unknown
	Memory Subsystem Controller Manufacturer ID: Unknown
	Memory Subsystem Controller Product ID: Unknown
	Non-Volatile Size: None
	Volatile Size: 8 GB
	Cache Size: None
	Logical Size: None

Handle 0x0086, DMI type 17, 92 bytes
Memory Device
	Array Handle: 0x0071
	Error Information Handle: 0x0088
	Total Width: Unknown
	Data Width: Unknown
	Size: No Module Installed
	Form Factor: DIMM
	Set: None
	Locator: Socket 1 DIMM 6
	Bank Locator: Bank 6
	Type: Unknown
	Type Detail: Unknown
	Speed: Unknown
	Manufacturer: Array 1 Manufacturer 6
	Serial Number: Array 1 Serial Number 6
	Asset Tag: Array 1 Asset Tag 6
	Part Number: Array 1 Part Number 6
	Rank: Unknown
	Configured Memory Speed: Unknown
	Minimum Voltage: Unknown
	Maximum Voltage: Unknown
	Configured Voltage: Unknown
	Memory Technology: Unknown
	Memory Operating Mode Capability: Unknown
	Firmware Version: Not Specified
	Module Manufacturer ID: Unknown
	Module Product ID: Unknown
	Memory Subsystem Controller Manufacturer ID: Unknown
	Memory Subsystem Controller Product ID: Unknown
	Non-Volatile Size: None
	Volatile Size: None
	Cache Size: None
	Logical Size: None

Handle 0x0089, DMI type 17, 92 bytes
Memory Device
	Array Handle: 0x0071
	Error Information Handle: No Error
	Total Width: 72 bits
	Data Width: 64 bits
	Size: 8 GB
	Form Factor: DIMM
	Set: None
	Locator: Socket 1 DIMM 7
	Bank Locator: Bank 7
	Type: DDR4
	Type Detail: Registered (Buffered)
	Speed: 3200 MT/s
	Manufacturer: Samsung
	Serial Number: 01971985
	Asset Tag: Array 1 Asset Tag 7
	Part Number: M393A1K43DB2-CWE
	Rank: 1
	Configured Memory Speed: 3200 MT/s
	Minimum Voltage: 1.14 V
	Maximum Voltage: 1.26 V
	Configured Voltage: 1.2 V
	Memory Technology: DRAM
	Memory Operating Mode Capability: None
	Firmware Version: Not Specified
	Module Manufacturer ID: Bank 1, Hex 0xCE
	Module Product ID: Unknown
	Memory Subsystem Controller Manufacturer ID: Unknown
	Memory Subsystem Controller Product ID: Unknown
	Non-Volatile Size: None
	Volatile Size: 8 GB
	Cache Size: None
	Logical Size: None

Handle 0x008C, DMI type 17, 92 bytes
Memory Device
	Array Handle: 0x0071
	Error Information Handle: 0x008E
	Total Width: Unknown
	Data Width: Unknown
	Size: No Module Installed
	Form Factor: DIMM
	Set: None
	Locator: Socket 1 DIMM 8
	Bank Locator: Bank 8
	Type: Unknown
	Type Detail: Unknown
	Speed: Unknown
	Manufacturer: Array 1 Manufacturer 8
	Serial Number: Array 1 Serial Number 8
	Asset Tag: Array 1 Asset Tag 8
	Part Number: Array 1 Part Number 8
	Rank: Unknown
	Configured Memory Speed: Unknown
	Minimum Voltage: Unknown
	Maximum Voltage: Unknown
	Configured Voltage: Unknown
	Memory Technology: Unknown
	Memory Operating Mode Capability: Unknown
	Firmware Version: Not Specified
	Module Manufacturer ID: Unknown
	Module Product ID: Unknown
	Memory Subsystem Controller Manufacturer ID: Unknown
	Memory Subsystem Controller Product ID: Unknown
	Non-Volatile Size: None
	Volatile Size: None
	Cache Size: None
	Logical Size: None

Handle 0x008F, DMI type 17, 92 bytes
Memory Device
	Array Handle: 0x0071
	Error Information Handle: No Error
	Total Width: 72 bits
	Data Width: 64 bits
	Size: 8 GB
	Form Factor: DIMM
	Set: None
	Locator: Socket 1 DIMM 9
	Bank Locator: Bank 9
	Type: DDR4
	Type Detail: Registered (Buffered)
	Speed: 3200 MT/s
	Manufacturer: Samsung
	Serial Number: 01971917
	Asset Tag: Array 1 Asset Tag 9
	Part Number: M393A1K43DB2-CWE
	Rank: 1
	Configured Memory Speed: 3200 MT/s
	Minimum Voltage: 1.14 V
	Maximum Voltage: 1.26 V
	Configured Voltage: 1.2 V
	Memory Technology: DRAM
	Memory Operating Mode Capability: None
	Firmware Version: Not Specified
	Module Manufacturer ID: Bank 1, Hex 0xCE
	Module Product ID: Unknown
	Memory Subsystem Controller Manufacturer ID: Unknown
	Memory Subsystem Controller Product ID: Unknown
	Non-Volatile Size: None
	Volatile Size: 8 GB
	Cache Size: None
	Logical Size: None

Handle 0x0092, DMI type 17, 92 bytes
Memory Device
	Array Handle: 0x0071
	Error Information Handle: 0x0094
	Total Width: Unknown
	Data Width: Unknown
	Size: No Module Installed
	Form Factor: DIMM
	Set: None
	Locator: Socket 1 DIMM 10
	Bank Locator: Bank 10
	Type: Unknown
	Type Detail: Unknown
	Speed: Unknown
	Manufacturer: Array 1 Manufacturer 10
	Serial Number: Array 1 Serial Number 10
	Asset Tag: Array 1 Asset Tag 10
	Part Number: Array 1 Part Number 10
	Rank: Unknown
	Configured Memory Speed: Unknown
	Minimum Voltage: Unknown
	Maximum Voltage: Unknown
	Configured Voltage: Unknown
	Memory Technology: Unknown
	Memory Operating Mode Capability: Unknown
	Firmware Version: Not Specified
	Module Manufacturer ID: Unknown
	Module Product ID: Unknown
	Memory Subsystem Controller Manufacturer ID: Unknown
	Memory Subsystem Controller Product ID: Unknown
	Non-Volatile Size: None
	Volatile Size: None
	Cache Size: None
	Logical Size: None

Handle 0x0095, DMI type 17, 92 bytes
Memory Device
	Array Handle: 0x0071
	Error Information Handle: No Error
	Total Width: 72 bits
	Data Width: 64 bits
	Size: 8 GB
	Form Factor: DIMM
	Set: None
	Locator: Socket 1 DIMM 11
	Bank Locator: Bank 11
	Type: DDR4
	Type Detail: Registered (Buffered)
	Speed: 3200 MT/s
	Manufacturer: Samsung
	Serial Number: 01971984
	Asset Tag: Array 1 Asset Tag 11
	Part Number: M393A1K43DB2-CWE
	Rank: 1
	Configured Memory Speed: 3200 MT/s
	Minimum Voltage: 1.14 V
	Maximum Voltage: 1.26 V
	Configured Voltage: 1.2 V
	Memory Technology: DRAM
	Memory Operating Mode Capability: None
	Firmware Version: Not Specified
	Module Manufacturer ID: Bank 1, Hex 0xCE
	Module Product ID: Unknown
	Memory Subsystem Controller Manufacturer ID: Unknown
	Memory Subsystem Controller Product ID: Unknown
	Non-Volatile Size: None
	Volatile Size: 8 GB
	Cache Size: None
	Logical Size: None

Handle 0x0098, DMI type 17, 92 bytes
Memory Device
	Array Handle: 0x0071
	Error Information Handle: 0x009A
	Total Width: Unknown
	Data Width: Unknown
	Size: No Module Installed
	Form Factor: DIMM
	Set: None
	Locator: Socket 1 DIMM 12
	Bank Locator: Bank 12
	Type: Unknown
	Type Detail: Unknown
	Speed: Unknown
	Manufacturer: Array 1 Manufacturer 12
	Serial Number: Array 1 Serial Number 12
	Asset Tag: Array 1 Asset Tag 12
	Part Number: Array 1 Part Number 12
	Rank: Unknown
	Configured Memory Speed: Unknown
	Minimum Voltage: Unknown
	Maximum Voltage: Unknown
	Configured Voltage: Unknown
	Memory Technology: Unknown
	Memory Operating Mode Capability: Unknown
	Firmware Version: Not Specified
	Module Manufacturer ID: Unknown
	Module Product ID: Unknown
	Memory Subsystem Controller Manufacturer ID: Unknown
	Memory Subsystem Controller Product ID: Unknown
	Non-Volatile Size: None
	Volatile Size: None
	Cache Size: None
	Logical Size: None

Handle 0x009B, DMI type 17, 92 bytes
Memory Device
	Array Handle: 0x0071
	Error Information Handle: No Error
	Total Width: 72 bits
	Data Width: 64 bits
	Size: 8 GB
	Form Factor: DIMM
	Set: None
	Locator: Socket 1 DIMM 13
	Bank Locator: Bank 13
	Type: DDR4
	Type Detail: Registered (Buffered)
	Speed: 3200 MT/s
	Manufacturer: Samsung
	Serial Number: 01971B37
	Asset Tag: Array 1 Asset Tag 13
	Part Number: M393A1K43DB2-CWE
	Rank: 1
	Configured Memory Speed: 3200 MT/s
	Minimum Voltage: 1.14 V
	Maximum Voltage: 1.26 V
	Configured Voltage: 1.2 V
	Memory Technology: DRAM
	Memory Operating Mode Capability: None
	Firmware Version: Not Specified
	Module Manufacturer ID: Bank 1, Hex 0xCE
	Module Product ID: Unknown
	Memory Subsystem Controller Manufacturer ID: Unknown
	Memory Subsystem Controller Product ID: Unknown
	Non-Volatile Size: None
	Volatile Size: 8 GB
	Cache Size: None
	Logical Size: None

Handle 0x009E, DMI type 17, 92 bytes
Memory Device
	Array Handle: 0x0071
	Error Information Handle: 0x00A0
	Total Width: Unknown
	Data Width: Unknown
	Size: No Module Installed
	Form Factor: DIMM
	Set: None
	Locator: Socket 1 DIMM 14
	Bank Locator: Bank 14
	Type: Unknown
	Type Detail: Unknown
	Speed: Unknown
	Manufacturer: Array 1 Manufacturer 14
	Serial Number: Array 1 Serial Number 14
	Asset Tag: Array 1 Asset Tag 14
	Part Number: Array 1 Part Number 14
	Rank: Unknown
	Configured Memory Speed: Unknown
	Minimum Voltage: Unknown
	Maximum Voltage: Unknown
	Configured Voltage: Unknown
	Memory Technology: Unknown
	Memory Operating Mode Capability: Unknown
	Firmware Version: Not Specified
	Module Manufacturer ID: Unknown
	Module Product ID: Unknown
	Memory Subsystem Controller Manufacturer ID: Unknown
	Memory Subsystem Controller Product ID: Unknown
	Non-Volatile Size: None
	Volatile Size: None
	Cache Size: None
	Logical Size: None

Handle 0x00A1, DMI type 17, 92 bytes
Memory Device
	Array Handle: 0x0071
	Error Information Handle: No Error
	Total Width: 72 bits
	Data Width: 64 bits
	Size: 8 GB
	Form Factor: DIMM
	Set: None
	Locator: Socket 1 DIMM 15
	Bank Locator: Bank 15
	Type: DDR4
	Type Detail: Registered (Buffered)
	Speed: 3200 MT/s
	Manufacturer: Samsung
	Serial Number: 01971C99
	Asset Tag: Array 1 Asset Tag 15
	Part Number: M393A1K43DB2-CWE
	Rank: 1
	Configured Memory Speed: 3200 MT/s
	Minimum Voltage: 1.14 V
	Maximum Voltage: 1.26 V
	Configured Voltage: 1.2 V
	Memory Technology: DRAM
	Memory Operating Mode Capability: None
	Firmware Version: Not Specified
	Module Manufacturer ID: Bank 1, Hex 0xCE
	Module Product ID: Unknown
	Memory Subsystem Controller Manufacturer ID: Unknown
	Memory Subsystem Controller Product ID: Unknown
	Non-Volatile Size: None
	Volatile Size: 8 GB
	Cache Size: None
	Logical Size: None

Handle 0x00A4, DMI type 17, 92 bytes
Memory Device
	Array Handle: 0x0071
	Error Information Handle: 0x00A6
	Total Width: Unknown
	Data Width: Unknown
	Size: No Module Installed
	Form Factor: DIMM
	Set: None
	Locator: Socket 1 DIMM 16
	Bank Locator: Bank 16
	Type: Unknown
	Type Detail: Unknown
	Speed: Unknown
	Manufacturer: Array 1 Manufacturer 16
	Serial Number: Array 1 Serial Number 16
	Asset Tag: Array 1 Asset Tag 16
	Part Number: Array 1 Part Number 16
	Rank: Unknown
	Configured Memory Speed: Unknown
	Minimum Voltage: Unknown
	Maximum Voltage: Unknown
	Configured Voltage: Unknown
	Memory Technology: Unknown
	Memory Operating Mode Capability: Unknown
	Firmware Version: Not Specified
	Module Manufacturer ID: Unknown
	Module Product ID: Unknown
	Memory Subsystem Controller Manufacturer ID: Unknown
	Memory Subsystem Controller Product ID: Unknown
	Non-Volatile Size: None
	Volatile Size: None
	Cache Size: None
	Logical Size: None
```

## Linux cmdline

```
BOOT_IMAGE=/boot/vmlinuz-5.15.0-46-generic root=UUID=7d1d0e77-4df0-43df-9619-a99db29ffb83 ro audit=0 default_hugepagesz=2M hugepagesz=1G hugepages=32 hugepagesz=2M hugepages=32768 iommu.passthrough=1 isolcpus=1-10,29-38 nmi_watchdog=0 nohz_full=1-10,29-38 nosoftlockup processor.max_cstate=1 rcu_nocbs=1-10,29-38 console=ttyAMA0,115200n8 quiet
```
