---
bookToc: true
title: "Huawei Taishan"
---

# Huawei Taishan

## Linux lscpu

```
Architecture:           aarch64
  CPU op-mode(s):       32-bit, 64-bit
  Byte Order:           Little Endian
CPU(s):                 64
  On-line CPU(s) list:  0-63
Vendor ID:              ARM
  Model name:           Cortex-A72
    Model:              2
    Thread(s) per core: 1
    Core(s) per socket: 32
    Socket(s):          2
    Stepping:           r0p2
    BogoMIPS:           100.00
    Flags:              fp asimd evtstrm aes pmull sha1 sha2 crc32 cpuid
Caches (sum of all):
  L1d:                  2 MiB (64 instances)
  L1i:                  3 MiB (64 instances)
  L2:                   16 MiB (16 instances)
  L3:                   64 MiB (4 instances)
NUMA:
  NUMA node(s):         4
  NUMA node0 CPU(s):    0-15
  NUMA node1 CPU(s):    16-31
  NUMA node2 CPU(s):    32-47
  NUMA node3 CPU(s):    48-63
Vulnerabilities:
  Itlb multihit:        Not affected
  L1tf:                 Not affected
  Mds:                  Not affected
  Meltdown:             Not affected
  Mmio stale data:      Not affected
  Retbleed:             Not affected
  Spec store bypass:    Vulnerable
  Spectre v1:           Mitigation; __user pointer sanitization
  Spectre v2:           Vulnerable
  Srbds:                Not affected
  Tsx async abort:      Not affected
```

## Linux dmidecode

```
# dmidecode 3.3
Getting SMBIOS data from sysfs.
SMBIOS 3.0.0 present.
Table at 0x39150000.

Handle 0x0000, DMI type 0, 24 bytes
BIOS Information
	Vendor: Huawei Corp.
	Version: Estuary-5.1 D05 LTS
	Release Date: 05/25/2018
	Address: 0xA4800
	Runtime Size: 366 kB
	ROM Size: 3 MB
	Characteristics:
		PCI is supported
		BIOS is upgradeable
		BIOS shadowing is allowed
		Boot from CD is supported
		Selectable boot is supported
		EDD is supported
		Japanese floppy for NEC 9800 1.2 MB is supported (int 13h)
		Japanese floppy for Toshiba 1.2 MB is supported (int 13h)
		5.25"/360 kB floppy services are supported (int 13h)
		5.25"/1.2 MB floppy services are supported (int 13h)
		3.5"/720 kB floppy services are supported (int 13h)
		3.5"/2.88 MB floppy services are supported (int 13h)
		8042 keyboard services are supported (int 9h)
		CGA/mono video services are supported (int 10h)
		ACPI is supported
		USB legacy is supported
		BIOS boot specification is supported
		Targeted content distribution is supported
		UEFI is supported
	BIOS Revision: 0.0

Handle 0x0001, DMI type 1, 27 bytes
System Information
	Manufacturer: Huawei
	Product Name: D05
	Version: VER.A
	Serial Number: 2102311TBJ10J1000089
	UUID: e11a0a38-f920-11e7-8c7d-a0a33bc11426
	Wake-up Type: Power Switch
	SKU Number: To be filled by O.E.M.
	Family: To be filled by O.E.M.

Handle 0x0002, DMI type 3, 25 bytes
Chassis Information
	Manufacturer: Huawei
	Type: Main Server Chassis
	Lock: Not Present
	Version: To be filled by O.E.M.
	Serial Number: To be filled by O.E.M.
	Asset Tag: To be filled by O.E.M.
	Boot-up State: Safe
	Power Supply State: Safe
	Thermal State: Safe
	Security Status: None
	OEM Information: 0x00000000
	Height: 2 U
	Number Of Power Cords: 1
	Contained Elements: 0
	SKU Number: Not Specified

Handle 0x0003, DMI type 2, 17 bytes
Base Board Information
	Manufacturer: Huawei
	Product Name: D05
	Version: Estuary
	Serial Number: 024APL10H8000089
	Asset Tag: To be filled by O.E.M.
	Features:
		Board is a hosting board
		Board is replaceable
	Location In Chassis: To Be Filled By O.E.M.
	Chassis Handle: 0x0002
	Type: Motherboard
	Contained Object Handles: 0
```

## Linux dmidecode memory

```
Handle 0x0007, DMI type 16, 23 bytes
Physical Memory Array
	Location: System Board Or Motherboard
	Use: System Memory
	Error Correction Type: None
	Maximum Capacity: 512 GB
	Error Information Handle: Not Provided
	Number Of Devices: 16

Handle 0x0009, DMI type 17, 40 bytes
Memory Device
	Array Handle: 0x0007
	Error Information Handle: Not Provided
	Total Width: 72 bits
	Data Width: 64 bits
	Size: 16 GB
	Form Factor: DIMM
	Set: None
	Locator: DIMM000 J5
	Bank Locator: SOCKET 0 CHANNEL 0 DIMM 0
	Type: DDR4
	Type Detail: Synchronous Registered (Buffered)
	Speed: 2400 MT/s
	Manufacturer: Samsung
	Serial Number: 0x37663087
	Asset Tag: Unknown
	Part Number: M393A2K43BB1-CRC
	Rank: 2
	Configured Memory Speed: 2400 MT/s
	Minimum Voltage: 1.2 V
	Maximum Voltage: 2.0 V
	Configured Voltage: 1.2 V

Handle 0x000A, DMI type 17, 40 bytes
Memory Device
	Array Handle: 0x0007
	Error Information Handle: Not Provided
	Total Width: Unknown
	Data Width: Unknown
	Size: No Module Installed
	Form Factor: DIMM
	Set: None
	Locator: DIMM001 J6
	Bank Locator: SOCKET 0 CHANNEL 0 DIMM 1
	Type: Unknown
	Type Detail: Unknown Synchronous
	Speed: Unknown
	Manufacturer: NO DIMM
	Serial Number: NO DIMM
	Asset Tag: NO DIMM
	Part Number: NO DIMM
	Rank: Unknown
	Configured Memory Speed: Unknown
	Minimum Voltage: Unknown
	Maximum Voltage: Unknown
	Configured Voltage: Unknown

Handle 0x000B, DMI type 17, 40 bytes
Memory Device
	Array Handle: 0x0007
	Error Information Handle: Not Provided
	Total Width: 72 bits
	Data Width: 64 bits
	Size: 16 GB
	Form Factor: DIMM
	Set: None
	Locator: DIMM010 J8
	Bank Locator: SOCKET 0 CHANNEL 1 DIMM 0
	Type: DDR4
	Type Detail: Synchronous Registered (Buffered)
	Speed: 2400 MT/s
	Manufacturer: Samsung
	Serial Number: 0x37663064
	Asset Tag: Unknown
	Part Number: M393A2K43BB1-CRC
	Rank: 2
	Configured Memory Speed: 2400 MT/s
	Minimum Voltage: 1.2 V
	Maximum Voltage: 2.0 V
	Configured Voltage: 1.2 V

Handle 0x000C, DMI type 17, 40 bytes
Memory Device
	Array Handle: 0x0007
	Error Information Handle: Not Provided
	Total Width: Unknown
	Data Width: Unknown
	Size: No Module Installed
	Form Factor: DIMM
	Set: None
	Locator: DIMM011 J9
	Bank Locator: SOCKET 0 CHANNEL 1 DIMM 1
	Type: Unknown
	Type Detail: Unknown Synchronous
	Speed: Unknown
	Manufacturer: NO DIMM
	Serial Number: NO DIMM
	Asset Tag: NO DIMM
	Part Number: NO DIMM
	Rank: Unknown
	Configured Memory Speed: Unknown
	Minimum Voltage: Unknown
	Maximum Voltage: Unknown
	Configured Voltage: Unknown

Handle 0x000D, DMI type 17, 40 bytes
Memory Device
	Array Handle: 0x0007
	Error Information Handle: Not Provided
	Total Width: 72 bits
	Data Width: 64 bits
	Size: 16 GB
	Form Factor: DIMM
	Set: None
	Locator: DIMM020 J11
	Bank Locator: SOCKET 0 CHANNEL 2 DIMM 0
	Type: DDR4
	Type Detail: Synchronous Registered (Buffered)
	Speed: 2400 MT/s
	Manufacturer: Samsung
	Serial Number: 0x3766308B
	Asset Tag: Unknown
	Part Number: M393A2K43BB1-CRC
	Rank: 2
	Configured Memory Speed: 2400 MT/s
	Minimum Voltage: 1.2 V
	Maximum Voltage: 2.0 V
	Configured Voltage: 1.2 V

Handle 0x000E, DMI type 17, 40 bytes
Memory Device
	Array Handle: 0x0007
	Error Information Handle: Not Provided
	Total Width: Unknown
	Data Width: Unknown
	Size: No Module Installed
	Form Factor: DIMM
	Set: None
	Locator: DIMM021 J12
	Bank Locator: SOCKET 0 CHANNEL 2 DIMM 1
	Type: Unknown
	Type Detail: Unknown Synchronous
	Speed: Unknown
	Manufacturer: NO DIMM
	Serial Number: NO DIMM
	Asset Tag: NO DIMM
	Part Number: NO DIMM
	Rank: Unknown
	Configured Memory Speed: Unknown
	Minimum Voltage: Unknown
	Maximum Voltage: Unknown
	Configured Voltage: Unknown

Handle 0x000F, DMI type 17, 40 bytes
Memory Device
	Array Handle: 0x0007
	Error Information Handle: Not Provided
	Total Width: 72 bits
	Data Width: 64 bits
	Size: 16 GB
	Form Factor: DIMM
	Set: None
	Locator: DIMM030 J14
	Bank Locator: SOCKET 0 CHANNEL 3 DIMM 0
	Type: DDR4
	Type Detail: Synchronous Registered (Buffered)
	Speed: 2400 MT/s
	Manufacturer: Samsung
	Serial Number: 0x376630DA
	Asset Tag: Unknown
	Part Number: M393A2K43BB1-CRC
	Rank: 2
	Configured Memory Speed: 2400 MT/s
	Minimum Voltage: 1.2 V
	Maximum Voltage: 2.0 V
	Configured Voltage: 1.2 V

Handle 0x0010, DMI type 17, 40 bytes
Memory Device
	Array Handle: 0x0007
	Error Information Handle: Not Provided
	Total Width: Unknown
	Data Width: Unknown
	Size: No Module Installed
	Form Factor: DIMM
	Set: None
	Locator: DIMM031 J15
	Bank Locator: SOCKET 0 CHANNEL 3 DIMM 1
	Type: Unknown
	Type Detail: Unknown Synchronous
	Speed: Unknown
	Manufacturer: NO DIMM
	Serial Number: NO DIMM
	Asset Tag: NO DIMM
	Part Number: NO DIMM
	Rank: Unknown
	Configured Memory Speed: Unknown
	Minimum Voltage: Unknown
	Maximum Voltage: Unknown
	Configured Voltage: Unknown

Handle 0x0011, DMI type 17, 40 bytes
Memory Device
	Array Handle: 0x0007
	Error Information Handle: Not Provided
	Total Width: 72 bits
	Data Width: 64 bits
	Size: 16 GB
	Form Factor: DIMM
	Set: None
	Locator: DIMM100 J17
	Bank Locator: SOCKET 1 CHANNEL 0 DIMM 0
	Type: DDR4
	Type Detail: Synchronous Registered (Buffered)
	Speed: 2400 MT/s
	Manufacturer: Samsung
	Serial Number: 0x379A2774
	Asset Tag: Unknown
	Part Number: M393A2K43BB1-CRC
	Rank: 2
	Configured Memory Speed: 2400 MT/s
	Minimum Voltage: 1.2 V
	Maximum Voltage: 2.0 V
	Configured Voltage: 1.2 V

Handle 0x0012, DMI type 17, 40 bytes
Memory Device
	Array Handle: 0x0007
	Error Information Handle: Not Provided
	Total Width: Unknown
	Data Width: Unknown
	Size: No Module Installed
	Form Factor: DIMM
	Set: None
	Locator: DIMM101 J18
	Bank Locator: SOCKET 1 CHANNEL 0 DIMM 1
	Type: Unknown
	Type Detail: Unknown Synchronous
	Speed: Unknown
	Manufacturer: NO DIMM
	Serial Number: NO DIMM
	Asset Tag: NO DIMM
	Part Number: NO DIMM
	Rank: Unknown
	Configured Memory Speed: Unknown
	Minimum Voltage: Unknown
	Maximum Voltage: Unknown
	Configured Voltage: Unknown

Handle 0x0013, DMI type 17, 40 bytes
Memory Device
	Array Handle: 0x0007
	Error Information Handle: Not Provided
	Total Width: 72 bits
	Data Width: 64 bits
	Size: 16 GB
	Form Factor: DIMM
	Set: None
	Locator: DIMM110 J20
	Bank Locator: SOCKET 1 CHANNEL 1 DIMM 0
	Type: DDR4
	Type Detail: Synchronous Registered (Buffered)
	Speed: 2400 MT/s
	Manufacturer: Samsung
	Serial Number: 0x3766308A
	Asset Tag: Unknown
	Part Number: M393A2K43BB1-CRC
	Rank: 2
	Configured Memory Speed: 2400 MT/s
	Minimum Voltage: 1.2 V
	Maximum Voltage: 2.0 V
	Configured Voltage: 1.2 V

Handle 0x0014, DMI type 17, 40 bytes
Memory Device
	Array Handle: 0x0007
	Error Information Handle: Not Provided
	Total Width: Unknown
	Data Width: Unknown
	Size: No Module Installed
	Form Factor: DIMM
	Set: None
	Locator: DIMM111 J21
	Bank Locator: SOCKET 1 CHANNEL 1 DIMM 1
	Type: Unknown
	Type Detail: Unknown Synchronous
	Speed: Unknown
	Manufacturer: NO DIMM
	Serial Number: NO DIMM
	Asset Tag: NO DIMM
	Part Number: NO DIMM
	Rank: Unknown
	Configured Memory Speed: Unknown
	Minimum Voltage: Unknown
	Maximum Voltage: Unknown
	Configured Voltage: Unknown

Handle 0x0015, DMI type 17, 40 bytes
Memory Device
	Array Handle: 0x0007
	Error Information Handle: Not Provided
	Total Width: 72 bits
	Data Width: 64 bits
	Size: 16 GB
	Form Factor: DIMM
	Set: None
	Locator: DIMM120 J23
	Bank Locator: SOCKET 1 CHANNEL 2 DIMM 0
	Type: DDR4
	Type Detail: Synchronous Registered (Buffered)
	Speed: 2400 MT/s
	Manufacturer: Samsung
	Serial Number: 0x376630B0
	Asset Tag: Unknown
	Part Number: M393A2K43BB1-CRC
	Rank: 2
	Configured Memory Speed: 2400 MT/s
	Minimum Voltage: 1.2 V
	Maximum Voltage: 2.0 V
	Configured Voltage: 1.2 V

Handle 0x0016, DMI type 17, 40 bytes
Memory Device
	Array Handle: 0x0007
	Error Information Handle: Not Provided
	Total Width: Unknown
	Data Width: Unknown
	Size: No Module Installed
	Form Factor: DIMM
	Set: None
	Locator: DIMM121 J24
	Bank Locator: SOCKET 1 CHANNEL 2 DIMM 1
	Type: Unknown
	Type Detail: Unknown Synchronous
	Speed: Unknown
	Manufacturer: NO DIMM
	Serial Number: NO DIMM
	Asset Tag: NO DIMM
	Part Number: NO DIMM
	Rank: Unknown
	Configured Memory Speed: Unknown
	Minimum Voltage: Unknown
	Maximum Voltage: Unknown
	Configured Voltage: Unknown

Handle 0x0017, DMI type 17, 40 bytes
Memory Device
	Array Handle: 0x0007
	Error Information Handle: Not Provided
	Total Width: 72 bits
	Data Width: 64 bits
	Size: 16 GB
	Form Factor: DIMM
	Set: None
	Locator: DIMM130 J26
	Bank Locator: SOCKET 1 CHANNEL 3 DIMM 0
	Type: DDR4
	Type Detail: Synchronous Registered (Buffered)
	Speed: 2400 MT/s
	Manufacturer: Samsung
	Serial Number: 0x376630A0
	Asset Tag: Unknown
	Part Number: M393A2K43BB1-CRC
	Rank: 2
	Configured Memory Speed: 2400 MT/s
	Minimum Voltage: 1.2 V
	Maximum Voltage: 2.0 V
	Configured Voltage: 1.2 V

Handle 0x0018, DMI type 17, 40 bytes
Memory Device
	Array Handle: 0x0007
	Error Information Handle: Not Provided
	Total Width: Unknown
	Data Width: Unknown
	Size: No Module Installed
	Form Factor: DIMM
	Set: None
	Locator: DIMM131 J27
	Bank Locator: SOCKET 1 CHANNEL 3 DIMM 1
	Type: Unknown
	Type Detail: Unknown Synchronous
	Speed: Unknown
	Manufacturer: NO DIMM
	Serial Number: NO DIMM
	Asset Tag: NO DIMM
	Part Number: NO DIMM
	Rank: Unknown
	Configured Memory Speed: Unknown
	Minimum Voltage: Unknown
	Maximum Voltage: Unknown
	Configured Voltage: Unknown
```

## Linux cmdline

```
BOOT_IMAGE=/boot/vmlinuz-5.4.0-65-generic root=UUID=7d1d0e77-4df0-43df-9619-a99db29ffb83 ro audit=0 intel_iommu=on isolcpus=1-27,29-55 nmi_watchdog=0 nohz_full=1-27,29-55 nosoftlockup processor.max_cstate=1 rcu_nocbs=1-27,29-55 console=ttyAMA0,115200n8 quiet
```
