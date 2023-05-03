---
bookToc: true
title: "GigaByte ThunderX2"
---

# GigaByte ThunderX2

## Linux lscpu

```
Architecture:           aarch64
  CPU op-mode(s):       64-bit
  Byte Order:           Little Endian
CPU(s):                 56
  On-line CPU(s) list:  0-55
Vendor ID:              Cavium
  Model name:           ThunderX2 99xx
    Model:              1
    Thread(s) per core: 1
    Core(s) per socket: 28
    Socket(s):          2
    Stepping:           0x1
    Frequency boost:    disabled
    CPU max MHz:        2000.0000
    CPU min MHz:        1000.0000
    BogoMIPS:           400.00
    Flags:              fp asimd evtstrm aes pmull sha1 sha2 crc32 atomics cpuid asimdrdm
Caches (sum of all):
  L1d:                  1.8 MiB (56 instances)
  L1i:                  1.8 MiB (56 instances)
  L2:                   14 MiB (56 instances)
  L3:                   64 MiB (2 instances)
NUMA:
  NUMA node(s):         2
  NUMA node0 CPU(s):    0-27
  NUMA node1 CPU(s):    28-55
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
SMBIOS 3.1.1 present.
Table at 0xFE340000.

Handle 0x0000, DMI type 0, 26 bytes
BIOS Information
	Vendor: GIGABYTE
	Version: F28
	Release Date: 12/27/2019
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
		ACPI is supported
		BIOS boot specification is supported
		Targeted content distribution is supported
		UEFI is supported
	BIOS Revision: 7.3

Handle 0x0001, DMI type 1, 27 bytes
System Information
	Manufacturer: GIGABYTE
	Product Name: R181-T90-00
	Version: 0100
	Serial Number: GIG7P9512A0022
	UUID: 00000000-0000-0040-8000-e0d55eae7026
	Wake-up Type: Power Switch
	SKU Number: SABER SKU
	Family: Server

Handle 0x0002, DMI type 2, 15 bytes
Base Board Information
	Manufacturer: GIGABYTE
	Product Name: MT91-FS1-00
	Version: 01000100
	Serial Number: IH6P8800035
	Asset Tag: 01234567890123456789AB
	Features:
		Board is a hosting board
		Board is replaceable
	Location In Chassis: Default string
	Chassis Handle: 0x0003
	Type: Motherboard
	Contained Object Handles: 0

Handle 0x0003, DMI type 3, 22 bytes
Chassis Information
	Manufacturer: GIGABYTE
	Type: Rack Mount Chassis
	Lock: Not Present
	Version: 1.0
	Serial Number: K61186073100003
	Asset Tag: 01234567890123456789AB
	Boot-up State: Safe
	Power Supply State: Safe
	Thermal State: Safe
	Security Status: None
	OEM Information: 0x00000000
	Height: Unspecified
	Number Of Power Cords: 1
	Contained Elements: 0
	SKU Number: Default string

Handle 0x0004, DMI type 10, 6 bytes
On Board Device Information
	Type: Unknown
	Status: Enabled
	Description: Device 1

Handle 0x0005, DMI type 12, 5 bytes
System Configuration Options
	Option 1: Default string

Handle 0x0006, DMI type 13, 22 bytes
BIOS Language Information
	Language Description Format: Long
	Installable Languages: 1
		en|US|iso8859-1
	Currently Installed Language: en|US|iso8859-1

Handle 0x0007, DMI type 31, 28 bytes
Boot Integrity Services Entry Point
	Checksum: Invalid
	16-bit Entry Point Address: FFFF:FFFF
	32-bit Entry Point Address: 0xFFFFFFFF

Handle 0x0008, DMI type 32, 11 bytes
System Boot Information
	Status: No errors detected

Handle 0x0009, DMI type 39, 22 bytes
System Power Supply
	Power Unit Group: 1
	Location: CHINA
	Name: FSP1200-20ERM
	Manufacturer: FSP GROUP
	Serial Number: WS8011100823
	Asset Tag: Default string
	Model Part Number: FSP1200-20ERM
	Revision: 10
	Max Power Capacity: 2648 W
	Status: Present, OK
	Type: Switching
	Input Voltage Range Switching: Auto-switch
	Plugged: Yes
	Hot Replaceable: No

Handle 0x0010, DMI type 39, 22 bytes
System Power Supply
	Power Unit Group: 1
	Location: CHINA
	Name: FSP1200-20ERM
	Manufacturer: FSP GROUP
	Serial Number: WS8011100830
	Asset Tag: Default string
	Model Part Number: FSP1200-20ERM
	Revision: 10
	Max Power Capacity: 2648 W
	Status: Present, OK
	Type: Switching
	Input Voltage Range Switching: Auto-switch
	Plugged: Yes
	Hot Replaceable: No

Handle 0x0011, DMI type 41, 11 bytes
Onboard Device
	Reference Designation: Device 1
	Type: Unknown
	Status: Enabled
	Type Instance: 1
	Bus Address: 0000:00:00.0

Handle 0x0012, DMI type 41, 11 bytes
Onboard Device
	Reference Designation: Device 2
	Type: Unknown
	Status: Enabled
	Type Instance: 1
	Bus Address: 0000:00:00.0

Handle 0x0013, DMI type 41, 11 bytes
Onboard Device
	Reference Designation: Device 3
	Type: Unknown
	Status: Enabled
	Type Instance: 1
	Bus Address: 0000:00:00.0

Handle 0x0014, DMI type 41, 11 bytes
Onboard Device
	Reference Designation: Device 4
	Type: Unknown
	Status: Enabled
	Type Instance: 1
	Bus Address: 0000:00:00.0

Handle 0x0015, DMI type 41, 11 bytes
Onboard Device
	Reference Designation: Device 5
	Type: Unknown
	Status: Enabled
	Type Instance: 1
	Bus Address: 0000:00:00.0

Handle 0x0016, DMI type 38, 18 bytes
IPMI Device Information
	Interface Type: SSIF (SMBus System Interface)
	Specification Version: 2.0
	I2C Slave Address: 0x10
	NV Storage Device: Not Present
	Base Address: 0x10 (SMBus)

Handle 0x0017, DMI type 42, 12 bytes
Management Controller Host Interface
	Interface Type: OEM
	Vendor ID: 0xFF0102FF

Handle 0x0029, DMI type 11, 5 bytes
OEM Strings
	String 1: HWID=E38C
	String 2: cavium.com
	String 3: Saber

Handle 0x002A, DMI type 13, 22 bytes
BIOS Language Information
	Language Description Format: Abbreviated
	Installable Languages: 1
		enUS
	Currently Installed Language: enUS

Handle 0x002B, DMI type 4, 48 bytes
Processor Information
	Socket Designation: Socket 0
	Type: Central Processor
	Family: ARM
	Manufacturer: Cavium Inc.
	ID: F1 0A 1F 43 00 00 00 00
	Signature: Implementor 0x43, Variant 0x1, Architecture 15, Part 0x0af, Revision 1
	Version: Cavium ThunderX2(R) CPU CN9975 v2.1 @ 2.0GHz
	Voltage: 0.8 V
	External Clock: 33 MHz
	Max Speed: 2500 MHz
	Current Speed: 2000 MHz
	Status: Populated, Enabled
	Upgrade: Other
	L1 Cache Handle: 0x002C
	L2 Cache Handle: 0x002E
	L3 Cache Handle: 0x002F
	Serial Number: 000081D4-4003326A
	Asset Tag: Not Specified
	Part Number: CN9975-2000BG4077-Y21-G
	Core Count: 28
	Core Enabled: 28
	Thread Count: 28
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
Handle 0x003E, DMI type 16, 23 bytes
Physical Memory Array
	Location: System Board Or Motherboard
	Use: System Memory
	Error Correction Type: Multi-bit ECC
	Maximum Capacity: 2 TB
	Error Information Handle: Not Provided
	Number Of Devices: 12

Handle 0x003F, DMI type 17, 40 bytes
Memory Device
	Array Handle: 0x003E
	Error Information Handle: Not Provided
	Total Width: 72 bits
	Data Width: 64 bits
	Size: 32 GB
	Form Factor: DIMM
	Set: None
	Locator: DIMM_P0_A0
	Bank Locator: N0
	Type: DDR4
	Type Detail: Registered (Buffered)
	Speed: 2400 MT/s
	Manufacturer: Micron Technology
	Serial Number: 469570327
	Asset Tag: Not Specified
	Part Number: 36ASF4G72PZ-2G3B1
	Rank: 2
	Configured Memory Speed: 2400 MT/s
	Minimum Voltage: 1.2 V
	Maximum Voltage: 1.2 V
	Configured Voltage: 1.2 V

Handle 0x0040, DMI type 17, 40 bytes
Memory Device
	Array Handle: 0x003E
	Error Information Handle: Not Provided
	Total Width: 72 bits
	Data Width: 64 bits
	Size: 32 GB
	Form Factor: DIMM
	Set: None
	Locator: DIMM_P0_B0
	Bank Locator: N0
	Type: DDR4
	Type Detail: Registered (Buffered)
	Speed: 2400 MT/s
	Manufacturer: Micron Technology
	Serial Number: 469570172
	Asset Tag: Not Specified
	Part Number: 36ASF4G72PZ-2G3B1
	Rank: 2
	Configured Memory Speed: 2400 MT/s
	Minimum Voltage: 1.2 V
	Maximum Voltage: 1.2 V
	Configured Voltage: 1.2 V

Handle 0x0050, DMI type 16, 23 bytes
Physical Memory Array
	Location: System Board Or Motherboard
	Use: System Memory
	Error Correction Type: Multi-bit ECC
	Maximum Capacity: 2 TB
	Error Information Handle: Not Provided
	Number Of Devices: 12

Handle 0x0051, DMI type 17, 40 bytes
Memory Device
	Array Handle: 0x0050
	Error Information Handle: Not Provided
	Total Width: 72 bits
	Data Width: 64 bits
	Size: 32 GB
	Form Factor: DIMM
	Set: None
	Locator: DIMM_P1_I0
	Bank Locator: N1
	Type: DDR4
	Type Detail: Registered (Buffered)
	Speed: 2400 MT/s
	Manufacturer: Micron Technology
	Serial Number: 469567519
	Asset Tag: Not Specified
	Part Number: 36ASF4G72PZ-2G3B1
	Rank: 2
	Configured Memory Speed: 2400 MT/s
	Minimum Voltage: 1.2 V
	Maximum Voltage: 1.2 V
	Configured Voltage: 1.2 V

Handle 0x0052, DMI type 17, 40 bytes
Memory Device
	Array Handle: 0x0050
	Error Information Handle: Not Provided
	Total Width: 72 bits
	Data Width: 64 bits
	Size: 32 GB
	Form Factor: DIMM
	Set: None
	Locator: DIMM_P1_J0
	Bank Locator: N1
	Type: DDR4
	Type Detail: Registered (Buffered)
	Speed: 2400 MT/s
	Manufacturer: Micron Technology
	Serial Number: 469567696
	Asset Tag: Not Specified
	Part Number: 36ASF4G72PZ-2G3B1
	Rank: 2
	Configured Memory Speed: 2400 MT/s
	Minimum Voltage: 1.2 V
	Maximum Voltage: 1.2 V
	Configured Voltage: 1.2 V
```

## Linux cmdline

```
BOOT_IMAGE=/boot/vmlinuz-5.4.0-65-generic root=UUID=7d1d0e77-4df0-43df-9619-a99db29ffb83 ro audit=0 intel_iommu=on isolcpus=1-27,29-55 nmi_watchdog=0 nohz_full=1-27,29-55 nosoftlockup processor.max_cstate=1 rcu_nocbs=1-27,29-55 console=ttyAMA0,115200n8 quiet
```
