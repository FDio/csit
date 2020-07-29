# SuperMicro Denverton Servers - HW and BIOS Configuration

1. [Linux lscpu](#linux-lscpu)
1. [Linux dmidecode](#dmidecode)
1. [Atom Dnv Server BIOS Configuration](#atom-dnv-server-bios-configuration)
   1. [Boot Feature](#boot-feature)
   1. [CPU Configuration](#cpu-configuration)
   1. [Chipset Configuration](#chipset-configuration)
      1. [North Bridge Configuration](#north-bridge-configuration)
      1. [South Bridge Configuration](#south-bridge-configuration)
   1. [PCIe/PCI/PnP Configuration](#pciepcipnp-configuration)
   1. [ACPI Settings](#acpi-settings)
1. [Atom Dnv Server Firmware Inventory](#atom-dnv-server-firmware-inventory)

## Linux lscpu

```
$ lscpu
Architecture:        x86_64
CPU op-mode(s):      32-bit, 64-bit
Byte Order:          Little Endian
CPU(s):              12
On-line CPU(s) list: 0-11
Thread(s) per core:  1
Core(s) per socket:  12
Socket(s):           1
NUMA node(s):        1
Vendor ID:           GenuineIntel
CPU family:          6
Model:               95
Model name:          Intel(R) Atom(TM) CPU C3858 @ 2.00GHz
Stepping:            1
CPU MHz:             2000.000
CPU max MHz:         2000.0000
CPU min MHz:         800.0000
BogoMIPS:            4000.00
Virtualization:      VT-x
L1d cache:           24K
L1i cache:           32K
L2 cache:            2048K
NUMA node0 CPU(s):   0-11
Flags:               fpu vme de pse tsc msr pae mce cx8 apic sep mtrr pge mca
cmov pat pse36 clflush dts acpi mmx fxsr sse sse2 ss ht tm pbe syscall nx
pdpe1gb rdtscp lm constant_tsc art arch_perfmon pebs bts rep_good nopl xtopology
nonstop_tsc cpuid aperfmperf tsc_known_freq pni pclmulqdq dtes64 monitor ds_cpl
vmx est tm2 ssse3 sdbg cx16 xtpr pdcm sse4_1 sse4_2 x2apic movbe popcnt
tsc_deadline_timer aes xsave rdrand lahf_lm 3dnowprefetch cpuid_fault epb cat_l2
ssbd ibrs ibpb stibp tpr_shadow vnmi flexpriority ept vpid ept_ad fsgsbase
tsc_adjust smep erms mpx rdt_a rdseed smap clflushopt intel_pt sha_ni xsaveopt
xsavec xgetbv1 xsaves dtherm arat pln pts md_clear arch_capabilities

```

### Linux dmidecode

```
  # dmidecode 3.1
  Getting SMBIOS data from sysfs.
  SMBIOS 3.0.0 present.
  Table at 0x7F0C8000.

  Handle 0x0000, DMI type 0, 24 bytes
  BIOS Information
          Vendor: American Megatrends Inc.
          Version: 1.0b
          Release Date: 12/12/2017
          Address: 0xF0000
          Runtime Size: 64 kB
          ROM Size: 16 MB
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
          BIOS Revision: 5.13

  Handle 0x0001, DMI type 1, 27 bytes
  System Information
          Manufacturer: Supermicro
          Product Name: SYS-E300-9A
          Version: 0123456789
          Serial Number: S292431X8616427
          UUID: 03000200-0400-0500-0006-0CC47AFCCA92
          Wake-up Type: Power Switch
          SKU Number: To be filled by O.E.M.
          Family: To be filled by O.E.M.

  Handle 0x0002, DMI type 2, 15 bytes
  Base Board Information
          Manufacturer: Supermicro
          Product Name: A2SDi-TP8F
          Version: 1.10
          Serial Number: OM184S023953
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
          Serial Number: CE300AG39040925
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

  Handle 0x0028, DMI type 4, 48 bytes
  Processor Information
          Socket Designation: CPU
          Type: Central Processor
          Family: Atom
          Manufacturer: Intel(R) Corporation
          ID: F1 06 05 00 FF FB EB BF
          Signature: Type 0, Family 6, Model 95, Stepping 1
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
          Version: Intel(R) Atom(TM) CPU C3858 @ 2.00GHz
          Voltage: 1.6 V
          External Clock: 100 MHz
          Max Speed: 3800 MHz
          Current Speed: 2000 MHz
          Status: Populated, Enabled
          Upgrade: Other
          L1 Cache Handle: 0x0026
          L2 Cache Handle: 0x0027
          L3 Cache Handle: Not Provided
          Serial Number: Not Specified
          Asset Tag: UNKNOWN
          Part Number: Not Specified
          Core Count: 12
          Core Enabled: 12
          Thread Count: 12
          Characteristics:
                  64-bit capable
                  Multi-Core
                  Hardware Thread
                  Execute Protection
                  Enhanced Virtualization
                  Power/Performance Control
```

## Atom Dnv Server BIOS Configuration

### Boot Feature

```
  |  Quiet Boot                                [Enabled]               |Enable or disable to         |
  |                                                                    |display graphic logo during  |
  |  Bootup NumLock State                      [On]                    |POST                         |
  |  Wait For "F1" If Error                    [Enabled]               |                             |
  |                                                                    |                             |
  |  Power Configuration                                               |                             |
  |  Watch Dog Function                        [Disabled]              |                             |
  |  Power Button Function                     [Instant Off]           |                             |
  |  Restore on AC Power Loss                  [Power On]              |                             |
```

### CPU Configuration

```
  |  CPU Configuration                                                 |Enable/Disable EIST. GV3     |
  |                                                                    |and TM1 must be enabled for  |
  |  Intel(R) Atom(TM) CPU C3858 @ 2.00GHz                             |TM2 to be available. GV3     |
  |  Processor ID                              000506F1                |must be enabled for Turbo.   |
  |  Microcode Revision                        00000020                |Auto - Enable for B0 CPU     |
  |  Processor Frequency                       2.000GHz                |stepping, all others         |
  |  CPU BCLK Frequency                          100MHZ                |disabled, change setting to  |
  |  L1 Cache RAM                                  56KB                |override.                    |
  |  L2 Cache RAM                               12288KB                |                             |
  |                                                                    |                             |
  |  EIST (GV3)                                [Enable]                |                             |
  |  BIOS Request Frequency                    [Enable]                |                             |
  |  TM1                                       [Enable]                |                             |
  |  TM2 Mode                                  [Adaptive Throttling]   |                             |
  |  Dynamic Self Refresh                      [Disable]               |                             |
  |  CPU C State                               [Disable]               |                             |
  |  Package C State Limit                     [No Limit]              |                             |
  |  Max Core C-State                          [C6]                    |                             |
  |  Enhanced Hait State (C1E)                 [Enable]                |                             |
  |  Monitor/Mwait                             [Enable]                |                             |
  |  L1 Prefetcher                             [Enable]                |                             |
  |  L1 Prefetcher                             [Enable]                |                             |
  |  ACPI 3.0 T-States                         [Disable]               |                             |
  |  Max CPUID Value Limit                     [Disable]               |                             |
  |  Execute Disable Bit                       [Enable]                |                             |
  |  Virtualization Technology                 [Enable]                |                             |
  |  Extended APIC                             [Enable]                |                             |
  |  AES-NI                                    [Enable]                |                             |
  |  Lock PACKAGE_RAPL_LIMIT                   [Disable]               |                             |
  |  PL1 Time Window                           45                      |                             |
  |  PL1 Power Level                           25                      |                             |
  |  PL2 Power Level                           29                      |                             |
  |  Active Processor Cores                    0                       |                             |
```

### Chipset Configuration

```
  |  WARNING: Setting wrong values in below sections may cause         |North Bridge Parameters      |
  |           system to malfunction.                                   |                             |
  |> North Bridge Configuration                                        |                             |
  |> South Bridge Configuration                                        |                             |
```

#### North Bridge Configuration

```
  |  North Bridge Configuration                                        |COption to Ebable / Disable  |
  |                                                                    |VT-d                         |
  |  Memory Information                                                |                             |
  |  MRC Version                               0.149.4.43              |                             |
  |  Total Memory                              32768 MB                |                             |
  |  Memory Frequency                          DDR4 - 2400 MHZ         |                             |
  |                                                                    |                             |
  |  VT-d                                      [Enabled]               |                             |
  |  VT-d Interrupt remapping                  [Enabled]               |                             |
  |                                                                    |                             |
  |  Fast Boot                                 [Enabled]               |                             |
  |  Command Address Parity                    [Disabled]              |                             |
  |  Memory Frequency                          [DDR-2400]              |                             |
  |  MMIO Size / BMBOUND Base                  [Auto]                  |                             |
  |  TCL performance                           [Enabled]               |                             |
  |  Memory Preservation                       [Disabled]              |                             |
  |  Patrol scrub Enable                       [Enabled]               |                             |
  |  Patrol scrub Period                       [24 hours]              |                             |
  |  Demand Scrub Enable                       [Enabled]               |                             |
  |  Write Data Early Enble                    [Disabled]              |                             |
  |  Select Refresh Rate                       [1x/2x]                 |                             |
  |  CKE Power Down                            [Disabled]              |                             |
  |  Memory Thermal Throttling                 [Disabled]              |                             |
  |  Scrambler                                 [Enabled]               |                             |
  |  Slow Power Down Exit                      [Enabled]               |                             |
```

#### South Bridge Configuration

```
  |  South Bridge Configuration                                        |Enables Legacy USB support.  |
  |                                                                    |AUTO option disables legacy  |
  |  USB Module Version                        19                      |support if no USB devices    |
  |  USB Controllers:                                                  |are connected. DISABLE       |
  |        1 XHCI                                                      |option will keep USB         |
  |  USB Devices:                                                      |devices available only for   |
  |        2 Keyboards, 1 Mouse, 3 Hubs                                |EFI applications.            |
  |                                                                    |                             |
  |  Legacy USB Support                        [Enabled]               |                             |
  |  XHCI Hand-off                             [Enabled]               |                             |
  |  Port 60/64 Emulation                      [Enabled]               |                             |

```

### PCIe/PCI/PnP Configuration

```
  |  PCI Bus Driver Version                    A5.01.12                |Enables or Disables 64bit    |
  |                                                                    |capable Devices to be        |
  |  PCI Devices Common Settings:                                      |Decoded in Above 4G Address  |
  |  Above 4G Decoding                         [Enabled]               |Space (Only if System        |
  |  SR-IOV Support                            [Enabled]               |Supports 64 bit PCI          |
  |  Maximum Payload                           [Auto]                  |Decoding).                   |
  |  Maximum Read Request                      [Auto]                  |                             |
  |  ASPM Support                              [Disabled]              |                             |
  |  ARI Forwarding                            [Disabled]              |                             |
  |                                                                    |                             |
  |  RSC-RR1U-E8 OPROM                         [EFI]                   |                             |
  |  M.2 PCI-E 3.0 X4 OPROM                    [EFI]                   |                             |
  |  Mini PCI-E OPROM                          [EFI]                   |                             |
  |                                                                    |                             |
  |  Onboard LAN OPROM Type                    [EFI]                   |                             |
  |                                                                    |                             |
  |  Onboard Video OPROM                       [EFI]                   |                             |
  |  VGA Priority                              [Onboard]               |                             |
  |                                                                    |                             |
  |  Network Stack                             [Enabled]               |                             |
  |  IPv4 PXE Support                          [Enabled]               |                             |
  |  IPv6 PXE Support                          [Disabled]              |                             |
  |  PXE boot wait time                        0                       |                             |
  |  Media detect count                        1                       |                             |
```

### ACPI Settings

```
  |  ACPI Settings                                                     |Enable/Disable WHEA ACPI     |
  |                                                                    |support                      |
  |  WHEA Support                              [Enabled]               |                             |
```

## Atom Dnv Server Firmware Inventory

```
Host.           IPMI IP.      BMC.   BIOS.  CPU Microcode.  PCI Bus.   ME Operation FW.  X553 Firmware.  ixgbe.
s29-t26-sut1.   10.30.55.11.  3.60.  1.0b.  0x2e.           A5.01.12.  4.0.4.139.        0x8000083f      5.1.0-k
s30-t35-sut1.   10.30.55.12.  3.60.  1.0b.  0x2e.           A5.01.12.  4.0.4.139.        0x8000083f      5.1.0-k
s31-t35-sut2.   10.30.55.13.  3.60.  1.0b.  0x2e.           A5.01.12.  4.0.4.139.        0x8000083f      5.1.0-k
```
