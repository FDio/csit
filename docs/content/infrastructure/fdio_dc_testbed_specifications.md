---
bookToc: true
title: "FD.io DC Testbed Specifications"
weight: 2
---

# FD.io DC Testbed Specifications

## Purpose

This note includes specification of the physical testbed infrastructure
hosted by LFN FD.io CSIT project.

## Server Management

### Addressing

Each server has a LOM (Lights-Out-Management e.g. SM IPMI) and a
Management port, which are connected to two different VLANs.

#### LOM (IPMI) VLAN

   - Subnet: 10.30.50.0/24
   - Gateway: 10.30.50.1
   - Broadcast: 10.30.50.255
   - DNS1: 199.204.44.24
   - DNS2: 199.204.47.54

#### Management VLAN
   - Subnet: 10.30.51.0/24
   - Gateway: 10.30.51.1
   - Broadcast: 10.30.51.255
   - DNS1: 199.204.44.24
   - DNS2: 199.204.47.54

To access these hosts, VPN connection is required.

## Testbeds Overview

### Summary List

```
 #. Type                 Purpose  SUT   TG    #TB  #SUT #TG  #skx #ps1 #rng #tx2 #tsh #alt #clx #zn2 #icx #snr #spr
 1. 1-Node-Skylake         nomad  skx   na    5    5    0    5    0    0    0    0    0    0    0    0    0    0
 2. 1-Node-Cascadelake     nomad  clx   na    1    1    0    0    0    0    0    0    0    1    0    0    0    0
 3. 1-Node-AmpereAltra     nomad  alt   na    2    2    0    0    0    0    0    0    2    0    0    0    0    0
 4. 2-Node-IxiaPS1L47      tcp    skx   ps1   1    1    1    1    1    0    0    0    0    0    0    0    0    0
 5. 2-Node-Cascadelake     perf   clx   clx   3    3    3    0    0    0    0    0    0    6    0    0    0    0
 6. 2-Node-ThunderX2       perf   tx2   skx   1    1    .5   .5   0    0    1    0    0    0    0    0    0    0
 7. 2-Node-Icelake         perf   icx   icx   4    4    4    0    0    0    0    0    0    0    0    8    0    0
 8. 3-Node-Rangeley        perf   rng   skx   1    3    1    0    0    2    0    0    0    0    0    0    0    0
 9. 3-Node-Taishan         perf   tsh   skx   1    2    .5   .5   0    0    0    2    0    0    0    0    0    0
10. 3-Node-Altra           perf   alt   icx   1    2    1    0    0    0    0    0    2    0    0    1    0    0
11. 2-Node-Zen2            perf   zn2   zn2   1    1    1    0    0    0    0    0    0    0    2    0    0    0
12. 3-Node-Icelake         perf   icx   icx   2    4    2    0    0    0    0    0    0    0    0    6    0    0
13. 3-Node-SnowRidge       perf   snr   icx   1    2    .5   0    0    0    0    0    0    0    0    .5   2    0
13. 2-Node-SapphireRapids  perf   spr   spr   4    4    4    0    0    0    0    0    0    0    0    0    0    8
                                     Totals: 28   35  18.5   7    1    2    1    2    4    7    2   15.5  2    8
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
TG (Server-Type-E32) connected in a 3-node circular topology
([Server Types](#server-types)).
Used for FD.io performance tests.

### 3-Node-Icelake Xeon Intel (3n-icx)

Each 3-Node-Icelake testbed includes two SUTs (Server-Type-F3) and one
TG (Server-Type-F3) connected in a 3-node circular topology
([Server Types](#server-types)).
Used for FD.io performance tests.

### 3-Node-SnowRidge Atom Intel (3n-snr)

Each 3-Node-SnowRidge testbed includes two SUTs (Server-Type-G1) and one
TG (Server-Type-F5) connected in a 3-node circular topology
([Server Types](#server-types)).
Used for FD.io performance tests.

### 2-Node-SapphireRapids Xeon Intel (2n-spr)

Each 2-Node-SapphireRapids testbed includes one SUT (Server-Type-H5) and
one TG (Server-Type-H6) connected in a 2-node or 3-node circular topology
([Server Types](#server-types)).
Used for FD.io performance tests.


## Tesdtbed Naming Convention

Following naming convention is used within this page to specify physical
connectivity and wiring across defined CSIT testbeds:

- **testbedname**: testbedN.
- **hostname**:
    - traffic-generator: tN-tgW.
    - system-under-testX: tN-sutX.
- **portnames**:
    - tN-tgW-cY/pZ.
    - tN-sutX-cY/pZ.
- **where**:
    - N - testbed number.
    - tgW - server acts as traffic-generator with W index.
    - sutX - server acts as system-under-test with X index.
    - Y - PCIe slot number denoting a NIC card number within the host.
    - Z - port number on the NIC card.

## Server Types

FD.io CSIT lab contains following server types:

1. **Server-Type-B2**: Purpose - Skylake Xeon hosts for FD.io builds and data processing.
    - Quantity: 2
    - Physical connectivity:
        - IPMI and host management ports.
    - Main HW configuration:
        - Chassis: SuperMicro SYS-7049GP-TRT.
        - Motherboard: SuperMicro X11DPG-QT.
        - Processors: 2* Intel Platinum 8180 2.5 GHz.
        - RAM Memory: 16* 16GB DDR4-2666MHz.
        - Disks: 2* 1.6TB 6G SATA SSD.
    - NICs configuration:
        - Numa0: (x16, x16, x16 PCIe3.0 lanes)
            - PCIe Slot2 18:00.xx: empty.
            - PCIe Slot4 3b:00.xx: empty.
            - PCIe Slot9 5e:00.xx: empty.
        - Numa1: (x16, x16, x16 PCIe3.0 lanes)
            - PCIe Slot6 86:00.xx: empty.
            - PCIe Slot8 af:00.xx: empty.
            - PCIe Slot10 d8:00.xx: empty.

2. **Server-Type-B6**: Purpose - Skylake Xeon SUT for FD.io VPP_Device functional tests.
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

3. **Server-Type-B7**: Purpose - Ixia PerfectStorm One Appliance TG for FD.io TCP/IP performance tests.
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

4. **Server-Type-B8**: Purpose - Skylake Xeon SUT for TCP/IP host stack tests.
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
5. Server-Type-C1: Purpose - Cascadelake Xeon SUT for FD.io VPP_Device functional tests.
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

6. **Server-Type-C2**: Purpose - Cascadelake Xeon SUT for FD.io performance testing.
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

7. **Server-Type-C3**: Purpose - Cascadelake Xeon TG for FD.io performance testing.
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

8. **Server-Type-C4**: Purpose - Cascadelake Xeon Backend hosts for FD.io builds and data processing.
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

9. **Server-Type-D1**: Purpose - Zen2 EPYC SUT for FD.io performance testing.
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

10. **Server-Type-D2**: Purpose - Zen2 EPYC TG for FD.io performance testing.
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

11. **Server-Type-E11**: Purpose - ThunderX2 Arm Marvell SUT for FD.io VPP_Device functional tests.
    - Quantity: 2.
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

12. **Server-Type-E21**: Purpose - TaiShan Arm Huawei SUT for FD.io performance testing.
    - Quantity: 2.
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

13. **Server-Type-E22**: Purpose - ThunderX2 Arm Marvell SUT for FD.io performance testing.
    - Quantity: 1.
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
            - no cards
        - Numa1:
            - PCIe Slot18 91:00.xx: XL710-QDA2-2p40GE Intel.

14. **Server-Type-E23**: Purpose - Altra Arm Ampere SUT for FD.io performance testing.
    - Quantity: 2.
    - Physical connectivity:
        - IPMI and host management ports.
        - NIC ports connected into 3-node topologies.
    - Main HW configuration:
        - Chassis: WIWYNN Mt.Jade Server System B81.030Z1.0007 2U
        - Motherboard: Mt.Jade Motherboard
        - Processors: 2* Ampere(R) Altra(R) Q80-30 Processor (Neoverse N1)
        - Processor Signature: Implementor 0x41, Variant 0x3, Architecture 15, Part 0xd0c, Revision 1
        - RAM Memory: 16* 8GB DDR4-3200MT/s
        - Disks: 2* 960GB SSD Samsung M.2 NVMe PM983
    - NICs configuration:
        - Numa0: (x16, x16 PCIe4.0 lanes)
            - PCIe Slot1 0004:04:00.x: xl710-QDA2-2p40GE Intel.
            - PCIe Slot8 0001:00:00.x: ConnectX6-2p100GE Mellanox.
        - Numa1:
            - no cards.

15. **Server-Type-E24**: Purpose - Altra Arm Ampere for FD.io build.
    - Quantity: 2.
    - Physical connectivity:
        - IPMI and host management ports.
    - Main HW configuration:
        - Chassis: Gigabyte R152-P30-00 1U
        - Motherboard: MP32-AR1-00
        - Processors: 1* Ampere(R) Altra(R) Q80-30 Processor (Neoverse N1)
        - Processor Signature: Implementor 0x0a, Variant 0x1, Architecture 6, Part 0x000, Revision 1
        - RAM Memory: 12* 16GB DDR4-3200MT/s
        - Disks: 1* 960GB SSD Samsung M.2 NVMe PM983

16. **Server-Type-E31**: Purpose - Skylake Xeon Shared TG for FD.io performance testing.
    - Quantity: 1.
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

17. **Server-Type-E32**: Purpose - Icelake Xeon Shared TG for FD.io performance testing.
    - Quantity: 1.
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
        - Numa0: (x16, x16, x16 PCIe4.0 lanes)
            - PCIe Slot2 4b:00.xx: xxv710-DA2-2p25GE Intel.
            - PCIe Slot4 31:00.xx: xl710-QDA2-2p40GE Intel.
            - PCIe Slot9 ff:00.xx: empty.
        - Numa1: (x16, x16, x16 PCIe4.0 lanes)
            - PCIe Slot6 ca:00.xx: e810-XXVDA4-4p25GE Intel.
            - PCIe Slot8 b1:00.xx: e810-2CQDA2-2p100GE Intel.
            - PCIe Slot10 ff:00.xx: empty.

18. **Server-Type-F1**: Purpose - Icelake Xeon SUT for FD.io performance testing.
    - Quantity: 4.
    - Physical connectivity:
        - IPMI and host management ports.
        - NIC ports connected into 2-node topology.
    - Main HW configuration:
        - Chassis: SuperMicro SYS-740GP-TNRT.
        - Motherboard: Super X12DPG-QT6.
        - Processors: 2* Intel Platinum 8358 2.6 GHz.
        - RAM Memory: 16* 16GB DDR4-3200.
        - Disks: 2* 960GB SATA SSD.
    - NICs configuration:
        - Numa0: (x16, x16, x16 PCIe4.0 lanes)
            - PCIe Slot2 18:00.xx: xxv710-DA2-2p25GE Intel.
            - PCIe Slot4 3b:00.xx: e810-XXVDA4-4p25GE Intel.
            - PCIe Slot9 5e:00.xx: e810-2CQDA2-2p100GE Intel.
        - Numa1: (x16, x16, x16 PCIe4.0 lanes)
            - PCIe Slot6 86:00.xx: empty.
            - PCIe Slot8 af:00.xx: ConnectX7-2p200GE Mellanox.
            - PCIe Slot10 d8:00.xx: empty.

19. **Server-Type-F2**: Purpose - Icelake Xeon TG for FD.io performance testing.
    - Quantity: 4.
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
        - Numa0: (x16, x16, x16 PCIe4.0 lanes)
            - PCIe Slot2 18:00.xx: xxv710-DA2-2p25GE Intel.
            - PCIe Slot4 3b:00.xx: e810-XXVDA4-4p25GE Intel.
            - PCIe Slot9 5e:00.xx: e810-2CQDA2-2p100GE Intel.
        - Numa1: (x16, x16, x16 PCIe4.0 lanes)
            - PCIe Slot6 86:00.xx: e810-2CQDA2-2p100GE Intel.
            - PCIe Slot8 af:00.xx: ConnectX7-2p200GE Mellanox.
            - PCIe Slot10 d8:00.xx: empty.

20. **Server-Type-F3**: Purpose - Icelake Xeon TG or SUT for FD.io performance testing.
    - Quantity: 6.
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
        - Numa0: (x16, x16, x16 PCIe4.0 lanes)
            - PCIe Slot2 18:00.xx: xxv710-DA2-2p25GE Intel.
            - PCIe Slot4 3b:00.xx: e810-XXVDA4-4p25GE Intel.
            - PCIe Slot9 5e:00.xx: e810-2CQDA2-2p100GE Intel.
        - Numa1: (x16, x16, x16 PCIe4.0 lanes)
            - PCIe Slot6 86:00.xx: ConnectX6-2p100GE Mellanox.
            - PCIe Slot8 af:00.xx: empty.
            - PCIe Slot10 d8:00.xx: empty.

21. **Server-Type-F4**: Purpose - Icelake Xeon TG for FD.io performance testing.
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
        - Numa0: (x16, x16, x16 PCIe4.0 lanes)
            - PCIe Slot2 18:00.xx: xxv710-DA2-2p25GE Intel.
            - PCIe Slot4 3b:00.xx: e810-XXVDA4-4p25GE Intel.
            - PCIe Slot9 5e:00.xx: e810-2CQDA2-2p100GE Intel.
        - Numa1: (x16, x16, x16 PCIe4.0 lanes)
            - PCIe Slot6 86:00.xx: ConnectX6-2p100GE Mellanox.
            - PCIe Slot8 af:00.xx: empty.
            - PCIe Slot10 d8:00.xx: empty.

22. **Server-Type-F5**: Purpose - Icelake Xeon Shared TG for FD.io performance testing.
    - Quantity: 2.
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
        - Numa0: (x16, x16, x16 PCIe4.0 lanes)
            - PCIe Slot2 4b:00.xx: xxv710-DA2-2p25GE Intel.
            - PCIe Slot4 31:00.xx: empty.
            - PCIe Slot9 ff:00.xx: empty.
        - Numa1: (x16, x16, x16 PCIe4.0 lanes)
            - PCIe Slot6 ca:00.xx: e810-XXVDA4-4p25GE Intel.
            - PCIe Slot8 b1:00.xx: e810-2CQDA2-2p100GE Intel.
            - PCIe Slot10 ff:00.xx: empty.

23. **Server-Type-G1**: Purpose - SnowRidge Atom SUT for FD.io performance testing.
    - Quantity: 2
    - Physical connectivity:
        - IPMI and host management ports.
        - NIC ports connected into 3-node testbed topology.
    - Main HW configuration:
        - Chassis: Intel JACOBSVILLE SDP.
        - Motherboard: Intel JACOBSVILLE E63448-400.
        - Processors: 1* Intel Atom P5362B 2.2 GHz.
        - RAM Memory: 2* 16GB DDR4-2933.
        - Disks: ?* ? SATA SSD.
    - NICs configuration:
        - Numa0: (x16, PCIe3.0 lane)
            - PCIe BuiltIn ec:00.xx: e810-XXVDA4-4p25GE Intel.

24. **Server-Type-H1**: Purpose - SapphireRapids Xeon SUT for FD.io full system performance testing.
    - Quantity: 1.
    - Physical connectivity:
        - IPMI and host management ports.
        - NIC ports connected into 3-numa-node testbed topologies.
    - Main HW configuration:
        - Chassis: SuperMicro SYS-741GE-TNRT.
        - Motherboard: Super X13DEG-QT-P.
        - Processors: 2* Intel Platinum 8462Y+ 32 core 2.8 GHz 300W TDP.
        - RAM Memory: 16* 32GB DDR5-4800.
        - Disks: 2* 960GB SATA SSD.
    - NICs configuration:
        - Numa0: (x16, x16, x16 PCIe5.0 lanes)
            - PCIe Slot2 18:00.xx: MCX713106AS-VEAT ConnectX7-2p200GE Nvidia.
            - PCIe Slot4 3b:00.xx: MCX713106AS-VEAT ConnectX7-2p200GE Nvidia.
            - PCIe Slot10 5e:00.xx: MCX713106AS-VEAT ConnectX7-2p200GE Nvidia.
        - Numa1: (x16, x16, x16 PCIe5.0 lanes)
            - PCIe Slot7 86:00.xx: MCX713106AS-VEAT ConnectX7-2p200GE Nvidia.
            - PCIe Slot9 af:00.xx: MCX713106AS-VEAT ConnectX7-2p200GE Nvidia.
            - PCIe Slot11 d8:00.xx: MCX713106AS-VEAT ConnectX7-2p200GE Nvidia.

25. **Server-Type-H2**: Purpose - SapphireRapids Xeon TG for FD.io full system performance testing.
    - Quantity: 1.
    - Physical connectivity:
        - IPMI and host management ports.
        - NIC ports connected into 3-numa-node testbed topologies.
    - Main HW configuration:
        - Chassis: SuperMicro SYS-741GE-TNRT.
        - Motherboard: Super X13DEG-QT-P.
        - Processors: 2* Intel Platinum 8462Y+ 32 core 2.8 GHz 300W TDP.
        - RAM Memory: 16* 32GB DDR5-4800.
        - Disks: 2* 960GB SATA SSD.
    - NICs configuration:
        - Numa0: (x16, x16, x16 PCIe5.0 lanes)
            - PCIe Slot2 18:00.xx: MCX713106AS-VEAT ConnectX7-2p200GE Nvidia.
            - PCIe Slot4 3b:00.xx: MCX713106AS-VEAT ConnectX7-2p200GE Nvidia.
            - PCIe Slot10 5e:00.xx: MCX713106AS-VEAT ConnectX7-2p200GE Nvidia.
        - Numa1: (x16, x16, x16 PCIe5.0 lanes)
            - PCIe Slot7 86:00.xx: MCX713106AS-VEAT ConnectX7-2p200GE Nvidia.
            - PCIe Slot9 af:00.xx: MCX713106AS-VEAT ConnectX7-2p200GE Nvidia.
            - PCIe Slot11 d8:00.xx: empty.

26. **Server-Type-H3**: Purpose - SapphireRapids Xeon SUT for FD.io performance testing.
    - Quantity: 1.
    - Physical connectivity:
        - IPMI and host management ports.
        - NIC ports connected into 3-numa-node testbed topologies.
    - Main HW configuration:
        - Chassis: SuperMicro SYS-741GE-TNRT.
        - Motherboard: Super X13DEG-QT-P.
        - Processors: 2* Intel Platinum 8462Y+ 32 core 2.8 GHz 300W TDP.
        - RAM Memory: 16* 32GB DDR5-4800.
        - Disks: 2* 960GB SATA SSD.
    - NICs configuration:
        - Numa0: (x16, x16, x16 PCIe5.0 lanes)
            - PCIe Slot2 18:00.xx: e810-2CQDA2-2p100GE Intel.
            - PCIe Slot4 3b:00.xx: e810-XXVDA4-4p25GE Intel.
            - PCIe Slot10 5e:00.xx: empty.
        - Numa1: (x16, x16, x16 PCIe5.0 lanes)
            - PCIe Slot7 86:00.xx: e810-2CQDA2-2p100GE Intel.
            - PCIe Slot9 af:00.xx: e810-XXVDA4-4p25GE Intel.
            - PCIe Slot11 d8:00.xx: empty.

27. **Server-Type-H4**: Purpose - SapphireRapids Xeon TG for FD.io performance testing.
    - Quantity: 1.
    - Physical connectivity:
        - IPMI and host management ports.
        - NIC ports connected into 3-numa-node testbed topologies.
    - Main HW configuration:
        - Chassis: SuperMicro SYS-741GE-TNRT.
        - Motherboard: Super X13DEG-QT-P.
        - Processors: 2* Intel Platinum 8462Y+ 32 core 2.8 GHz 300W TDP.
        - RAM Memory: 16* 32GB DDR5-4800.
        - Disks: 2* 960GB SATA SSD.
    - NICs configuration:
        - Numa0: (x16, x16, x16 PCIe5.0 lanes)
            - PCIe Slot2 18:00.xx: e810-2CQDA2-2p100GE Intel.
            - PCIe Slot4 3b:00.xx: e810-XXVDA4-4p25GE Intel.
            - PCIe Slot10 5e:00.xx: empty.
        - Numa1: (x16, x16, x16 PCIe5.0 lanes)
            - PCIe Slot7 86:00.xx: empty.
            - PCIe Slot9 af:00.xx: empty.
            - PCIe Slot11 d8:00.xx: empty.

28. **Server-Type-H5**: Purpose - SapphireRapids Xeon SUT for FD.io performance testing.
    - Quantity: 2.
    - Physical connectivity:
        - IPMI and host management ports.
        - NIC ports connected into 2-node testbed topologies.
    - Main HW configuration:
        - Chassis: SuperMicro SYS-741GE-TNRT.
        - Motherboard: Super X13DEG-QT-P.
        - Processors: 2* Intel Platinum 8462Y+ 32 core 2.8 GHz 300W TDP.
        - RAM Memory: 16* 32GB DDR5-4800.
        - Disks: 2* 960GB SATA SSD.
    - NICs configuration:
        - Numa0: (x16, x16, x16 PCIe5.0 lanes)
            - PCIe Slot2 18:00.xx: MCX713106AS-VEAT ConnectX7-2p200GE Nvidia.
            - PCIe Slot4 3b:00.xx: e810-2CQDA2-2p100GE Intel.
            - PCIe Slot10 5e:00.xx: e810-XXVDA4-4p25GE Intel.
        - Numa1: (x16, x16, x16 PCIe5.0 lanes)
            - PCIe Slot7 86:00.xx: empty.
            - PCIe Slot9 af:00.xx: empty.
            - PCIe Slot11 d8:00.xx: empty.

29. **Server-Type-H6**: Purpose - SapphireRapids Xeon TG for FD.io performance testing.
    - Quantity: 2.
    - Physical connectivity:
        - IPMI and host management ports.
        - NIC ports connected into 2-node testbed topologies plus loopbacks in Numa1 for TG self-test.
    - Main HW configuration:
        - Chassis: SuperMicro SYS-741GE-TNRT.
        - Motherboard: Super X13DEG-QT-P.
        - Processors: 2* Intel Platinum 8462Y+ 32 core 2.8 GHz 300W TDP.
        - RAM Memory: 16* 32GB DDR5-4800.
        - Disks: 2* 960GB SATA SSD.
    - NICs configuration:
        - Numa0: (x16, x16, x16 PCIe5.0 lanes)
            - PCIe Slot2 18:00.xx: MCX713106AS-VEAT ConnectX7-2p200GE Nvidia.
            - PCIe Slot4 3b:00.xx: e810-2CQDA2-2p100GE Intel.
            - PCIe Slot10 5e:00.xx: e810-XXVDA4-4p25GE Intel.
        - Numa1: (x16, x16, x16 PCIe5.0 lanes)
            - PCIe Slot7 86:00.xx: MCX713106AS-VEAT ConnectX7-2p200GE Nvidia.
            - PCIe Slot9 af:00.xx: e810-2CQDA2-2p100GE Intel.
            - PCIe Slot11 d8:00.xx: empty.

## Testbeds Configuration

### 1-Node-Skylake (1n-skx)

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

### 1-Node-ThunderX2 (1n-tx2)

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

### 1-Node-Cascadelake (1n-clx)

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

### 2-Node-IxiaPS1L47 (2n-ps1)

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

### 2-Node-Cascadelake (2n-clx)

{{< figure src="/cdocs/testbed-2n-clx.svg" >}}

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

### 2-Node-Zen2 (2n-zn2)

{{< figure src="/cdocs/testbed-2n-zn2.svg" >}}

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

### 2-Node-ThunderX2 (2x-tx2)

{{< figure src="/cdocs/testbed-2n-tx2.svg" >}}

```
- SUT [Server-Type-E22]:
    - testbedname: testbed211.
    - hostname: s27-t211-sut1.
    - IPMI IP: 10.30.50.69
    - Host IP: 10.30.51.69
    - portnames:
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

### 2-Node-Icelake (2n-icx)

{{< figure src="/cdocs/testbed-2n-icx.svg" >}}

```
- SUT [Server-Type-F1]:
    - testbedname: testbed212.
    - hostname: s71-t212-sut1.
    - IPMI IP: 10.30.50.81
    - Host IP: 10.30.51.81
    - portnames:
        - s71-t212-sut1-c2/p1 - 25GE-port1 xxv710-DA2-2p25GE.
        - s71-t212-sut1-c2/p2 - 25GE-port2 xxv710-DA2-2p25GE.
        - s71-t212-sut1-c4/p1 - 25GE-port1 e810-XXVDA4-4p25GE.
        - s71-t212-sut1-c4/p2 - 25GE-port2 e810-XXVDA4-4p25GE.
        - s71-t212-sut1-c4/p3 - 25GE-port3 e810-XXVDA4-4p25GE.
        - s71-t212-sut1-c4/p4 - 25GE-port4 e810-XXVDA4-4p25GE.
        - s71-t212-sut1-c9/p1 - 100GE-port1 e810-2CQDA2-2p100GE.
        - s71-t212-sut1-c9/p2 - 100GE-port2 e810-2CQDA2-2p100GE.
        - s71-t212-sut1-c8/p1 - 200GE-port1 ConnectX7-2p200GE.
        - s71-t212-sut1-c8/p2 - 200GE-port2 ConnectX7-2p200GE.
- TG [Server-Type-F2]:
    - testbedname: testbed212.
    - hostname: s72-t212-tg1.
    - IPMI IP: 10.30.50.82
    - Host IP: 10.30.51.82
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
        - s72-t212-tg1-c8/p1 - 200GE-port1 ConnectX7-2p200GE.
        - s72-t212-tg1-c8/p2 - 200GE-port2 ConnectX7-2p200GE.
- SUT [Server-Type-F1]:
    - testbedname: testbed213.
    - hostname: s83-t213-sut1.
    - IPMI IP: 10.30.50.83
    - Host IP: 10.30.51.83
    - portnames:
        - s83-t213-sut1-c2/p1 - 25GE-port1 xxv710-DA2-2p25GE.
        - s83-t213-sut1-c2/p2 - 25GE-port2 xxv710-DA2-2p25GE.
        - s83-t213-sut1-c4/p1 - 25GE-port1 e810-XXVDA4-4p25GE.
        - s83-t213-sut1-c4/p2 - 25GE-port2 e810-XXVDA4-4p25GE.
        - s83-t213-sut1-c4/p3 - 25GE-port3 e810-XXVDA4-4p25GE.
        - s83-t213-sut1-c4/p4 - 25GE-port4 e810-XXVDA4-4p25GE.
        - s83-t213-sut1-c9/p1 - 100GE-port1 e810-2CQDA2-2p100GE.
        - s83-t213-sut1-c9/p2 - 100GE-port2 e810-2CQDA2-2p100GE.
        - s83-t213-sut1-c8/p1 - 200GE-port1 ConnectX7-2p200GE.
        - s83-t213-sut1-c8/p2 - 200GE-port2 ConnectX7-2p200GE.
- TG [Server-Type-F2]:
    - testbedname: testbed213.
    - hostname: s84-t213-tg1.
    - IPMI IP: 10.30.50.84
    - Host IP: 10.30.51.84
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
        - s84-t213-tg1-c8/p1 - 200GE-port1 ConnectX7-2p200GE.
        - s84-t213-tg1-c8/p2 - 200GE-port2 ConnectX7-2p200GE.
- SUT [Server-Type-F1]:
    - testbedname: testbed214.
    - hostname: s85-t214-sut1.
    - IPMI IP: 10.30.50.85
    - Host IP: 10.30.51.85
    - portnames:
        - s85-t214-sut1-c2/p1 - 25GE-port1 xxv710-DA2-2p25GE.
        - s85-t214-sut1-c2/p2 - 25GE-port2 xxv710-DA2-2p25GE.
        - s85-t214-sut1-c4/p1 - 25GE-port1 e810-XXVDA4-4p25GE.
        - s85-t214-sut1-c4/p2 - 25GE-port2 e810-XXVDA4-4p25GE.
        - s85-t214-sut1-c4/p3 - 25GE-port3 e810-XXVDA4-4p25GE.
        - s85-t214-sut1-c4/p4 - 25GE-port4 e810-XXVDA4-4p25GE.
        - s85-t214-sut1-c9/p1 - 100GE-port1 e810-2CQDA2-2p100GE.
        - s85-t214-sut1-c9/p2 - 100GE-port2 e810-2CQDA2-2p100GE.
        - s85-t214-sut1-c8/p1 - 200GE-port1 ConnectX7-2p200GE.
        - s85-t214-sut1-c8/p2 - 200GE-port2 ConnectX7-2p200GE.
- TG [Server-Type-F2]:
    - testbedname: testbed214.
    - hostname: s86-t214-tg1.
    - IPMI IP: 10.30.50.86
    - Host IP: 10.30.51.86
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
        - s86-t214-tg1-c8/p1 - 200GE-port1 ConnectX7-2p200GE.
        - s86-t214-tg1-c8/p2 - 200GE-port2 ConnectX7-2p200GE.
- SUT [Server-Type-F1]:
    - testbedname: testbed215.
    - hostname: s87-t215-sut1.
    - IPMI IP: 10.30.50.87
    - Host IP: 10.30.51.87
    - portnames:
        - s87-t215-sut1-c2/p1 - 25GE-port1 xxv710-DA2-2p25GE.
        - s87-t215-sut1-c2/p2 - 25GE-port2 xxv710-DA2-2p25GE.
        - s87-t215-sut1-c4/p1 - 25GE-port1 e810-XXVDA4-4p25GE.
        - s87-t215-sut1-c4/p2 - 25GE-port2 e810-XXVDA4-4p25GE.
        - s87-t215-sut1-c4/p3 - 25GE-port3 e810-XXVDA4-4p25GE.
        - s87-t215-sut1-c4/p4 - 25GE-port4 e810-XXVDA4-4p25GE.
        - s87-t215-sut1-c9/p1 - 100GE-port1 e810-2CQDA2-2p100GE.
        - s87-t215-sut1-c9/p2 - 100GE-port2 e810-2CQDA2-2p100GE.
        - s87-t215-sut1-c8/p1 - 200GE-port1 ConnectX7-2p200GE.
        - s87-t215-sut1-c8/p2 - 200GE-port2 ConnectX7-2p200GE.
- TG [Server-Type-F2]:
    - testbedname: testbed215.
    - hostname: s88-t215-tg1.
    - IPMI IP: 10.30.50.88
    - Host IP: 10.30.51.88
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
        - s88-t215-tg1-c8/p1 - 200GE-port1 ConnectX7-2p200GE.
        - s88-t215-tg1-c8/p2 - 200GE-port2 ConnectX7-2p200GE.
```

### 3-Node-Rangeley (3n-rng)

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

### 3-Node-Taishan (3n-tsh)

{{< figure src="/cdocs/testbed-3n-tsh.svg" >}}

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

### 3-Node-Altra (3n-alt)

{{< figure src="/cdocs/testbed-3n-alt.svg" >}}

```
- SUT [Server-Type-E23]:
    - testbedname: testbed34.
    - hostname: s62-t34-sut1.
    - IPMI IP: 10.30.50.72
    - Host IP: 10.30.51.72
    - portnames:
        - s62-t34-sut1-c1/p1 - 40GE-port1 xl710-QDA2-2p40GE.
        - s62-t34-sut1-c1/p2 - 40GE-port2 xl710-QDA2-2p40GE.
        - s62-t34-sut1-c8/p1 - 100GE-port1 ConnectX6-2p100GE Mellanox.
        - s62-t34-sut1-c8/p2 - 100GE-port1 ConnectX6-2p100GE Mellanox.
- SUT [Server-Type-E23]:
    - testbedname: testbed34.
    - hostname: s63-t34-sut2.
    - IPMI IP: 10.30.50.73
    - Host IP: 10.30.51.73
    - portnames:
        - s63-t34-sut2-c1/p1 - 40GE-port1 xl710-QDA2-2p40GE.
        - s63-t34-sut2-c1/p2 - 40GE-port2 xl710-QDA2-2p40GE.
        - s63-t34-sut2-c8/p1 - 100GE-port1 ConnectX6-2p100GE Mellanox.
        - s63-t34-sut2-c8/p2 - 100GE-port1 ConnectX6-2p100GE Mellanox.
- TG [Server-Type-E32]:
    - testbedname: testbed34.
    - hostname: s64-t34-tg1.
    - IPMI IP: 10.30.50.74
    - Host IP: 10.30.51.74
    - portnames:
        - s64-t34-tg1-c2/p1 - 25GE-port1 xxv710-DA2-2p25GE.
        - s64-t34-tg1-c2/p2 - 25GE-port2 xxv710-DA2-2p25GE.
        - s64-t34-tg1-c4/p1 - 40GE-port1 xl710-QDA2-2p40GE.
        - s64-t34-tg1-c4/p2 - 40GE-port2 xl710-QDA2-2p40GE.
        - s64-t34-tg1-c6/p1 - 25GE-port1 e810-XXVDA4-4p25GE.
        - s64-t34-tg1-c6/p2 - 25GE-port2 e810-XXVDA4-4p25GE.
        - s64-t34-tg1-c6/p3 - 25GE-port3 e810-XXVDA4-4p25GE.
        - s64-t34-tg1-c6/p4 - 25GE-port4 e810-XXVDA4-4p25GE.
        - s64-t34-tg1-c8/p1 - 100GE-port1 e810-2CQDA2-2p100GE.
        - s64-t34-tg1-c8/p2 - 100GE-port2 e810-2CQDA2-2p100GE.
```

### 3-Node-Icelake (3n-icx)

{{< figure src="/cdocs/testbed-3n-icx.svg" >}}

```
- SUT1 [Server-Type-F3]:
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
        - s65-t37-sut1-c6/p1 - 100GE-port1 ConnectX6-2p100GE.
        - s65-t37-sut1-c6/p2 - 100GE-port1 ConnectX6-2p100GE.
- SUT2 [Server-Type-F3]:
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
        - s65-t37-sut1-c6/p1 - 100GE-port1 ConnectX6-2p100GE.
        - s65-t37-sut1-c6/p2 - 100GE-port1 ConnectX6-2p100GE.
- TG [Server-Type-F3]:
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
        - s67-t37-tg1-c6/p1 - 100GE-port1 ConnectX6-2p100GE.
        - s67-t37-tg1-c6/p2 - 100GE-port1 ConnectX6-2p100GE.
- SUT1 [Server-Type-F3]:
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
        - s78-t38-sut1-c6/p1 - 100GE-port1 ConnectX6-2p100GE.
        - s78-t38-sut1-c6/p2 - 100GE-port1 ConnectX6-2p100GE.
- SUT2 [Server-Type-F3]:
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
        - s79-t38-sut2-c6/p1 - 100GE-port1 ConnectX6-2p100GE.
        - s79-t38-sut2-c6/p2 - 100GE-port1 ConnectX6-2p100GE.
- TG [Server-Type-F3]:
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
        - s80-t38-tg1-c6/p1 - 100GE-port1 ConnectX6-2p100GE.
        - s80-t38-tg1-c6/p2 - 100GE-port1 ConnectX6-2p100GE.
```

### 3-Node-SnowRidge (3n-snr)

{{< figure src="/cdocs/testbed-3n-snr.svg" >}}

```
- ServerG1 [Server-Type-G1]:
    - testbedname: testbed39.
    - hostname: s93-t39-sut1.
    - IPMI IP: 10.30.50.93
    - Host IP: 10.30.51.93
    - portnames:
        - s93-t39-sut1-c1/p1 - 25GE-port1 e810-XXVDA4-4p25GE.
        - s93-t39-sut1-c1/p2 - 25GE-port2 e810-XXVDA4-4p25GE.
        - s93-t39-sut1-c1/p2 - 25GE-port3 e810-XXVDA4-4p25GE.
        - s93-t39-sut1-c1/p2 - 25GE-port4 e810-XXVDA4-4p25GE.
- ServerG1 [Server-Type-G1]:
    - testbedname: testbed39.
    - hostname: s94-t39-sut2.
    - IPMI IP: 10.30.50.94
    - Host IP: 10.30.51.94
    - portnames:
        - s94-t39-sut2-c1/p1 - 25GE-port1 e810-XXVDA4-4p25GE.
        - s94-t39-sut2-c1/p2 - 25GE-port2 e810-XXVDA4-4p25GE.
        - s94-t39-sut2-c1/p3 - 25GE-port3 e810-XXVDA4-4p25GE.
        - s94-t39-sut2-c1/p4 - 25GE-port4 e810-XXVDA4-4p25GE.
- ServerF4 [Server-Type-F5]:
    - testbedname: testbed39.
    - hostname: s89-t39t310-tg1.
    - IPMI IP: 10.30.50.89
    - Host IP: 10.30.51.89
    - portnames:
        - s89-t39t310-tg1-c6/p1 - 25GE-port1 e810-XXVDA4-4p25GE.
        - s89-t39t310-tg1-c6/p2 - 25GE-port2 e810-XXVDA4-4p25GE.
        - s89-t39t310-tg1-c6/p3 - 25GE-port3 e810-XXVDA4-4p25GE.
        - s89-t39t310-tg1-c6/p4 - 25GE-port4 e810-XXVDA4-4p25GE.
```

### 2-Node-SapphireRapids (2n-spr)

{{< figure src="/cdocs/testbed-2n-spr.svg" >}}

```
- SUT [Server-Type-H1]:
    - testbedname: testbed21.
    - hostname: s52-t21-sut1.
    - IPMI IP: 10.30.50.52
    - Host IP: 10.30.51.52
    - portnames:
        - s52-t21-sut1-c10/p1 - 200GE-port1 ConnectX7-2p200GE.
        - s52-t21-sut1-c10/p2 - 200GE-port2 ConnectX7-2p200GE.
        - s52-t21-sut1-c4/p1 - 200GE-port1 ConnectX7-2p200GE.
        - s52-t21-sut1-c4/p2 - 200GE-port2 ConnectX7-2p200GE.
        - s52-t21-sut1-c2/p1 - 200GE-port1 ConnectX7-2p200GE.
        - s52-t21-sut1-c2/p2 - 200GE-port2 ConnectX7-2p200GE.
        - s52-t21-sut1-c9/p1 - 200GE-port1 ConnectX7-2p200GE.
        - s52-t21-sut1-c9/p2 - 200GE-port2 ConnectX7-2p200GE.
        - s52-t21-sut1-c7/p1 - 200GE-port1 ConnectX7-2p200GE.
        - s52-t21-sut1-c7/p2 - 200GE-port2 ConnectX7-2p200GE.
- TG [Server-Type-H2]:
    - testbedname: testbed21.
    - hostname: s53-t21-tg1.
    - IPMI IP: 10.30.50.53
    - Host IP: 10.30.51.53
    - portnames:
        - s53-t21-tg1-c10/p1 - 200GE-port1 ConnectX7-2p200GE.
        - s53-t21-tg1-c10/p2 - 200GE-port2 ConnectX7-2p200GE.
        - s53-t21-tg1-c4/p1 - 200GE-port1 ConnectX7-2p200GE.
        - s53-t21-tg1-c4/p2 - 200GE-port2 ConnectX7-2p200GE.
        - s53-t21-tg1-c2/p1 - 200GE-port1 ConnectX7-2p200GE.
        - s53-t21-tg1-c2/p2 - 200GE-port2 ConnectX7-2p200GE.
        - s53-t21-tg1-c9/p1 - 200GE-port1 ConnectX7-2p200GE.
        - s53-t21-tg1-c9/p2 - 200GE-port2 ConnectX7-2p200GE.
        - s53-t21-tg1-c7/p1 - 200GE-port1 ConnectX7-2p200GE.
        - s53-t21-tg1-c7/p2 - 200GE-port2 ConnectX7-2p200GE.
- SUT [Server-Type-H3]:
    - testbedname: testbed22.
    - hostname: s54-t22-sut1.
    - IPMI IP: 10.30.50.54
    - Host IP: 10.30.51.54
    - portnames:
        - s54-t22-sut1-c2/p1 - 100GE-port1 e810-2CQDA2-2p100GE.
        - s54-t22-sut1-c2/p2 - 100GE-port2 e810-2CQDA2-2p100GE.
        - s54-t22-sut1-c4/p1 - 25GE-port1 e810-XXVDA4-4p25GE.
        - s54-t22-sut1-c4/p2 - 25GE-port2 e810-XXVDA4-4p25GE.
        - s54-t22-sut1-c4/p3 - 25GE-port3 e810-XXVDA4-4p25GE.
        - s54-t22-sut1-c4/p4 - 25GE-port4 e810-XXVDA4-4p25GE.
        - s54-t22-sut1-c7/p1 - 100GE-port1 e810-2CQDA2-2p100GE.
        - s54-t22-sut1-c7/p2 - 100GE-port2 e810-2CQDA2-2p100GE.
        - s54-t22-sut1-c9/p1 - 25GE-port1 e810-XXVDA4-4p25GE.
        - s54-t22-sut1-c9/p2 - 25GE-port2 e810-XXVDA4-4p25GE.
        - s54-t22-sut1-c9/p3 - 25GE-port3 e810-XXVDA4-4p25GE.
        - s54-t22-sut1-c9/p4 - 25GE-port4 e810-XXVDA4-4p25GE.
- TG [Server-Type-H4]:
    - testbedname: testbed22.
    - hostname: s55-t22-tg1.
    - IPMI IP: 10.30.50.55
    - Host IP: 10.30.51.55
    - portnames:
        - s55-t22-tg1-c2/p1 - 100GE-port1 e810-2CQDA2-2p100GE.
        - s55-t22-tg1-c2/p2 - 100GE-port2 e810-2CQDA2-2p100GE.
        - s55-t22-tg1-c4/p1 - 25GE-port1 e810-XXVDA4-4p25GE.
        - s55-t22-tg1-c4/p2 - 25GE-port2 e810-XXVDA4-4p25GE.
        - s55-t22-tg1-c4/p3 - 25GE-port3 e810-XXVDA4-4p25GE.
        - s55-t22-tg1-c4/p4 - 25GE-port4 e810-XXVDA4-4p25GE.
- SUT [Server-Type-H5]:
    - testbedname: testbed23.
    - hostname: s56-t23-sut1.
    - IPMI IP: 10.30.50.56
    - Host IP: 10.30.51.56
    - portnames:
        - s56-t23-sut1-c2/p1 - 200GE-port1 ConnectX7-2p200GE.
        - s56-t23-sut1-c2/p2 - 200GE-port2 ConnectX7-2p200GE.
        - s56-t23-sut1-c4/p1 - 100GE-port1 e810-2CQDA2-2p100GE.
        - s56-t23-sut1-c4/p2 - 100GE-port2 e810-2CQDA2-2p100GE.
        - s56-t23-sut1-c10/p1 - 25GE-port1 e810-XXVDA4-4p25GE.
        - s56-t23-sut1-c10/p2 - 25GE-port2 e810-XXVDA4-4p25GE.
        - s56-t23-sut1-c10/p3 - 25GE-port3 e810-XXVDA4-4p25GE.
        - s56-t23-sut1-c10/p4 - 25GE-port4 e810-XXVDA4-4p25GE.
- TG [Server-Type-H6]:
    - testbedname: testbed23.
    - hostname: s57-t23-tg1.
    - IPMI IP: 10.30.50.57
    - Host IP: 10.30.51.57
    - portnames:
        - s57-t23-tg1-c2/p1 - 200GE-port1 ConnectX7-2p200GE.
        - s57-t23-tg1-c2/p2 - 200GE-port2 ConnectX7-2p200GE.
        - s57-t23-tg1-c4/p1 - 100GE-port1 e810-2CQDA2-2p100GE.
        - s57-t23-tg1-c4/p2 - 100GE-port2 e810-2CQDA2-2p100GE.
        - s57-t23-tg1-c10/p1 - 25GE-port1 e810-XXVDA4-4p25GE.
        - s57-t23-tg1-c10/p2 - 25GE-port2 e810-XXVDA4-4p25GE.
        - s57-t23-tg1-c10/p3 - 25GE-port3 e810-XXVDA4-4p25GE.
        - s57-t23-tg1-c10/p4 - 25GE-port4 e810-XXVDA4-4p25GE.
        - s57-t23-tg1-c7/p1 - 200GE-port1 ConnectX7-2p200GE.
        - s57-t23-tg1-c7/p2 - 200GE-port2 ConnectX7-2p200GE.
        - s57-t23-tg1-c9/p1 - 100GE-port1 e810-2CQDA2-2p100GE.
        - s57-t23-tg1-c9/p2 - 100GE-port2 e810-2CQDA2-2p100GE.
- SUT [Server-Type-H5]:
    - testbedname: testbed24.
    - hostname: s58-t24-sut1.
    - IPMI IP: 10.30.50.58
    - Host IP: 10.30.51.58
    - portnames:
        - s58-t24-sut1-c2/p1 - 200GE-port1 ConnectX7-2p200GE.
        - s58-t24-sut1-c2/p2 - 200GE-port2 ConnectX7-2p200GE.
        - s58-t24-sut1-c4/p1 - 100GE-port1 e810-2CQDA2-2p100GE.
        - s58-t24-sut1-c4/p2 - 100GE-port2 e810-2CQDA2-2p100GE.
        - s58-t24-sut1-c10/p1 - 25GE-port1 e810-XXVDA4-4p25GE.
        - s58-t24-sut1-c10/p2 - 25GE-port2 e810-XXVDA4-4p25GE.
        - s58-t24-sut1-c10/p3 - 25GE-port3 e810-XXVDA4-4p25GE.
        - s58-t24-sut1-c10/p4 - 25GE-port4 e810-XXVDA4-4p25GE.
- TG [Server-Type-H6]:
    - testbedname: testbed24.
    - hostname: s59-t24-tg1.
    - IPMI IP: 10.30.50.59
    - Host IP: 10.30.51.59
    - portnames:
        - s59-t24-tg1-c2/p1 - 200GE-port1 ConnectX7-2p200GE.
        - s59-t24-tg1-c2/p2 - 200GE-port2 ConnectX7-2p200GE.
        - s59-t24-tg1-c4/p1 - 100GE-port1 e810-2CQDA2-2p100GE.
        - s59-t24-tg1-c4/p2 - 100GE-port2 e810-2CQDA2-2p100GE.
        - s59-t24-tg1-c10/p1 - 25GE-port1 e810-XXVDA4-4p25GE.
        - s59-t24-tg1-c10/p2 - 25GE-port2 e810-XXVDA4-4p25GE.
        - s59-t24-tg1-c10/p3 - 25GE-port3 e810-XXVDA4-4p25GE.
        - s59-t24-tg1-c10/p4 - 25GE-port4 e810-XXVDA4-4p25GE.
        - s59-t24-tg1-c7/p1 - 200GE-port1 ConnectX7-2p200GE.
        - s59-t24-tg1-c7/p2 - 200GE-port2 ConnectX7-2p200GE.
        - s59-t24-tg1-c9/p1 - 100GE-port1 e810-2CQDA2-2p100GE.
        - s59-t24-tg1-c9/p2 - 100GE-port2 e810-2CQDA2-2p100GE.
```

## Testbed Wiring

### 1-Node-Skylake (1n-skx)

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

### 1-Node-ThunderX2 (1n-tx2)

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

### 2-Node-IxiaPS1L47 (2n-ps1)

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

### 2-Node-Cascadelake (2n-clx)

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

### 2-Node-Zen2 (2n-zn2)

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

### 2-Node-ThunderX2 (2n-tx2)

```
- testbed211:
    - ring1 10GE-ports x520-2p10GE on SUTs:
        - s27-t211-sut1-c18/p1 - s19-t33t211-tg1-c8/p1.
        - s27-t211-sut1-c18/p2 - s19-t33t211-tg1-c8/p2.
```

### 2-Node-Icelake (2n-icx)

```
- testbed212:
    - ring1 25GE-ports xxv710-DA2-2p25GE:
        - s72-t212-tg1-c2/p1 to s71-t212-sut1-c2/p1.
        - s71-t212-sut1-c2/p2 to s72-t212-tg1-c2/p2.
    - ring2 25GE-ports e810-XXVDA4-2p25GE:
        - s72-t212-tg1-c4/p1 to s71-t212-sut1-c4/p1.
        - s71-t212-sut1-c4/p2 to s72-t212-tg1-c4/p2.
        - s72-t212-tg1-c4/p3 to s71-t212-sut1-c4/p3.
        - s71-t212-sut1-c4/p4 to s72-t212-tg1-c4/p4.
    - ring3 100GE-ports e810-2CQDA2-2p100GE:
        - s72-t212-tg1-c9/p1 to s71-t212-sut1-c9/p1.
        - s71-t212-sut1-c9/p2 to s72-t212-tg1-c9/p2.
    - ring4 100GE-ports e810-2CQDA2-2p100GE:
        - s72-t212-tg1-c6/p1 to s72-t212-tg1-c6/p2.
        - s72-t212-tg1-c6/p2 to s72-t212-tg1-c6/p1.
    - ring5 100GE-ports ConnectX7-2p100GE:
        - s72-t212-tg1-c8/p1 to s71-t212-sut1-c8/p1.
        - s71-t212-sut1-c8/p2 to s72-t212-tg1-c8/p2.
- testbed213:
    - ring1 25GE-ports xxv710-DA2-2p25GE:
        - s84-t213-tg1-c2/p1 to s83-t213-sut1-c2/p1.
        - s83-t213-sut1-c2/p2 to s84-t213-tg1-c2/p2.
    - ring2 25GE-ports e810-XXVDA4-2p25GE:
        - s84-t213-tg1-c4/p1 to s83-t213-sut1-c4/p1.
        - s83-t213-sut1-c4/p2 to s84-t213-tg1-c4/p2.
        - s84-t213-tg1-c4/p3 to s83-t213-sut1-c4/p3.
        - s83-t213-sut1-c4/p4 to s84-t213-tg1-c4/p4.
    - ring3 100GE-ports e810-2CQDA2-2p100GE:
        - s84-t213-tg1-c9/p1 to s83-t213-sut1-c9/p1.
        - s83-t213-sut1-c9/p2 to s84-t213-tg1-c9/p2.
    - ring4 100GE-ports e810-2CQDA2-2p100GE:
        - s84-t213-tg1-c6/p1 to s84-t213-tg1-c6/p2.
        - s84-t213-tg1-c6/p2 to s84-t213-tg1-c6/p1.
    - ring5 100GE-ports ConnectX7-2p100GE:
        - s84-t213-tg1-c8/p1 to s83-t213-sut1-c8/p1.
        - s83-t213-sut1-c8/p2 to s84-t213-tg1-c8/p2.
- testbed214:
    - ring1 25GE-ports xxv710-DA2-2p25GE:
        - s86-t214-tg1-c2/p1 to s85-t214-sut1-c2/p1.
        - s85-t214-sut1-c2/p2 to s86-t214-tg1-c2/p2.
    - ring2 25GE-ports e810-XXVDA4-2p25GE:
        - s86-t214-tg1-c4/p1 to s85-t214-sut1-c4/p1.
        - s85-t214-sut1-c4/p2 to s86-t214-tg1-c4/p2.
        - s86-t214-tg1-c4/p3 to s85-t214-sut1-c4/p3.
        - s85-t214-sut1-c4/p4 to s86-t214-tg1-c4/p4.
    - ring3 100GE-ports e810-2CQDA2-2p100GE:
        - s86-t214-tg1-c9/p1 to s85-t214-sut1-c9/p1.
        - s85-t214-sut1-c9/p2 to s86-t214-tg1-c9/p2.
    - ring4 100GE-ports e810-2CQDA2-2p100GE:
        - s86-t214-tg1-c6/p1 to s86-t214-tg1-c6/p2.
        - s86-t214-tg1-c6/p2 to s86-t214-tg1-c6/p1.
    - ring5 100GE-ports ConnectX7-2p100GE:
        - s86-t214-tg1-c8/p1 to s85-t214-sut1-c8/p1.
        - s85-t214-sut1-c8/p2 to s86-t214-tg1-c8/p2.
- testbed215:
    - ring1 25GE-ports xxv710-DA2-2p25GE:
        - s88-t215-tg1-c2/p1 to s87-t215-sut1-c2/p1.
        - s87-t215-sut1-c2/p2 to s88-t215-tg1-c2/p2.
    - ring2 25GE-ports e810-XXVDA4-2p25GE:
        - s88-t215-tg1-c4/p1 to s87-t215-sut1-c4/p1.
        - s87-t215-sut1-c4/p2 to s88-t215-tg1-c4/p2.
        - s88-t215-tg1-c4/p3 to s87-t215-sut1-c4/p3.
        - s87-t215-sut1-c4/p4 to s88-t215-tg1-c4/p4.
    - ring3 100GE-ports e810-2CQDA2-2p100GE:
        - s88-t215-tg1-c9/p1 to s87-t215-sut1-c9/p1.
        - s87-t215-sut1-c9/p2 to s88-t215-tg1-c9/p2.
    - ring4 100GE-ports e810-2CQDA2-2p100GE:
        - s88-t215-tg1-c6/p1 to s88-t215-tg1-c6/p2.
        - s88-t215-tg1-c6/p2 to s88-t215-tg1-c6/p1.
    - ring5 100GE-ports ConnectX7-2p100GE:
        - s88-t215-tg1-c8/p1 to s87-t215-sut1-c8/p1.
        - s87-t215-sut1-c8/p2 to s88-t215-tg1-c8/p2.
```

### 3-Node-Rangeley (3n-rng)

```
To be completed.
```

### 3-Node-Taishan (3n-tsh)

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

### 3-Node-Altra (3n-alt)

```
- testbed34:
    - ring1 40GE-ports xl710-QDA2-2p40GE on SUTs:
        - s64-t34-tg1-c4/p1 - s62-t34-sut1-c1/p2.
        - s62-t34-sut1-c1/p1 - s63-t34-sut2-c1/p2.
        - s63-t34-sut2-c1/p1 - s64-t34-tg1-c4/p2.
    - ring2 100GE-ports ConnectX6-2p100GE Mellanox on SUTs:
        - s64-t34-tg1-c8/p1 - s62-t34-sut1-c8/p2.
        - s62-t34-sut1-c8/p1 - s63-t34-sut2-c8/p2.
        - s63-t34-sut2-c8/p1 - s64-t34-tg1-c8/p2.
```

### 3-Node-Icelake (3n-icx)

```
- testbed37:
    - ring1 25GE-ports xxv710-DA2-2p25GE:
        - s67-t37-tg1-c2/p1 to s65-t37-sut1-c2/p1.
        - s65-t37-sut1-c2/p2 to s66-t37-sut2-c2/p2.
        - s66-t37-sut2-c2/p1 to s67-t37-tg1-c2/p2.
    - ring2 25GE-ports e810-XXVDA4-4p25GE:
        - s67-t37-tg1-c4/p1 to s65-t37-sut1-c4/p1.
        - s65-t37-sut1-c4/p2 to s66-t37-sut2-c4/p2.
        - s66-t37-sut2-c4/p1 to s67-t37-tg1-c4/p2.
        - s67-t37-tg1-c4/p3 to s65-t37-sut1-c4/p3.
        - s65-t37-sut1-c4/p4 to s66-t37-sut2-c4/p4.
        - s66-t37-sut2-c4/p3 to s67-t37-tg1-c4/p4.
    - ring3 100GE-ports e810-2CQDA2-2p100GE:
        - s67-t37-tg1-c9/p1 to s65-t37-sut1-c9/p1.
        - s65-t37-sut1-c9/p2 to s66-t37-sut2-c9/p2.
        - s66-t37-sut2-c9/p1 to s67-t37-tg1-c9/p2.
    - ring4 100GE-ports ConnectX6-2p100GE:
        - s67-t37-tg1-c6/p1 - s65-t37-sut1-c6/p2.
        - s65-t37-sut1-c6/p1 - s66-t37-sut2-c6/p2.
        - s66-t37-sut2-c6/p1 - s67-t37-tg1-c9-c6/p2.
- testbed38:
    - ring1 25GE-ports xxv710-DA2-2p25GE:
        - s80-t38-tg1-c2/p1 to s78-t38-sut1-c2/p1.
        - s78-t38-sut1-c2/p2 to s79-t38-sut2-c2/p2.
        - s79-t38-sut2-c2/p1 to s80-t38-tg1-c2/p2.
    - ring2 25GE-ports e810-XXVDA4-4p25GE:
        - s80-t38-tg1-c4/p1 to s78-t38-sut1-c4/p1.
        - s78-t38-sut1-c4/p2 to s79-t38-sut2-c4/p2.
        - s79-t38-sut2-c4/p1 to s80-t38-tg1-c4/p2.
        - s80-t38-tg1-c4/p3 to s78-t38-sut1-c4/p3.
        - s78-t38-sut1-c4/p4 to s79-t38-sut2-c4/p4.
        - s79-t38-sut2-c4/p3 to s80-t38-tg1-c4/p4.
    - ring3 100GE-ports e810-2CQDA2-2p100GE:
        - s80-t38-tg1-c9/p1 to s78-t38-sut1-c9/p1.
        - s78-t38-sut1-c9/p2 to s79-t38-sut2-c9/p2.
        - s79-t38-sut2-c9/p1 to s80-t38-tg1-c9/p2.
    - ring4 100GE-ports ConnectX6-2p100GE:
        - s80-t38-tg1-c6/p1 to s78-t38-sut1-c6/p1.
        - s78-t38-sut1-c6/p2 to s79-t38-sut2-c6/p2.
        - s79-t38-sut2-c6/p1 to s80-t38-tg1-c6/p2.
```

### 3-Node-SnowRidge (3n-snr)

```
- testbed39:
    - ring1 25GE-ports e810-XXVDA4-4p25GE:
        - s89-t39t310-tg1-c6/p1 to s93-t39-sut1-c1/p1.
        - s93-t39-sut1-c1/p2 to s94-t39-sut2-c1/p2.
        - s94-t39-sut2-c1/p1 to s89-t39t310-tg1-c6/p2.
        - s89-t39t310-tg1-c6/p3 to s93-t39-sut1-c1/p3.
        - s93-t39-sut1-c1/p4 to s94-t39-sut2-c1/p4.
        - s94-t39-sut2-c1/p3 to s89-t39t310-tg1-c6/p4.
```

### 2-Node-SapphireRapids (2n-spr)

```
- testbed21:
    - ring1 200GE-ports ConnectX7-2p200GE:
        - s53-t21-tg1-c2/p1 to s52-t21-sut1-c2/p1
        - s53-t21-tg1-c7/p1 to s52-t21-sut1-c7/p1
        - s52-t21-sut1-c4/p2 to s52-t21-sut1-c9/p2
    - ring2 200GE-ports ConnectX7-2p200GE:
        - s53-t21-tg1-c2/p2 to s52-t21-sut1-c2/p2
        - s53-t21-tg1-c7/p2 to s52-t21-sut1-c7/p2
        - s52-t21-sut1-c10/p1 to s52-t21-sut1-c11/p1
    - ring3 200GE-ports ConnectX7-2p200GE:
        - s53-t21-tg1-c4/p1 to s52-t21-sut1-c4/p1
        - s53-t21-tg1-c9/p1 to s52-t21-sut1-c9/p1
        - s52-t21-sut1-c10/p2 to s52-t21-sut1-c11/p2
- testbed22:
    - ring1 100GE-ports e810-2CQDA2-2p100GE:
        - s55-t22-tg1-c4/p1  to s54-t22-sut1-c9/p2
        - s55-t22-tg1-c4/p2  to s54-t22-sut1-c4/p2
        - s54-t22-sut1-c9/p1 to s54-t22-sut1-c4/p1
    - ring2 25GE-ports e810-XXVDA4-4p25GE:
        - s55-t22-tg1-c2/p1  to s54-t22-sut1-c2/p1
        - s55-t22-tg1-c2/p2  to s54-t22-sut1-c7/p1
        - s54-t22-sut1-c2/p2 to s54-t22-sut1-c7/p2
- testbed23:
    - ring1 200GE-ports ConnectX7-2p200GE:
        - s56-t23-sut1-c2/p1 to s57-t23-tg1-c2/p1.
        - s57-t23-tg1-c2/p2 to s56-t23-sut1-c2/p2.
    - ring2 100GE-ports e810-2CQDA2-2p100GE:
        - s56-t23-sut1-c4/p1 to s57-t23-tg1-c4/p1.
        - s57-t23-tg1-c4/p2 to s56-t23-sut1-c4/p2.
    - ring3 25GE-ports e810-XXVDA4-2p25GE:
        - s56-t23-sut1-c10/p1 to s57-t23-tg1-c10/p1.
        - s56-t23-sut1-c10/p2 to s57-t23-tg1-c10/p2.
        - s56-t23-sut1-c10/p3 to s57-t23-tg1-c10/p3.
        - s56-t23-sut1-c10/p4 to s57-t23-tg1-c10/p4.
    - ring4 200GE-ports ConnectX7-2p200GE:
        - s57-t23-tg1-c7/p1 to s57-t23-tg1-c7/p2.
    - ring5 100GE-ports e810-2CQDA2-2p100GE:
        - s57-t23-tg1-c9/p1 to s57-t23-tg1-c9/p2.
- testbed24:
    - ring1 200GE-ports ConnectX7-2p200GE:
        - s58-t24-sut1-c2/p1 to s59-t24-tg1-c2/p1.
        - s59-t24-tg1-c2/p2 to s58-t24-sut1-c2/p2.
    - ring2 100GE-ports e810-2CQDA2-2p100GE:
        - s58-t24-sut1-c4/p1 to s59-t24-tg1-c4/p1.
        - s59-t24-tg1-c4/p2 to s58-t24-sut1-c4/p2.
    - ring3 25GE-ports e810-XXVDA4-2p25GE:
        - s58-t24-sut1-c10/p1 to s59-t24-tg1-c10/p1.
        - s58-t24-sut1-c10/p2 to s59-t24-tg1-c10/p2.
        - s58-t24-sut1-c10/p3 to s59-t24-tg1-c10/p3.
        - s58-t24-sut1-c10/p4 to s59-t24-tg1-c10/p4.
    - ring4 200GE-ports ConnectX7-2p200GE:
        - s59-t24-tg1-c7/p1 to s59-t24-tg1-c7/p2.
    - ring5 100GE-ports e810-2CQDA2-2p100GE:
        - s59-t24-tg1-c9/p1 to s59-t24-tg1-c9/p2.
```