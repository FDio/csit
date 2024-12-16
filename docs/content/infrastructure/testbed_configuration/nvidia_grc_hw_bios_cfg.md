---
bookToc: true
title: "NVidia Grace CPU"
---

# MegaRac Altra

## Linux lscpu

```
Architecture:             aarch64
  CPU op-mode(s):         64-bit
  Byte Order:             Little Endian
CPU(s):                   72
  On-line CPU(s) list:    0-71
Vendor ID:                ARM
  Model name:             Neoverse-V2
    Model:                0
    Thread(s) per core:   1
    Core(s) per socket:   72
    Socket(s):            1
    Stepping:             r0p0
    BogoMIPS:             2000.00
    Flags:                fp asimd evtstrm aes pmull sha1 sha2 crc32 atomics fphp asimdhp cpuid asimdrdm jscvt fcma lrcpc dcpop sha3 sm3
                          sm4 asimddp sha512 sve asimdfhm dit uscat ilrcpc flagm ssbs sb paca pacg dcpodp sve2 sveaes svepmull svebitperm
                           svesha3 svesm4 flagm2 frint svei8mm svebf16 i8mm bf16 dgh bti
Caches (sum of all):
  L1d:                    4.5 MiB (72 instances)
  L1i:                    4.5 MiB (72 instances)
  L2:                     72 MiB (72 instances)
  L3:                     114 MiB (1 instance)
NUMA:
  NUMA node(s):           1
  NUMA node0 CPU(s):      0-71
Vulnerabilities:
  Gather data sampling:   Not affected
  Itlb multihit:          Not affected
  L1tf:                   Not affected
  Mds:                    Not affected
  Meltdown:               Not affected
  Mmio stale data:        Not affected
  Reg file data sampling: Not affected
  Retbleed:               Not affected
  Spec rstack overflow:   Not affected
  Spec store bypass:      Mitigation; Speculative Store Bypass disabled via prctl
  Spectre v1:             Mitigation; __user pointer sanitization
  Spectre v2:             Not affected
  Srbds:                  Not affected
  Tsx async abort:        Not affected
```

## Linux dmidecode

```
# dmidecode 3.5
Getting SMBIOS data from sysfs.
SMBIOS 3.6.0 present.
# SMBIOS implementations newer than version 3.5.0 are not
# fully supported by this version of dmidecode.
Table at 0x3C63C70000.

Handle 0x0000, DMI type 42, 124 bytes
Management Controller Host Interface
        Host Interface Type: Network
        Device Type: <OUT OF SPEC>
        Vendor ID: 0x11:0x25:0x05:0xa2
        Protocol ID: 04 (Redfish over IP)
                Service UUID: a6bd26ba-b0f4-413a-9054-75344b6e5bf5
                Host IP Assignment Type: Static
                Host IP Address Format: IPv4
                IPv4 Address: 10.0.1.2
                IPv4 Mask: 255.255.255.0
                Redfish Service IP Discovery Type: Static
                Redfish Service IP Address Format: IPv4
                IPv4 Redfish Service Address: 10.0.1.1
                IPv4 Redfish Service Mask: 255.255.255.0
                Redfish Service Port: 443
                Redfish Service Vlan: 0
                Redfish Service Hostname: legoc1

Handle 0x0001, DMI type 0, 26 bytes
BIOS Information
        Vendor: NVIDIA
        Version:         00020003
        Release Date: 20240516
        ROM Size: 64 MB
        Characteristics:
                PCI is supported
                PNP is supported
                BIOS is upgradeable
                BIOS shadowing is allowed
                Boot from CD is supported
                Selectable boot is supported
                Serial services are supported (int 14h)
                ACPI is supported
                Targeted content distribution is supported
                UEFI is supported
        Firmware Revision: 24.3

Handle 0x0002, DMI type 7, 27 bytes
Cache Information
        Socket Designation: L1 Instruction Cache
        Configuration: Enabled, Not Socketed, Level 1
        Operational Mode: Write Back
        Location: Internal
        Installed Size: 4608 kB
        Maximum Size: 4608 kB
        Supported SRAM Types:
                Unknown
        Installed SRAM Type: Unknown
        Speed: Unknown
        Error Correction Type: Unknown
        System Type: Instruction
        Associativity: 4-way Set-associative

Handle 0x0003, DMI type 7, 27 bytes
Cache Information
        Socket Designation: L1 Data Cache
        Configuration: Enabled, Not Socketed, Level 1
        Operational Mode: Write Back
        Location: Internal
        Installed Size: 4608 kB
        Maximum Size: 4608 kB
        Supported SRAM Types:
                Unknown
        Installed SRAM Type: Unknown
        Speed: Unknown
        Error Correction Type: Unknown
        System Type: Data
        Associativity: 4-way Set-associative

Handle 0x0004, DMI type 7, 27 bytes
Cache Information
        Socket Designation: L2 Cache
        Configuration: Enabled, Not Socketed, Level 2
        Operational Mode: Write Back
        Location: Internal
        Installed Size: 72 MB
        Maximum Size: 72 MB
        Supported SRAM Types:
                Unknown
        Installed SRAM Type: Unknown
        Speed: Unknown
        Error Correction Type: Unknown
        System Type: Unified
        Associativity: 8-way Set-associative

Handle 0x0005, DMI type 7, 27 bytes
Cache Information
        Socket Designation: L3 Cache
        Configuration: Enabled, Not Socketed, Level 3
        Operational Mode: Write Back
        Location: Internal
        Installed Size: 114 MB
        Maximum Size: 114 MB
        Supported SRAM Types:
                Unknown
        Installed SRAM Type: Unknown
        Speed: Unknown
        Error Correction Type: Unknown
        System Type: Unified
        Associativity: 12-way Set-associative

Handle 0x0006, DMI type 4, 50 bytes
Processor Information
        Socket Designation: G1:0.0
        Type: Central Processor
        Family: <OUT OF SPEC>
        Manufacturer: NVIDIA
        ID: 41 02 6B 03 02 00 00 00
        Version: Grace A02
        Voltage: Unknown
        External Clock: 1000 MHz
        Max Speed: 4000 MHz
        Current Speed: 3447 MHz
        Status: Populated, Enabled
        Upgrade: None
        L1 Cache Handle: 0x0003
        L2 Cache Handle: 0x0004
        L3 Cache Handle: 0x0005
        Serial Number: 0x00000001780A01860C00000016010200
        Asset Tag: <BAD INDEX>
        Part Number: <BAD INDEX>
        Core Count: 72
        Core Enabled: 72
        Thread Count: 72
        Characteristics:
                64-bit capable
                Execute Protection
                Arm64 SoC ID

Handle 0x0007, DMI type 9, 24 bytes
System Slot Information
        Designation: PCIe Slot 1
        Type: x16 PCI Express 5 x16
        Current Usage: In Use
        Length: Long
        ID: 1
        Characteristics: None
        Bus Address: 0000:01:00.0
        Data Bus Width: 13
        Peer Devices: 0
        PCI Express Generation: 5
        Slot Physical Width: x16
        Height: Full height

Handle 0x0008, DMI type 9, 24 bytes
System Slot Information
        Designation: PCIe Slot 2
        Type: x16 PCI Express 5 x16
        Current Usage: In Use
        Length: Long
        ID: 2
        Characteristics: None
        Bus Address: 0002:01:00.0
        Data Bus Width: 13
        Peer Devices: 0
        PCI Express Generation: 5
        Slot Physical Width: x16
        Height: Full height

Handle 0x0009, DMI type 9, 24 bytes
System Slot Information
        Designation: M.2 NVMe Drive Slot 1
        Type: x4 M.2 Socket 3
        Current Usage: In Use
        Length: Other
        Characteristics: None
        Bus Address: 0004:01:00.0
        Data Bus Width: 10
        Peer Devices: 0
        Slot Physical Width: x4
        Height: Other

Handle 0x000A, DMI type 9, 24 bytes
System Slot Information
        Designation: M.2 NVMe Drive Slot 2
        Type: x4 M.2 Socket 3
        Current Usage: In Use
        Length: Other
        Characteristics: None
        Bus Address: 0005:01:00.0
        Data Bus Width: 10
        Peer Devices: 0
        Slot Physical Width: x4
        Height: Other

Handle 0x000B, DMI type 9, 24 bytes
System Slot Information
        Designation: PCIe Slot 3
        Type: x16 PCI Express 5 x16
        Current Usage: In Use
        Length: Long
        ID: 5
        Characteristics: None
        Bus Address: 0006:01:00.0
        Data Bus Width: 13
        Peer Devices: 0
        PCI Express Generation: 5
        Slot Physical Width: x16
        Height: Full height

Handle 0x000C, DMI type 11, 5 bytes
OEM Strings

Handle 0x000D, DMI type 13, 22 bytes
BIOS Language Information
        Language Description Format: Abbreviated
        Installable Languages: 1
                enUS
        Currently Installed Language: enUS

Handle 0x000E, DMI type 16, 23 bytes
Physical Memory Array
        Location: System Board Or Motherboard
        Use: System Memory
        Error Correction Type: Single-bit ECC
        Maximum Capacity: 240 GB
        Error Information Handle: No Error
        Number Of Devices: 1

Handle 0x000F, DMI type 17, 92 bytes
Memory Device
        Array Handle: 0x000E
        Error Information Handle: 0x0000
        Total Width: 540 bits
        Data Width: 480 bits
        Size: 240 GB
        Form Factor: Die
        Set: None
        Locator: LP5x_0
        Bank Locator: LP5x_0
        Type: LPDDR5
        Type Detail: None
        Speed: 8532 MT/s
        Manufacturer: NVIDIA
        Serial Number: 9223381050307638979
        Asset Tag: Not Specified
        Part Number: Not Specified
        Rank: 1
        Configured Memory Speed: Unknown
        Minimum Voltage: 1.1 V
        Maximum Voltage: 1.1 V
        Configured Voltage: 1.1 V
        Memory Technology: DRAM
        Memory Operating Mode Capability: None
        Firmware Version: Not Specified
        Module Manufacturer ID: Bank 4, Hex 0x6B
        Module Product ID: Unknown
        Memory Subsystem Controller Manufacturer ID: Unknown
        Memory Subsystem Controller Product ID: Unknown
        Non-Volatile Size: None
        Volatile Size: 240 GB
        Cache Size: None
        Logical Size: None

Handle 0x0010, DMI type 19, 31 bytes
Memory Array Mapped Address
        Starting Address: 0x00080000000
        Ending Address: 0x03C800003FF
        Range Size: 240 GB
        Physical Array Handle: 0x000E
        Partition Width: 0

Handle 0x0011, DMI type 2, 17 bytes
Base Board Information
        Manufacturer: Not Specified
        Product Name: Not Specified
        Version: Not Specified
        Serial Number: Not Specified
        Asset Tag: Not Specified
        Features:
                Board requires at least one daughter board
                Board is replaceable
        Location In Chassis: Unknown
        Chassis Handle: 0xFFFE
        Type: System Management Module
        Contained Object Handles: 0

Handle 0x0012, DMI type 2, 17 bytes
Base Board Information
        Manufacturer: Not Specified
        Product Name: Not Specified
        Version: Not Specified
        Serial Number: Not Specified
        Asset Tag: Not Specified
        Features:
                Board requires at least one daughter board
                Board is replaceable
        Location In Chassis: Unknown
        Chassis Handle: 0xFFFE
        Type: Processor+Memory Module
        Contained Object Handles: 1
                0x000F

Handle 0x0013, DMI type 32, 11 bytes
System Boot Information
        Status: No errors detected

Handle 0x0014, DMI type 38, 18 bytes
IPMI Device Information
        Interface Type: SSIF (SMBus System Interface)
        Specification Version: 2.0
        I2C Slave Address: 0x08
        NV Storage Device Address: 0
        Base Address: 0x08 (SMBus)

Handle 0x0015, DMI type 41, 11 bytes
Onboard Device
        Reference Designation: Embedded Video Controller
        Type: Video
        Status: Enabled
        Type Instance: 1
        Bus Address: 0008:02:00.0

Handle 0x0016, DMI type 45, 24 bytes
Firmware Inventory Information
        Firmware Component Name: UEFI
        Firmware Version: buildbrain-gcid-36287995
        Firmware ID: UEFI
        Release Date: 2024-05-15T20:26:25+00:00
        Manufacturer: NVIDIA
        Lowest Supported Firmware Version: buildbrain-gcid-36287995
        Image Size: 64 MB
        Characteristics:
                Updatable: No
                Write-Protect: Yes
        State: Enabled
        Associated Components: 0

Handle 0x0017, DMI type 45, 24 bytes
Firmware Inventory Information
        Firmware Component Name: System ROM
        Firmware Version:         00020003
        Firmware ID: NVIDIA System Firmware
        Release Date: 20240516
        Manufacturer: NVIDIA
        Lowest Supported Firmware Version:         00020003
        Image Size: 64 MB
        Characteristics:
                Updatable: Yes
                Write-Protect: No
        State: Enabled
        Associated Components: 0

Handle 0x0018, DMI type 45, 26 bytes
Firmware Inventory Information
        Firmware Component Name: Full FW Image
        Firmware Version: 28.41.1000
        Firmware ID: Full FW Image
        Release Date: Not Specified
        Manufacturer: Not Specified
        Lowest Supported Firmware Version: 0x00000002
        Image Size: None
        Characteristics:
                Updatable: Yes
                Write-Protect: No
        State: Enabled
        Associated Components: 1
                0x0008

Handle 0x0019, DMI type 45, 24 bytes
Firmware Inventory Information
        Firmware Component Name: FW_FPGA_0
        Firmware Version: 0.96
        Firmware ID: FW_FPGA_0
        Release Date: Not Specified
        Manufacturer: Not Specified
        Lowest Supported Firmware Version: 0.96
        Image Size: Unknown
        Characteristics:
                Updatable: Yes
                Write-Protect: Yes
        State: Enabled
        Associated Components: 0

Handle 0xFEFF, DMI type 127, 4 bytes
End Of Table
```

## Linux cmdline

```
$ cat /proc/cmdline
BOOT_IMAGE=/boot/vmlinuz-6.8.0-45-generic root=UUID=5c1b9bd0-cddf-411f-8f05-a1ede3a45f78 ro audit=0 default_hugepagesz=2M hugepagesz=1G hugepages=32 hugepagesz=2M hugepages=32768 iommu.passthrough=1 isolcpus=1-71 nmi_watchdog=0 nohz_full=1-71 nosoftlockup processor.max_cstate=1 rcu_nocbs=1-71 cpufreq.off=1 cpuidle.off=1
```

## NVidia Grace Server Firmware Inventory

```
Host.           IPMI IP.      BMC.      BIOS. Cx-7 Firmware.  mlx5.
s36-t27-sut1.   10.30.50.36.  ?.        ?.    TBD.            24.04-0.7.0.0.
```