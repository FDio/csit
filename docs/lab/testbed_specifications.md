<!-- TOC depthFrom:1 depthTo:6 withLinks:1 updateOnSave:1 orderedList:0 -->

	- [FD.io CSIT Testbed Specifications](#fdio-csit-testbed-specifications)
	- [Testbeds Overview](#testbeds-overview)
		- [Summary List](#summary-list)
		- [1-Node-Skylake Xeon Intel (1n-skx)](#1-node-skylake-xeon-intel-1n-skx)
		- [1-Node-ThunderX2 Arm Marvell (1n-tx2)](#1-node-thunderx2-arm-marvell-1n-tx2)
		- [2-Node-Skylake Xeon Intel (2n-skx)](#2-node-skylake-xeon-intel-2n-skx)
		- [2-Node-Denverton Atom Intel (2n-dnv)](#2-node-denverton-atom-intel-2n-dnv)
		- [2-Node-IxiaPS1L47 Ixia PSOne L47 (2n-ps1)](#2-node-ixiaps1l47-ixia-psone-l47-2n-ps1)
		- [3-Node-Haswell Xeon Intel (3n-skx)](#3-node-haswell-xeon-intel-3n-skx)
		- [3-Node-Skylake Xeon Intel (3n-skx)](#3-node-skylake-xeon-intel-3n-skx)
		- [3-Node-TaiShan Arm Huawei (3n-tsh)](#3-node-taishan-arm-huawei-3n-tsh)
		- [3-Node-MACCHIATObin Arm Marvell](#3-node-macchiatobin-arm-marvell)
		- [3-Node-Rangeley Atom Testbeds](#3-node-rangeley-atom-testbeds)
	- [Server Management](#server-management)
		- [Requirements](#requirements)
		- [Addressing](#addressing)
		- [LOM (IPMI) VLAN IP Addresses](#lom-ipmi-vlan-ip-addresses)
		- [Management VLAN IP Addresses](#management-vlan-ip-addresses)
	- [Server Type Specification](#server-type-specification)
		- [Server and Port Naming](#server-and-port-naming)
	- [Testbeds Configuration](#testbeds-configuration)
		- [Per Testbed Server Allocation and Naming](#per-testbed-server-allocation-and-naming)
			- [1-Node-Skylake (1n-skx) PROD](#1-node-skylake-1n-skx-prod)
			- [1-Node-Thunderx2 (1n-tx2) WIP](#1-node-thunderx2-1n-tx2-wip)
			- [2-Node-Skylake (2n-skx) PROD](#2-node-skylake-2n-skx-prod)
			- [2-Node-Denverton (2n-dnv) TODO](#2-node-denverton-2n-dnv-todo)
			- [2-Node-IxiaPS1L47 (2n-ps1) VERIFY](#2-node-ixiaps1l47-2n-ps1-verify)
			- [3-Node-Haswell (3n-hsw) PROD](#3-node-haswell-3n-hsw-prod)
			- [3-Node-Skylake (3n-skx) PROD](#3-node-skylake-3n-skx-prod)
			- [3-Node-Rangeley (3n-rng) VERIFY](#3-node-rangeley-3n-rng-verify)
			- [3-Node-Taishan (3n-tsh) WIP](#3-node-taishan-3n-tsh-wip)
			- [3-Node-Mcbin (3n-mcb) TODO](#3-node-mcbin-3n-mcb-todo)
		- [Per Testbed Wiring](#per-testbed-wiring)
			- [1-Node-Skylake (1n-skx) PROD](#1-node-skylake-1n-skx-prod)
			- [1-Node-Thunderx2 (1n-tx2) WIP](#1-node-thunderx2-1n-tx2-wip)
			- [2-Node-Skylake (2n-skx) PROD](#2-node-skylake-2n-skx-prod)
			- [2-Node-Denverton (2n-dnv) TODO](#2-node-denverton-2n-dnv-todo)
			- [2-Node-IxiaPS1L47 (2n-ps1) VERIFY](#2-node-ixiaps1l47-2n-ps1-verify)
			- [3-Node-Haswell (3n-hsw) PROD](#3-node-haswell-3n-hsw-prod)
			- [3-Node-Skylake (3n-skx) PROD](#3-node-skylake-3n-skx-prod)
			- [3-Node-Rangeley (3n-rng) TODO](#3-node-rangeley-3n-rng-todo)
			- [3-Node-Taishan (3n-tsh) WIP](#3-node-taishan-3n-tsh-wip)
			- [3-Node-Mcbin (3n-mcb) WIP](#3-node-mcbin-3n-mcb-wip)
	- [Inventory](#inventory)
		- [Appliances](#appliances)
		- [Arm Servers](#arm-servers)
		- [Xeon and Atom Servers](#xeon-and-atom-servers)
		- [Network Interface Cards](#network-interface-cards)
		- [Pluggables and Cables](#pluggables-and-cables)
		- [Other Parts](#other-parts)

<!-- /TOC -->
## FD.io CSIT Testbed Specifications

This note includes specification of the physical testbed infrastructure
hosted by LFN FD.io CSIT project.

## Testbeds Overview

### Summary List

```
 #. CSIT_tb          Purpose  SUT   TG    #TB  #SUT #TG  #hsw #skx #ps1 #rng #dnv #tx2 #tsh #mcb
 1. 1-Node-Skylake     func   skx   na    2    2    0    0    2    0    0    0    0    0    0
 2. 1-Node-Thunderx2   func   tx2   na    1    1    0    0    0    0    0    0    1    0    0
 3. 2-Node-Skylake     perf   skx   skx   4    4    4    0    8    0    0    0    0    0    0
 4. 2-Node-Denverton   perf   dnv   skx   1    1    1    0    .5   0    0    1    0    0    0
 5. 2-Node-IxiaPS1L47  tcp    skx   ps1   1    1    1    0    1    1    0    0    0    0    0
 6. 3-Node-Haswell     perf   hsw   hsw   3    6    3    9    0    0    0    0    0    0    0
 7. 3-Node-Skylake     perf   skx   skx   2    4    2    0    6    0    0    0    0    0    0
 8. 3-Node-Rangeley    perf   rng   skx   1    3    1    0    0    0    2    0    0    0    0
 9. 3-Node-Taishan     perf   tsh   skx   1    2    1    0    .5   0    0    0    0    2    0
10. 3-Node-Mcbin       perf   mcb   skx   1    2    1    0    .5   0    0    0    0    0    2
11. 1-Node-VIRL        func   hsw   ---   3    3    0    3    0    0    0    0    0    0    0
                                 Totals: 17   26   14   12   19    1    2    1    1    2    2
```

### 1-Node-Skylake Xeon Intel (1n-skx)

Each 1-Node-Skylake testbed includes one SUT (Type-B6 server) with NIC
ports connected back-to-back.
Used for FD.io VPP_Device functional driver tests.

### 1-Node-ThunderX2 Arm Marvell (1n-tx2)

Each 1-Node-ThunderX2 testbed includes one SUT (Type-B9 server) with NIC
ports connected back-to-back.
Used for FD.io VPP_Device functional driver tests.

### 2-Node-Skylake Xeon Intel (2n-skx)

Each 2-Node-Skylake testbed includes one SUT (Type-B1 server) and one TG
(Type-B2 server) connected back-to-back.
Used for FD.io performance tests.

### 2-Node-Denverton Atom Intel (2n-dnv)

Each 2-Node-Skylake testbed includes one SUT (Type-B10 server) and one TG
(Type-B2 server) connected back-to-back.
Used for FD.io performance tests.

### 2-Node-IxiaPS1L47 Ixia PSOne L47 (2n-ps1)

Each 2-Node-IxiaPS1L47 testbed includes one SUT (Type-B1 server) and one
TG (Ixia PSOne appliance) with 10GE interfaces connected back-to-back.
Used for FD.io TCP/IP and HTTP performance tests.

### 3-Node-Haswell Xeon Intel (3n-skx)

### 3-Node-Skylake Xeon Intel (3n-skx)

Each 3-Node-Skylake testbed includes two SUTs (Type-B1 servers) and one
TG (Type-B2 server) connected in full-mesh triangle.
Used for FD.io performance tests.

### 3-Node-TaiShan Arm Huawei (3n-tsh)

Each 3-Node-TaiShan testbed includes two SUTs (Type-B3 server) and one TG
(Type-B2 server) connected in full-mesh triangle.
Used for FD.io performance tests.

### 3-Node-MACCHIATObin Arm Marvell

Each 3-Node-MACCHIATObin testbed includes two SUTs (Type-B4 server) and
one TG (Type-B2 server) connected in full-mesh triangle.
Used for FD.io performance tests.

### 3-Node-Rangeley Atom Testbeds

Each 3-Node-Rangeley testbed includes two SUTs (Type-B5 Netgate device)
and one TG (Type-2 server) connected in full-mesh triangle.
Used for FD.io performance tests.

## Server Management

### Requirements

For management purposes, each server must have following two ports
connected to the management network:

```
- 1GE IPMI port
  - IPMI - Intelligent Platform Management Interface.
  - Required for access to embedded server management with WebUI, CLI, SNMPv3,
    IPMIv2.0, for firmware (BIOS) and OS updates.
- 1GE/10GE/40GE management port
  - hostOS management port for general system management.
```

### Addressing

Each server has a LOM (Lights-Out-Management e.g. SM IPMI) and a Management
port, which are connected to two different VLANs.

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
10.30.50.16  | t1-tg1
10.30.50.17  | t1-sut1
10.30.50.18  | t1-sut2
10.30.50.20  | t2-tg1
10.30.50.21  | t2-sut1
10.30.50.22  | t2-sut2
10.30.50.24  | t3-tg1
10.30.50.25  | t3-sut1
10.30.50.26  | t3-sut-2
10.30.50.28  | t4-sut1
10.30.50.29  | t4-sut2
10.30.50.30  | t4-sut3
10.30.50.36  | s17-t33-sut1
10.30.50.37  | s18-t33-sut2
10.30.50.41  | s3-t21-sut1
10.30.50.42  | s4-t21-tg1
10.30.50.43  | s11-t31-sut1
10.30.50.44  | s12-t31-sut2
10.30.50.45  | s13-t31-tg1
10.30.50.46  | s19-t33t34-tg1
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
10.30.50.69  | s27-t13-sut
10.30.50.255 | Broadcast

### Management VLAN IP Addresses

Name                      | Comment
------------------------- | -------
10.30.51.0                | network
10.30.51.1                | Router
10.30.51.2                | LF Reserved
10.30.51.3                | LF Reserved
10.30.51.4                | LF Reserved
10.30.51.5                | LF Reserved
10.30.51.6                | LF Reserved
10.30.51.7                | LF Reserved
10.30.51.8                | LF Reserved
10.30.51.9                | s22-t35-sut1 (netgate-1)
10.30.51.10               | s23-t35-sut2 (netgate-2)
10.30.51.11               | s24-t35-sut3 (netgate-3)
10.30.51.12               | softiron-1
10.30.51.13               | softiron-2
10.30.51.14               | softiron-3
10.30.51.15               | LF Reserved
10.30.51.16               | t1-tg1
10.30.51.17               | t1-sut1
10.30.51.18               | t1-sut2
10.30.51.20               | t2-tg1
10.30.51.21               | t2-sut1
10.30.51.22               | t2-sut2
10.30.51.24               | t3-tg1
10.30.51.25               | t3-sut1
10.30.51.26               | t3-sut-2
10.30.51.28               | t4-sut1
10.30.51.29               | t4-sut2
10.30.51.29               | s22-t35-sut1 screen -r /dev/ttyUSB0, TO BE VERIFIED
10.30.51.30               | t4-sut3
10.30.51.30               | s23-t35-sut2 screen -r /dev/ttyUSB1, TO BE VERIFIED
10.30.51.30               | s24-t35-sut3 screen -r /dev/ttyUSB2, TO BE VERIFIED
10.30.51.36               | s17-t33-sut1
10.30.51.37               | s18-t33-sut2
10.30.51.41               | s20-t34-sut1
10.30.51.42               | s21-t34-sut2
10.30.51.44               | s3-t21-sut1
10.30.51.45               | s4-t21-tg1
10.30.51.46               | s11-t31-sut1
10.30.51.47               | s12-t31-sut2
10.30.51.48               | s13-t31-tg1
10.30.51.49               | s19-t33t34-tg1
10.30.51.50               | s1-t11-sut1
10.30.51.51               | s2-t12-sut1
10.30.51.52               | s5-t22-sut1
10.30.51.53               | s6-t22-tg1
10.30.51.54               | s7-t23-sut1
10.30.51.55               | s8-t23-tg1
10.30.51.56               | s9-t24-sut1
10.30.51.57               | s10-t24-tg1
10.30.51.58               | s14-t32-sut1
10.30.51.59               | s15-t32-sut2
10.30.51.60               | s16-t32-tg1
10.30.51.61               | s25-t25-sut1
10.30.51.62               | s26-t25-tg1
10.30.51.69               | s27-t13-sut1
10.30.51.70-10.30.51.105  | VIRL1 TO BE VERIFIED
10.30.51.106-10.30.51.180 | VIRL2
10.30.51.181-10.30.51.254 | VIRL3
10.30.51.255              | Broadcast

## Server Type Specification

FD.io CSIT lab contains following server types:
```
1. Type-A1: Purpose - Haswell Xeon SUT (Systems Under Test) for FD.io performance testing.
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
            - PCIe Slot1: Cisco VIC 1385 2p40GE.
            - PCIe Slot2: Intel NIC x520 2p10GE.
            - PCIe Slot3: empty.
        - Numa1: Left PCIe Riser Board (Riser 2) (x8, x16, x8 PCIe3.0 lanes)
            - PCIe Slot4: Intel NIC xl710 2p40GE.
            - PCIe Slot5: Intel NIC x710 2p10GE.
            - PCIe Slot6: Intel QAT 8950 50G (Walnut Hill)
        - MLOM slot: Cisco VIC 1227 2p10GE (x8 PCIe2.0 lanes).
2. Type-A2: Purpose - Haswell Xeon TG (Traffic Generators) for FD.io performance testing.
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
        - Numa0: Right PCIe Riser Board (Riser 1) (x8, x8, x8 lanes)
            - PCIe Slot1: Intel NIC xl710 2p40GE.
            - PCIe Slot2: Intel NIC x710 2p10GE.
            - PCIe Slot3: Intel NIC x710 2p10GE.
        - Numa1: Left PCIe Riser Board (Riser 2) (x8, x16, x8 lanes)
            - PCIe Slot4: Intel NIC xl710 2p40GE.
            - PCIe Slot5: Intel NIC x710 2p10GE.
            - PCIe Slot6: Intel NIC x710 2p10GE.
        - MLOM slot: empty.
3. Type-A3: Purpose - Haswell Xeon VIRL hosts for FD.io functional testing.
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
4. Type-B1: Purpose - Skylake Xeon SUT for FD.io performance testing.
    - Quantity: ---
    - Physical connectivity:
        - IPMI and host management ports.
        - NIC ports connected into 2-node and 3-node topologies.
    - Main HW configuration:
        - Chassis: SuperMicro SYS-7049GP-TRT.
        - Motherboard: SuperMicro X11DPG-QT.
        - Processors: 2* Intel Platinum 8180 2.3 GHz.
        - RAM Memory: 16* 16GB DDR4-2666MHz.
        - Disks: 2* 1.6TB 6G SATA SSD.
    - NICs configuration:
        - Numa0: (x16, x16, x16 PCIe3.0 lanes)
            - PCIe Slot2 18:00.xx: x710-4p10GE Intel.
            - PCIe Slot4 3b:00.xx: xxv710-DA2-2p25GE Intel.
            - PCIe Slot9 5e:00.xx: FUTURE ConnectX5-2p100GE Mellanox.
        - Numa1: (x16, x16, x16 PCIe3.0 lanes)
            - PCIe Slot6 86:00.xx: empty.
            - PCIe Slot8 af:00.xx: empty.
            - PCIe Slot10 d8:00.xx: empty.
2. Type-B2: Purpose - Skylake Xeon TG for FD.io performance testing.
    - Quantity: ---
    - Physical connectivity:
        - IPMI and host management ports.
        - NIC ports connected into 2-node and 3-node topologies.
    - Main HW configuration:
        - Chassis: SuperMicro SYS-7049GP-TRT.
        - Motherboard: SuperMicro X11DPG-QT.
        - Processors: 2* Intel Platinum 8180 2.3 GHz.
        - RAM Memory: 16* 16GB DDR4-2666MHz.
        - Disks: 2* 1.6TB 6G SATA SSD.
    - NICs configuration:
        - Numa0: (x16, x16, x16 PCIe3.0 lanes)
            - PCIe Slot2 18:00.xx: x710-4p10GE Intel.
            - PCIe Slot4 3b:00.xx: xxv710-DA2 2p25GE Intel.
            - PCIe Slot9 5e:00.xx: FUTURE ConnectX5-2p100GE Mellanox.
        - Numa1: (x16, x16, x16 PCIe3.0 lanes)
            - PCIe Slot6 86:00.xx: empty.
            - PCIe Slot8 af:00.xx: empty.
            - PCIe Slot10 d8:00.xx: x710-4p10GE Intel.
3. Type-B3: Purpose - TaiShan Arm Huawei SUT for FD.io performance testing.
    - Quantity: 2
    - Physical connectivity:
        - IPMI(?) and host management ports.
        - NIC ports connected into 3-node topology.
    - Main HW configuration:
        - Chassis: Huawei TaiShan 2280.
        - Processors: 1* hip07-d05 ~ 64* Arm Cortex-A72
        - RAM Memory: 8* 16GB DDR4-2400MT/s
        - Disks: 1* 4TB SATA HDD
    - NICs configuration:
        - PCIe Slot4 e9:00.xx: connectx4-2p25GE Mellanox.
        - PCIe Slot6 11:00.xx: 82599-2p10GE Intel.
4. Type-B4: Purpose - MACCHIATObin Arm Marvell SUT for FD.io performance testing.
    - Quantity: 3
    - Physical connectivity:
        - Host management ports.
        - NIC ports connected into 2-node and 3-node topologies.
    - Main HW configuration:
        - Chassis: MACCHIATObin.
        - Processors: 1* Armada 8040 ~ 4* Arm Cortex-A72
        - RAM Memory: 1* 16GB DDR4
        - Disks: 1* 128GB(?) SATA SDD
    - NICs configuration:
        - pp2-2p10GE Marvell (on-chip Ethernet ports ; marvell plugin in VPP)
5. Type-B5: Purpose - Rangeley Atom SUT for FD.io performance testing.
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
6. Type-B6: Purpose - Skylake Xeon SUT for FD.io VPP_Device functional tests.
    - Quantity: 2.
    - Physical connectivity:
        - IPMI and host management ports.
        - NIC ports connected into 2-node and 3-node topologies.
    - Main HW configuration:
        - Chassis: SuperMicro SYS-7049GP-TRT.
        - Motherboard: SuperMicro X11DPG-QT.
        - Processors: 2* Intel Platinum 8180 2.3 GHz.
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
7. Type-B7: Purpose - Ixia PerfectStorm One Appliance TG for FD.io TCP/IP performance tests.
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
8. Type-B8: Purpose - Skylake Xeon SUT for TCP/IP host stack tests.
    - Quantity: 1.
    - Physical connectivity:
        - IPMI and host management ports.
        - NIC ports.
    - Main HW configuration:
        - Chassis: SuperMicro SYS-7049GP-TRT.
        - Motherboard: SuperMicro X11DPG-QT.
        - Processors: 2* Intel Platinum 8180 2.3 GHz.
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
9. Type-B9: Purpose - ThunderX2 Arm Marvell SUT for FD.io VPP_Device functional tests.
    - Quantity: 1
    - Physical connectivity:
        - IPMI and host management ports.
        - NIC ports connected into 1-node topologies.
    - Main HW configuration:
        - Chassis: Gigabyte R181-T90 1U
        - Motheboard: MT91-FS1
        - Processors: 1* ThunderX2 ARMv8 CN9975 2.0 GHz
        - RAM Memory: 4* 32GB RDIMM
        - Disks: 1* 480GB SSD Micron, 1* 1000GB HDD Seagate_25
    - NICs configuration:
        - Numa0:
            - PCIe Slot1 05:00.xx: XL710-QDA2.
            - PCIe Slot3 08:00.xx: XL710-QDA2.
        - Numa1:
            - PCIe Slot6 85:00.xx: XL710-QDA2.
10. Type-B10: Purpose - Denverton Atom SUT for FD.io performance testing.
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
```

### Server and Port Naming

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

#### 1-Node-Skylake (1n-skx) PROD

```
- ServerB1 [Type-B6]:
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
- ServerB2 [Type-B6]:
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

#### 1-Node-Thunderx2 (1n-tx2) WIP

```
- ServerB17 [Type-B9]:
    - testbedname: testbed13.
    - hostname: s27-t13-sut1.
    - IPMI IP: 10.30.50.69
    - Host IP: 10.30.51.69
    - portnames:
        - s27-t13-sut1-c1/p1 - 40GE-port1 XL710-QDA2-2p40GE.
        - s27-t13-sut1-c1/p2 - 40GE-port2 XL710-QDA2-2p40GE.
        - s27-t13-sut1-c3/p1 - 40GE-port1 XL710-QDA2-2p40GE.
        - s27-t13-sut1-c3/p2 - 40GE-port2 XL710-QDA2-2p40GE.
        - s27-t13-sut1-c6/p1 - 40GE-port1 XL710-QDA2-2p40GE.
        - s27-t13-sut1-c6/p2 - 40GE-port2 XL710-QDA2-2p40GE.
```

#### 2-Node-Skylake (2n-skx) PROD

```
- ServerB3 [Type-B1]:
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
        - s3-t21-sut1-c9/p1 - FUTURE 100GE-port1 ConnectX5-2p100GE.
        - s3-t21-sut1-c9/p2 - FUTURE 100GE-port2 ConnectX5-2p100GE.
- ServerB4 [Type-B2]:
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
        - s4-t21-tg1-c9/p1 - FUTURE 100GE-port1 ConnectX5-2p100GE.
        - s4-t21-tg1-c9/p2 - FUTURE 100GE-port2 ConnectX5-2p100GE.
- ServerB5 [Type-B1]:
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
        - s5-t22-sut1-c9/p1 - FUTURE 100GE-port1 ConnectX5-2p100GE.
        - s5-t22-sut1-c9/p2 - FUTURE 100GE-port2 ConnectX5-2p100GE.
- ServerB6 [Type-B2]:
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
        - s6-t22-tg1-c9/p1 - FUTURE 100GE-port1 ConnectX5-2p100GE.
        - s6-t22-tg1-c9/p2 - FUTURE 100GE-port2 ConnectX5-2p100GE.
- ServerB7 [Type-B1]:
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
        - s7-t23-sut1-c9/p1 - FUTURE 100GE-port1 ConnectX5-2p100GE.
        - s7-t23-sut1-c9/p2 - FUTURE 100GE-port2 ConnectX5-2p100GE.
- ServerB8 [Type-B2]:
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
        - s8-t23-tg1-c9/p1 - FUTURE 100GE-port1 ConnectX5-2p100GE.
        - s8-t23-tg1-c9/p2 - FUTURE 100GE-port2 ConnectX5-2p100GE.
- ServerB9 [Type-B1]:
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
        - s9-t24-sut1-c9/p1 - FUTURE 100GE-port1 ConnectX5-2p100GE.
        - s9-t24-sut1-c9/p2 - FUTURE 100GE-port2 ConnectX5-2p100GE.
- ServerB10 [Type-B2]:
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
        - s10-t24-tg1-c9/p1 - FUTURE 100GE-port1 ConnectX5-2p100GE.
        - s10-t24-tg1-c9/p2 - FUTURE 100GE-port2 ConnectX5-2p100GE.
```

#### 2-Node-Denverton (2n-dnv) TODO

```
To be completed.
```

#### 2-Node-IxiaPS1L47 (2n-ps1) VERIFY

```
- ServerB25 [Type-B8]:
    - testbedname: testbed25.
    - hostname: s25-t25-sut1.
    - IPMI IP: 10.30.50.58
    - Host IP: 10.30.51.61
    - portnames:
        - s25-t25-sut1-c2/p1 - 10GE-port1 x710-4p10GE.
        - s25-t25-sut1-c2/p2 - 10GE-port2 x710-4p10GE.
        - s25-t25-sut1-c2/p3 - 10GE-port3 x710-4p10GE.
        - s25-t25-sut1-c2/p4 - 10GE-port4 x710-4p10GE.
- ServerB26 [Type-B7]:
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

#### 3-Node-Haswell (3n-hsw) PROD

```
 1. Server1 of Type-1:
    - testbedname: testbed1.
    - hostname: t1-sut1.
    - CIMC IP: 10.30.50.17
    - Host IP: 10.30.51.17
    - portnames:
        - t1-sut1-c1/p1 - 10GE port1 on Intel NIC x520 2p10GE.
        - t1-sut1-c1/p2 - 10GE port2 on Intel NIC x520 2p10GE.
        - t1-sut1-c2/p1 - 40GE port1 on Cisco VIC 1385 2p40GE.
        - t1-sut1-c2/p2 - 40GE port2 on Cisco VIC 1385 2p40GE.
        - t1-sut1-c4/p1 - 40GE port1 on Intel NIC xl710 2p40GE.
        - t1-sut1-c4/p2 - 40GE port2 on Intel NIC xl710 2p40GE.
        - t1-sut1-c5/p1 - 10GE port1 on Intel NIC x710 2p10GE.
        - t1-sut1-c5/p2 - 10GE port2 on Intel NIC x710 2p10GE.
        - t1-sut1-cm/p1 - 10GE port1 on Cisco VIC 1227 2p10GE.
        - t1-sut1-cm/p2 - 10GE port2 on Cisco VIC 1227 2p10GE.
 2. Server2 of Type-1:
    - testbedname: testbed1.
    - hostname: t1-sut2.
    - CIMC IP: 10.30.50.18
    - Host IP: 10.30.51.18
    - portnames:
        - t1-sut2-c1/p1 - 10GE port1 on Intel NIC x520 2p10GE.
        - t1-sut2-c1/p2 - 10GE port2 on Intel NIC x520 2p10GE.
        - t1-sut2-c2/p1 - 40GE port1 on Cisco VIC 1385 2p40GE.
        - t1-sut2-c2/p2 - 40GE port2 on Cisco VIC 1385 2p40GE.
        - t1-sut2-c4/p1 - 40GE port1 on Intel NIC xl710 2p40GE.
        - t1-sut2-c4/p2 - 40GE port2 on Intel NIC xl710 2p40GE.
        - t1-sut2-c5/p1 - 10GE port1 on Intel NIC x710 2p10GE.
        - t1-sut2-c5/p2 - 10GE port2 on Intel NIC x710 2p10GE.
        - t1-sut2-cm/p1 - 10GE port1 on Cisco VIC 1227 2p10GE.
        - t1-sut2-cm/p2 - 10GE port2 on Cisco VIC 1227 2p10GE.
 3. Server3 of Type-2:
    - testbedname: testbed1.
    - hostname: t1-tg1.
    - CIMC IP: 10.30.50.16
    - Host IP: 10.30.51.16
    - portnames:
        - t1-tg1-c1/p1 - 40GE port1 on Intel NIC xl710 2p40GE.
        - t1-tg1-c1/p2 - 40GE port2 on Intel NIC xl710 2p40GE.
        - t1-tg1-c2/p1 - 10GE port1 on Intel NIC x710 2p10GE.
        - t1-tg1-c2/p2 - 10GE port2 on Intel NIC x710 2p10GE.
        - t1-tg1-c3/p1 - 10GE port1 on Intel NIC x710 2p10GE.
        - t1-tg1-c3/p2 - 10GE port2 on Intel NIC x710 2p10GE.
        - t1-tg1-c4/p1 - 40GE port1 on Intel NIC xl710 2p40GE.
        - t1-tg1-c4/p2 - 40GE port2 on Intel NIC xl710 2p40GE.
        - t1-tg1-c5/p1 - 10GE port1 on Intel NIC x710 2p10GE.
        - t1-tg1-c5/p2 - 10GE port2 on Intel NIC x710 2p10GE.
        - t1-tg1-c6/p1 - 10GE port1 on Intel NIC x710 2p10GE.
        - t1-tg1-c6/p2 - 10GE port2 on Intel NIC x710 2p10GE.
 4. Server4 of Type-1:
    - testbedname: testbed2.
    - hostname: t2-sut1.
    - CIMC IP: 10.30.50.21
    - Host IP: 10.30.51.21
    - portnames:
        - t2-sut1-c1/p1 - 10GE port1 on Intel NIC x520 2p10GE.
        - t2-sut1-c1/p2 - 10GE port2 on Intel NIC x520 2p10GE.
        - t2-sut1-c2/p1 - 40GE port1 on Cisco VIC 1385 2p40GE.
        - t2-sut1-c2/p2 - 40GE port2 on Cisco VIC 1385 2p40GE.
        - t2-sut1-c4/p1 - 40GE port1 on Intel NIC xl710 2p40GE.
        - t2-sut1-c4/p2 - 40GE port2 on Intel NIC xl710 2p40GE.
        - t2-sut1-c5/p1 - 10GE port1 on Intel NIC x710 2p10GE.
        - t2-sut1-c5/p2 - 10GE port2 on Intel NIC x710 2p10GE.
        - t2-sut1-cm/p1 - 10GE port1 on Cisco VIC 1227 2p10GE.
        - t2-sut1-cm/p2 - 10GE port2 on Cisco VIC 1227 2p10GE.
 5. Server5 of Type-1:
    - testbedname: testbed2.
    - hostname: t2-sut2.
    - CIMC IP: 10.30.50.22
    - Host IP: 10.30.51.22
    - portnames:
        - t2-sut2-c1/p1 - 10GE port1 on Intel NIC x520 2p10GE.
        - t2-sut2-c1/p2 - 10GE port2 on Intel NIC x520 2p10GE.
        - t2-sut2-c2/p1 - 40GE port1 on Cisco VIC 1385 2p40GE.
        - t2-sut2-c2/p2 - 40GE port2 on Cisco VIC 1385 2p40GE.
        - t2-sut2-c4/p1 - 40GE port1 on Intel NIC xl710 2p40GE.
        - t2-sut2-c4/p2 - 40GE port2 on Intel NIC xl710 2p40GE.
        - t2-sut2-c5/p1 - 10GE port1 on Intel NIC x710 2p10GE.
        - t2-sut2-c5/p2 - 10GE port2 on Intel NIC x710 2p10GE.
        - t2-sut2-cm/p1 - 10GE port1 on Cisco VIC 1227 2p10GE.
        - t2-sut2-cm/p2 - 10GE port2 on Cisco VIC 1227 2p10GE.
 6. Server6 of Type-2:
    - testbedname: testbed2.
    - hostname: t2-tg1.
    - CIMC IP: 10.30.50.20
    - Host IP: 10.30.51.20
    - portnames:
        - t2-tg1-c1/p1 - 40GE port1 on Intel NIC xl710 2p40GE.
        - t2-tg1-c1/p2 - 40GE port2 on Intel NIC xl710 2p40GE.
        - t2-tg1-c2/p1 - 10GE port1 on Intel NIC x710 2p10GE.
        - t2-tg1-c2/p2 - 10GE port2 on Intel NIC x710 2p10GE.
        - t2-tg1-c3/p1 - 10GE port1 on Intel NIC x710 2p10GE.
        - t2-tg1-c3/p2 - 10GE port2 on Intel NIC x710 2p10GE.
        - t2-tg1-c4/p1 - 40GE port1 on Intel NIC xl710 2p40GE.
        - t2-tg1-c4/p2 - 40GE port2 on Intel NIC xl710 2p40GE.
        - t2-tg1-c5/p1 - 10GE port1 on Intel NIC x710 2p10GE.
        - t2-tg1-c5/p2 - 10GE port2 on Intel NIC x710 2p10GE.
        - t2-tg1-c6/p1 - 10GE port1 on Intel NIC x710 2p10GE.
        - t2-tg1-c6/p2 - 10GE port2 on Intel NIC x710 2p10GE.
 7. Server7 of Type-1:
    - testbedname: testbed3.
    - hostname: t3-sut1.
    - CIMC IP: 10.30.50.25
    - Host IP: 10.30.51.25
    - portnames:
        - t3-sut1-c1/p1 - 10GE port1 on Intel NIC x520 2p10GE.
        - t3-sut1-c1/p2 - 10GE port2 on Intel NIC x520 2p10GE.
        - t3-sut1-c2/p1 - 40GE port1 on Cisco VIC 1385 2p40GE.
        - t3-sut1-c2/p2 - 40GE port2 on Cisco VIC 1385 2p40GE.
        - t3-sut1-c4/p1 - 40GE port1 on Intel NIC xl710 2p40GE.
        - t3-sut1-c4/p2 - 40GE port2 on Intel NIC xl710 2p40GE.
        - t3-sut1-c5/p1 - 10GE port1 on Intel NIC x710 2p10GE.
        - t3-sut1-c5/p2 - 10GE port2 on Intel NIC x710 2p10GE.
        - t3-sut1-cm/p1 - 10GE port1 on Cisco VIC 1227 2p10GE.
        - t3-sut1-cm/p2 - 10GE port2 on Cisco VIC 1227 2p10GE.
 8. Server8 of Type-1:
    - testbedname: testbed3.
    - hostname: t3-sut2.
    - CIMC IP: 10.30.50.26
    - Host IP: 10.30.51.26
    - portnames:
        - t3-sut2-c1/p1 - 10GE port1 on Intel NIC x520 2p10GE.
        - t3-sut2-c1/p2 - 10GE port2 on Intel NIC x520 2p10GE.
        - t3-sut2-c2/p1 - 40GE port1 on Cisco VIC 1385 2p40GE.
        - t3-sut2-c2/p2 - 40GE port2 on Cisco VIC 1385 2p40GE.
        - t3-sut2-c4/p1 - 40GE port1 on Intel NIC xl710 2p40GE.
        - t3-sut2-c4/p2 - 40GE port2 on Intel NIC xl710 2p40GE.
        - t3-sut2-c5/p1 - 10GE port1 on Intel NIC x710 2p10GE.
        - t3-sut2-c5/p2 - 10GE port2 on Intel NIC x710 2p10GE.
        - t3-sut2-cm/p1 - 10GE port1 on Cisco VIC 1227 2p10GE.
        - t3-sut2-cm/p2 - 10GE port2 on Cisco VIC 1227 2p10GE.
 9. Server9 of Type-2:
    - testbedname: testbed3.
    - hostname: t3-tg1.
    - CIMC IP: 10.30.50.24
    - Host IP: 10.30.51.24
    - portnames:
        - t3-tg1-c1/p1 - 40GE port1 on Intel NIC xl710 2p40GE.
        - t3-tg1-c1/p2 - 40GE port2 on Intel NIC xl710 2p40GE.
        - t3-tg1-c2/p1 - 10GE port1 on Intel NIC x710 2p10GE.
        - t3-tg1-c2/p2 - 10GE port2 on Intel NIC x710 2p10GE.
        - t3-tg1-c3/p1 - 10GE port1 on Intel NIC x710 2p10GE.
        - t3-tg1-c3/p2 - 10GE port2 on Intel NIC x710 2p10GE.
        - t3-tg1-c4/p1 - 40GE port1 on Intel NIC xl710 2p40GE.
        - t3-tg1-c4/p2 - 40GE port2 on Intel NIC xl710 2p40GE.
        - t3-tg1-c5/p1 - 10GE port1 on Intel NIC x710 2p10GE.
        - t3-tg1-c5/p2 - 10GE port2 on Intel NIC x710 2p10GE.
        - t3-tg1-c6/p1 - 10GE port1 on Intel NIC x710 2p10GE.
        - t3-tg1-c6/p2 - 10GE port2 on Intel NIC x710 2p10GE.
```

#### 3-Node-Skylake (3n-skx) PROD

```
- ServerB11 [Type-B1]:
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
        - s11-t31-sut1-c9/p1 - FUTURE 100GE-port1 ConnectX5-2p100GE.
        - s11-t31-sut1-c9/p2 - FUTURE 100GE-port2 ConnectX5-2p100GE.
- ServerB12 [Type-B1]:
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
        - s12-t31-sut2-c9/p1 - FUTURE 100GE-port1 ConnectX5-2p100GE.
        - s12-t31-sut2-c9/p2 - FUTURE 100GE-port2 ConnectX5-2p100GE.
- ServerB13 [Type-B2]:
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
        - s13-t31-tg1-c9/p1 - FUTURE 100GE-port1 ConnectX5-2p100GE.
        - s13-t31-tg1-c9/p2 - FUTURE 100GE-port2 ConnectX5-2p100GE.
- ServerB14 [Type-B1]:
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
        - s14-t32-sut1-c9/p1 - FUTURE 100GE-port1 ConnectX5-2p100GE.
        - s14-t32-sut1-c9/p2 - FUTURE 100GE-port2 ConnectX5-2p100GE.
- ServerB15 [Type-B1]:
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
        - s15-t32-sut2-c9/p1 - FUTURE 100GE-port1 ConnectX5-2p100GE.
        - s15-t32-sut2-c9/p2 - FUTURE 100GE-port2 ConnectX5-2p100GE.
- ServerB16 [Type-B2]:
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
        - s16-t32-tg1-c9/p1 - FUTURE 100GE-port1 ConnectX5-2p100GE.
        - s16-t32-tg1-c9/p2 - FUTURE 100GE-port2 ConnectX5-2p100GE.
```

Note: ServerB19 (TG) is shared between testbed33 & testbed34

#### 3-Node-Rangeley (3n-rng) VERIFY

Note: There is no IPMI. Serial console is accessible via VIRL2 and VIRL3 USB.

```
- ServerB22 [Type-B5]:
    - testbedname: testbed35.
    - hostname: s22-t35-sut1 (vex-yul-rot-netgate-1).
    - IPMI IP: 10.30.51.29 - screen -r /dev/ttyUSB0
    - Host IP: 10.30.51.9
    - portnames:
        - s22-t35-sut1-p1 - 10GE-port1 ix0 82599.
        - s22-t35-sut1-p2 - 10GE-port2 ix1 82599.
    - 1GB ports (tbd)
- ServerB23 [Type-B5]:
    - testbedname: testbed35.
    - hostname: s23-t35-sut2 (vex-yul-rot-netgate-2).
    - IPMI IP: 10.30.51.30 - screen -r /dev/ttyUSB1
    - Host IP: 10.30.51.10
    - portnames:
        - s23-t35-sut1-p1 - 10GE-port1 ix0 82599.
        - s23-t35-sut1-p2 - 10GE-port2 ix1 82599.
    - 1GB ports (tbd)
- ServerB24 [Type-B5]:
    - testbedname: testbed35.
    - hostname: s24-t35-sut3 (vex-yul-rot-netgate-3).
    - IPMI IP: 10.30.51.30 - screen -r /dev/ttyUSB2
    - Host IP: 10.30.51.11
    - portnames:
        - s24-t35-sut1-p1 - 10GE-port1 ix0 82599.
        - s24-t35-sut1-p2 - 10GE-port2 ix1 82599.
    - 1GB ports (tbd)
```

#### 3-Node-Taishan (3n-tsh) WIP

```
- ServerB17 [Type-B3]:
    - testbedname: testbed33.
    - hostname: s17-t33-sut1.
    - IPMI IP: 10.30.50.36
    - Host IP: 10.30.51.36
    - portnames:
        - s17-t33-sut1-c6/p1 - 10GE-port1 82599-2p10GE.
        - s17-t33-sut1-c6/p2 - 10GE-port2 82599-2p10GE.
        - s17-t33-sut1-c4/p1 - 25GE-port1 cx4-2p25GE.
        - s17-t33-sut1-c4/p2 - 25GE-port2 cx4-2p25GE.
- ServerB18 [Type-B3]:
    - testbedname: testbed33.
    - hostname: s18-t33-sut2.
    - IPMI IP: 10.30.50.37
    - Host IP: 10.30.51.37
    - portnames:
        - s18-t33-sut2-c6/p1 - 10GE-port1 82599-2p10GE.
        - s18-t33-sut2-c6/p2 - 10GE-port2 82599-2p10GE.
        - s18-t33-sut2-c4/p1 - 25GE-port1 cx4-2p25GE.
        - s18-t33-sut2-c4/p2 - 25GE-port2 cx4-2p25GE.
- ServerB19 [Type-B2]:
    - testbednames: testbed33 and testbed34.
    - hostname: s19-t33t34-tg1.
    - IPMI IP: 10.30.50.46
    - Host IP: 10.30.51.49
    - portnames:
        - s19-t33t34-tg1-c2/p1 - 10GE-port1 x710-4p10GE.
        - s19-t33t34-tg1-c2/p2 - 10GE-port2 x710-4p10GE.
        - s19-t33t34-tg1-c2/p3 - 10GE-port3 x710-4p10GE.
        - s19-t33t34-tg1-c2/p4 - 10GE-port4 x710-4p10GE.
        - s19-t33t34-tg1-c4/p1 - 25GE-port1 xxv710-DA2-2p25GE.
        - s19-t33t34-tg1-c4/p2 - 25GE-port2 xxv710-DA2-2p25GE.
        - s19-t33t34-tg1-c10/p1 - 10GE-port1 x710-4p10GE.
        - s19-t33t34-tg1-c10/p2 - 10GE-port2 x710-4p10GE.
        - s19-t33t34-tg1-c10/p3 - 10GE-port3 x710-4p10GE.
        - s19-t33t34-tg1-c10/p4 - 10GE-port4 x710-4p10GE.
- ServerB20 [Type-B4]:
    - testbedname: testbed34.
    - hostname: s20-t34-sut1.
    - IPMI IP: N/A
    - Host IP: 10.30.51.41
    - portnames:
        - s20-t34-sut1-ca/p1 - 10GE-port1 Marvell.
        - s20-t34-sut1-ca/p2 - 10GE-port2 Marvell.
- ServerB21 [Type-B4]:
    - testbedname: testbed34.
    - hostname: s21-t34-sut2.
    - IPMI IP: N/A
    - Host IP: 10.30.51.42
    - portnames:
        - s21-t34-sut2-ca/p1 - 10GE-port1 Marvell.
        - s21-t34-sut2-ca/p2 - 10GE-port2 Marvell.
```

#### 3-Node-Mcbin (3n-mcb) TODO

```
To be completed.
```

### Per Testbed Wiring

#### 1-Node-Skylake (1n-skx) PROD

```
- testbed11:
    - ring1 10GE-ports x710-4p10GE:
        - s1-t11-sut1-c2/p1 to s1-t11-sut1-c4/p1.
    - ring2 10GE-ports x710-4p10GE:
        - s1-t11-sut1-c2/p2 to s1-t11-sut1-c4/p2.
    - ring3 10GE-ports x710-4p10GE:
        - s1-t11-sut1-c2/p3 to s1-t11-sut1-c4/p3.
    - ring4 10GE-ports x710-4p10GE:
        - s1-t11-sut1-c2/p3 to s1-t11-sut1-c4/p3.
- testbed12:
    - ring1 10GE-ports x710-4p10GE:
        - s2-t12-sut1-c2/p1 to s2-t12-sut1-c4/p1.
    - ring2 10GE-ports x710-4p10GE:
        - s2-t12-sut1-c2/p2 to s2-t12-sut1-c4/p2.
    - ring3 10GE-ports x710-4p10GE:
        - s2-t12-sut1-c2/p3 to s2-t12-sut1-c4/p3.
    - ring4 10GE-ports x710-4p10GE:
        - s2-t12-sut1-c2/p3 to s2-t12-sut1-c4/p3.
```

#### 1-Node-Thunderx2 (1n-tx2) WIP

```
- testbed13:
    - ring1 40GE-ports XL710-QDA2-2p40GE on SUTs:
        - s27-t13-sut1-c1/p2 - s27-t13-sut1-c3/p1.
    - ring2 40GE-ports XL710-QDA2-2p40GE on SUTs:
        - s27-t13-sut1-c3/p2 - s27-t13-sut1-c6/p1.
    - ring3 40GE-ports XL710-QDA2-2p40GE on SUTs:
        - s27-t13-sut1-c6/p2 - s27-t13-sut1-c1/p1.
```

#### 2-Node-Skylake (2n-skx) PROD

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
    - FUTURE ring4 100GE-ports ConnectX5-2p100GE on SUT:
        - s4-t21-tg1-c9/p1 to s3-t21-sut1-c9/p1.
        - s3-t21-sut1-c9/p2 to s4-t21-tg1-c9/p2.
    - ring5 10GE-ports x710-4p10GE loopbacks on TG for self-tests:
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
    - FUTURE ring4 100GE-ports ConnectX5-2p100GE on SUT:
        - t22-tg1-c9/p1 to s5-t22-sut1-c9/p1.
        - s5-t22-sut1-c9/p2 to s6-t22-tg1-c9/p2.
    - ring5 10GE-ports x710-4p10GE loopbacks on TG for self-tests:
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
    - FUTURE ring4 100GE-ports ConnectX5-2p100GE on SUT:
        - s8-t23-tg1-c9/p1 to s7-t23-sut1-c9/p1.
        - s7-t23-sut1-c9/p2 to s8-t23-tg1-c9/p2.
    - ring5 10GE-ports x710-4p10GE loopbacks on TG for self-tests:
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
    - FUTURE ring4 100GE-ports ConnectX5-2p100GE on SUT:
        - s10-t24-tg1-c9/p1 to s9-t24-sut1-c9/p1.
        - s9-t24-sut1-c9/p2 to s10-t24-tg1-c9/p2.
    - ring5 10GE-ports x710-4p10GE loopbacks on TG for self-tests:
        - s10-t24-tg1-c10/p1 to s10-t24-tg1-c10/p2.
        - s10-t24-tg1-c10/p3 to s10-t24-tg1-c10/p4.
```

#### 2-Node-Denverton (2n-dnv) TODO

```
To be completed.
```

#### 2-Node-IxiaPS1L47 (2n-ps1) VERIFY

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

#### 3-Node-Haswell (3n-hsw) PROD

```
 1. testbed1:
    - ring of 40GE ports on Cisco VIC 1385 2p40GE on SUTs
        - t1-tg1-c1/p1 to t1-sut1-c1/p2.
        - t1-sut1-c1/p1 to t1-sut2-c1/p2.
        - t1-sut2-c1/p1 to t1-tg1-c1/p2.
    - ring of 10GE ports on Intel NIC x520 2p10GE on SUTs
        - t1-tg1-c2/p1 to t1-sut1-c2/p2.
        - t1-sut1-c2/p1 to t1-sut2-c2/p2.
        - t1-sut2-c2/p1 to t1-tg1-c2/p2.
    - ring of 40GE ports on Intel NIC xl710 2p40GE on SUTs
        - t1-tg1-c4/p1 to t1-sut1-c4/p2.
        - t1-sut1-c4/p1 to t1-sut2-c4/p2.
        - t1-sut2-c4/p1 to t1-tg1-c4/p2.
    - ring of 10GE ports on Intel NIC x710 2p10GE on SUTs
        - t1-tg1-c5/p1 to t1-sut1-c5/p2.
        - t1-sut1-c5/p1 to t1-sut2-c5/p2.
        - t1-sut2-c5/p1 to t1-tg1-c5/p2.
    - ring of 10GE ports on Cisco VIC 1227 2p10GE on SUTs
        - t1-tg1-c2/p1 to t1-sut1-cm/p2.
        - t1-sut1-cm/p1 to t1-sut2-cm/p2.
        - t1-sut2-cm/p1 to t1-tg1-c2/p2.
    - TG loopback ports Intel NIC x710 2p10GE
        - t1-tg1-c6/p1 to t1-tg1-c6/p2.

 2. testbed2:
    - ring of 40GE ports on Cisco VIC 1385 2p40GE on SUTs
        - t2-tg1-c1/p1 to t2-sut1-c1/p2.
        - t2-sut1-c1/p1 to t2-sut2-c1/p2.
        - t2-sut2-c1/p1 to t2-tg1-c1/p2.
    - ring of 10GE ports on Intel NIC x520 2p10GE on SUTs
        - t2-tg1-c2/p1 to t2-sut1-c2/p2.
        - t2-sut1-c2/p1 to t2-sut2-c2/p2.
        - t2-sut2-c2/p1 to t2-tg1-c2/p2.
    - ring of 40GE ports on Intel NIC xl710 2p40GE on SUTs
        - t2-tg1-c4/p1 to t2-sut1-c4/p2.
        - t2-sut1-c4/p1 to t2-sut2-c4/p2.
        - t2-sut2-c4/p1 to t2-tg1-c4/p2.
    - ring of 10GE ports on Intel NIC x710 2p10GE on SUTs
        - t2-tg1-c5/p1 to t2-sut1-c5/p2.
        - t2-sut1-c5/p1 to t2-sut2-c5/p2.
        - t2-sut2-c5/p1 to t2-tg1-c5/p2.
    - ring of 10GE ports on Cisco VIC 1227 2p10GE on SUTs
        - t2-tg1-c2/p1 to t2-sut1-cm/p2.
        - t2-sut1-cm/p1 to t2-sut2-cm/p2.
        - t2-sut2-cm/p1 to t2-tg1-c2/p2.
    - TG loopback ports Intel NIC x710 2p10GE
        - t2-tg1-c6/p1 to t2-tg1-c6/p2.

 3. testbed3:
    - ring of 40GE ports on Cisco VIC 1385 2p40GE on SUTs
        - t3-tg1-c1/p1 to t3-sut1-c1/p2.
        - t3-sut1-c1/p1 to t3-sut2-c1/p2.
        - t3-sut2-c1/p1 to t3-tg1-c1/p2.
    - ring of 10GE ports on Intel NIC x520 2p10GE on SUTs
        - t3-tg1-c2/p1 to t3-sut1-c2/p2.
        - t3-sut1-c2/p1 to t3-sut2-c2/p2.
        - t3-sut2-c2/p1 to t3-tg1-c2/p2.
    - ring of 40GE ports on Intel NIC xl710 2p40GE on SUTs
        - t3-tg1-c4/p1 to t3-sut1-c4/p2.
        - t3-sut1-c4/p1 to t3-sut2-c4/p2.
        - t3-sut2-c4/p1 to t3-tg1-c4/p2.
    - ring of 10GE ports on Intel NIC x710 2p10GE on SUTs
        - t3-tg1-c5/p1 to t3-sut1-c5/p2.
        - t3-sut1-c5/p1 to t3-sut2-c5/p2.
        - t3-sut2-c5/p1 to t3-tg1-c5/p2.
    - ring of 10GE ports on Cisco VIC 1227 2p10GE on SUTs
        - t3-tg1-c2/p1 to t3-sut1-cm/p2.
        - t3-sut1-cm/p1 to t3-sut2-cm/p2.
        - t3-sut2-cm/p1 to t3-tg1-c2/p2.
    - TG loopback ports Intel NIC x710 2p10GE
        - t3-tg1-c6/p1 to t3-tg1-c6/p2.
```

#### 3-Node-Skylake (3n-skx) PROD

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

#### 3-Node-Rangeley (3n-rng) TODO

```
To be completed.
```

#### 3-Node-Taishan (3n-tsh) WIP

```
- testbed33:
    - ring1 10GE-ports 82599-2p10GE on SUTs:
        - t33t34-tg1-c2/p2 - t33-sut1-c6/p2.
        - t33-sut1-c6/p1 - t33-sut2-c6/p2.
        - t33-sut2-c6/p1 - t33t34-tg1-c2/p1.
    - ring2 25GE-ports cx4-2p25GE on SUTs:
        - t33t34-tg1-c4/p2 - t33-sut1-c4/p2.
        - t33-sut1-c4/p1 - t33-sut2-c4/p2.
        - t33-sut2-c4/p1 - t33t34-tg1-c4/p1.
```

#### 3-Node-Mcbin (3n-mcb) WIP

```
- testbed34:
    - ring1 10GE-ports Marvell on SUTs:
        - t33t34-tg1-c2/p3 - t34-sut1-ca/p1.
        - t34-sut1-ca/p2 - t34-sut2-ca/p1.
        - t34-sut2-ca/p2 - t33t34-tg1-c2/p4.
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

### Arm Servers

```
1. Arm Cortex A-72 servers
    - 1 * ThunderX2
        - Chassis: Marvell ThunderX2
        - Processors: 2* ThunderX2 CN9975 ~ 112* ThunderX2.
        - RAM Memory: 4* 32GB RDIMM
        - Disks: 1* 480GB SSD Micron, 1* 1000GB HDD Seagate_25
    - 2 * Huawei TaiShan 2280.
        - Chassis: Huawei TaiShan 2280.
        - Processors: 1* hip07-d05 ~ 64* Arm Cortex-A72.
        - RAM Memory: 8* 16GB DDR4-2400MT/s.
        - Disks: 1* 4TB SATA HDD.
    - 3 * MACCHIATObin
        - Chassis: MACCHIATObin.
        - Processors: 1* Armada 8040 ~ 4* Arm Cortex-A72.
        - RAM Memory: 1* 16GB DDR4.
        - Disks: 1* 128GB(?) SATA SDD.
```

### Xeon and Atom Servers

```
1. Intel Xeon servers:
    - 20 * SuperMicro SYS-7049GP-TRT with Xeon Skylake processors.
        - Chassis: SuperMicro SYS-7049GP-TRT.
        - Motherboard: SuperMicro X11DPG-QT.
        - Processors: 2* Intel Platinum 8180 2.3 GHz.
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
