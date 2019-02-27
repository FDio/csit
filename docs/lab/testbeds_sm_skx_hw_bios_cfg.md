<!-- TOC depthFrom:1 depthTo:6 withLinks:1 updateOnSave:1 orderedList:0 -->

	- [SuperMicro Xeon Skylake Servers - Hardware and BIOS Configuration](#supermicro-xeon-skylake-servers-hardware-and-bios-configuration)
		- [Linux lscpu TODO](#linux-lscpu-todo)
		- [Linux dmidecode pci TODO](#linux-dmidecode-pci-todo)
		- [Linux dmidecode memory TODO](#linux-dmidecode-memory-todo)
		- [Xeon Skx Server BIOS Configuration](#xeon-skx-server-bios-configuration)
			- [Boot Feature](#boot-feature)
			- [CPU Configuration](#cpu-configuration)
				- [Advanced Power Management Configuration](#advanced-power-management-configuration)
					- [CPU P State Control](#cpu-p-state-control)
					- [Hardware PM State Control](#hardware-pm-state-control)
					- [CPU C State Control](#cpu-c-state-control)
					- [Package C State Control](#package-c-state-control)
					- [CPU T State Control](#cpu-t-state-control)
				- [Chipset Configuration](#chipset-configuration)
					- [North Bridge](#north-bridge)
					- [UPI Configuration](#upi-configuration)
					- [Memory Configuration](#memory-configuration)
					- [IIO Configuration](#iio-configuration)
					- [CPU1 Configuration](#cpu1-configuration)
					- [CPU2 Configuration](#cpu2-configuration)
				- [South Bridge](#south-bridge)
			- [PCIe/PCI/PnP Configuration](#pciepcipnp-configuration)
			- [ACPI Settings](#acpi-settings)
			- [DMIDECODE](#dmidecode)
		- [Xeon Skx Server Firmware Inventory](#xeon-skx-server-firmware-inventory)

<!-- /TOC -->

## SuperMicro Xeon Skylake Servers - Hardware and BIOS Configuration

### Linux lscpu TODO

### Linux dmidecode pci TODO

### Linux dmidecode memory TODO

### Xeon Skx Server BIOS Configuration

#### Boot Feature

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
  |  Throttle on Power Fail                    [Disabled]              |                             |
```

#### CPU Configuration

```
  |  Processor Configuration                                           |Enables Hyper Threading      |
  |  --------------------------------------------------                |(Software Method to          |
  |  Processor BSP Revision                    50654 - SKX H0          |Enable/Disable Logical       |
  |  Processor Socket                          CPU1      |  CPU2       |Processor threads.           |
  |  Processor ID                              00050654* |  000506...  |                             |
  |  Processor Frequency                       2.500GHz  |  2.500GHz   |                             |
  |  Processor Max Ratio                            19H  |  19H        |                             |
  |  Processor Min Ratio                            0AH  |  0AH        |                             |
  |  Microcode Revision                        02000030                |                             |
  |  L1 Cache RAM                                  64KB  |      64KB   |                             |
  |  L2 Cache RAM                                1024KB  |    1024KB   |                             |
  |  L3 Cache RAM                               39424KB  |   39424KB   |                             |
  |  Processor 0 Version                                               |                             |
  |  Intel(R) Xeon(R) Platinum 8180 CPU @ 2.50GHz                      |                             |
  |  Processor 1 Version                                               |                             |
  |  Intel(R) Xeon(R) Platinum 8180 CPU @ 2.50GHz                      |                             |
  |                                                                    |                             |
  |  Hyper-Threading [ALL]                     [Enable]                |                             |
  |  Core Disable Bitmap(Hex)                  0                       |                             |
  |  Execute Disable Bit                       [Enable]                |                             |
  |  Intel Virtualization Technology           [Enable]                |                             |
  |  PPIN Control                              [Unlock/Enable]         |                             |
  |  Hardware Prefetcher                       [Enable]                |                             |
  |  Adjacent Cache Prefetch                   [Enable]                |                             |
  |  DCU Streamer Prefetcher                   [Enable]                |                             |
  |  DCU IP Prefetcher                         [Enable]                |                             |
  |  LLC Prefetch                              [Disable]               |                             |
  |  Extended APIC                             [Disable]               |                             |
  |  AES-NI                                    [Enable]                |                             |
  |> Advanced Power Management Configuration                           |                             |
```

##### Advanced Power Management Configuration

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

###### CPU P State Control

```
  |  CPU P State Control                                               |Enable/Disable EIST          |
  |                                                                    |(P-States)                   |
  |  SpeedStep (Pstates)                       [Disable]               |                             |
  |  EIST PSD Function                         [HW_ALL]                |                             |
```

###### Hardware PM State Control

```
  |  Hardware PM State Control                                         |Disable: Hardware chooses a  |
  |                                                                    |P-state based on OS Request  |
  |  Hardware P-States                         [Disable]               |(Legacy P-States)            |
  |                                                                    |Native Mode:Hardware         |
  |                                                                    |chooses a P-state based on   |
  |                                                                    |OS guidance                  |
  |                                                                    |Out of Band Mode:Hardware    |
  |                                                                    |autonomously chooses a       |
  |                                                                    |P-state (no OS guidance)     |
```

###### CPU C State Control

```
  |  CPU C State Control                                               |Autonomous Core C-State      |
  |                                                                    |Control                      |
  |  Autonomous Core C-State                   [Disable]               |                             |
  |  CPU C6 report                             [Disable]               |                             |
  |  Enhanced Halt State (C1E)                 [Disable]               |                             |
```

###### Package C State Control

```
  |  Package C State Control                                           |Package C State limit        |
  |                                                                    |                             |
  |  Package C State                           [C0/C1 state]           |                             |
```

###### CPU T State Control

```
  |  CPU T State Control                                               |Enable/Disable Software      |
  |                                                                    |Controlled T-States          |
  |  Software Controlled T-States              [Disable]               |                             |
```

##### Chipset Configuration

```
  |  WARNING: Setting wrong values in below sections may cause         |North Bridge Parameters      |
  |           system to malfunction.                                   |                             |
  |> North Bridge                                                      |                             |
  |> South Bridge                                                      |                             |
```

###### North Bridge

```
  |> UPI Configuration                                                 |Displays and provides        |
  |> Memory Configuration                                              |option to change the UPI     |
  |> IIO Configuration                                                 |Settings                     |
```

###### UPI Configuration

```
  |  UPI Configuration                                                 |Choose Topology Precedence   |
  |  --------------------------------------------------                |to degrade features if       |
  |  Number of CPU                             2                       |system options are in        |
  |  Number of Active UPI Link                 3                       |conflict or choose Feature   |
  |  Current UPI Link Speed                    Fast                    |Precedence to degrade        |
  |  Current UPI Link Frequency                10.4 GT/s               |topology if system options   |
  |  UPI Global MMIO Low Base / Limit          90000000 / FBFFFFFF     |are in conflict.             |
  |  UPI Global MMIO High Base / Limit         0000000000000000 / ...  |                             |
  |  UPI Pci-e Configuration Base / Size       80000000 / 10000000     |                             |
  |  Degrade Precedence                        [Topology Precedence]   |                             |
  |  Link L0p Enable                           [Disable]               |                             |
  |  Link L1 Enable                            [Disable]               |                             |
  |  IO Directory Cache (IODC)                 [Auto]                  |                             |
  |  SNC                                       [Disable]               |                             |
  |  XPT Prefetch                              [Disable]               |                             |
  |  KTI Prefetch                              [Enable]                |                             |
  |  Local/Remote Threshold                    [Auto]                  |                             |
  |  Stale AtoS                                [Disable]               |                             |
  |  LLC dead line alloc                       [Enable]                |                             |
  |  Isoc Mode                                 [Auto]                  |                             |
```

###### Memory Configuration

```
  |                                                                    |POR - Enforces Plan Of       |
  |  --------------------------------------------------                |Record restrictions for      |
  |  Integrated Memory Controller (iMC)                                |DDR4 frequency and voltage   |
  |  --------------------------------------------------                |programming. Disable -       |
  |                                                                    |Disables this feature.       |
  |  Enforce POR                               [Disable]               |                             |
  |  Memory Frequency                          [2666]                  |                             |
  |  Data Scrambling for NVMDIMM               [Auto]                  |                             |
  |  Data Scrambling for DDR4                  [Auto]                  |                             |
  |  tCCD_L Relaxation                         [Auto]                  |                             |
  |  Memory tRWSR Relaxation                   [Enable]                |                             |
  |  2X REFRESH                                [Auto]                  |                             |
  |  Page Policy                               [Auto]                  |                             |
  |  IMC Interleaving                          [2-way Interleave]      |                             |
  |> Memory Topology                                                   |                             |
  |> Memory RAS Configuration                                          |                             |
```

###### IIO Configuration

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

###### CPU1 Configuration

```
  |  IOU0 (IIO PCIe Br1)                       [Auto]                  |Selects PCIe port            |
  |  IOU1 (IIO PCIe Br2)                       [Auto]                  |Bifurcation for selected     |
  |  IOU2 (IIO PCIe Br3)                       [Auto]                  |slot(s)                      |
  |> CPU1 SLOT2 PCI-E 3.0 X16                                          |                             |
  |> CPU1 SLOT4 PCI-E 3.0 X16                                          |                             |
  |> CPU1 SLOT9 PCI-E 3.0 X16                                          |                             |
```

###### CPU2 Configuration

```
  |  IOU0 (IIO PCIe Br1)                       [Auto]                  |Selects PCIe port            |
  |  IOU1 (IIO PCIe Br2)                       [Auto]                  |Bifurcation for selected     |
  |  IOU2 (IIO PCIe Br3)                       [Auto]                  |slot(s)                      |
  |> CPU2 SLOT6 PCI-E 3.0 X16                                          |                             |
  |> CPU2 SLOT8 PCI-E 3.0 X16                                          |                             |
  |> CPU2 SLOT10 PCI-E 3.0 X16                                         |                             |
```

##### South Bridge

```
  |                                                                    |Enables Legacy USB support.  |
  |  USB Module Version                        17                      |AUTO option disables legacy  |
  |                                                                    |support if no USB devices    |
  |  USB Devices:                                                      |are connected. DISABLE       |
  |        1 Keyboard, 1 Mouse, 1 Hub                                  |option will keep USB         |
  |                                                                    |devices available only for   |
  |  Legacy USB Support                        [Enabled]               |EFI applications.            |
  |  XHCI Hand-off                             [Disabled]              |                             |
  |  Port 60/64 Emulation                      [Enabled]               |                             |
  |  PCIe PLL SSC                              [Disable]               |                             |
  |  Real USB Wake Up                          [Enabled]               |                             |
  |  Front USB Wake Up                         [Enabled]               |                             |
  |                                                                    |                             |
  |  Azalia                                    [Auto]                  |                             |
  |    Azalia PME Enable                       [Disabled]              |                             |
```

#### PCIe/PCI/PnP Configuration

```
  |  PCI Bus Driver Version                    A5.01.12                |Enables or Disables 64bit    |
  |                                                                    |capable Devices to be        |
  |  PCI Devices Common Settings:                                      |Decoded in Above 4G Address  |
  |  Above 4G Decoding                         [Enabled]               |Space (Only if System        |
  |  SR-IOV Support                            [Enabled]               |Supports 64 bit PCI          |
  |  MMIO High Base                            [56T]                   |Decoding).                   |
  |  MMIO High Granularity Size                [256G]                  |                             |
  |  Maximum Read Request                      [Auto]                  |                             |
  |  MMCFG Base                                [2G]                    |                             |
  |  NVMe Firmware Source                      [Vendor Defined Fi...]  |                             |
  |  VGA Priority                              [Onboard]               |                             |
  |  CPU1 SLOT2 PCI-E 3.0 X16 OPROM            [Legacy]                |                             |
  |  CPU1 SLOT4 PCI-E 3.0 X16 OPROM            [Legacy]                |                             |
  |  CPU2 SLOT6 PCI-E 3.0 X16 OPROM            [Legacy]                |                             |
  |  CPU2 SLOT8 PCI-E 3.0 X16 OPROM            [Legacy]                |                             |
  |  CPU1 SLOT9 PCI-E 3.0 X16 OPROM            [Legacy]                |                             |
  |  CPU2 SLOT10 PCI-E 3.0 X16 OPROM           [Legacy]                |                             |
  |  CPU2 SLOT11 PCI-E 3.0 X4(IN X8) OPROM     [Legacy]                |                             |
  |  M.2 CONNECTOR OPROM                       [Legacy]                |                             |
  |  Onboard LAN1 Option ROM                   [Legacy]                |                             |
  |  Onboard LAN2 Option ROM                   [Disabled]              |                             |
  |  Onboard Video Option ROM                  [Legacy]                |                             |
  |> Network Stack Configuration                                       |                             |
```

#### ACPI Settings

```
  |  ACPI Settings                                                     |Enable or Disable Non        |
  |                                                                    |uniform Memory Access        |
  |  NUMA                                      [Enabled]               |(NUMA).                      |
  |  WHEA Support                              [Enabled]               |                             |
  |  High Precision Event Timer                [Enabled]               |                             |
  |  ACPI Sleep State                          [S3 (Suspend to RAM)]   |                             |
```

#### DMIDECODE

```
  # dmidecode 3.1
  Getting SMBIOS data from sysfs.
  SMBIOS 3.1.1 present.
  Table at 0x000E89C0.

  Handle 0x0000, DMI type 0, 26 bytes
  BIOS Information
        Vendor: American Megatrends Inc.
        Version: 2.0
        Release Date: 11/29/2017
        Address: 0xF0000
        Runtime Size: 64 kB
        ROM Size: 64 MB
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
        BIOS Revision: 5.12

  Handle 0x0001, DMI type 1, 27 bytes
  System Information
        Manufacturer: Supermicro
        Product Name: SYS-7049GP-TRT
        Version: 0123456789
        Serial Number: S291427X8332242
        UUID: 00000000-0000-0000-0000-AC1F6B8A8DB6
        Wake-up Type: Power Switch
        SKU Number: To be filled by O.E.M.
        Family: To be filled by O.E.M.

  Handle 0x0002, DMI type 2, 15 bytes
  Base Board Information
        Manufacturer: Supermicro
        Product Name: X11DPG-QT
        Version: 1.02
        Serial Number: VM183S014930
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
        Serial Number: C7470KH06A20167
        Asset Tag: To be filled by O.E.M.
        Boot-up State: Safe
        Power Supply State: Safe
        Thermal State: Safe
        Security Status: None
        OEM Information: 0x00000000

  Handle 0x0050, DMI type 4, 48 bytes
  Processor Information
        Socket Designation: CPU1
        Type: Central Processor
        Family: Xeon
        Manufacturer: Intel(R) Corporation
        ID: 54 06 05 00 FF FB EB BF
        Signature: Type 0, Family 6, Model 85, Stepping 4
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
        Version: Intel(R) Xeon(R) Platinum 8180 CPU @ 2.50GHz
        Voltage: 1.6 V
        External Clock: 100 MHz
        Max Speed: 4000 MHz
        Current Speed: 2500 MHz
        Status: Populated, Enabled
        Upgrade: Other
        L1 Cache Handle: 0x004D
        L2 Cache Handle: 0x004E
        L3 Cache Handle: 0x004F
        Serial Number: Not Specified
        Asset Tag: UNKNOWN
        Part Number: Not Specified
        Core Count: 28
        Core Enabled: 28
        Thread Count: 56
        Characteristics:
                64-bit capable
                Multi-Core
                Hardware Thread
                Execute Protection
                Enhanced Virtualization
                Power/Performance Control


  Handle 0x0054, DMI type 4, 48 bytes
  Processor Information
        Socket Designation: CPU2
        Type: Central Processor
        Family: Xeon
        Manufacturer: Intel(R) Corporation
        ID: 54 06 05 00 FF FB EB BF
        Signature: Type 0, Family 6, Model 85, Stepping 4
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
        Version: Intel(R) Xeon(R) Platinum 8180 CPU @ 2.50GHz
        Voltage: 1.6 V
        External Clock: 100 MHz
        Max Speed: 4000 MHz
        Current Speed: 2500 MHz
        Status: Populated, Enabled
        Upgrade: Other
        L1 Cache Handle: 0x0051
        L2 Cache Handle: 0x0052
        L3 Cache Handle: 0x0053
        Serial Number: Not Specified
        Asset Tag: UNKNOWN
        Part Number: Not Specified
        Core Count: 28
        Core Enabled: 28
        Thread Count: 56
        Characteristics:
                64-bit capable
                Multi-Core
                Hardware Thread
                Execute Protection
                Enhanced Virtualization
                Power/Performance Control
```

### Xeon Skx Server Firmware Inventory

```
Host.           IPMI IP.      BIOS. CPLD.     Aptio SU.   CPU Microcode.  PCI Bus.   ME Operation FW.    X710 Firmware.            XXV710 Firmware.          i40e.
s1-t11-sut1.    10.30.50.47.  2.1.  03.B1.03. 2.19.1268.  02000043.       A5.01.12.  4.0.4.294.          6.01 0x80003554 1.1747.0. 6.01 0x80003554 1.1747.0. 2.1.14-k.
s2-t12-sut1.    10.30.50.48.  2.1.  03.B1.03. 2.19.1268.  02000043.       A5.01.12.  4.0.4.294.          6.01 0x80003554 1.1747.0. 6.01 0x80003554 1.1747.0. 2.1.14-k.
s3-t21-sut1.    10.30.50.41.  2.0b. 03.B1.03. 2.19.1268.  02000043.       A5.01.12.  4.0.4.294.          6.01 0x80003554 1.1747.0. 6.01 0x80003554 1.1747.0. 2.1.14-k.
s4-t21-tg1.     10.30.50.42.  2.0b. 03.B1.03. 2.19.1268.  02000043.       A5.01.12.  4.0.4.294.          6.01 0x80003554 1.1747.0. 6.01 0x80003554 1.1747.0. 2.1.14-k.
s5-t22-sut1.    10.30.50.49.  2.0b. 03.B1.03. 2.19.1268.  02000043.       A5.01.12.  4.0.4.294.          6.01 0x80003554 1.1747.0. 6.01 0x80003554 1.1747.0. 2.1.14-k.
s6-t22-tg1.     10.30.50.50.  2.0b. 03.B1.03. 2.19.1268.  02000043.       A5.01.12.  4.0.4.294.          6.01 0x80003554 1.1747.0. 6.01 0x80003554 1.1747.0. 2.1.14-k.
s7-t23-sut1.    10.30.50.51.  2.0b. 03.B1.03. 2.19.1268.  02000043.       A5.01.12.  4.0.4.294.          6.01 0x80003554 1.1747.0. 6.01 0x80003554 1.1747.0. 2.1.14-k.
s8-t23-tg1.     10.30.50.52.  2.0b. 03.B1.03. 2.19.1268.  02000043.       A5.01.12.  4.0.4.294.          6.01 0x80003554 1.1747.0. 6.01 0x80003554 1.1747.0. 2.1.14-k.
s9-t24-sut1.    10.30.50.53.  2.0b. 03.B1.03. 2.19.1268.  02000043.       A5.01.12.  4.0.4.294.          6.01 0x80003554 1.1747.0. 6.01 0x80003554 1.1747.0. 2.1.14-k.
s10-t24-tg1.    10.30.50.54.  2.0b. 03.B1.03. 2.19.1268.  02000043.       A5.01.12.  4.0.4.294.          6.01 0x80003554 1.1747.0. 6.01 0x80003554 1.1747.0. 2.1.14-k.
s11-t31-sut1.   10.30.50.43.  2.0b. 03.B1.03. 2.19.1268.  02000043.       A5.01.12.  4.0.4.294.          6.01 0x80003554 1.1747.0. 6.01 0x80003554 1.1747.0. 2.1.14-k.
s12-t31-sut2.   10.30.50.44.  2.0b. 03.B1.03. 2.19.1268.  02000043.       A5.01.12.  4.0.4.294.          6.01 0x80003554 1.1747.0. 6.01 0x80003554 1.1747.0. 2.1.14-k.
s13-t31-tg1.    10.30.50.45.  2.0b. 03.B1.03. 2.19.1268.  02000043.       A5.01.12.  4.0.4.294.          6.01 0x80003554 1.1747.0. 6.01 0x80003554 1.1747.0. 2.1.14-k.
s14-t32-sut1.   10.30.50.55.  2.0b. 03.B1.03. 2.19.1268.  02000043.       A5.01.12.  4.0.4.294.          6.01 0x80003554 1.1747.0. 6.01 0x80003554 1.1747.0. 2.1.14-k.
s15-t32-sut2.   10.30.50.56.  2.0b. 03.B1.03. 2.19.1268.  02000043.       A5.01.12.  4.0.4.294.          6.01 0x80003554 1.1747.0. 6.01 0x80003554 1.1747.0. 2.1.14-k.
s16-t32-tg1.    10.30.50.57.  2.0b. 03.B1.03. 2.19.1268.  02000043.       A5.01.12.  4.0.4.294.          6.01 0x80003554 1.1747.0. 6.01 0x80003554 1.1747.0. 2.1.14-k.
s19-t33t34-tg1. 10.30.50.46.  2.0b. 03.B1.03. 2.19.1268.  02000043.       A5.01.12.  4.0.4.294.          6.01 0x80003554 1.1747.0. 6.01 0x80003554 1.1747.0. 2.1.14-k.
```
