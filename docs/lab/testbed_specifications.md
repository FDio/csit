# FD.io CSIT Testbed Specifications

1. [Purpose](#purpose)
1. [Testbeds Overview](#testbeds-overview)
   1. [Summary List](#summary-list)
   1. [1-Node-Skylake Xeon Intel (1n-skx)](#1-node-skylake-xeon-intel-1n-skx)
   1. [1-Node-ThunderX2 Arm Marvell (1n-tx2)](#1-node-thunderx2-arm-marvell-1n-tx2)
   1. [1-Node-Cascadelake Xeon Intel (1n-clx)](#1-node-cascadelake-xeon-intel-1n-clx)
   1. [2-Node-Skylake Xeon Intel (2n-skx)](#2-node-skylake-xeon-intel-2n-skx)
   1. [2-Node-Denverton Atom Intel (2n-dnv)](#2-node-denverton-atom-intel-2n-dnv)
   1. [2-Node-IxiaPS1L47 Ixia PSOne L47 (2n-ps1)](#2-node-ixiaps1l47-ixia-psone-l47-2n-ps1)
   1. [2-Node-Cascadelake Xeon Intel (2n-clx)](#2-node-cascadelake-xeon-intel-2n-clx)
   1. [2-Node-Zen2 EPYC AMD (2n-zn2)](#2-node-zen2-epyc-amd-2n-zn)
   1. [2-Node-ThunderX2 Arm Marvell (2x-tx2)](#2-node-thunderx2-arm-marvell-2n-tx2)
   1. [2-Node-Icelake Xeon Intel (2n-icx)](#2-node-icelake-xeon-intel-2n-icx)
   1. [3-Node-Skylake Xeon Intel (3n-skx)](#3-node-skylake-xeon-intel-3n-skx)
   1. [3-Node-Rangeley Atom Testbeds](#3-node-rangeley-atom-testbeds)
   1. [3-Node-TaiShan Arm Huawei (3n-tsh)](#3-node-taishan-arm-huawei-3n-tsh)
   1. [3-Node-Altra Arm Ampere (3n-alt)](#3-node-altra-arm-armpere-3n-alt)
   1. [3-Node-Icelake Xeon Intel (3n-icx)](#3-node-icelake-xeon-intel-3n-icx)
   1. [3-Node-SnowRidge Atom Intel (3n-snr)](#3-node-snowridge-atom-intel-3n-snr)
1. [Server Management](#server-management)
   1. [Requirements](#requirements)
   1. [Addressing](#addressing)
   1. [LOM (IPMI) VLAN IP Addresses](#lom-ipmi-vlan-ip-addresses)
   1. [Management VLAN IP Addresses](#management-vlan-ip-addresses)
1. [Server Specifications](#server-specifications)
   1. [Server Types](#server-types)
   1. [Naming Convention](#naming-convention)
1. [Testbeds Configuration](#testbeds-configuration)
   1. [Per Testbed Server Allocation and Naming](#per-testbed-server-allocation-and-naming)
      1. [1-Node-Skylake Servers (1n-skx) PROD](#1-node-skylake-servers-1n-skx-prod)
      1. [1-Node-ThunderX2 Servers (1n-tx2) PROD](#1-node-thunderx2-servers-1n-tx2-prod)
      1. [1-Node-Cascadelake Servers (1n-clx) PROD](#1-node-cascadelake-servers-1n-clx-prod)
      1. [2-Node-Skylake Servers (2n-skx) PROD](#2-node-skylake-servers-2n-skx-prod)
      1. [2-Node-Denverton Servers (2n-dnv) PROD](#2-node-denverton-servers-2n-dnv-prod)
      1. [2-Node-IxiaPS1L47 Servers (2n-ps1) VERIFY](#2-node-ixiaps1l47-servers-2n-ps1-verify)
      1. [2-Node-Cascadelake Servers (2n-clx) PROD](#2-node-cascadelake-servers-2n-clx-prod)
      1. [2-Node-Zen2 Servers (2n-zn2) PROD](#2-node-zen2-servers-2n-zn2-prod])
      1. [2-Node-ThunderX2 Servers (2n-tx2) PROD](#2-node-thunderx2-servers-2n-tx2-prod)
      1. [2-Node-Icelake Servers (2n-icx) PROD](#2-node-icelake-servers-2n-icx-prod)
      1. [3-Node-Skylake Servers (3n-skx) PROD](#3-node-skylake-servers-3n-skx-prod)
      1. [3-Node-Rangeley Servers (3n-rng) VERIFY](#3-node-rangeley-servers-3n-rng-verify)
      1. [3-Node-Taishan Servers (3n-tsh) PROD](#3-node-taishan-servers-3n-tsh-prod)
      1. [3-Node-Altra Servers (3n-alt) PROD](#3-node-altra-servers-3n-alt-prod)
      1. [3-Node-Icelake Servers (3n-icx) PROD](#3-node-icelake-servers-3n-icx-prod)
      1. [3-Node-SnowRidge Servers (3n-snr) PROD](#3-node-snowridge-servers-3n-snr-prod)
   1. [Per Testbed Wiring](#per-testbed-wiring)
      1. [1-Node-Skylake Wiring (1n-skx) PROD](#1-node-skylake-wiring-1n-skx-prod)
      1. [1-Node-ThunderX2 Wiring (1n-tx2) PROD](#1-node-thunderx2-wiring-1n-tx2-prod)
      1. [1-Node-Cascadelake Wiring (1n-clx) PROD](#1-node-cascadelake-wiring-1n-clx-prod)
      1. [2-Node-Skylake Wiring (2n-skx) PROD](#2-node-skylake-wiring-2n-skx-prod)
      1. [2-Node-Denverton Wiring (2n-dnv) PROD](#2-node-denverton-wiring-2n-dnv-prod)
      1. [2-Node-IxiaPS1L47 Wiring (2n-ps1) VERIFY](#2-node-ixiaps1l47-wiring-2n-ps1-verify)
      1. [2-Node-Cascadelake Wiring (2n-clx) PROD](#2-node-cascadelake-wiring-2n-clx-prod)
      1. [2-Node-Zen2 Wiring (2n-zn2) PROD](#2-node-zen2-wiring-2n-zn2-prod])
      1. [2-Node-ThunderX2 Wiring (2n-tx2) PROD](#2-node-thunderx2-wiring-2n-tx2-prod)
      1. [2-Node-Icelake Servers (2n-icx) PROD](#2-node-icelake-servers-2n-icx-prod)
      1. [3-Node-Skylake Wiring (3n-skx) PROD](#3-node-skylake-wiring-3n-skx-prod)
      1. [3-Node-Rangeley Wiring (3n-rng) VERIFY](#3-node-rangeley-wiring-3n-rng-todo)
      1. [3-Node-Taishan Wiring (3n-tsh) PROD](#3-node-taishan-wiring-3n-tsh-prod)
      1. [3-Node-Altra Wiring (3n-alt) PROD](#3-node-altra-wiring-3n-alt-prod)
      1. [3-Node-Icelake Wiring (3n-icx) PROD](#3-node-icelake-wiring-3n-icx-prod)
      1. [3-Node-SnowRidge Wiring (3n-snr) PROD](#3-node-snowridge-wiring-3n-snr-prod)
1. [Inventory](#inventory)
   1. [Appliances](#appliances)
   1. [Arm Servers](#arm-servers)
   1. [Xeon and Atom Servers](#xeon-and-atom-servers)
   1. [Network Interface Cards](#network-interface-cards)
   1. [Pluggables and Cables](#pluggables-and-cables)
   1. [Other Parts](#other-parts)

## Purpose

This note includes specification of the physical testbed infrastructure
hosted by LFN FD.io CSIT project.

## Testbeds Overview

### Summary List

```
 #. CSIT_tb          Purpose  SUT   TG    #TB  #SUT #TG  #hsw #skx #ps1 #rng #dnv #tx2 #tsh #alt #clx #zn2 #icx #snr
 1. 1-Node-Haswell     nomad  hsw   na    4    4    0    4    0    0    0    0    0    0    0    0    0    0    0
 2. 1-Node-Skylake     dev    skx   na    2    2    0    0    2    0    0    0    0    0    0    0    0    0    0
 3. 1-Node-ThunderX2   dev    tx2   na    2    2    0    0    0    0    0    0    2    0    0    0    0    0    0
 4. 1-Node-Cascadelake dev    clx   lcx   1    1    0    0    0    0    0    0    0    0    0    1    0    0    0
 5. 1-Node-AmpereAltra nomad  alt   na    2    2    0    0    0    0    0    0    0    0    2    0    0    0    0
 6. 2-Node-Skylake     perf   skx   skx   3    3    3    0    6    0    0    0    0    0    0    0    0    0    0
 7. 2-Node-Denverton   perf   dnv   skx   1    1    1    0    .5   0    0    1    0    0    0    0    0    0    0
 8. 2-Node-IxiaPS1L47  tcp    skx   ps1   1    1    1    0    1    1    0    0    0    0    0    0    0    0    0
 9. 2-Node-Cascadelake perf   clx   clx   3    3    3    0    0    0    0    0    0    0    0    6    0    0    0
10. 2-Node-ThunderX2   perf   tx2   skx   1    1    .5   0    .5   0    0    0    1    0    0    0    0    0    0
11. 2-Node-Icelake     perf   icx   icx   4    4    4    0    0    0    0    0    0    0    0    0    0    8    0
12. 3-Node-Skylake     perf   skx   skx   2    4    2    0    6    0    0    0    0    0    0    0    0    0    0
13. 3-Node-Rangeley    perf   rng   skx   1    3    1    0    0    0    2    0    0    0    0    0    0    0    0
14. 3-Node-Taishan     perf   tsh   skx   1    2    .5   0    .5   0    0    0    0    2    0    0    0    0    0
15. 3-Node-Altra       perf   alt   icx   1    2    .5   0    0    0    0    0    0    0    2    0    0    .5   0
16. 3-Node-Denverton   perf   dnv   skx   1    2    1    0    .5   0    0    2    0    0    0    0    0    0    0
17. 2-Node-Zen2        perf   zn2   zn2   1    1    1    0    0    0    0    0    0    0    0    0    2    0    0
18. 3-Node-Icelake     perf   icx   icx   2    4    2    0    0    0    0    0    0    0    0    0    0    6    0
19. 3-Node-SnowRidge   perf   snr   icx   1    2    .5   0    0    0    0    0    0    0    0    0    0    .5   2
                                 Totals: 34   44   21    4   17    1    2    3    3    2    4    7    2   15    2
```

### 1-Node-Skylake Xeon Intel (1n-skx)

Each 1-Node-Skylake testbed includes one SUT (Server-Type-B6) with NIC
ports connected back-to-back ([Server Types](#server-types)).
Used for FD.io VPP_Device functional driver tests.

### 1-Node-ThunderX2 Arm Marvell (1n-tx2)

Each 1-Node-ThunderX2 testbed includes one SUT (Server-Type-E11) with NIC
ports connected back-to-back ([Server Types](#server-types)).
Used for FD.io VPP_Device functional driver tests.

### 1-Node-Cascadelake Xeon Intel (1n-clx)

Each 1-Node-Cascadelake testbed includes one SUT (Server-Type-C1) with
NIC ports connected back-to-back ([Server Types](#server-types)).

Used for FD.io VPP_Device functional driver tests.

### 2-Node-Skylake Xeon Intel (2n-skx)

Each 2-Node-Skylake testbed includes one SUT (Server-Type-B1) and one TG
(Server-Type-B2) connected in a 2-node circular topology
([Server Types](#server-types)).
Used for FD.io performance tests.

### 2-Node-Denverton Atom Intel (2n-dnv)

Each 2-Node-Skylake testbed includes one SUT (Server-Type-B10) and one
TG (Server-Type-B2) connected in a 2-node circular topology
([Server Types](#server-types)).
Used for FD.io performance tests.

### 2-Node-IxiaPS1L47 Ixia PSOne L47 (2n-ps1)

Each 2-Node-IxiaPS1L47 testbed includes one SUT (Server-Type-B1) and one
TG (Ixia PSOne appliance) with 10GE interfaces connected in a 2-node
circular topology ([Server Types](#server-types)).
Used for FD.io TCP/IP and HTTP performance tests.

### 2-Node-Cascadelake Xeon Intel (2n-clx)

Each 2-Node-Cascadelake testbed includes one SUT (Server-Type-C2) and
one TG (Server-Type-C3) connected in a 2-node circular topology
([Server Types](#server-types)).
Used for FD.io performance tests.

### 2-Node-Zen2 EPYC AMD (2n-zn2)

Each 2-Node-Zen2 testbed includes one SUT (Server-Type-D1) and
one TG (Server-Type-D2) connected in a 2-node circular topology
([Server Types](#server-types)).
Used for FD.io performance tests.

### 2-Node-ThunderX2 Arm Marvell (2x-tx2)

Each 2-Node-ThunderX2 testbed includes one SUT (Server-Type-E22) and
one TG (Server-Type-E31) connected in a 2-node circular topology
([Server Types](#server-types)).
Used for FD.io performance tests.

### 2-Node-Icelake Xeon Intel (2n-icx)

Each 2-Node-Icelake testbed includes one SUT (Server-Type-F1) and
one TG (Server-Type-F2) connected in a 2-node circular topology
([Server Types](#server-types)).
Used for FD.io performance tests.

### 3-Node-Haswell Xeon Intel (3n-hsw)

Each 3-Node-Haswell testbed includes two SUTs (Server-Type-A1) and one
TG (Server-Type-A2) connected in a 3-node circular topology
([Server Types](#server-types)).
Used for FD.io performance tests.

### 3-Node-Skylake Xeon Intel (3n-skx)

Each 3-Node-Skylake testbed includes two SUTs (Server-Type-B1) and one
TG (Server-Type-B2) connected in a 3-node circular topology.
Used for FD.io performance tests.

### 3-Node-Rangeley Atom Testbeds

Each 3-Node-Rangeley testbed includes two SUTs (Server-Type-B5) and one
TG (Server-Type-2) connected in a 3-node circular topology
([Server Types](#server-types)).
Used for FD.io performance tests.

### 3-Node-TaiShan Arm Huawei (3n-tsh)

Each 3-Node-TaiShan testbed includes two SUTs (Server-Type-E21) and one
TG (Server-Type-E31) connected in a 3-node circular topology
([Server Types](#server-types)).
Used for FD.io performance tests.

### 3-Node-Altra Arm Ampere (3n-alt)

Each 3-Node-Altra testbed includes two SUTs (Server-Type-E23) and one
TG (Server-Type-F4) connected in a 3-node circular topology
([Server Types](#server-types)).
Used for FD.io performance tests.

### 3-Node-Icelake Xeon Intel (3n-icx)

Each 3-Node-Icelake testbed includes two SUTs (Server-Type-F1) and one
TG (Server-Type-F3) connected in a 3-node circular topology
([Server Types](#server-types)).
Used for FD.io performance tests.

### 3-Node-SnowRidge Atom Intel (3n-snr)

Each 3-Node-SnowRidge testbed includes two SUTs (Server-Type-G1) and one
TG (Server-Type-F4) connected in a 3-node circular topology
([Server Types](#server-types)).
Used for FD.io performance tests.


## Server Management

### Requirements

For management purposes, each server must have following two ports
connected to the management network:

```
- 1GE IPMI port
  - IPMI - Intelligent Platform Management Interface.
  - Required for access to embedded server management with WebUI, CLI,
    SNMPv3, IPMIv2.0, for firmware (BIOS) and OS updates.
- 1GE/10GE/40GE management port
  - hostOS management port for general system management.
```

### Addressing

Each server has a LOM (Lights-Out-Management e.g. SM IPMI) and a
Management port, which are connected to two different VLANs.

```
1. LOM (IPMI) VLAN:
    - Subnet: 10.30.50.0/24
    - Gateway: 10.30.50.1
    - Broadcast: 10.30.50.255
    - DNS1: 199.204.44.24
    - DNS2: 199.204.47.54
2. Management Vlan:
    - Subnet: 10.30.51.0/24
    - Gateway: 10.30.51.1
    - Broadcast: 10.30.51.255
    - DNS1: 199.204.44.24
    - DNS2: 199.204.47.54
```

To access these hosts, VPN connection is required.

### LOM (IPMI) VLAN IP Addresses

Name         | Comment
------------ | -------
10.30.50.0   | network
10.30.51.1   | Router
10.30.50.2   | LF Reserved
10.30.50.3   | LF Reserved
10.30.50.4   | LF Reserved
10.30.50.5   | LF Reserved
10.30.50.6   | LF Reserved
10.30.50.7   | LF Reserved
10.30.50.8   | LF Reserved
10.30.50.9   | LF Reserved
10.30.50.10  | LF Reserved
10.30.50.11  | LF Reserved
10.30.50.12  | LF Reserved
10.30.50.13  | LF Reserved
10.30.50.14  | LF Reserved
10.30.50.15  | LF Reserved
10.30.50.22  | s42-nomad
10.30.50.24  | s43-nomad
10.30.50.25  | s44-nomad
10.30.50.26  | s45-nomad
10.30.50.28  | s41-nomad
10.30.50.29  | s39-nomad
10.30.51.29  | s22-t35-sut1 screen -r /dev/ttyusb0
10.30.50.30  | s40-nomad
10.30.51.30  | s23-t35-sut2 screen -r /dev/ttyusb1
10.30.51.30  | s24-t35-sut3 screen -r /dev/ttyusb2
10.30.50.36  | s17-t33-sut1
10.30.50.37  | s18-t33-sut2
10.30.50.38  | fdio-marvell-dev
10.30.50.39  | s53-nomad
10.30.50.40  | s54-nomad
10.30.50.41  | s3-t21-sut1
10.30.50.42  | s4-t21-tg1
10.30.50.43  | s11-t31-sut1
10.30.50.44  | s12-t31-sut2
10.30.50.45  | s13-t31-tg1
10.30.50.46  | s19-t33t211-tg1
10.30.50.47  | s1-t11-sut1
10.30.50.48  | s2-t12-sut1
10.30.50.49  | s5-t22-sut1
10.30.50.50  | s6-t22-tg1
10.30.50.51  | s7-t23-sut1
10.30.50.52  | s8-t23-tg1
10.30.50.53  | s9-t24-sut1
10.30.50.54  | s10-t24-tg1
10.30.50.55  | s14-t32-sut1
10.30.50.56  | s15-t32-sut2
10.30.50.57  | s16-t32-tg1
10.30.50.58  | s25-t25-sut1
10.30.50.59  | s26-t25-tg1
10.30.50.65  | s52-nomad
10.30.50.66  | s51-nomad
10.30.50.67  | s49-nomad
10.30.50.68  | s50-nomad
10.30.50.69  | s27-t211-sut1
10.30.50.70  | s55-t13-sut1
10.30.50.71  | s56-t14-sut1
10.30.50.72  | s62-t34-sut1
10.30.50.73  | s63-t34-sut2
10.30.50.74  | s64-t34t36-tg1
10.30.50.75  | s65-t37-sut1
10.30.50.76  | s66-t37-sut2
10.30.50.77  | s67-t37-tg1
10.30.50.78  | s78-t38-sut1
10.30.50.79  | s79-t38-sut2
10.30.50.80  | s80-t38-tg1
10.30.50.81  | s71-t212-sut1
10.30.50.82  | s72-t212-tg1
10.30.50.83  | s83-t213-sut1
10.30.50.84  | s84-t213-tg1
10.30.50.85  | s85-t214-sut1
10.30.50.86  | s86-t214-tg1
10.30.50.87  | s87-t215-sut1
10.30.50.88  | s88-t215-tg1
10.30.50.89  | s89-t39t310-tg1
10.30.50.90  | s90-t311t312-tg1
10.30.50.91  | s58-nomad
10.30.50.92  | s59-nomad
10.30.50.93  | s93-t39-sut1
10.30.50.94  | s94-t39-sut2
10.30.50.255 | Broadcast
10.30.55.0   | network
10.30.55.1   | Router
10.30.55.10  | s28-t26t35-tg1
10.30.55.11  | s29-t26-sut1
10.30.55.12  | s30-t35-sut1
10.30.55.13  | s31-t35-sut2
10.30.55.14  | s46-nomad
10.30.55.15  | s47-nomad
10.30.55.16  | s48-nomad
10.30.55.17  | s57-nomad
10.30.55.18  | s33-t27-sut1
10.30.55.19  | s34-t27-tg1
10.30.55.20  | s35-t28-sut1
10.30.55.21  | s36-t28-tg1
10.30.55.22  | s37-t29-sut1
10.30.55.23  | s38-t29-tg1
10.30.55.24  | s60-t210-sut1
10.30.55.25  | s61-t210-tg1
10.30.55.255 | Broadcast

### Management VLAN IP Addresses

Name         | Comment
-------------| -------
10.30.51.0   | network
10.30.51.1   | Router
10.30.51.2   | LF Reserved
10.30.51.3   | LF Reserved
10.30.51.4   | LF Reserved
10.30.51.5   | LF Reserved
10.30.51.6   | LF Reserved
10.30.51.7   | LF Reserved
10.30.51.8   | LF Reserved
10.30.51.15  | LF Reserved
10.30.51.22  | s42-nomad
10.30.51.24  | s43-nomad
10.30.51.25  | s44-nomad
10.30.51.26  | s45-nomad
10.30.51.28  | s41-nomad
10.30.51.29  | s39-nomad
10.30.51.30  | s40-nomad
10.30.51.36  | s17-t33-sut1
10.30.51.37  | s18-t33-sut2
10.30.51.38  | fdio-marvell-dev
10.30.51.39  | s53-nomad
10.30.51.40  | s54-nomad
10.30.51.44  | s3-t21-sut1
10.30.51.45  | s4-t21-tg1
10.30.51.46  | s11-t31-sut1
10.30.51.47  | s12-t31-sut2
10.30.51.48  | s13-t31-tg1
10.30.51.49  | s19-t33t211-tg1
10.30.51.50  | s1-t11-sut1
10.30.51.51  | s2-t12-sut1
10.30.51.52  | s5-t22-sut1
10.30.51.53  | s6-t22-tg1
10.30.51.54  | s7-t23-sut1
10.30.51.55  | s8-t23-tg1
10.30.51.56  | s9-t24-sut1
10.30.51.57  | s10-t24-tg1
10.30.51.58  | s14-t32-sut1
10.30.51.59  | s15-t32-sut2
10.30.51.60  | s16-t32-tg1
10.30.51.61  | s25-t25-sut1
10.30.51.62  | s26-t25-tg1
10.30.51.65  | s52-nomad
10.30.51.66  | s51-nomad
10.30.51.67  | s49-nomad
10.30.51.68  | s50-nomad
10.30.51.69  | s27-t211-sut1
10.30.51.70  | s55-t13-sut1
10.30.51.71  | s56-t14-sut1
10.30.51.72  | s62-t34-sut1
10.30.51.73  | s63-t34-sut2
10.30.51.74  | s64-t34t36-tg1
10.30.51.75  | s65-t37-sut1
10.30.51.76  | s66-t37-sut2
10.30.51.77  | s67-t37-tg1
10.30.51.78  | s78-t38-sut1
10.30.51.79  | s79-t38-sut2
10.30.51.80  | s80-t38-tg1
10.30.51.81  | s71-t212-sut1
10.30.51.82  | s72-t212-tg1
10.30.51.83  | s83-t213-sut1
10.30.51.84  | s84-t213-tg1
10.30.51.85  | s85-t214-sut1
10.30.51.86  | s86-t214-tg1
10.30.51.87  | s87-t215-sut1
10.30.51.88  | s88-t215-tg1
10.30.51.89  | s89-t39t310-tg1
10.30.51.90  | s90-t311t312-tg1
10.30.51.91  | s58-nomad
10.30.51.92  | s59-nomad
10.30.51.93  | s93-t39-sut1
10.30.51.94  | s94-t39-sut2
10.30.51.255 | Broadcast
10.32.8.0    | network
10.32.8.1    | Router
10.32.8.10   | s28-t26t35-tg1
10.32.8.11   | s29-t26-sut1
10.32.8.12   | s30-t35-sut1
10.32.8.13   | s31-t35-sut2
10.32.8.14   | s46-nomad
10.32.8.15   | s47-nomad
10.32.8.16   | s48-nomad
10.32.8.17   | s57-nomad
10.32.8.18   | s33-t27-sut1
10.32.8.19   | s34-t27-tg1
10.32.8.20   | s35-t28-sut1
10.32.8.21   | s36-t28-tg1
10.32.8.22   | s37-t29-sut1
10.32.8.23   | s38-t29-tg1
10.32.8.24   | s60-t210-sut1
10.32.8.25   | s61-t210-tg1
10.32.8.255  | Broadcast

## Server Specifications

### Server Types

FD.io CSIT lab contains following server types:
```
1. Server-Type-A1: Purpose - Haswell Xeon SUT (Systems Under Test) for FD.io performance testing.
    - Quantity: 6 servers.
    - Physical connectivity:
        - CIMC and host management ports.
        - NIC ports connected in 3-node topologies.
    - Main HW configuration:
        - Chassis: UCSC-C240-M4SX with 6 PCIe3.0 slots.
        - Processors: 2* E5-2699v3 2.3 GHz.
        - RAM Memory: 16* 32GB DDR4-2133MHz.
        - Disks: 2* 2TB 12G SAS 7.2K RPM SFF HDD.
    - NICs configuration:
        - Numa0: Right PCIe Riser Board (Riser 1) (x8, x8, x8 PCIe3.0 lanes)
            - PCIe Slot1: empty.
            - PCIe Slot2: empty.
            - PCIe Slot3: empty.
        - Numa1: Left PCIe Riser Board (Riser 2) (x8, x16, x8 PCIe3.0 lanes)
            - PCIe Slot4: empty.
            - PCIe Slot5: empty.
            - PCIe Slot6: empty
        - MLOM slot: Cisco VIC 1227 2p10GE (x8 PCIe2.0 lanes).
2. Server-Type-A2: Purpose - Haswell Xeon TG (Traffic Generators) for FD.io performance testing.
    - Quantity: 3 servers.
    - Physical connectivity:
        - CIMC and host management ports.
        - NIC ports connected in 3-node topologies.
    - Main HW configuration:
        - Chassis: UCSC-C240-M4SX with 6 PCIe3.0 slots.
        - Processors: 2* E5-2699v3 2.3 GHz.
        - RAM Memory: 16* 32GB DDR4-2133MHz.
        - Disks: 2* 2TB 12G SAS 7.2K RPM SFF HDD.
    - NICs configuration:
        - Numa0: Right PCIe Riser Board (Riser 1) (x8, x8, x8 PCIe3.0 lanes)
            - PCIe Slot1: empty.
            - PCIe Slot2: empty.
            - PCIe Slot3: empty.
        - Numa1: Left PCIe Riser Board (Riser 2) (x8, x16, x8 PCIe3.0 lanes)
            - PCIe Slot4: empty.
            - PCIe Slot5: empty.
            - PCIe Slot6: empty
        - MLOM slot: empty.
3. Server-Type-A3: Purpose - Haswell Xeon VIRL hosts for FD.io functional testing.
    - Quantity: 3 servers.
    - Physical connectivity:
        - CIMC and host management ports.
        - no NIC ports, standalone setup.
    - Main HW configuration:
        - Chassis: UCSC-C240-M4SX with 6 PCIe3.0 slots.
        - Processors: 2* E5-2699v3 2.3 GHz.
        - RAM Memory: 16* 32GB DDR4-2133MHz.
        - Disks: 2* 480 GB 2.5inch 6G SATA SSD.
    - NICs configuration:
        - Numa0: Right PCIe Riser Board (Riser 1) (x8, x8, x8 lanes)
            - no cards.
        - Numa1: Left PCIe Riser Board (Riser 2) (x8, x16, x8 lanes)
            - no cards.
        - MLOM slot: empty.
4. Server-Type-B1: Purpose - Skylake Xeon SUT for FD.io performance testing.
    - Quantity: ---
    - Physical connectivity:
        - IPMI and host management ports.
        - NIC ports connected into 2-node and 3-node topologies.
    - Main HW configuration:
        - Chassis: SuperMicro SYS-7049GP-TRT.
        - Motherboard: SuperMicro X11DPG-QT.
        - Processors: 2* Intel Platinum 8180 2.5 GHz.
        - RAM Memory: 16* 16GB DDR4-2666MHz.
        - Disks: 2* 1.6TB 6G SATA SSD.
    - NICs configuration:
        - Numa0: (x16, x16, x16 PCIe3.0 lanes)
            - PCIe Slot2 18:00.xx: x710-4p10GE Intel.
            - PCIe Slot4 3b:00.xx: xxv710-DA2-2p25GE Intel.
            - PCIe Slot9 5e:00.xx: empty.
        - Numa1: (x16, x16, x16 PCIe3.0 lanes)
            - PCIe Slot6 86:00.xx: empty.
            - PCIe Slot8 af:00.xx: empty.
            - PCIe Slot10 d8:00.xx: empty.
5. Server-Type-B2: Purpose - Skylake Xeon TG for FD.io performance testing.
    - Quantity: ---
    - Physical connectivity:
        - IPMI and host management ports.
        - NIC ports connected into 2-node and 3-node topologies.
    - Main HW configuration:
        - Chassis: SuperMicro SYS-7049GP-TRT.
        - Motherboard: SuperMicro X11DPG-QT.
        - Processors: 2* Intel Platinum 8180 2.5 GHz.
        - RAM Memory: 16* 16GB DDR4-2666MHz.
        - Disks: 2* 1.6TB 6G SATA SSD.
    - NICs configuration:
        - Numa0: (x16, x16, x16 PCIe3.0 lanes)
            - PCIe Slot2 18:00.xx: x710-4p10GE Intel.
            - PCIe Slot4 3b:00.xx: xxv710-DA2 2p25GE Intel.
            - PCIe Slot9 5e:00.xx: empty.
        - Numa1: (x16, x16, x16 PCIe3.0 lanes)
            - PCIe Slot6 86:00.xx: empty.
            - PCIe Slot8 af:00.xx: empty.
            - PCIe Slot10 d8:00.xx: x710-4p10GE Intel.
6. Server-Type-B5: Purpose - Rangeley Atom SUT for FD.io performance testing.
    - Quantity: TBD based on testbed allocation.
    - Physical connectivity:
        - Management: serial Port (usb) for console
        - NIC ports connected into 2-node.
    - Main HW configuration:
        - Chassis: Netgate XG-2758-1u
        - Processors: 1* Rangeley (Atom) C2758 2.4 GHz
        - RAM Memory: 16GB ECC
        - Disks: 150 GB
    - NICs configuration:
        - 2x 10Gb Intel 82599ES
        - 4x 1GB Intel I354
7. Server-Type-B6: Purpose - Skylake Xeon SUT for FD.io VPP_Device functional tests.
    - Quantity: 2.
    - Physical connectivity:
        - IPMI and host management ports.
        - NIC ports connected into 1-node topologies.
    - Main HW configuration:
        - Chassis: SuperMicro SYS-7049GP-TRT.
        - Motherboard: SuperMicro X11DPG-QT.
        - Processors: 2* Intel Platinum 8180 2.5 GHz.
        - RAM Memory: 16* 16GB DDR4-2666MHz.
        - Disks: 2* 1.6TB 6G SATA SSD.
    - NICs configuration:
        - Numa0: (x16, x16, x16 PCIe3.0 lanes)
            - PCIe Slot2 18:00.xx: x710-4p10GE Intel.
            - PCIe Slot4 3b:00.xx: x710-4p10GE Intel.
            - PCIe Slot9 5e:00.xx: empty.
        - Numa1: (x16, x16, x16 PCIe3.0 lanes)
            - PCIe Slot6 86:00.xx: empty.
            - PCIe Slot8 af:00.xx: empty.
            - PCIe Slot10 d8:00.xx: empty.
8. Server-Type-B7: Purpose - Ixia PerfectStorm One Appliance TG for FD.io TCP/IP performance tests.
    - Quantity: 1.
    - Physical connectivity:
        - Host management interface: 10/100/1000-BaseT.
        - 8-port 10GE SFP+ integrated NIC.
    - Main HW configuration:
        - Chassis: PS10GE4NG.
        - Motherboard: SuperMicro X11DPG-QT.
        - Processors: Quad-Core, Intel Processor.
        - HW accelerators: FPGA offload.
        - RAM Memory: 64GB.
        - Disks: 1 * 1 TB, Enterprise Class, High MTBF.
        - Physical Interfaces: 4 * 10GE SFP+.
        - Operating System: Native IxOS.
    - Interface configuration:
        - Port-1: 10GE SFP+.
        - Port-2: 10GE SFP+.
        - Port-3: 10GE SFP+.
        - Port-4: 10GE SFP+.
9. Server-Type-B8: Purpose - Skylake Xeon SUT for TCP/IP host stack tests.
    - Quantity: 1.
    - Physical connectivity:
        - IPMI and host management ports.
        - NIC ports.
    - Main HW configuration:
        - Chassis: SuperMicro SYS-7049GP-TRT.
        - Motherboard: SuperMicro X11DPG-QT.
        - Processors: 2* Intel Platinum 8180 2.5 GHz.
        - RAM Memory: 16* 16GB DDR4-2666MHz.
        - Disks: 2* 1.6TB 6G SATA SSD.
    - NICs configuration:
        - Numa0: (x16, x16, x16 PCIe3.0 lanes)
            - PCIe Slot2 18:00.xx: x710-4p10GE Intel.
            - PCIe Slot4 3b:00.xx: empty.
            - PCIe Slot9 5e:00.xx: empty.
        - Numa1: (x16, x16, x16 PCIe3.0 lanes)
            - PCIe Slot6 86:00.xx: empty.
            - PCIe Slot8 af:00.xx: empty.
            - PCIe Slot10 d8:00.xx: empty.
10. Server-Type-B10: Purpose - Denverton Atom SUT for FD.io performance testing.
    - Quantity: 4
    - Physical connectivity:
        - IPMI and host management ports.
        - NIC ports.
    - Main HW configuration:
        - Chassis: SuperMicro SYS-E300-9A
        - Processors: 1* Intel(R) Atom(TM) CPU C3858 @ 2.00GHz
        - RAM Memory: 32GB ECC
        - Disks: 480 GB
    - NICs configuration:
        - 2x 10Gb Intel x553 fiber ports
        - 2x 10Gb Intel x553 copper ports
        - 4x 1GB Intel I350 ports
11. Server-Type-C1: Purpose - Cascadelake Xeon SUT for FD.io VPP_Device functional tests.
    - Quantity: 1.
    - Physical connectivity:
        - IPMI and host management ports.
        - NIC ports connected into 1-node testbed topologies.
    - Main HW configuration:
        - Chassis: SuperMicro SYS-7049GP-TRT.
        - Motherboard: SuperMicro X11DPG-QT.
        - Processors: 2* Intel Platinum 8280 2.7 GHz.
        - RAM Memory: 12* 16GB DDR4-2933.
        - Disks: 2* 1.92TB SATA SSD.
    - NICs configuration:
        - Numa0: (x16, x16, x16 PCIe3.0 lanes)
            - PCIe Slot2 18:00.xx: x710-4p10GE Intel.
            - PCIe Slot4 3b:00.xx: x710-4p10GE Intel.
            - PCIe Slot9 5e:00.xx: empty.
        - Numa1: (x16, x16, x16 PCIe3.0 lanes)
            - PCIe Slot6 86:00.xx: empty.
            - PCIe Slot8 af:00.xx: empty.
            - PCIe Slot10 d8:00.xx: empty.
12. Server-Type-C2: Purpose - Cascadelake Xeon SUT for FD.io performance testing.
    - Quantity: 3
    - Physical connectivity:
        - IPMI and host management ports.
        - NIC ports connected into 2-node testbed topologies.
    - Main HW configuration:
        - Chassis: SuperMicro SYS-7049GP-TRT.
        - Motherboard: SuperMicro X11DPG-QT.
        - Processors: 2* Intel Gold 6252N 2.3 GHz.
        - RAM Memory: 12* 16GB DDR4-2933.
        - Disks: 2* 1.92TB SATA SSD.
    - NICs configuration:
        - Numa0: (x16, x16, x16 PCIe3.0 lanes)
            - PCIe Slot2 18:00.xx: x710-4p10GE Intel.
            - PCIe Slot4 3b:00.xx: xxv710-DA2-2p25GE Intel.
            - PCIe Slot9 5e:00.xx: ConnectX5-2p100GE Mellanox.
        - Numa1: (x16, x16, x16 PCIe3.0 lanes)
            - PCIe Slot6 86:00.xx: e810-2p100GE Intel.
            - PCIe Slot8 af:00.xx: empty.
            - PCIe Slot10 d8:00.xx: empty.
13. Server-Type-C3: Purpose - Cascadelake Xeon TG for FD.io performance testing.
    - Quantity: 3.
    - Physical connectivity:
        - IPMI and host management ports.
        - NIC ports connected into 2-node testbed topologies.
    - Main HW configuration:
        - Chassis: SuperMicro SYS-7049GP-TRT.
        - Motherboard: SuperMicro X11DPG-QT.
        - Processors: 2* Intel Platinum 8280 2.7 GHz.
        - RAM Memory: 12* 16GB DDR4-2933.
        - Disks: 2* 1.92TB SATA SSD.
    - NICs configuration:
        - Numa0: (x16, x16, x16 PCIe3.0 lanes)
            - PCIe Slot2 18:00.xx: x710-4p10GE Intel.
            - PCIe Slot4 3b:00.xx: xxv710-DA2 2p25GE Intel.
            - PCIe Slot9 5e:00.xx: ConnectX5-2p100GE Mellanox.
        - Numa1: (x16, x16, x16 PCIe3.0 lanes)
            - PCIe Slot6 86:00.xx: ConnectX5-2p100GE Mellanox.
            - PCIe Slot8 af:00.xx: ConnectX5-2p100GE Mellanox.
            - PCIe Slot10 d8:00.xx: empty.
14. Server-Type-C4: Purpose - Cascadelake Xeon Backend hosts for FD.io builds and data processing.
    - Quantity: 3.
    - Physical connectivity:
        - IPMI and host management ports.
        - no NIC ports, standalone setup.
    - Main HW configuration:
        - Chassis: SuperMicro 1029P-WTRT.
        - Motherboard: SuperMicro X11DDW-NT.
        - Processors: 2* Intel Platinum 8280 2.7 GHz.
        - RAM Memory: 12* 16GB DDR4-2933.
        - Disks: 4* 1.92TB SATA SSD.
    - NICs configuration:
        - Numa0:
            - no cards.
        - Numa1:
            - no cards.
15. Server-Type-D1: Purpose - Zen2 EPYC SUT for FD.io performance testing.
    - Quantity: 1.
    - Physical connectivity:
        - IPMI and host management ports.
        - NIC ports connected into 2-node testbed topologies.
    - Main HW configuration:
        - Chassis: SuperMicro AS-1114S-WTRT
        - Processors: 1* AMD EPYC 7532 2.4 GHz.
        - RAM Memory: 8* 32GB DDR4-2933.
        - Disks: 1* 1TB SATA SSD.
    - NICs configuration:
        - Numa0: (x16, x16, x16 PCIe3.0 lanes)
            - PCIe Slot1 01:00.xx: x710-4p10GE Intel.
            - PCIe Slot2 41:00.xx: xxv710-DA2-2p25GE Intel.
            - PCIe Slot3 81:00.xx: mcx556a-edat ConnectX5-2p100GE Mellanox.
16. Server-Type-D2: Purpose - Zen2 EPYC TG for FD.io performance testing.
    - Quantity: 1.
    - Physical connectivity:
        - IPMI and host management ports.
        - NIC ports connected into 2-node testbed topologies.
    - Main HW configuration:
        - Chassis: SuperMicro AS-1114S-WTRT
        - Processors: 1* AMD EPYC 7532 2.4 GHz.
        - RAM Memory: 8* 32GB DDR4-2933.
        - Disks: 1* 1TB SATA SSD.
    - NICs configuration:
        - Numa0: (x16, x16, x16 PCIe3.0 lanes)
            - PCIe Slot1 01:00.xx: mcx556a-edat ConnectX5-2p100GE Mellanox.
            - PCIe Slot2 41:00.xx: x710-4p10GE Intel.
            - PCIe Slot3 81:00.xx: xxv710-DA2 2p25GE Intel.
17.  Server-Type-E11: Purpose - ThunderX2 Arm Marvell SUT for FD.io VPP_Device functional tests.
    - Quantity: 2
    - Physical connectivity:
        - IPMI and host management ports.
        - NIC ports connected into 1-node topologies.
    - Main HW configuration:
        - Chassis: GIGABYTE Rack Mount
        - Motherboard: MT91-FS4-00
        - Processors: 2 * ThunderX2 ARMv8 CN9980 2.20 GHz
        - RAM Memory: 16 * 16GB DIMM
        - Disks: 2 * 480GB 6G SATA SSD SAMSUNG MZ7LH480
    - NICs configuration:
        - Numa0:
            - PCIe Slot4 05:00.xx: XL710-QDA2-2p40GE Intel.
            - PCIe Slot8 0b:00.xx: ConnectX5-2p10/25GE Mellanox.
        - Numa1:
            - PCIe Slot14 91:00.xx: XL710-QDA2-2p40GE Intel.
            - PCIe Slot26 9a:00.xx: ConnectX5-2p10/25GE Mellanox.
18.  Server-Type-E21: Purpose - TaiShan Arm Huawei SUT for FD.io performance testing.
    - Quantity: 2
    - Physical connectivity:
        - IPMI(?) and host management ports.
        - NIC ports connected into 3-node topology.
    - Main HW configuration:
        - Chassis: Huawei TaiShan 2280.
        - Processors: 2* hip07-d05 ~ 32* Arm Cortex-A72
        - RAM Memory: 8* 16GB DDR4-2400MT/s
        - Disks: 1* 4TB SATA HDD
    - NICs configuration:
        - PCIe Slot4 e9:00.xx: connectx4-2p25GE Mellanox.
        - PCIe Slot6 11:00.xx: x520-2p10GE Intel.
19.  Server-Type-E22: Purpose - ThunderX2 Arm Marvell SUT for FD.io performance testing.
    - Quantity: 1
    - Physical connectivity:
        - IPMI and host management ports.
        - NIC ports connected into 2-node topologies.
    - Main HW configuration:
        - Chassis: Gigabyte R181-T90 1U
        - Motherboard: MT91-FS1
        - Processors: 2* ThunderX2 ARMv8 CN9975 2.0 GHz
        - RAM Memory: 4* 32GB RDIMM
        - Disks: 1* 480GB SSD Micron, 1* 1000GB HDD Seagate_25
    - NICs configuration:
        - Numa0:
            - PCIe Slot6 08:00.xx: XL710-QDA2-2p40GE Intel.
        - Numa1:
            - PCIe Slot18 91:00.xx: XL710-QDA2-2p40GE Intel.
20.  Server-Type-E23: Purpose - Altra Arm Ampere SUT for FD.io performance testing.
    - Quantity: 1
    - Physical connectivity:
        - IPMI and host management ports.
        - NIC ports connected into 3-node topologies.
    - Main HW configuration:
        - Chassis: TBD
        - Motherboard: TBD
        - Processors: n* TBD
        - RAM Memory: n* TBD
        - Disks: TBD
    - NICs configuration:
        - Numa0:
            - PCIe Slotn xx:xx.xx: XL710-QDA2-2p40GE Intel.
            - PCIe Slotk xx:xx.xx: mcx556a-edat ConnectX5-2p100GE Mellanox.
        - Numa1:
            - PCIe Slotn xx:xx.xx: XL710-QDA2-2p40GE Intel.
            - PCIe Slotk xx:xx.xx: mcx556a-edat ConnectX5-2p100GE Mellanox.
21.  Server-Type-E31: Purpose - Skylake Xeon TG for FD.io performance testing.
    - Quantity: 1
    - Physical connectivity:
        - IPMI and host management ports.
        - NIC ports connected into 2-node and 3-node topologies.
    - Main HW configuration:
        - Chassis: SuperMicro SYS-7049GP-TRT.
        - Motherboard: SuperMicro X11DPG-QT.
        - Processors: 2* Intel Platinum 8180 2.5 GHz.
        - RAM Memory: 16* 16GB DDR4-2666MHz.
        - Disks: 2* 1.6TB 6G SATA SSD.
    - NICs configuration:
        - Numa0: (x16, x16, x16 PCIe3.0 lanes)
            - PCIe Slot2 18:00.xx: x710-4p10GE Intel.
            - PCIe Slot4 3b:00.xx: xxv710-DA2 2p25GE Intel.
            - PCIe Slot9 5e:00.xx: empty.
        - Numa1: (x16, x16, x16 PCIe3.0 lanes)
            - PCIe Slot6 86:00.xx: empty.
            - PCIe Slot8 af:00.xx: XL710-QDA2-2p40GE Intel.
            - PCIe Slot10 d8:00.xx: x710-4p10GE Intel.
22. Server-Type-F1: Purpose - Icelake Xeon SUT for FD.io performance testing.
    - Quantity: 8.
    - Physical connectivity:
        - IPMI and host management ports.
        - NIC ports connected into 2-node or 3-node testbed topologies.
    - Main HW configuration:
        - Chassis: SuperMicro SYS-740GP-TNRT.
        - Motherboard: Super X12DPG-QT6.
        - Processors: 2* Intel Platinum 8358 2.6 GHz.
        - RAM Memory: 16* 16GB DDR4-3200.
        - Disks: 2* 960GB SATA SSD.
    - NICs configuration:
        - Numa0: (x16, x16, x16 PCIe3.0 lanes)
            - PCIe Slot2 18:00.xx: xxv710-DA2-2p25GE Intel.
            - PCIe Slot4 3b:00.xx: e810-XXVDA4-4p25GE Intel.
            - PCIe Slot9 5e:00.xx: e810-2CQDA2-2p100GE Intel.
        - Numa1: (x16, x16, x16 PCIe3.0 lanes)
            - PCIe Slot6 86:00.xx: empty.
            - PCIe Slot8 af:00.xx: empty.
            - PCIe Slot10 d8:00.xx: empty.
23. Server-Type-F2: Purpose - Icelake Xeon TG for FD.io performance testing.
    - Quantity: 3.
    - Physical connectivity:
        - IPMI and host management ports.
        - NIC ports connected into 2-node testbed topologies.
    - Main HW configuration:
        - Chassis: SuperMicro SYS-740GP-TNRT.
        - Motherboard: Super X12DPG-QT6.
        - Processors: 2* Intel Platinum 8358 2.6 GHz.
        - RAM Memory: 16* 16GB DDR4-3200.
        - Disks: 2* 960GB SATA SSD.
    - NICs configuration:
        - Numa0: (x16, x16, x16 PCIe3.0 lanes)
            - PCIe Slot2 18:00.xx: xxv710-DA2-2p25GE Intel.
            - PCIe Slot4 3b:00.xx: e810-XXVDA4-4p25GE Intel.
            - PCIe Slot9 5e:00.xx: e810-2CQDA2-2p100GE Intel.
        - Numa1: (x16, x16, x16 PCIe3.0 lanes)
            - PCIe Slot6 86:00.xx: e810-2CQDA2-2p100GE Intel.
            - PCIe Slot8 af:00.xx: empty.
            - PCIe Slot10 d8:00.xx: empty.
24. Server-Type-F3: Purpose - Icelake Xeon TG for FD.io performance testing.
    - Quantity: 3.
    - Physical connectivity:
        - IPMI and host management ports.
        - NIC ports connected into 3-node testbed topologies.
    - Main HW configuration:
        - Chassis: SuperMicro SYS-740GP-TNRT.
        - Motherboard: Super X12DPG-QT6.
        - Processors: 2* Intel Platinum 8358 2.6 GHz.
        - RAM Memory: 16* 16GB DDR4-3200.
        - Disks: 2* 960GB SATA SSD.
    - NICs configuration:
        - Numa0: (x16, x16, x16 PCIe3.0 lanes)
            - PCIe Slot2 18:00.xx: xxv710-DA2-2p25GE Intel.
            - PCIe Slot4 3b:00.xx: e810-XXVDA4-4p25GE Intel.
            - PCIe Slot9 5e:00.xx: e810-2CQDA2-2p100GE Intel.
        - Numa1: (x16, x16, x16 PCIe3.0 lanes)
            - PCIe Slot6 86:00.xx: empty.
            - PCIe Slot8 af:00.xx: empty.
            - PCIe Slot10 d8:00.xx: empty.
25. Server-Type-F4: Purpose - Icelake Xeon Shared TG for FD.io performance testing.
    - Quantity: 3.
    - Physical connectivity:
        - IPMI and host management ports.
        - NIC ports connected into 2-node and/or 3-node testbed topologies.
    - Main HW configuration:
        - Chassis: SuperMicro SYS-740GP-TNRT.
        - Motherboard: Super X12DPG-QT6.
        - Processors: 2* Intel Platinum 8358 2.6 GHz.
        - RAM Memory: 16* 16GB DDR4-3200.
        - Disks: 2* 960GB SATA SSD.
    - NICs configuration:
        - Numa0: (x16, x16, x16 PCIe3.0 lanes)
            - PCIe Slot2 18:00.xx: xxv710-DA2-2p25GE Intel.
            - PCIe Slot4 3b:00.xx: empty.
            - PCIe Slot9 5e:00.xx: empty.
        - Numa1: (x16, x16, x16 PCIe3.0 lanes)
            - PCIe Slot6 86:00.xx: e810-XXVDA4-4p25GE Intel.
            - PCIe Slot8 af:00.xx: e810-2CQDA2-2p100GE Intel.
            - PCIe Slot10 d8:00.xx: empty.
26. Server-Type-E24 : Purpose - Altra Arm Ampere for FD.io build.
    - Quantity: 2.
    - Physical connectivity:
        - IPMI and host management ports.
    - Main HW configuration:
        - Chassis: Gigabyte R152-P30-00 1U
        - Motherboard: MP32-AR1-00
        - Processors: 1* Ampere(R) Altra(R) Processor (Neoverse N1)
        - RAM Memory: 4* 16GB RDIMM-3200MHz
        - Disks: 1* 960GB SSD Samsung M.2 NVMe PM983
27. Server-Type-G1: Purpose - SnowRidge Atom SUT for FD.io performance testing.
    - Quantity: 2
    - Physical connectivity:
        - IPMI and host management ports.
        - NIC ports connected into 3-node testbed topology.
    - Main HW configuration:
        - Chassis: ?.
        - Motherboard: ?.
        - Processors: ?* Intel Atom P5362B 2.2 GHz.
        - RAM Memory: ?* ?GB DDR4-2933.
        - Disks: ?* ? SATA SSD.
    - NICs configuration:
        - Numa0: (x16, PCIe3.0 lane)
            - PCIe Slot yy:00.xx: ?.
```

### Naming Convention

Following naming convention is used within this page to specify physical
connectivity and wiring across defined CSIT testbeds:

```
- testbedname: testbedN.
- hostname:
    - traffic-generator: tN-tgW.
    - system-under-testX: tN-sutX.
- portnames:
    - tN-tgW-cY/pZ.
    - tN-sutX-cY/pZ.
- where:
    - N - testbed number.
    - tgW - server acts as traffic-generator with W index.
    - sutX - server acts as system-under-test with X index.
    - Y - PCIe slot number denoting a NIC card number within the host.
    - Z - port number on the NIC card.
```

## Testbeds Configuration

### Per Testbed Server Allocation and Naming

#### 1-Node-Skylake Servers (1n-skx) PROD

```
- SUT [Server-Type-B6]:
    - testbedname: testbed11.
    - hostname: s1-t11-sut1.
    - IPMI IP: 10.30.50.47
    - Host IP: 10.30.51.50
    - portnames:
        - s1-t11-sut1-c2/p1 - 10GE-port1 x710-4p10GE.
        - s1-t11-sut1-c2/p2 - 10GE-port2 x710-4p10GE.
        - s1-t11-sut1-c2/p3 - 10GE-port3 x710-4p10GE.
        - s1-t11-sut1-c2/p4 - 10GE-port4 x710-4p10GE.
        - s1-t11-sut1-c4/p1 - 10GE-port1 x710-4p10GE.
        - s1-t11-sut1-c4/p2 - 10GE-port2 x710-4p10GE.
        - s1-t11-sut1-c4/p3 - 10GE-port3 x710-4p10GE.
        - s1-t11-sut1-c4/p4 - 10GE-port4 x710-4p10GE.
- SUT [Server-Type-B6]:
    - testbedname: testbed12.
    - hostname: s2-t12-sut1.
    - IPMI IP: 10.30.50.48
    - Host IP: 10.30.51.51
    - portnames:
        - s2-t12-sut1-c2/p1 - 10GE-port1 x710-4p10GE.
        - s2-t12-sut1-c2/p2 - 10GE-port2 x710-4p10GE.
        - s2-t12-sut1-c2/p3 - 10GE-port3 x710-4p10GE.
        - s2-t12-sut1-c2/p4 - 10GE-port4 x710-4p10GE.
        - s2-t12-sut1-c4/p1 - 10GE-port1 x710-4p10GE.
        - s2-t12-sut1-c4/p2 - 10GE-port2 x710-4p10GE.
        - s2-t12-sut1-c4/p3 - 10GE-port3 x710-4p10GE.
        - s2-t12-sut1-c4/p4 - 10GE-port4 x710-4p10GE.
```

#### 1-Node-ThunderX2 Servers (1n-tx2) PROD

```
- SUT [Server-Type-E11]:
    - testbedname: testbed13
    - hostname: s55-t13-sut1
    - IPMI IP: 10.30.50.70
    - Host IP: 10.30.51.70
    - portnames:
        - s55-t13-sut1-c4/p1 - 40GE-port1 XL710-QDA2-2p40GE.
        - s55-t13-sut1-c4/p2 - 40GE-port2 XL710-QDA2-2p40GE.
        - s55-t13-sut1-c8/p1 - 40GE-port1 ConnectX5-2p10/25GE Mellanox.
        - s55-t13-sut1-c8/p2 - 40GE-port2 ConnectX5-2p10/25GE Mellanox.
        - s55-t13-sut1-c14/p1 - 40GE-port1 XL710-QDA2-2p40GE.
        - s55-t13-sut1-c14/p2 - 40GE-port2 XL710-QDA2-2p40GE.
        - s55-t13-sut1-c26/p1 - 40GE-port1 ConnectX5-2p10/25GE Mellanox.
        - s55-t13-sut1-c26/p2 - 40GE-port2 ConnectX5-2p10/25GE Mellanox.
- SUT [Server-Type-E11]:
    - testbedname: testbed14
    - hostname: s56-t14-sut1
    - IPMI IP: 10.30.50.71
    - Host IP: 10.30.51.71
    - portnames:
        - s56-t14-sut1-c4/p1 - 40GE-port1 XL710-QDA2-2p40GE.
        - s56-t14-sut1-c4/p2 - 40GE-port2 XL710-QDA2-2p40GE.
        - s56-t14-sut1-c8/p1 - 40GE-port1 ConnectX5-2p10/25GE Mellanox.
        - s56-t14-sut1-c8/p2 - 40GE-port2 ConnectX5-2p10/25GE Mellanox.
        - s56-t14-sut1-c14/p1 - 40GE-port1 XL710-QDA2-2p40GE.
        - s56-t14-sut1-c14/p2 - 40GE-port2 XL710-QDA2-2p40GE.
        - s56-t14-sut1-c26/p1 - 40GE-port1 ConnectX5-2p10/25GE Mellanox.
        - s56-t14-sut1-c26/p2 - 40GE-port2 ConnectX5-2p10/25GE Mellanox.
```

#### 1-Node-Cascadelake Servers (1n-clx) PROD

```
- SUT [Server-Type-C1]:
    - testbedname: testbed11.
    - hostname: s32-t14-sut1.
    - IPMI IP: 10.30.55.17
    - Host IP: 10.32.8.17
    - portnames:
        - s32-t14-sut1-c2/p1 - 10GE-port1 x710-4p10GE.
        - s32-t14-sut1-c2/p2 - 10GE-port2 x710-4p10GE.
        - s32-t14-sut1-c2/p3 - 10GE-port3 x710-4p10GE.
        - s32-t14-sut1-c2/p4 - 10GE-port4 x710-4p10GE.
        - s32-t14-sut1-c4/p1 - 10GE-port1 x710-4p10GE.
        - s32-t14-sut1-c4/p2 - 10GE-port2 x710-4p10GE.
        - s32-t14-sut1-c4/p3 - 10GE-port3 x710-4p10GE.
        - s32-t14-sut1-c4/p4 - 10GE-port4 x710-4p10GE.
```

#### 2-Node-Skylake Servers (2n-skx) PROD

```
- SUT [Server-Type-B1]:
    - testbedname: testbed21.
    - hostname: s3-t21-sut1.
    - IPMI IP: 10.30.50.41
    - Host IP: 10.30.51.44
    - portnames:
        - s3-t21-sut1-c2/p1 - 10GE-port1 x710-4p10GE.
        - s3-t21-sut1-c2/p2 - 10GE-port2 x710-4p10GE.
        - s3-t21-sut1-c2/p3 - 10GE-port3 x710-4p10GE.
        - s3-t21-sut1-c2/p4 - 10GE-port4 x710-4p10GE.
        - s3-t21-sut1-c4/p1 - 25GE-port1 xxv710-DA2-2p25GE.
        - s3-t21-sut1-c4/p2 - 25GE-port2 xxv710-DA2-2p25GE.
- TG [Server-Type-B2]:
    - testbedname: testbed21.
    - hostname: s4-t21-tg1.
    - IPMI IP: 10.30.50.42
    - Host IP: 10.30.51.45
    - portnames:
        - s4-t21-tg1-c2/p1 - 10GE-port1 x710-4p10GE.
        - s4-t21-tg1-c2/p2 - 10GE-port2 x710-4p10GE.
        - s4-t21-tg1-c2/p3 - 10GE-port3 x710-4p10GE.
        - s4-t21-tg1-c2/p4 - 10GE-port4 x710-4p10GE.
        - s4-t21-tg1-c4/p1 - 25GE-port1 xxv710-DA2-2p25GE.
        - s4-t21-tg1-c4/p2 - 25GE-port2 xxv710-DA2-2p25GE.
        - s3-t21-tg1-c10/p1 - 10GE-port1 x710-4p10GE.
        - s3-t21-tg1-c10/p2 - 10GE-port2 x710-4p10GE.
        - s3-t21-tg1-c10/p3 - 10GE-port3 x710-4p10GE.
        - s3-t21-tg1-c10/p4 - 10GE-port4 x710-4p10GE.
- SUT [Server-Type-B1]:
    - testbedname: testbed22.
    - hostname: s5-t22-sut1.
    - IPMI IP: 10.30.50.49
    - Host IP: 10.30.51.52
    - portnames:
        - s5-t22-sut1-c2/p1 - 10GE-port1 x710-4p10GE.
        - s5-t22-sut1-c2/p2 - 10GE-port2 x710-4p10GE.
        - s5-t22-sut1-c2/p3 - 10GE-port3 x710-4p10GE.
        - s5-t22-sut1-c2/p4 - 10GE-port4 x710-4p10GE.
        - s5-t22-sut1-c4/p1 - 25GE-port1 xxv710-DA2-2p25GE.
        - s5-t22-sut1-c4/p2 - 25GE-port2 xxv710-DA2-2p25GE.
- TG [Server-Type-B2]:
    - testbedname: testbed22.
    - hostname: s6-t22-tg1.
    - IPMI IP: 10.30.50.50
    - Host IP: 10.30.51.53
    - portnames:
        - s6-t22-tg1-c2/p1 - 10GE-port1 x710-4p10GE.
        - s6-t22-tg1-c2/p2 - 10GE-port2 x710-4p10GE.
        - s6-t22-tg1-c2/p3 - 10GE-port3 x710-4p10GE.
        - s6-t22-tg1-c2/p4 - 10GE-port4 x710-4p10GE.
        - s6-t22-tg1-c4/p1 - 25GE-port1 xxv710-DA2-2p25GE.
        - s6-t22-tg1-c4/p2 - 25GE-port2 xxv710-DA2-2p25GE.
        - s6-t22-tg1-c10/p1 - 10GE-port1 x710-4p10GE.
        - s6-t22-tg1-c10/p2 - 10GE-port2 x710-4p10GE.
        - s6-t22-tg1-c10/p3 - 10GE-port3 x710-4p10GE.
        - s6-t22-tg1-c10/p4 - 10GE-port4 x710-4p10GE.
- SUT [Server-Type-B1]:
    - testbedname: testbed23.
    - hostname: s7-t23-sut1.
    - IPMI IP: 10.30.50.51
    - Host IP: 10.30.51.54
    - portnames:
        - s7-t23-sut1-c2/p1 - 10GE-port1 x710-4p10GE.
        - s7-t23-sut1-c2/p2 - 10GE-port2 x710-4p10GE.
        - s7-t23-sut1-c2/p3 - 10GE-port3 x710-4p10GE.
        - s7-t23-sut1-c2/p4 - 10GE-port4 x710-4p10GE.
        - s7-t23-sut1-c4/p1 - 25GE-port1 xxv710-DA2-2p25GE.
        - s7-t23-sut1-c4/p2 - 25GE-port2 xxv710-DA2-2p25GE.
- TG [Server-Type-B2]:
    - testbedname: testbed23.
    - hostname: s8-t23-tg1.
    - IPMI IP: 10.30.50.52
    - Host IP: 10.30.51.55
    - portnames:
        - s8-t23-tg1-c2/p1 - 10GE-port1 x710-4p10GE.
        - s8-t23-tg1-c2/p2 - 10GE-port2 x710-4p10GE.
        - s8-t23-tg1-c2/p3 - 10GE-port3 x710-4p10GE.
        - s8-t23-tg1-c2/p4 - 10GE-port4 x710-4p10GE.
        - s8-t23-tg1-c4/p1 - 25GE-port1 xxv710-DA2-2p25GE.
        - s8-t23-tg1-c4/p2 - 25GE-port2 xxv710-DA2-2p25GE.
        - s8-t23-tg1-c10/p1 - 10GE-port1 x710-4p10GE.
        - s8-t23-tg1-c10/p2 - 10GE-port2 x710-4p10GE.
        - s8-t23-tg1-c10/p3 - 10GE-port3 x710-4p10GE.
        - s8-t23-tg1-c10/p4 - 10GE-port4 x710-4p10GE.
- SUT [Server-Type-B1]:
    - testbedname: testbed24.
    - hostname: s9-t24-sut1.
    - IPMI IP: 10.30.50.53
    - Host IP: 10.30.51.56
    - portnames:
        - s9-t24-sut1-c2/p1 - 10GE-port1 x710-4p10GE.
        - s9-t24-sut1-c2/p2 - 10GE-port2 x710-4p10GE.
        - s9-t24-sut1-c2/p3 - 10GE-port3 x710-4p10GE.
        - s9-t24-sut1-c2/p4 - 10GE-port4 x710-4p10GE.
        - s9-t24-sut1-c4/p1 - 25GE-port1 xxv710-DA2-2p25GE.
        - s9-t24-sut1-c4/p2 - 25GE-port2 xxv710-DA2-2p25GE.
- TG [Server-Type-B2]:
    - testbedname: testbed24.
    - hostname: s10-t24-tg1.
    - IPMI IP: 10.30.50.54
    - Host IP: 10.30.51.57
    - portnames:
        - s10-t24-tg1-c2/p1 - 10GE-port1 x710-4p10GE.
        - s10-t24-tg1-c2/p2 - 10GE-port2 x710-4p10GE.
        - s10-t24-tg1-c2/p3 - 10GE-port3 x710-4p10GE.
        - s10-t24-tg1-c2/p4 - 10GE-port4 x710-4p10GE.
        - s10-t24-tg1-c4/p1 - 25GE-port1 xxv710-DA2-2p25GE.
        - s10-t24-tg1-c4/p2 - 25GE-port2 xxv710-DA2-2p25GE.
        - s10-t24-tg1-c10/p1 - 10GE-port1 x710-4p10GE.
        - s10-t24-tg1-c10/p2 - 10GE-port2 x710-4p10GE.
        - s10-t24-tg1-c10/p3 - 10GE-port3 x710-4p10GE.
        - s10-t24-tg1-c10/p4 - 10GE-port4 x710-4p10GE.
```

#### 2-Node-Denverton Servers (2n-dnv) PROD

Note: ServerB28 (TG) is shared between testbed26 & testbed35

```
- TG [Server-Type-B2]:
    - testbednames: testbed26 and testbed35.
    - hostname: s28-t26t35-tg1.
    - IPMI IP: 10.30.55.10
    - Host IP: 10.32.8.10
    - portnames:
        - s28-t26t35-tg1-c2/p1 - 10GE-port1 x710da2-2p10GE.
        - s28-t26t35-tg1-c2/p2 - 10GE-port2 x710da2-2p10GE.
        - s28-t26t35-tg1-c4/p1 - 10GE-port1 x550t2-2p10GE.
        - s28-t26t35-tg1-c4/p2 - 10GE-port2 x550t2-2p10GE.
        - s28-t26t35-tg1-c9/p1 - 10GE-port1 x550t2-2p10GE.
        - s28-t26t35-tg1-c9/p2 - 10GE-port2 x550t2-2p10GE.
        - s28-t26t35-tg1-c6/p1 - 10GE-port1 x710da2-2p10GE.
        - s28-t26t35-tg1-c6/p2 - 10GE-port2 x710da2-2p10GE.
        - s28-t26t35-tg1-c8/p1 - 10GE-port1 x550t2-2p10GE.
        - s28-t26t35-tg1-c8/p2 - 10GE-port2 x550t2-2p10GE.
        - s28-t26t35-tg1-c10/p1 - 10GE-port1 x550t2-2p10GE.
        - s28-t26t35-tg1-c10/p2 - 10GE-port2 x550t2-2p10GE.
- SUT [Server-Type-B10]:
    - testbednames: testbed26.
    - hostname: s29-t26-sut1.
    - IPMI IP: 10.30.55.11
    - Host IP: 10.32.8.11
    - portnames:
        - s29-t26-sut1-p1 - 10GE-port1 x553 copper port.
        - s29-t26-sut1-p2 - 10GE-port2 x553 copper port.
        - s29-t26-sut1-p3 - 10GE-port3 x553 fiber port.
        - s29-t26-sut1-p4 - 10GE-port4 x553 fiber port.
```

#### 2-Node-IxiaPS1L47 Servers (2n-ps1) VERIFY

```
- SUT [Server-Type-B8]:
    - testbedname: testbed25.
    - hostname: s25-t25-sut1.
    - IPMI IP: 10.30.50.58
    - Host IP: 10.30.51.61
    - portnames:
        - s25-t25-sut1-c2/p1 - 10GE-port1 x710-4p10GE.
        - s25-t25-sut1-c2/p2 - 10GE-port2 x710-4p10GE.
        - s25-t25-sut1-c2/p3 - 10GE-port3 x710-4p10GE.
        - s25-t25-sut1-c2/p4 - 10GE-port4 x710-4p10GE.
- TG [Server-Type-B7]:
    - testbedname: testbed25.
    - hostname: s26-t25-tg1.
    - IPMI IP: 10.30.50.59
    - Host IP: 10.30.51.62
    - portnames:
        - s26-t25-tg1-p1 - 10GE-port1.
        - s26-t25-tg1-p2 - 10GE-port2.
        - s26-t25-tg1-p3 - 10GE-port3.
        - s26-t25-tg1-p4 - 10GE-port4.
```

#### 2-Node-Cascadelake Servers (2n-clx) PROD

```
- SUT [Server-Type-C2]:
    - testbedname: testbed27.
    - hostname: s33-t27-sut1.
    - IPMI IP: 10.30.55.18
    - Host IP: 10.32.8.18
    - portnames:
        - s33-t27-sut1-c2/p1 - 10GE-port1 x710-4p10GE.
        - s33-t27-sut1-c2/p2 - 10GE-port2 x710-4p10GE.
        - s33-t27-sut1-c2/p3 - 10GE-port3 x710-4p10GE.
        - s33-t27-sut1-c2/p4 - 10GE-port4 x710-4p10GE.
        - s33-t27-sut1-c4/p1 - 25GE-port1 xxv710-DA2-2p25GE.
        - s33-t27-sut1-c4/p2 - 25GE-port2 xxv710-DA2-2p25GE.
        - s33-t27-sut1-c6/p1 - 100GE-port1 e810-2p100GE.
        - s33-t27-sut1-c6/p2 - 100GE-port2 e810-2p100GE.
        - s33-t27-sut1-c9/p1 - 100GE-port1 ConnectX5-2p100GE.
        - s33-t27-sut1-c9/p2 - 100GE-port2 ConnectX5-2p100GE.
- TG [Server-Type-C3]:
    - testbedname: testbed27.
    - hostname: s34-t27-tg1.
    - IPMI IP: 10.30.55.19
    - Host IP: 10.32.8.19
    - portnames:
        - s34-t27-tg1-c2/p1 - 10GE-port1 x710-4p10GE.
        - s34-t27-tg1-c2/p2 - 10GE-port2 x710-4p10GE.
        - s34-t27-tg1-c2/p3 - 10GE-port3 x710-4p10GE.
        - s34-t27-tg1-c2/p4 - 10GE-port4 x710-4p10GE.
        - s34-t27-tg1-c4/p1 - 25GE-port1 xxv710-DA2-2p25GE.
        - s34-t27-tg1-c4/p2 - 25GE-port2 xxv710-DA2-2p25GE.
        - s34-t27-tg1-c6/p1 - 100GE-port1 ConnectX5-2p100GE.
        - s34-t27-tg1-c6/p2 - 100GE-port2 ConnectX5-2p100GE.
        - s38-t27-tg1-c8/p1 - 100GE-port1 ConnectX5-2p100GE.
        - s38-t27-tg1-c8/p2 - 100GE-port2 ConnectX5-2p100GE.
        - s34-t27-tg1-c9/p1 - 100GE-port1 ConnectX5-2p100GE.
        - s34-t27-tg1-c9/p2 - 100GE-port2 ConnectX5-2p100GE.
- SUT [Server-Type-C2]:
    - testbedname: testbed28.
    - hostname: s35-t28-sut1.
    - IPMI IP: 10.30.55.20
    - Host IP: 10.32.8.20
    - portnames:
        - s35-t28-sut1-c2/p1 - 10GE-port1 x710-4p10GE.
        - s35-t28-sut1-c2/p2 - 10GE-port2 x710-4p10GE.
        - s35-t28-sut1-c2/p3 - 10GE-port3 x710-4p10GE.
        - s35-t28-sut1-c2/p4 - 10GE-port4 x710-4p10GE.
        - s35-t28-sut1-c4/p1 - 25GE-port1 xxv710-DA2-2p25GE.
        - s35-t28-sut1-c4/p2 - 25GE-port2 xxv710-DA2-2p25GE.
        - s35-t28-sut1-c6/p1 - 100GE-port1 e810-2p100GE.
        - s35-t28-sut1-c6/p2 - 100GE-port2 e810-2p100GE.
        - s35-t28-sut1-c9/p1 - 100GE-port1 ConnectX5-2p100GE.
        - s35-t28-sut1-c9/p2 - 100GE-port2 ConnectX5-2p100GE.
- TG [Server-Type-C3]:
    - testbedname: testbed28.
    - hostname: s36-t28-tg1.
    - IPMI IP: 10.30.55.21
    - Host IP: 10.32.8.21
    - portnames:
        - s36-t28-tg1-c2/p1 - 10GE-port1 x710-4p10GE.
        - s36-t28-tg1-c2/p2 - 10GE-port2 x710-4p10GE.
        - s36-t28-tg1-c2/p3 - 10GE-port3 x710-4p10GE.
        - s36-t28-tg1-c2/p4 - 10GE-port4 x710-4p10GE.
        - s36-t28-tg1-c4/p1 - 25GE-port1 xxv710-DA2-2p25GE.
        - s36-t28-tg1-c4/p2 - 25GE-port2 xxv710-DA2-2p25GE.
        - s36-t28-tg1-c6/p1 - 100GE-port1 ConnectX5-2p100GE.
        - s36-t28-tg1-c6/p2 - 100GE-port2 ConnectX5-2p100GE.
        - s38-t28-tg1-c8/p1 - 100GE-port1 ConnectX5-2p100GE.
        - s38-t28-tg1-c8/p2 - 100GE-port2 ConnectX5-2p100GE.
        - s36-t28-tg1-c9/p1 - 100GE-port1 ConnectX5-2p100GE.
        - s36-t28-tg1-c9/p2 - 100GE-port2 ConnectX5-2p100GE.
- SUT [Server-Type-C2]:
    - testbedname: testbed29.
    - hostname: s37-t29-sut1.
    - IPMI IP: 10.30.55.22
    - Host IP: 10.32.8.22
    - portnames:
        - s37-t29-sut1-c2/p1 - 10GE-port1 x710-4p10GE.
        - s37-t29-sut1-c2/p2 - 10GE-port2 x710-4p10GE.
        - s37-t29-sut1-c2/p3 - 10GE-port3 x710-4p10GE.
        - s37-t29-sut1-c2/p4 - 10GE-port4 x710-4p10GE.
        - s37-t29-sut1-c4/p1 - 25GE-port1 xxv710-DA2-2p25GE.
        - s37-t29-sut1-c4/p2 - 25GE-port2 xxv710-DA2-2p25GE.
        - s37-t29-sut1-c6/p1 - 100GE-port1 e810-2p100GE.
        - s37-t29-sut1-c6/p2 - 100GE-port2 e810-2p100GE.
        - s37-t29-sut1-c9/p1 - 100GE-port1 ConnectX5-2p100GE.
        - s37-t29-sut1-c9/p2 - 100GE-port2 ConnectX5-2p100GE.
- TG [Server-Type-C3]:
    - testbedname: testbed29.
    - hostname: s38-t29-tg1.
    - IPMI IP: 10.30.55.23
    - Host IP: 10.32.8.23
    - portnames:
        - s38-t29-tg1-c2/p1 - 10GE-port1 x710-4p10GE.
        - s38-t29-tg1-c2/p2 - 10GE-port2 x710-4p10GE.
        - s38-t29-tg1-c2/p3 - 10GE-port3 x710-4p10GE.
        - s38-t29-tg1-c2/p4 - 10GE-port4 x710-4p10GE.
        - s38-t29-tg1-c4/p1 - 25GE-port1 xxv710-DA2-2p25GE.
        - s38-t29-tg1-c4/p2 - 25GE-port2 xxv710-DA2-2p25GE.
        - s38-t29-tg1-c6/p1 - 100GE-port1 ConnectX5-2p100GE.
        - s38-t29-tg1-c6/p2 - 100GE-port2 ConnectX5-2p100GE.
        - s38-t29-tg1-c9/p1 - 100GE-port1 ConnectX5-2p100GE.
        - s38-t29-tg1-c9/p2 - 100GE-port2 ConnectX5-2p100GE.
```

#### 2-Node-Zen2 Servers (2n-zn2) PROD

```
- SUT [Server-Type-D1]:
    - testbedname: testbed210.
    - hostname: s60-t210-sut1.
    - IPMI IP: 10.30.55.24
    - Host IP: 10.32.8.24
    - portnames:
        - s60-t210-sut1-c1/p1 - 10GE-port1 x710-4p10GE.
        - s60-t210-sut1-c1/p2 - 10GE-port2 x710-4p10GE.
        - s60-t210-sut1-c1/p3 - 10GE-port3 x710-4p10GE.
        - s60-t210-sut1-c1/p4 - 10GE-port4 x710-4p10GE.
        - s60-t210-sut1-c2/p1 - 25GE-port1 xxv710-DA2-2p25GE.
        - s60-t210-sut1-c2/p2 - 25GE-port2 xxv710-DA2-2p25GE.
        - s60-t210-sut1-c3/p1 - 100GE-port1 ConnectX5-2p100GE.
        - s60-t210-sut1-c3/p2 - 100GE-port2 ConnectX5-2p100GE.
- TG [Server-Type-D2]:
    - testbedname: testbed210.
    - hostname: s61-t210-tg1.
    - IPMI IP: 10.30.55.25
    - Host IP: 10.32.8.25
    - portnames:
        - s61-t210-tg1-c1/p1 - 100GE-port1 ConnectX5-2p100GE.
        - s61-t210-tg1-c1/p2 - 100GE-port2 ConnectX5-2p100GE.
        - s61-t210-tg1-c2/p1 - 10GE-port1 x710-4p10GE.
        - s61-t210-tg1-c2/p2 - 10GE-port2 x710-4p10GE.
        - s61-t210-tg1-c2/p3 - 10GE-port3 x710-4p10GE.
        - s61-t210-tg1-c2/p4 - 10GE-port4 x710-4p10GE.
        - s61-t210-tg1-c3/p1 - 25GE-port1 xxv710-DA2-2p25GE.
        - s61-t210-tg1-c3/p2 - 25GE-port2 xxv710-DA2-2p25GE.
```

#### 2-Node-ThunderX2 Servers (2x-tx2) PROD

Note: Server19 (TG) is shared between testbed33 & testbed211

```
- SUT [Server-Type-E22]:
    - testbedname: testbed211.
    - hostname: s27-t211-sut1.
    - IPMI IP: 10.30.50.69
    - Host IP: 10.30.51.69
    - portnames:
        - s27-t211-sut1-c6/p1 - 40GE-port1 XL710-QDA2-2p40GE.
        - s27-t211-sut1-c6/p2 - 40GE-port2 XL710-QDA2-2p40GE.
        - s27-t211-sut1-c18/p1 - 40GE-port1 XL710-QDA2-2p40GE.
        - s27-t211-sut1-c18/p2 - 40GE-port2 XL710-QDA2-2p40GE.
- TG [Server-Type-E31]:
    - testbedname: testbed33 and testbed211.
    - hostname: s19-t33t211-tg1.
    - IPMI IP: 10.30.50.46
    - Host IP: 10.30.51.49
    - portnames:
        - s19-t33t211-tg1-c2/p1 - 10GE-port1 x710-4p10GE.
        - s19-t33t211-tg1-c2/p2 - 10GE-port2 x710-4p10GE.
        - s19-t33t211-tg1-c2/p3 - 10GE-port3 x710-4p10GE.
        - s19-t33t211-tg1-c2/p4 - 10GE-port4 x710-4p10GE.
        - s19-t33t211-tg1-c4/p1 - 25GE-port1 xxv710-DA2-2p25GE.
        - s19-t33t211-tg1-c4/p2 - 25GE-port2 xxv710-DA2-2p25GE.
        - s19-t33t211-tg1-c8/p1 - 40GE-port1 xl710-QDA2-2p40GE.
        - s19-t33t211-tg1-c8/p2 - 40GE-port2 xl710-QDA2-2p40GE.
        - s19-t33t211-tg1-c10/p1 - 10GE-port1 x710-4p10GE.
        - s19-t33t211-tg1-c10/p2 - 10GE-port2 x710-4p10GE.
        - s19-t33t211-tg1-c10/p3 - 10GE-port3 x710-4p10GE.
        - s19-t33t211-tg1-c10/p4 - 10GE-port4 x710-4p10GE.
```

#### 2-Node-Icelake Servers (2n-icx) PROD

```
- SUT [Server-Type-F1]:
    - testbedname: testbed212.
    - hostname: s71-t212-sut1.
    - IPMI IP: 10.30.51.81
    - Host IP: 10.30.50.81
    - portnames:
        - s71-t212-sut1-c2/p1 - 25GE-port1 xxv710-DA2-2p25GE.
        - s71-t212-sut1-c2/p2 - 25GE-port2 xxv710-DA2-2p25GE.
        - s71-t212-sut1-c4/p1 - 25GE-port1 e810-XXVDA4-4p25GE.
        - s71-t212-sut1-c4/p2 - 25GE-port2 e810-XXVDA4-4p25GE.
        - s71-t212-sut1-c4/p3 - 25GE-port3 e810-XXVDA4-4p25GE.
        - s71-t212-sut1-c4/p4 - 25GE-port4 e810-XXVDA4-4p25GE.
        - s71-t212-sut1-c9/p1 - 100GE-port1 e810-2CQDA2-2p100GE.
        - s71-t212-sut1-c9/p2 - 100GE-port2 e810-2CQDA2-2p100GE.
- TG [Server-Type-F2]:
    - testbedname: testbed212.
    - hostname: s72-t212-tg1.
    - IPMI IP: 10.30.51.82
    - Host IP: 10.30.50.82
    - portnames:
        - s72-t212-tg1-c2/p1 - 25GE-port1 xxv710-DA2-2p25GE.
        - s72-t212-tg1-c2/p2 - 25GE-port2 xxv710-DA2-2p25GE.
        - s72-t212-tg1-c4/p1 - 25GE-port1 e810-XXVDA4-4p25GE.
        - s72-t212-tg1-c4/p2 - 25GE-port2 e810-XXVDA4-4p25GE.
        - s72-t212-tg1-c4/p3 - 25GE-port3 e810-XXVDA4-4p25GE.
        - s72-t212-tg1-c4/p4 - 25GE-port4 e810-XXVDA4-4p25GE.
        - s72-t212-tg1-c9/p1 - 100GE-port1 e810-2CQDA2-2p100GE.
        - s72-t212-tg1-c9/p2 - 100GE-port2 e810-2CQDA2-2p100GE.
        - s72-t212-tg1-c6/p1 - 100GE-port1 e810-2CQDA2-2p100GE.
        - s72-t212-tg1-c6/p2 - 100GE-port2 e810-2CQDA2-2p100GE.
- SUT [Server-Type-F1]:
    - testbedname: testbed213.
    - hostname: s83-t213-sut1.
    - IPMI IP: 10.30.51.83
    - Host IP: 10.30.50.83
    - portnames:
        - s83-t213-sut1-c2/p1 - 25GE-port1 xxv710-DA2-2p25GE.
        - s83-t213-sut1-c2/p2 - 25GE-port2 xxv710-DA2-2p25GE.
        - s83-t213-sut1-c4/p1 - 25GE-port1 e810-XXVDA4-4p25GE.
        - s83-t213-sut1-c4/p2 - 25GE-port2 e810-XXVDA4-4p25GE.
        - s83-t213-sut1-c4/p3 - 25GE-port3 e810-XXVDA4-4p25GE.
        - s83-t213-sut1-c4/p4 - 25GE-port4 e810-XXVDA4-4p25GE.
        - s83-t213-sut1-c9/p1 - 100GE-port1 e810-2CQDA2-2p100GE.
        - s83-t213-sut1-c9/p2 - 100GE-port2 e810-2CQDA2-2p100GE.
- TG [Server-Type-F2]:
    - testbedname: testbed213.
    - hostname: s84-t213-tg1.
    - IPMI IP: 10.30.51.84
    - Host IP: 10.30.50.84
    - portnames:
        - s84-t213-tg1-c2/p1 - 25GE-port1 xxv710-DA2-2p25GE.
        - s84-t213-tg1-c2/p2 - 25GE-port2 xxv710-DA2-2p25GE.
        - s84-t213-tg1-c4/p1 - 25GE-port1 e810-XXVDA4-4p25GE.
        - s84-t213-tg1-c4/p2 - 25GE-port2 e810-XXVDA4-4p25GE.
        - s84-t213-tg1-c4/p3 - 25GE-port3 e810-XXVDA4-4p25GE.
        - s84-t213-tg1-c4/p4 - 25GE-port4 e810-XXVDA4-4p25GE.
        - s84-t213-tg1-c9/p1 - 100GE-port1 e810-2CQDA2-2p100GE.
        - s84-t213-tg1-c9/p2 - 100GE-port2 e810-2CQDA2-2p100GE.
        - s84-t213-tg1-c6/p1 - 100GE-port1 e810-2CQDA2-2p100GE.
        - s84-t213-tg1-c6/p2 - 100GE-port2 e810-2CQDA2-2p100GE.
- SUT [Server-Type-F1]:
    - testbedname: testbed214.
    - hostname: s85-t214-sut1.
    - IPMI IP: 10.30.51.85
    - Host IP: 10.30.50.85
    - portnames:
        - s85-t214-sut1-c2/p1 - 25GE-port1 xxv710-DA2-2p25GE.
        - s85-t214-sut1-c2/p2 - 25GE-port2 xxv710-DA2-2p25GE.
        - s85-t214-sut1-c4/p1 - 25GE-port1 e810-XXVDA4-4p25GE.
        - s85-t214-sut1-c4/p2 - 25GE-port2 e810-XXVDA4-4p25GE.
        - s85-t214-sut1-c4/p3 - 25GE-port3 e810-XXVDA4-4p25GE.
        - s85-t214-sut1-c4/p4 - 25GE-port4 e810-XXVDA4-4p25GE.
        - s85-t214-sut1-c9/p1 - 100GE-port1 e810-2CQDA2-2p100GE.
        - s85-t214-sut1-c9/p2 - 100GE-port2 e810-2CQDA2-2p100GE.
- TG [Server-Type-F2]:
    - testbedname: testbed214.
    - hostname: s86-t214-tg1.
    - IPMI IP: 10.30.51.86
    - Host IP: 10.30.50.86
    - portnames:
        - s86-t214-tg1-c2/p1 - 25GE-port1 xxv710-DA2-2p25GE.
        - s86-t214-tg1-c2/p2 - 25GE-port2 xxv710-DA2-2p25GE.
        - s86-t214-tg1-c4/p1 - 25GE-port1 e810-XXVDA4-4p25GE.
        - s86-t214-tg1-c4/p2 - 25GE-port2 e810-XXVDA4-4p25GE.
        - s86-t214-tg1-c4/p3 - 25GE-port3 e810-XXVDA4-4p25GE.
        - s86-t214-tg1-c4/p4 - 25GE-port4 e810-XXVDA4-4p25GE.
        - s86-t214-tg1-c9/p1 - 100GE-port1 e810-2CQDA2-2p100GE.
        - s86-t214-tg1-c9/p2 - 100GE-port2 e810-2CQDA2-2p100GE.
        - s86-t214-tg1-c6/p1 - 100GE-port1 e810-2CQDA2-2p100GE.
        - s86-t214-tg1-c6/p2 - 100GE-port2 e810-2CQDA2-2p100GE.
- SUT [Server-Type-F1]:
    - testbedname: testbed215.
    - hostname: s87-t215-sut1.
    - IPMI IP: 10.30.51.87
    - Host IP: 10.30.50.87
    - portnames:
        - s87-t215-sut1-c2/p1 - 25GE-port1 xxv710-DA2-2p25GE.
        - s87-t215-sut1-c2/p2 - 25GE-port2 xxv710-DA2-2p25GE.
        - s87-t215-sut1-c4/p1 - 25GE-port1 e810-XXVDA4-4p25GE.
        - s87-t215-sut1-c4/p2 - 25GE-port2 e810-XXVDA4-4p25GE.
        - s87-t215-sut1-c4/p3 - 25GE-port3 e810-XXVDA4-4p25GE.
        - s87-t215-sut1-c4/p4 - 25GE-port4 e810-XXVDA4-4p25GE.
        - s87-t215-sut1-c9/p1 - 100GE-port1 e810-2CQDA2-2p100GE.
        - s87-t215-sut1-c9/p2 - 100GE-port2 e810-2CQDA2-2p100GE.
- TG [Server-Type-F2]:
    - testbedname: testbed215.
    - hostname: s88-t215-tg1.
    - IPMI IP: 10.30.51.88
    - Host IP: 10.30.50.88
    - portnames:
        - s88-t215-tg1-c2/p1 - 25GE-port1 xxv710-DA2-2p25GE.
        - s88-t215-tg1-c2/p2 - 25GE-port2 xxv710-DA2-2p25GE.
        - s88-t215-tg1-c4/p1 - 25GE-port1 e810-XXVDA4-4p25GE.
        - s88-t215-tg1-c4/p2 - 25GE-port2 e810-XXVDA4-4p25GE.
        - s88-t215-tg1-c4/p3 - 25GE-port3 e810-XXVDA4-4p25GE.
        - s88-t215-tg1-c4/p4 - 25GE-port4 e810-XXVDA4-4p25GE.
        - s88-t215-tg1-c9/p1 - 100GE-port1 e810-2CQDA2-2p100GE.
        - s88-t215-tg1-c9/p2 - 100GE-port2 e810-2CQDA2-2p100GE.
        - s88-t215-tg1-c6/p1 - 100GE-port1 e810-2CQDA2-2p100GE.
        - s88-t215-tg1-c6/p2 - 100GE-port2 e810-2CQDA2-2p100GE.
```

#### 3-Node-Skylake Servers (3n-skx) PROD

```
- ServerB11 [Server-Type-B1]:
    - testbedname: testbed31.
    - hostname: s11-t31-sut1.
    - IPMI IP: 10.30.50.43
    - Host IP: 10.30.51.46
    - portnames:
        - s11-t31-sut1-c2/p1 - 10GE-port1 x710-4p10GE.
        - s11-t31-sut1-c2/p2 - 10GE-port2 x710-4p10GE.
        - s11-t31-sut1-c2/p3 - 10GE-port3 x710-4p10GE.
        - s11-t31-sut1-c2/p4 - 10GE-port4 x710-4p10GE.
        - s11-t31-sut1-c4/p1 - 25GE-port1 xxv710-DA2-2p25GE.
        - s11-t31-sut1-c4/p2 - 25GE-port2 xxv710-DA2-2p25GE.
- ServerB12 [Server-Type-B1]:
    - testbedname: testbed31.
    - hostname: s12-t31-sut2.
    - IPMI IP: 10.30.50.44
    - Host IP: 10.30.51.47
    - portnames:
        - s12-t31-sut2-c2/p1 - 10GE-port1 x710-4p10GE.
        - s12-t31-sut2-c2/p2 - 10GE-port2 x710-4p10GE.
        - s12-t31-sut2-c2/p3 - 10GE-port3 x710-4p10GE.
        - s12-t31-sut2-c2/p4 - 10GE-port4 x710-4p10GE.
        - s12-t31-sut2-c4/p1 - 25GE-port1 xxv710-DA2-2p25GE.
        - s12-t31-sut2-c4/p2 - 25GE-port2 xxv710-DA2-2p25GE.
- ServerB13 [Server-Type-B2]:
    - testbedname: testbed31.
    - hostname: s13-t31-tg1.
    - IPMI IP: 10.30.50.45
    - Host IP: 10.30.51.48
    - portnames:
        - s13-t31-tg1-c2/p1 - 10GE-port1 x710-4p10GE.
        - s13-t31-tg1-c2/p2 - 10GE-port2 x710-4p10GE.
        - s13-t31-tg1-c2/p3 - 10GE-port3 x710-4p10GE.
        - s13-t31-tg1-c2/p4 - 10GE-port4 x710-4p10GE.
        - s13-t31-tg1-c4/p1 - 25GE-port1 xxv710-DA2-2p25GE.
        - s13-t31-tg1-c4/p2 - 25GE-port2 xxv710-DA2-2p25GE.
        - s13-t31-tg1-c10/p1 - 10GE-port1 x710-4p10GE.
        - s13-t31-tg1-c10/p2 - 10GE-port2 x710-4p10GE.
        - s13-t31-tg1-c10/p3 - 10GE-port3 x710-4p10GE.
        - s13-t31-tg1-c10/p4 - 10GE-port4 x710-4p10GE.
- ServerB14 [Server-Type-B1]:
    - testbedname: testbed32.
    - hostname: s14-t32-sut1.
    - IPMI IP: 10.30.50.55
    - Host IP: 10.30.51.58
    - portnames:
        - s14-t32-sut1-c2/p1 - 10GE-port1 x710-4p10GE.
        - s14-t32-sut1-c2/p2 - 10GE-port2 x710-4p10GE.
        - s14-t32-sut1-c2/p3 - 10GE-port3 x710-4p10GE.
        - s14-t32-sut1-c2/p4 - 10GE-port4 x710-4p10GE.
        - s14-t32-sut1-c4/p1 - 25GE-port1 xxv710-DA2-2p25GE.
        - s14-t32-sut1-c4/p2 - 25GE-port2 xxv710-DA2-2p25GE.
- ServerB15 [Server-Type-B1]:
    - testbedname: testbed32.
    - hostname: s15-t32-sut2.
    - IPMI IP: 10.30.50.56
    - Host IP: 10.30.51.59
    - portnames:
        - s15-t32-sut2-c2/p1 - 10GE-port1 x710-4p10GE.
        - s15-t32-sut2-c2/p2 - 10GE-port2 x710-4p10GE.
        - s15-t32-sut2-c2/p3 - 10GE-port3 x710-4p10GE.
        - s15-t32-sut2-c2/p4 - 10GE-port4 x710-4p10GE.
        - s15-t32-sut2-c4/p1 - 25GE-port1 xxv710-DA2-2p25GE.
        - s15-t32-sut2-c4/p2 - 25GE-port2 xxv710-DA2-2p25GE.
- ServerB16 [Server-Type-B2]:
    - testbedname: testbed32.
    - hostname: s16-t32-tg1.
    - IPMI IP: 10.30.50.57
    - Host IP: 10.30.51.60
    - portnames:
        - s16-t32-tg1-c2/p1 - 10GE-port1 x710-4p10GE.
        - s16-t32-tg1-c2/p2 - 10GE-port2 x710-4p10GE.
        - s16-t32-tg1-c2/p3 - 10GE-port3 x710-4p10GE.
        - s16-t32-tg1-c2/p4 - 10GE-port4 x710-4p10GE.
        - s16-t32-tg1-c4/p1 - 25GE-port1 xxv710-DA2-2p25GE.
        - s16-t32-tg1-c4/p2 - 25GE-port2 xxv710-DA2-2p25GE.
        - s16-t32-tg1-c10/p1 - 10GE-port1 x710-4p10GE.
        - s16-t32-tg1-c10/p2 - 10GE-port2 x710-4p10GE.
        - s16-t32-tg1-c10/p3 - 10GE-port3 x710-4p10GE.
        - s16-t32-tg1-c10/p4 - 10GE-port4 x710-4p10GE.
```

#### 3-Node-Rangeley Servers (3n-rng) VERIFY

Note: There is no IPMI. Serial console is accessible via VIRL2 and VIRL3 USB.

```
- ServerB22 [Server-Type-B5]:
    - testbedname: testbed35.
    - hostname: s22-t35-sut1 (vex-yul-rot-netgate-1).
    - IPMI IP: 10.30.51.29 - screen -r /dev/ttyUSB0
    - Host IP: 10.30.51.9
    - portnames:
        - s22-t35-sut1-p1 - 10GE-port1 ix0 82599.
        - s22-t35-sut1-p2 - 10GE-port2 ix1 82599.
    - 1GB ports (tbd)
- ServerB23 [Server-Type-B5]:
    - testbedname: testbed35.
    - hostname: s23-t35-sut2 (vex-yul-rot-netgate-2).
    - IPMI IP: 10.30.51.30 - screen -r /dev/ttyUSB1
    - Host IP: 10.30.51.10
    - portnames:
        - s23-t35-sut1-p1 - 10GE-port1 ix0 82599.
        - s23-t35-sut1-p2 - 10GE-port2 ix1 82599.
    - 1GB ports (tbd)
- ServerB24 [Server-Type-B5]:
    - testbedname: testbed35.
    - hostname: s24-t35-sut3 (vex-yul-rot-netgate-3).
    - IPMI IP: 10.30.51.30 - screen -r /dev/ttyUSB2
    - Host IP: 10.30.51.11
    - portnames:
        - s24-t35-sut1-p1 - 10GE-port1 ix0 82599.
        - s24-t35-sut1-p2 - 10GE-port2 ix1 82599.
    - 1GB ports (tbd)
```

#### 3-Node-Taishan Servers (3n-tsh) PROD

Note: Server19 (TG) is shared between testbed33 & testbed211

```
- SUT [Server-Type-E21]:
    - testbedname: testbed33.
    - hostname: s17-t33-sut1.
    - IPMI IP: 10.30.50.36
    - Host IP: 10.30.51.36
    - portnames:
        - s17-t33-sut1-c6/p1 - 10GE-port1 x520-2p10GE.
        - s17-t33-sut1-c6/p2 - 10GE-port2 x520-2p10GE.
        - s17-t33-sut1-c4/p1 - 25GE-port1 cx4-2p25GE.
        - s17-t33-sut1-c4/p2 - 25GE-port2 cx4-2p25GE.
- SUT [Server-Type-E21]:
    - testbedname: testbed33.
    - hostname: s18-t33-sut2.
    - IPMI IP: 10.30.50.37
    - Host IP: 10.30.51.37
    - portnames:
        - s18-t33-sut2-c6/p1 - 10GE-port1 x520-2p10GE.
        - s18-t33-sut2-c6/p2 - 10GE-port2 x520-2p10GE.
        - s18-t33-sut2-c4/p1 - 25GE-port1 cx4-2p25GE.
        - s18-t33-sut2-c4/p2 - 25GE-port2 cx4-2p25GE.
- TG [Server-Type-E31]:
    - testbedname: testbed33 and testbed211.
    - hostname: s19-t33t211-tg1.
    - IPMI IP: 10.30.50.46
    - Host IP: 10.30.51.49
    - portnames:
        - s19-t33t211-tg1-c2/p1 - 10GE-port1 x710-4p10GE.
        - s19-t33t211-tg1-c2/p2 - 10GE-port2 x710-4p10GE.
        - s19-t33t211-tg1-c2/p3 - 10GE-port3 x710-4p10GE.
        - s19-t33t211-tg1-c2/p4 - 10GE-port4 x710-4p10GE.
        - s19-t33t211-tg1-c4/p1 - 25GE-port1 xxv710-DA2-2p25GE.
        - s19-t33t211-tg1-c4/p2 - 25GE-port2 xxv710-DA2-2p25GE.
        - s19-t33t211-tg1-c8/p1 - 40GE-port1 xl710-QDA2-2p40GE.
        - s19-t33t211-tg1-c8/p2 - 40GE-port2 xl710-QDA2-2p40GE.
        - s19-t33t211-tg1-c10/p1 - 10GE-port1 x710-4p10GE.
        - s19-t33t211-tg1-c10/p2 - 10GE-port2 x710-4p10GE.
        - s19-t33t211-tg1-c10/p3 - 10GE-port3 x710-4p10GE.
        - s19-t33t211-tg1-c10/p4 - 10GE-port4 x710-4p10GE.
```

#### 3-Node-Altra Servers (3n-alt) PROD

Note: Server64 (TG) is shared between testbed34 & testbed36

```
- SUT [Server-Type-E23]:
    - testbedname: testbed34.
    - hostname: s62-t34-sut1.
    - IPMI IP: 10.30.50.72
    - Host IP: 10.30.51.72
    - portnames:
        - s62-t34-sut1-cn/p1 - 40GE-port1 xl710-QDA2-2p40GE.
        - s62-t34-sut1-cn/p2 - 40GE-port2 xl710-QDA2-2p40GE.
        - s62-t34-sut1-ck/p1 - 100GE-port1 ConnectX5-2p100GE.
        - s62-t34-sut1-ck/p2 - 100GE-port1 ConnectX5-2p100GE.
- SUT [Server-Type-E23]:
    - testbedname: testbed34.
    - hostname: s63-t34-sut2.
    - IPMI IP: 10.30.50.73
    - Host IP: 10.30.51.73
    - portnames:
        - s63-t34-sut2-cn/p1 - 40GE-port1 xl710-QDA2-2p40GE.
        - s63-t34-sut2-cn/p2 - 40GE-port2 xl710-QDA2-2p40GE.
        - s63-t34-sut2-ck/p1 - 100GE-port1 ConnectX5-2p100GE.
        - s63-t34-sut2-ck/p2 - 100GE-port1 ConnectX5-2p100GE.
- TG [Server-Type-F4]:
    - testbedname: testbed34.
    - hostname: s64-t34t36-tg1.
    - IPMI IP: 10.30.50.74
    - Host IP: 10.30.51.74
    - portnames:
        - s64-t34-tg1-c1/p1 - 25GE-port1 xxv710-DA2-2p25GE.
        - s64-t34-tg1-c1/p2 - 25GE-port2 xxv710-DA2-2p25GE.
```

#### 3-Node-Denverton Servers (3n-dnv) PROD

```
- ServerB30 [Server-Type-B10]:
    - testbednames: testbed35.
    - hostname: s30-t35-sut1.
    - IPMI IP: 10.30.55.12
    - Host IP: 10.32.8.12
    - portnames:
        - s30-t35-sut1-p1 - 10GE-port1 x553 copper port.
        - s30-t35-sut1-p2 - 10GE-port2 x553 copper port.
        - s30-t35-sut1-p3 - 10GE-port3 x553 fiber port.
        - s30-t35-sut1-p4 - 10GE-port4 x553 fiber port.
- ServerB31 [Server-Type-B10]:
    - testbednames: testbed35.
    - hostname: s31-t35-sut2.
    - IPMI IP: 10.30.55.13
    - Host IP: 10.32.8.13
    - portnames:
        - s31-t35-sut2-p1 - 10GE-port1 x553 copper port.
        - s31-t35-sut2-p2 - 10GE-port2 x553 copper port.
        - s31-t35-sut2-p3 - 10GE-port3 x553 fiber port.
        - s31-t35-sut2-p4 - 10GE-port4 x553 fiber port.
```

#### 3-Node-Icelake Servers (3n-icx) PROD

```
- ServerF1 [Server-Type-F1]:
    - testbedname: testbed37.
    - hostname: s65-t37-sut1.
    - IPMI IP: 10.30.50.75
    - Host IP: 10.30.51.75
    - portnames:
        - s65-t37-sut1-c2/p1 - 25GE-port1 xxv710-DA2-2p25GE.
        - s65-t37-sut1-c2/p2 - 25GE-port2 xxv710-DA2-2p25GE.
        - s65-t37-sut1-c4/p1 - 25GE-port1 e810-XXVDA4-4p25GE.
        - s65-t37-sut1-c4/p2 - 25GE-port2 e810-XXVDA4-4p25GE.
        - s65-t37-sut1-c4/p3 - 25GE-port3 e810-XXVDA4-4p25GE.
        - s65-t37-sut1-c4/p4 - 25GE-port4 e810-XXVDA4-4p25GE.
        - s65-t37-sut1-c9/p1 - 100GE-port1 e810-2CQDA2-2p100GE.
        - s65-t37-sut1-c9/p2 - 100GE-port2 e810-2CQDA2-2p100GE.
- ServerF1 [Server-Type-F1]:
    - testbedname: testbed37.
    - hostname: s66-t37-sut2.
    - IPMI IP: 10.30.50.76
    - Host IP: 10.30.51.76
    - portnames:
        - s66-t37-sut2-c2/p1 - 25GE-port1 xxv710-DA2-2p25GE.
        - s66-t37-sut2-c2/p2 - 25GE-port2 xxv710-DA2-2p25GE.
        - s66-t37-sut2-c4/p1 - 25GE-port1 e810-XXVDA4-4p25GE.
        - s66-t37-sut2-c4/p2 - 25GE-port2 e810-XXVDA4-4p25GE.
        - s66-t37-sut2-c4/p3 - 25GE-port3 e810-XXVDA4-4p25GE.
        - s66-t37-sut2-c4/p4 - 25GE-port4 e810-XXVDA4-4p25GE.
        - s66-t37-sut2-c9/p1 - 100GE-port1 e810-2CQDA2-2p100GE.
        - s66-t37-sut2-c9/p2 - 100GE-port2 e810-2CQDA2-2p100GE.
- ServerF3 [Server-Type-F3]:
    - testbedname: testbed37.
    - hostname: s67-t37-tg1.
    - IPMI IP: 10.30.50.77
    - Host IP: 10.30.51.77
    - portnames:
        - s67-t37-tg1-c2/p1 - 25GE-port1 xxv710-DA2-2p25GE.
        - s67-t37-tg1-c2/p2 - 25GE-port2 xxv710-DA2-2p25GE.
        - s67-t37-tg1-c4/p1 - 25GE-port1 e810-XXVDA4-4p25GE.
        - s67-t37-tg1-c4/p2 - 25GE-port2 e810-XXVDA4-4p25GE.
        - s67-t37-tg1-c4/p3 - 25GE-port3 e810-XXVDA4-4p25GE.
        - s67-t37-tg1-c4/p4 - 25GE-port4 e810-XXVDA4-4p25GE.
        - s67-t37-tg1-c9/p1 - 100GE-port1 e810-2CQDA2-2p100GE.
        - s67-t37-tg1-c9/p2 - 100GE-port2 e810-2CQDA2-2p100GE.
- ServerF1 [Server-Type-F1]:
    - testbedname: testbed38.
    - hostname: s78-t38-sut1.
    - IPMI IP: 10.30.50.78
    - Host IP: 10.30.51.78
    - portnames:
        - s78-t38-sut1-c2/p1 - 25GE-port1 xxv710-DA2-2p25GE.
        - s78-t38-sut1-c2/p2 - 25GE-port2 xxv710-DA2-2p25GE.
        - s78-t38-sut1-c4/p1 - 25GE-port1 e810-XXVDA4-4p25GE.
        - s78-t38-sut1-c4/p2 - 25GE-port2 e810-XXVDA4-4p25GE.
        - s78-t38-sut1-c4/p3 - 25GE-port3 e810-XXVDA4-4p25GE.
        - s78-t38-sut1-c4/p4 - 25GE-port4 e810-XXVDA4-4p25GE.
        - s78-t38-sut1-c9/p1 - 100GE-port1 e810-2CQDA2-2p100GE.
        - s78-t38-sut1-c9/p2 - 100GE-port2 e810-2CQDA2-2p100GE.
- ServerF1 [Server-Type-F1]:
    - testbedname: testbed38.
    - hostname: s79-t38-sut2.
    - IPMI IP: 10.30.50.79
    - Host IP: 10.30.51.79
    - portnames:
        - s79-t38-sut2-c2/p1 - 25GE-port1 xxv710-DA2-2p25GE.
        - s79-t38-sut2-c2/p2 - 25GE-port2 xxv710-DA2-2p25GE.
        - s79-t38-sut2-c4/p1 - 25GE-port1 e810-XXVDA4-4p25GE.
        - s79-t38-sut2-c4/p2 - 25GE-port2 e810-XXVDA4-4p25GE.
        - s79-t38-sut2-c4/p3 - 25GE-port3 e810-XXVDA4-4p25GE.
        - s79-t38-sut2-c4/p4 - 25GE-port4 e810-XXVDA4-4p25GE.
        - s79-t38-sut2-c9/p1 - 100GE-port1 e810-2CQDA2-2p100GE.
        - s79-t38-sut2-c9/p2 - 100GE-port2 e810-2CQDA2-2p100GE.
- ServerF3 [Server-Type-F3]:
    - testbedname: testbed38.
    - hostname: s80-t38-tg1.
    - IPMI IP: 10.30.50.80
    - Host IP: 10.30.51.80
    - portnames:
        - s80-t38-tg1-c2/p1 - 25GE-port1 xxv710-DA2-2p25GE.
        - s80-t38-tg1-c2/p2 - 25GE-port2 xxv710-DA2-2p25GE.
        - s80-t38-tg1-c4/p1 - 25GE-port1 e810-XXVDA4-4p25GE.
        - s80-t38-tg1-c4/p2 - 25GE-port2 e810-XXVDA4-4p25GE.
        - s80-t38-tg1-c4/p3 - 25GE-port3 e810-XXVDA4-4p25GE.
        - s80-t38-tg1-c4/p4 - 25GE-port4 e810-XXVDA4-4p25GE.
        - s80-t38-tg1-c9/p1 - 100GE-port1 e810-2CQDA2-2p100GE.
        - s80-t38-tg1-c9/p2 - 100GE-port2 e810-2CQDA2-2p100GE.
```

#### 3-Node-SnowRidge Servers (3n-snr) PROD

```
- ServerG1 [Server-Type-G1]:
    - testbedname: testbed39.
    - hostname: s93-t39-sut1.
    - IPMI IP: 10.30.50.93
    - Host IP: 10.30.51.93
    - portnames:
        - s93-t39-sut1-c1/p1 - 100GE-port1 e810-DA2-2p100GE.
        - s93-t39-sut1-c1/p2 - 100GE-port2 e810-DA2-2p100GE.
- ServerG1 [Server-Type-G1]:
    - testbedname: testbed39.
    - hostname: s94-t39-sut2.
    - IPMI IP: 10.30.50.94
    - Host IP: 10.30.51.94
    - portnames:
        - s94-t39-sut2-c1/p1 - 100GE-port1 e810-DA2-2p100GE.
        - s94-t39-sut2-c1/p2 - 100GE-port1 e810-DA2-2p100GE.
- ServerF4 [Server-Type-F4]:
    - testbedname: testbed39.
    - hostname: s89-t39t310-tg1.
    - IPMI IP: 10.30.50.89
    - Host IP: 10.30.51.89
    - portnames:
        - s89-t39t310-tg1-c6/p1 - 100GE-port1 e810-DA2-2p100GE.
        - s89-t39t310-tg1-c6/p2 - 100GE-port1 e810-DA2-2p100GE.
```

### Per Testbed Wiring

#### 1-Node-Skylake Wiring (1n-skx) PROD

```
- testbed11:
    - ring1 10GE-ports x710-4p10GE:
        - s1-t11-sut1-c2/p1 to s1-t11-sut1-c4/p1.
    - ring2 10GE-ports x710-4p10GE:
        - s1-t11-sut1-c2/p2 to s1-t11-sut1-c4/p2.
    - ring3 10GE-ports x710-4p10GE:
        - s1-t11-sut1-c2/p3 to s1-t11-sut1-c4/p3.
    - ring4 10GE-ports x710-4p10GE:
        - s1-t11-sut1-c2/p4 to s1-t11-sut1-c4/p4.
    - ring5 100GE-ports e810-2p100GE:
        - s1-t11-sut1-c5/p1 to s1-t11-sut1-c6/p1.
    - ring6 100GE-ports e810-2p100GE:
        - s1-t11-sut1-c5/p2 to s1-t11-sut1-c6/p2.
- testbed12:
    - ring1 10GE-ports x710-4p10GE:
        - s2-t12-sut1-c2/p1 to s2-t12-sut1-c4/p1.
    - ring2 10GE-ports x710-4p10GE:
        - s2-t12-sut1-c2/p2 to s2-t12-sut1-c4/p2.
    - ring3 10GE-ports x710-4p10GE:
        - s2-t12-sut1-c2/p3 to s2-t12-sut1-c4/p3.
    - ring4 10GE-ports x710-4p10GE:
        - s2-t12-sut1-c2/p4 to s2-t12-sut1-c4/p4.
    - ring5 100GE-ports e810-2p100GE:
        - s2-t12-sut1-c5/p1 to s2-t12-sut1-c6/p1.
    - ring6 100GE-ports e810-2p100GE:
        - s2-t12-sut1-c5/p2 to s2-t12-sut1-c6/p2.
```

#### 1-Node-ThunderX2 Wiring (1n-tx2) PROD

```
- testbed13:
    - ring1 40GE-ports XL710-QDA2-2p40GE on SUTs:
        - s55-t13-sut1-c4/p1 - s55-t13-sut1-c14/p1.
    - ring2 40GE-ports XL710-QDA2-2p40GE on SUTs:
        - s55-t13-sut1-c4/p2 - s55-t13-sut1-c14/p2.
    - ring3 10/25GE-ports ConnectX5-2p10/25GE on SUTs:
        - s55-t13-sut1-c8/p1 - s55-t13-sut1-c26/p1.
    - ring4 10/25GE-ports ConnectX5-2p10/25GE on SUTs:
        - s55-t13-sut1-c8/p2 - s55-t13-sut1-c26/p2.

- testbed14:
    - ring1 40GE-ports XL710-QDA2-2p40GE on SUTs:
        - s56-t14-sut1-c4/p1 - s56-t14-sut1-c14/p1.
    - ring2 40GE-ports XL710-QDA2-2p40GE on SUTs:
        - s56-t14-sut1-c4/p2 - s56-t14-sut1-c14/p2.
    - ring3 10/25GE-ports ConnectX5-2p10/25GE on SUTs:
        - s56-t14-sut1-c8/p1 - s56-t14-sut1-c26/p1.
    - ring4 10/25GE-ports ConnectX5-2p10/25GE on SUTs:
        - s56-t14-sut1-c8/p2 - s56-t14-sut1-c26/p2.
```

#### 2-Node-Skylake Wiring (2n-skx) PROD

```
- testbed21:
    - ring1 10GE-ports x710-4p10GE on SUT:
        - s4-t21-tg1-c2/p1 to s3-t21-sut1-c2/p1.
        - s3-t21-sut1-c2/p2 to s4-t21-tg1-c2/p2.
    - ring2 10GE-ports x710-4p10GE on SUT:
        - s4-t21-tg1-c2/p3 to s3-t21-sut1-c2/p3.
        - s3-t21-sut1-c2/p4 to s4-t21-tg1-c2/p4.
    - ring3 25GE-ports xxv710-DA2-2p25GE on SUT
        - s4-t21-tg1-c4/p1 to s3-t21-sut1-c4/p1.
        - s3-t21-sut1-c4/p2 to s4-t21-tg1-c4/p2.
    - ring4 10GE-ports x710-4p10GE loopbacks on TG for self-tests:
        - s4-t21-tg1-c10/p1 to s4-t21-tg1-c10/p2.
        - s4-t21-tg1-c10/p3 to s4-t21-tg1-c10/p4.
- testbed22:
    - ring1 10GE-ports x710-4p10GE on SUT:
        - s6-t22-tg1-c2/p1 to s5-t22-sut1-c2/p1.
        - s5-t22-sut1-c2/p2 to s6-t22-tg1-c2/p2.
    - ring2 10GE-ports x710-4p10GE on SUT:
        - s6-t22-tg1-c2/p3 to s5-t22-sut1-c2/p3.
        - s5-t22-sut1-c2/p4 to s6-t22-tg1-c2/p4.
    - ring3 25GE-ports xxv710-DA2-2p25GE on SUT
        - s6-t22-tg1-c4/p1 to s5-t22-sut1-c4/p1.
        - s5-t22-sut1-c4/p2 to s6-t22-tg1-c4/p2.
    - ring4 10GE-ports x710-4p10GE loopbacks on TG for self-tests:
        - s6-t22-tg1-c10/p1 to s6-t22-tg1-c10/p2.
        - s6-t22-tg1-c10/p3 to s6-t22-tg1-c10/p4.
- testbed23:
    - ring1 10GE-ports x710-4p10GE on SUT:
        - s8-t23-tg1-c2/p1 to s7-t23-sut1-c2/p1.
        - s7-t23-sut1-c2/p2 to s8-t23-tg1-c2/p2.
    - ring2 10GE-ports x710-4p10GE on SUT:
        - s8-t23-tg1-c2/p3 to s7-t23-sut1-c2/p3.
        - s7-t23-sut1-c2/p4 to s8-t23-tg1-c2/p4.
    - ring3 25GE-ports xxv710-DA2-2p25GE on SUT
        - s8-t23-tg1-c4/p1 to s7-t23-sut1-c4/p1.
        - s7-t23-sut1-c4/p2 to s8-t23-tg1-c4/p2.
    - ring4 10GE-ports x710-4p10GE loopbacks on TG for self-tests:
        - s8-t23-tg1-c10/p1 to s8-t23-tg1-c10/p2.
        - s8-t23-tg1-c10/p3 to s8-t23-tg1-c10/p4.
- testbed24:
    - ring1 10GE-ports x710-4p10GE on SUT:
        - s10-t24-tg1-c2/p1 to s9-t24-sut1-c2/p1.
        - s9-t24-sut1-c2/p2 to s10-t24-tg1-c2/p2.
    - ring2 10GE-ports x710-4p10GE on SUT:
        - s10-t24-tg1-c2/p3 to s9-t24-sut1-c2/p3.
        - s9-t24-sut1-c2/p4 to s10-t24-tg1-c2/p4.
    - ring3 25GE-ports xxv710-DA2-2p25GE on SUT
        - s10-t24-tg1-c4/p1 to s9-t24-sut1-c4/p1.
        - s9-t24-sut1-c4/p2 to s10-t24-tg1-c4/p2.
    - ring4 10GE-ports x710-4p10GE loopbacks on TG for self-tests:
        - s10-t24-tg1-c10/p1 to s10-t24-tg1-c10/p2.
        - s10-t24-tg1-c10/p3 to s10-t24-tg1-c10/p4.
```

#### 2-Node-Denverton Wiring (2n-dnv) PROD

```
- testbed26:
    - ring1 10GE-ports x553 copper port on SUT:
        - s28-t26t35-tg1-c4/p1 to s29-t26-sut1-p1.
        - s28-t26t35-tg1-c9/p1 to s29-t26-sut1-p2.
    - ring2 10GE-ports x553 fiber port on SUT:
        - s28-t26t35-tg1-c2/p1 to s29-t26-sut1-p3.
        - s28-t26t35-tg1-c2/p2 to s29-t26-sut1-p4.
```

#### 2-Node-IxiaPS1L47 Wiring (2n-ps1) VERIFY

```
- testbed25:
    - link1 10GE-port x710-4p10GE on SUT:
        - t25-tg1-p1 to t25-sut1-c2/p1.
    - link2 10GE-port x710-4p10GE on SUT:
        - t25-tg1-p2 to t25-sut1-c2/p2.
    - link3 10GE-port x710-4p10GE on SUT:
        - t25-tg1-p3 to t25-sut1-c2/p3.
    - link4 10GE-port x710-4p10GE on SUT:
        - t25-tg1-p4 to t25-sut1-c2/p4.
```

#### 2-Node-Cascadelake Wiring (2n-clx) PROD

```
- testbed27:
    - ring1 10GE-ports x710-4p10GE on SUT:
        - s34-t27-tg1-c2/p1 to s33-t27-sut1-c2/p1.
        - s33-t27-sut1-c2/p2 to s34-t27-tg1-c2/p2.
    - ring2 10GE-ports x710-4p10GE on SUT:
        - s34-t27-tg1-c2/p3 to s33-t27-sut1-c2/p3.
        - s33-t27-sut1-c2/p4 to s34-t27-tg1-c2/p4.
    - ring3 25GE-ports xxv710-DA2-2p25GE on SUT
        - s34-t27-tg1-c4/p1 to s33-t27-sut1-c4/p1.
        - s33-t27-sut1-c4/p2 to s34-t27-tg1-c4/p2.
    - ring4 100GE-ports ConnectX5-2p100GE on SUT:
        - s34-t27-tg1-c9/p1 to s33-t27-sut1-c9/p1.
        - s33-t27-sut1-c9/p2 to s34-t27-tg1-c9/p2.
    - ring5 100GE-ports e810-2p100GE on SUT 100GE-ports ConnectX5-2p100GE on TG:
        - s34-t27-tg1-c6/p1 to s33-t27-sut1-c6/p1.
        - s33-t27-sut1-c6/p2 to s34-t27-tg1-c6/p2.
    - ring6 100GE-ports e810-2p100GE on TG:
        - s34-t27-tg1-c8/p1 to s34-t27-tg1-c8/p2.
        - s34-t27-tg1-c8/p2 to s34-t27-tg1-c8/p1.
- testbed28:
    - ring1 10GE-ports x710-4p10GE on SUT:
        - s36-t28-tg1-c2/p1 to s35-t28-sut1-c2/p1.
        - s35-t28-sut1-c2/p2 to s36-t28-tg1-c2/p2.
    - ring2 10GE-ports x710-4p10GE on SUT:
        - s36-t28-tg1-c2/p3 to s35-t28-sut1-c2/p3.
        - s35-t28-sut1-c2/p4 to s36-t28-tg1-c2/p4.
    - ring3 25GE-ports xxv710-DA2-2p25GE on SUT
        - s36-t28-tg1-c4/p1 to s35-t28-sut1-c4/p1.
        - s35-t28-sut1-c4/p2 to s36-t28-tg1-c4/p2.
    - ring4 100GE-ports ConnectX5-2p100GE on SUT:
        - s36-t28-tg1-c9/p1 to s35-t28-sut1-c9/p1.
        - s35-t28-sut1-c9/p2 to s36-t28-tg1-c9/p2.
    - ring5 100GE-ports e810-2p100GE on SUT 100GE-ports ConnectX5-2p100GE on TG:
        - s36-t28-tg1-c6/p1 to s35-t28-sut1-c6/p1.
        - s35-t28-sut1-c6/p2 to s36-t28-tg1-c6/p2.
    - ring6 100GE-ports e810-2p100GE on TG:
        - s36-t28-tg1-c8/p1 to s36-t28-tg1-c8/p2.
        - s36-t28-tg1-c8/p2 to s36-t28-tg1-c8/p1.
- testbed29:
    - ring1 10GE-ports x710-4p10GE on SUT:
        - s38-t29-tg1-c2/p1 to s37-t29-sut1-c2/p1.
        - s37-t29-sut1-c2/p2 to s38-t29-tg1-c2/p2.
    - ring2 10GE-ports x710-4p10GE on SUT:
        - s38-t29-tg1-c2/p3 to s37-t29-sut1-c2/p3.
        - s37-t29-sut1-c2/p4 to s38-t29-tg1-c2/p4.
    - ring3 25GE-ports xxv710-DA2-2p25GE on SUT
        - s38-t29-tg1-c4/p1 to s37-t29-sut1-c4/p1.
        - s37-t29-sut1-c4/p2 to s38-t29-tg1-c4/p2.
    - ring4 100GE-ports ConnectX5-2p100GE on SUT:
        - s38-t29-tg1-c9/p1 to s37-t29-sut1-c9/p1.
        - s37-t29-sut1-c9/p2 to s38-t29-tg1-c9/p2.
    - ring5 100GE-ports e810-2p100GE on SUT 100GE-ports ConnectX5-2p100GE on TG:
        - s38-t29-tg1-c6/p1 to s37-t29-sut1-c6/p1.
        - s37-t29-sut1-c6/p2 to s38-t29-tg1-c6/p2.
```

#### 2-Node-Zen2 Wiring (2n-zn2) PROD

```
- testbed210:
    - ring1 10GE-ports x710-4p10GE on SUT:
        - s61-t210-tg1-c2/p1 to s60-t210-sut1-c1/p1.
        - s60-t210-sut1-c1/p2 to s61-t210-tg1-c2/p2.
    - ring2 10GE-ports x710-4p10GE on SUT:
        - s61-t210-tg1-c2/p3 to s60-t210-sut1-c1/p3.
        - s60-t210-sut1-c1/p4 to s61-t210-tg1-c2/p4.
    - ring3 25GE-ports xxv710-DA2-2p25GE on SUT
        - s61-t210-tg1-c3/p1 to s60-t210-sut1-c2/p1.
        - s60-t210-sut1-c2/p2 to s61-t210-tg1-c3/p2.
    - ring4 100GE-ports ConnectX5-2p100GE on SUT:
        - s61-t210-tg1-c1/p1 to s60-t210-sut1-c3/p1.
        - s60-t210-sut1-c3/p2 to s61-t210-tg1-c1/p2.
```

#### 2-Node-ThunderX2 Wiring (2n-tx2) PROD

```
- testbed211:
    - ring1 10GE-ports x520-2p10GE on SUTs:
        - s27-t211-sut1-c18/p1 - s19-t33t211-tg1-c8/p1.
        - s27-t211-sut1-c18/p2 - s19-t33t211-tg1-c8/p2.
```

#### 2-Node-Icelake Wiring (2n-icx) PROD

```
- testbed212:
    - ring1 25GE-ports xxv710-DA2-2p25GE on SUT
        - s72-t212-tg1-c2/p1 to s71-t212-sut1-c2/p1.
        - s71-t212-sut1-c2/p2 to s72-t212-tg1-c2/p2.
    - ring2 25GE-ports e810-XXVDA4-2p25GE on SUT:
        - s72-t212-tg1-c4/p1 to s71-t212-sut1-c4/p1.
        - s71-t212-sut1-c4/p2 to s72-t212-tg1-c4/p2.
        - s72-t212-tg1-c4/p3 to s71-t212-sut1-c4/p3.
        - s71-t212-sut1-c4/p4 to s72-t212-tg1-c4/p4.
    - ring3 100GE-ports e810-2CQDA2-2p100GE on SUT:
        - s72-t212-tg1-c9/p1 to s71-t212-sut1-c9/p1.
        - s71-t212-sut1-c9/p2 to s72-t212-tg1-c9/p2.
    - ring4 100GE-ports e810-2CQDA2-2p100GE on SUT:
        - s72-t212-tg1-c6/p1 to s72-t212-tg1-c6/p2.
        - s72-t212-tg1-c6/p2 to s72-t212-tg1-c6/p1.
- testbed213:
    - ring1 25GE-ports xxv710-DA2-2p25GE on SUT
        - s84-t213-tg1-c2/p1 to s83-t213-sut1-c2/p1.
        - s83-t213-sut1-c2/p2 to s84-t213-tg1-c2/p2.
    - ring2 25GE-ports e810-XXVDA4-2p25GE on SUT:
        - s84-t213-tg1-c4/p1 to s83-t213-sut1-c4/p1.
        - s83-t213-sut1-c4/p2 to s84-t213-tg1-c4/p2.
        - s84-t213-tg1-c4/p3 to s83-t213-sut1-c4/p3.
        - s83-t213-sut1-c4/p4 to s84-t213-tg1-c4/p4.
    - ring3 100GE-ports e810-2CQDA2-2p100GE on SUT:
        - s84-t213-tg1-c9/p1 to s83-t213-sut1-c9/p1.
        - s83-t213-sut1-c9/p2 to s84-t213-tg1-c9/p2.
    - ring4 100GE-ports e810-2CQDA2-2p100GE on SUT:
        - s84-t213-tg1-c6/p1 to s84-t213-tg1-c6/p2.
        - s84-t213-tg1-c6/p2 to s84-t213-tg1-c6/p1.
- testbed214:
    - ring1 25GE-ports xxv710-DA2-2p25GE on SUT
        - s86-t214-tg1-c2/p1 to s85-t214-sut1-c2/p1.
        - s85-t214-sut1-c2/p2 to s86-t214-tg1-c2/p2.
    - ring2 25GE-ports e810-XXVDA4-2p25GE on SUT:
        - s86-t214-tg1-c4/p1 to s85-t214-sut1-c4/p1.
        - s85-t214-sut1-c4/p2 to s86-t214-tg1-c4/p2.
        - s86-t214-tg1-c4/p3 to s85-t214-sut1-c4/p3.
        - s85-t214-sut1-c4/p4 to s86-t214-tg1-c4/p4.
    - ring3 100GE-ports e810-2CQDA2-2p100GE on SUT:
        - s86-t214-tg1-c9/p1 to s85-t214-sut1-c9/p1.
        - s85-t214-sut1-c9/p2 to s86-t214-tg1-c9/p2.
    - ring4 100GE-ports e810-2CQDA2-2p100GE on SUT:
        - s86-t214-tg1-c6/p1 to s86-t214-tg1-c6/p2.
        - s86-t214-tg1-c6/p2 to s86-t214-tg1-c6/p1.
- testbed215:
    - ring1 25GE-ports xxv710-DA2-2p25GE on SUT
        - s88-t215-tg1-c2/p1 to s87-t215-sut1-c2/p1.
        - s87-t215-sut1-c2/p2 to s88-t215-tg1-c2/p2.
    - ring2 25GE-ports e810-XXVDA4-2p25GE on SUT:
        - s88-t215-tg1-c4/p1 to s87-t215-sut1-c4/p1.
        - s87-t215-sut1-c4/p2 to s88-t215-tg1-c4/p2.
        - s88-t215-tg1-c4/p3 to s87-t215-sut1-c4/p3.
        - s87-t215-sut1-c4/p4 to s88-t215-tg1-c4/p4.
    - ring3 100GE-ports e810-2CQDA2-2p100GE on SUT:
        - s88-t215-tg1-c9/p1 to s87-t215-sut1-c9/p1.
        - s87-t215-sut1-c9/p2 to s88-t215-tg1-c9/p2.
    - ring4 100GE-ports e810-2CQDA2-2p100GE on SUT:
        - s88-t215-tg1-c6/p1 to s88-t215-tg1-c6/p2.
        - s88-t215-tg1-c6/p2 to s88-t215-tg1-c6/p1.
```

#### 3-Node-Skylake Wiring (3n-skx) PROD

```
- testbed31:
    - ring1 10GE-ports x710-4p10GE on SUTs:
        - s13-t31-tg1-c2/p1 to s11-t31-sut1-c2/p1.
        - s11-t31-sut1-c2/p2 to s12-t31-sut2-c2/p2.
        - s12-t31-sut2-c2/p1 to s13-t31-tg1-c2/p2.
    - ring2 10GE-ports x710-4p10GE on SUT:
        - s13-t31-tg1-c2/p3 to s11-t31-sut1-c2/p3.
        - s11-t31-sut1-c2/p4 to s12-t31-sut2-c2/p4.
        - s12-t31-sut2-c2/p3 to s13-t31-tg1-c2/p4.
    - ring3 25GE-ports xxv710-DA2-2p25GE on SUT
        - s13-t31-tg1-c4/p1 to s11-t31-sut1-c4/p1.
        - s11-t31-sut1-c4/p2 to s12-t31-sut2-c4/p2.
        - s12-t31-sut2-c4/p1 to s13-t31-tg1-c4/p2.
    - FUTURE ring4 100GE-ports ConnectX5-2p100GE on SUT:
        - s13-t31-tg1-c9/p1 to s11-t31-sut1-c9/p1.
        - s11-t31-sut1-c9/p2 to s12-t31-sut2-c9/p2.
        - s12-t31-sut2-c9/p1 to s13-t31-tg1-c9/p2.
    - ring5 10GE-ports x710-4p10GE loopbacks on TG for self-tests:
        - s13-t31-tg1-c10/p1 to s13-t31-tg1-c10/p2.
        - s13-t31-tg1-c10/p3 to s13-t31-tg1-c10/p4.
- testbed32:
    - ring1 10GE-ports x710-4p10GE on SUTs:
        - s16-t32-tg1-c2/p1 to s14-t32-sut1-c2/p1.
        - s14-t32-sut1-c2/p2 to s15-t32-sut2-c2/p2.
        - s15-t32-sut2-c2/p1 to s16-t32-tg1-c2/p2.
    - ring2 10GE-ports x710-4p10GE on SUT:
        - s16-t32-tg1-c2/p3 to s14-t32-sut1-c2/p3.
        - s14-t32-sut1-c2/p4 to s15-t32-sut2-c2/p4.
        - s15-t32-sut2-c2/p3 to s16-t32-tg1-c2/p4.
    - ring3 25GE-ports xxv710-DA2-2p25GE on SUT
        - s16-t32-tg1-c4/p1 to s14-t32-sut1-c4/p1.
        - s14-t32-sut1-c4/p2 to s15-t32-sut2-c4/p2.
        - s15-t32-sut2-c4/p1 to s16-t32-tg1-c4/p2.
    - FUTURE ring4 100GE-ports ConnectX5-2p100GE on SUT:
        - s16-t32-tg1-c9/p1 to s14-t32-sut1-c9/p1.
        - s14-t32-sut1-c9/p2 to s15-t32-sut2-c9/p2.
        - s15-t32-sut2-c9/p1 to s16-t32-tg1-c9/p2.
    - ring5 10GE-ports x710-4p10GE loopbacks on TG for self-tests:
        - s16-t32-tg1-c10/p1 to s16-t32-tg1-c10/p2.
        - s16-t32-tg1-c10/p3 to s16-t32-tg1-c10/p4.
```

#### 3-Node-Rangeley Wiring (3n-rng) VERIFY

```
To be completed.
```

#### 3-Node-Taishan Wiring (3n-tsh) PROD

```
- testbed33:
    - ring1 10GE-ports x520-2p10GE on SUTs:
        - s19-t33t211-tg1-c2/p2 - s17-t33-sut1-c6/p2.
        - s17-t33-sut1-c6/p1 - s18-t33-sut2-c6/p2.
        - s18-t33-sut2-c6/p1 - s19-t33t211-tg1-c2/p1.
    - ring2 25GE-ports cx4-2p25GE on SUTs:
        - s19-t33t211-tg1-c4/p2 - s17-t33-sut1-c4/p2.
        - s17-t33-sut1-c4/p1 - s18-t33-sut2-c4/p2.
        - s18-t33-sut2-c4/p1 - s19-t33t211-tg1-c4/p1.
```

#### 3-Node-Altra Wiring (3n-alt) PROD

```
- testbed34:
    - ring1 40GE-ports xl710-QDA2-2p40GE on SUTs:
        - s64-t34-tg1-cn/p2 - s62-t34-sut1-cn/p2.
        - s62-t34-sut1-cn/p1 - s63-t34-sut2-cn/p2.
        - s63-t34-sut2-cn/p1 - s64-t34-tg1-cn/p1.
    - ring2 100GE-ports ConnectX5-2p100GE on SUTs:
        - s64-t34-tg1-ck/p2 - s62-t34-sut1-ck/p2.
        - s62-t34-sut1-ck/p1 - s63-t34-sut2-ckp2.
        - s63-t34-sut2-ck/p1 - s64-t34-tg1-ck/p1.
```

#### 3-Node-Denverton Wiring (3n-dnv) PROD

```
- testbed35:
    - ring1 10GE-ports x553 copper port on SUTs:
        - s28-t26t35-tg1-c8/p1 to s30-t35-sut1-p2.
        - s30-t35-sut1-p1 to s31-t35-sut2-p1.
        - s28-t26t35-tg1-c10/p1 to s31-t35-sut2-p2.
    - ring2 10GE-ports x553 fiber port on SUTs:
        - s28-t26t35-tg1-c6/p1 to s30-t35-sut1-p4.
        - s30-t35-sut1-p3 to s31-t35-sut2-p3.
        - s28-t26t35-tg1-c6/p2 to s31-t35-sut2-p4.
```

#### 3-Node-Icelake Wiring (3n-icx) PROD

```
- testbed37:
    - ring1 25GE-ports xxv710-DA2-2p25GE on SUTs:
        - s67-t37-tg1-c2/p1 to s65-t37-sut1-c2/p1.
        - s65-t37-sut1-c2/p2 to s66-t37-sut2-c2/p2.
        - s66-t37-sut2-c2/p1 to s67-t37-tg1-c2/p2.
    - ring2 25GE-ports e810-XXVDA4-4p25GE on SUT:
        - s67-t37-tg1-c4/p1 to s65-t37-sut1-c4/p1.
        - s65-t37-sut1-c4/p2 to s66-t37-sut2-c4/p2.
        - s66-t37-sut2-c4/p1 to s67-t37-tg1-c4/p2.
        - s67-t37-tg1-c4/p3 to s65-t37-sut1-c4/p3.
        - s65-t37-sut1-c4/p4 to s66-t37-sut2-c4/p4.
        - s66-t37-sut2-c4/p3 to s67-t37-tg1-c4/p4.
    - ring3 100GE-ports e810-2CQDA2-2p100GE on SUT
        - s67-t37-tg1-c9/p1 to s65-t37-sut1-c9/p1.
        - s65-t37-sut1-c9/p2 to s66-t37-sut2-c9/p2.
        - s66-t37-sut2-c9/p1 to s67-t37-tg1-c9/p2.
- testbed38:
    - ring1 25GE-ports xxv710-DA2-2p25GE on SUTs:
        - s80-t38-tg1-c2/p1 to s78-t38-sut1-c2/p1.
        - s78-t38-sut1-c2/p2 to s79-t38-sut2-c2/p2.
        - s79-t38-sut2-c2/p1 to s80-t38-tg1-c2/p2.
    - ring2 25GE-ports e810-XXVDA4-4p25GE on SUT:
        - s80-t38-tg1-c4/p1 to s78-t38-sut1-c4/p1.
        - s78-t38-sut1-c4/p2 to s79-t38-sut2-c4/p2.
        - s79-t38-sut2-c4/p1 to s80-t38-tg1-c4/p2.
        - s80-t38-tg1-c4/p3 to s78-t38-sut1-c4/p3.
        - s78-t38-sut1-c4/p4 to s79-t38-sut2-c4/p4.
        - s79-t38-sut2-c4/p3 to s80-t38-tg1-c4/p4.
    - ring3 100GE-ports e810-2CQDA2-2p100GE on SUT
        - s80-t38-tg1-c9/p1 to s78-t38-sut1-c9/p1.
        - s78-t38-sut1-c9/p2 to s79-t38-sut2-c9/p2.
        - s79-t38-sut2-c9/p1 to s80-t38-tg1-c9/p2.
```

#### 3-Node-SnowRidge Wiring (3n-snr) PROD

```
- testbed39:
    - ring1 100GE-ports e810-DA2-2p100GE on SUTs and TG:
        - s89-t39t310-tg1-c6/p1 to s93-t39-sut1-c1/p1.
        - s93-t39-sut1-c1/p2 to s94-t39-sut2-c1/p2.
        - s94-t39-sut2-c1/p1 to s89-t39t310-tg1-c6/p2.
```

## Inventory

### Appliances

```
1. Ixia PerfectStorm One Appliance
    - 1 * PS10GE4NG
        - Chassis: PS10GE4NG.
        - Motherboard: SuperMicro X11DPG-QT.
        - Processors: Quad-Core, Intel Processor.
        - HW accelerators: FPGA offload.
        - RAM Memory: 64GB.
        - Disks: 1 * 1 TB, Enterprise Class, High MTBF.
        - Physical Interfaces: 4 * 10GE SFP+.
        - Operating System: Native IxOS.
```

### Arm Servers

```
1. Arm Cortex A-72 servers
    - 2 * ThunderX2 (VPP Device)
        - Chassis: GIGABYTE Rack Mount
        - Processors: 2* ThunderX2 CN9980 ~ 32* ThunderX2
        - RAM Memory: 16* 16GB DIMM
        - Disks: 2* 480GB 6G SATA SSD SAMSUNG MZ7LH480
    - 1 * ThunderX2 (Performance)
        - Chassis: GIGABYTE Rack Mount
        - Processors: 2* ThunderX2 CN9975 ~ 28* ThunderX2.
        - RAM Memory: 4* 32GB RDIMM
        - Disks: 1* 480GB SSD Micron, 1* 1000GB HDD Seagate_25
    - 2 * Huawei TaiShan 2280.
        - Chassis: Huawei TaiShan 2280.
        - Processors: 2* hip07-d05 ~ 32* Arm Cortex-A72.
        - RAM Memory: 8* 16GB DDR4-2400MT/s.
        - Disks: 1* 4TB SATA HDD.
    - 2 * Ampere Altra
        - Chassis: TBD
        - Processors: TBD
        - RAM Memory: TBD
        - Disks: TBD
```

### Xeon and Atom Servers

```
1. Intel Xeon servers:
    - 20 * SuperMicro SYS-7049GP-TRT with Xeon Skylake processors.
        - Chassis: SuperMicro SYS-7049GP-TRT.
        - Motherboard: SuperMicro X11DPG-QT.
        - Processors: 2* Intel Platinum 8180 2.5 GHz.
        - RAM Memory: 16* 16GB DDR4-2666MHz.
        - Disks: 2* 1.6TB 6G SATA SSD.
2. Intel Atom servers with Rangely processors.
    - 3 * Netgate XG-2758-1u
        - Chassis: Netgate XG-2758-1u
        - Processors: 1* Rangely (Atom) C2758 2.4 GHz
        - RAM Memory: 16GB ECC
        - Disks: 150 GB
```

### Network Interface Cards

```
1. 10GE NICs
    - 14 * Intel® Ethernet Converged Network Adapter X710-DA4
    - 6 * Intel® Ethernet Converged Network Adapter X710-DA2
    - 6 * Intel® Ethernet Converged Network Adapter X520-DA2
2. 25GE NICs
    - 12 * Intel® Ethernet Network Adapter XXV710-DA2
3. 40GE NICs
    - 2 * Intel® Ethernet Converged Network Adapter XL710-QDA2
4. 100GE NICs
    - 4 * mcx556a-edat NICs (not on site yet, in transit)
```

### Pluggables and Cables

Pluggables:

```
1. 10GE SFP+
    - 16 * Intel E10GSFPSR Ethernet SFP+ SR Optics
    - 80 * 10G SR optic (generic, "Intel" compatible branded)
2. 25GE SFP28
    - None
3. 40GE QSFP+
    - None
4. 100GE
    - 8 * mcp1600-c002 qsfp28 pluggables and cables (not on site yet, in transit)
```

Standalone cables:

```
1. 10GE
    - None
2. 25GE
    - None
3. 40GE QSFP+
    - 20 * Intel XLDACBL5 40G QSFP+ Passive DAC Cable
4. 100GE
    - None
```

### Other Parts

None.
