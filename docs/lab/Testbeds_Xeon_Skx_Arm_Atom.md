## FD.io CSIT testbeds - Xeon Skylake, Arm, Atom
This is a low-level design implemented as an extensions of FD.io CSIT lab to accommodate the new Intel Xeon Skylake, Arm AArch64 and Atom devices. Content has been copied from [FD.io CSIT testbeds wiki page: Xeon_skx, Arm, Atom](https://wiki.fd.io/view/CSIT/Testbeds:_Xeon_Skx,_Arm,_Atom).

## Testbeds Overview
### Testbeds Type Breakdown
```
 #.  CSIT_tb.           Purpose.    SUT.  TG.   #tb.  #SUTs.  #TGs. #skx_node.
 1.  1-node Xeon.       func.       skx.  n/a.  2.    2.      0.    2.
 2.  2-node Xeon.       perf.       skx.  skx.  4.    4.      4.    8.
 3.  3-node Xeon.       perf.       skx.  skx.  2.    4.      2.    6.
 4.  tcp-l47.           tcp-stack.  skx.  ps1.  1.    1.      1.    1.
 5.  atom-netgate.      perf+func.  net.  skx.  1.    3.      1.    1.
 6.  aarch64-d05        perf+func.  arm.  skx.  2.    2.      1.    1.
 7.  aarch64-mcbin      perf        arm.  skx.  1.    2.      1.    1.
                                                 Total skx_node:   20.
```

### 1-Node Xeon Testbeds
One 1-node Xeon testbed for VPP_Device tests is built using one SUT (Type-6 server), with NIC ports connected back-to-back.

### 2-Node Xeon Testbeds
Four 2-node Xeon testbeds (are expected to be built|are built), with each testbed using one SUTs (Type-1 server) and one TG (Type-2 server) connected back-to-back. NIC cards placement into slots and NIC ports connectivity is following the testbed specification included in next sections.

### 3-Node Xeon Testbeds
Two 3-node Xeon testbeds (are expected to be built|are built), with each testbed using two SUTs (Type-1 server) and one TG (Type-2 server) connected in full-mesh triangle. NIC cards placement into slots and NIC ports connectivity is following the testbed specification included in next sections.

### Arm Testbeds
One 3-node Huawei testbeds (are expected to be built|are built), with each testbed using two SUTs (Type-3 server) and one TG (Type-2 server) connected in full-mesh triangle.

One 3-node Marvell testbeds (are expected to be built|are built), with each testbed using two SUTs (Type-4 server) and one TG (Type-2 server) connected in full-mesh triangle.

### TCP/IP and L47 Testbeds
One 2-node Ixia PS One and Xeon server testbed, for TCP/IP host stack tests.

### Atom Testbeds
One 3-node Atom (Netgate based) testbed is built consisting of three SUTs (Type-5 Netgate device.) NIC cards placement into slots and NIC ports connectivity is following the testbed specification included in the next section.

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

Platform Name and Specification | Role | Status | Hostname | IP | IPMI | Cores | RAM | Ethernet | Distro
------------------------------- | ---- | ------ | -------- | -- | ---- | ----- | --- | -------- | ------
[SoftIron OverDrive 1000](https://softiron.com/development-tools/overdrive-1000/) | CI build server | Up, Not Running Jobs | softiron-1 | 10.30.51.12 | N/A | 4 | 8GB |  | openSUSE
  | CI build server | Up, Not Running Jobs | softiron-2 | 10.30.51.13 | N/A | 4 | 8GB |   | openSUSE
  | CI build server | Up, Not Running Jobs | softiron-3 | 10.30.51.14 | N/A | 4 | 8GB |   | openSUSE
[Cavium ThunderX](https://cavium.com/product-thunderx-arm-processors.html) | CI build server | Up, Running VPP CI | nomad3arm | 10.30.51.38 | 10.30.50.38 | 96 | 128GB | 3x40GbE QSFP+ / 4x10GbE SFP+ | Ubuntu 16.04
  | CI build server | Up, Running VPP CI | nomad4arm | 10.30.51.39 | 10.30.50.39 | 96 | 128GB | 3x40GbE QSFP+ / 4x10GbE SFP+ | Ubuntu 16.04
  | CI build server | Up, Running VPP CI | nomad5arm | 10.30.51.40 | 10.30.50.40 | 96 | 128GB | 3x40GbE QSFP+ / 4x10GbE SFP+ | Ubuntu 16.04
  | CI build server | Up, Not Running Jobs, USB_NIC broken, QSFP wiring to be added | fdio-cavium4 | 10.30.51.65 | 10.30.50.65 | 96 | 256GB | 2xQSFP+ / USB Ethernet | Ubuntu 18.04.1
  | VPP dev debug | Up | fdio-cavium5 | 10.30.51.66 | 10.30.50.66 | 96 | 256GB | 2xQSFP+ / USB Ethernet | Ubuntu 18.04.1
  | CI build server | Up, Not Running Jobs, USB_NIC broken, QSFP wiring to be added | fdio-cavium6 | 10.30.51.67 | 10.30.50.67 | 96 | 256GB | 2xQSFP+ / USB Ethernet | Ubuntu 16.04.1
  | VPP dev debug | Up | fdio-cavium7 | 10.30.51.68 | 10.30.50.68 | 96 | 256GB | 2xQSFP+ / USB Ethernet | Ubuntu 16.04.1
Huawei TaiShan 2280 | CSIT Performance | Up, Manual perf experiments | s17-t33-sut1 | 10.30.51.36 | 10.30.50.36 | 64 | 128GB | 2x10GbE SFP+ Intel 82599 / 2x25GbE SFP28 Mellanox CX-4 | Ubuntu 17.10
  | CSIT Performance | Up, Manual perf experiments | s18-t33-sut2 | 10.30.51.37 | 10.30.50.37 | 64 | 128GB | 2x10GbE SFP+ Intel 82599 / 2x25GbE SFP28 Mellanox CX-4 | Ubuntu 17.10
[Marvell MACCHIATObin](http://macchiatobin.net/) | CSIT Performance | Up, Manual experiments, Full Skx TG too much for it - suggest to use LXC/DRC TG(!) | s20-t34-sut1 | 10.30.51.41 | 10.30.51.49, then connect to /dev/ttyUSB0 | 4 | 16GB | 2x10GbE SFP+ | Ubuntu 16.04.4
  | CSIT Performance | Up, Manual experiments, Full Skx TG too much for it - suggest to use LXC/DRC TG(!) | s21-t34-sut2 | 10.30.51.42 | 10.30.51.49, then connect to /dev/ttyUSB1 | 4 | 16GB | 2x10GbE SFP+ | Ubuntu 16.04.5
  | VPP dev debug | Up, Manual VPP Device experiments, Full Skx TG too much for it - suggest to use LXC/DRC TG(!) | fdio-mcbin3 | 10.30.51.43 | 10.30.51.49, then connect to /dev/ttyUSB2 | 4 | 16GB | 2x10GbE SFP+ | Ubuntu 16.04.5

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

### Other Network Cards
Any QATs?

## Installation Status
Lab installation status is tracked by LF IT team in [FD.io Server Status](https://docs.google.com/document/d/16TdvGC73wuNQjkP355MTXRckv7yqnaxJkWwX7G7izEo/edit?ts=5b10411b#heading=h.dprb64shku8u).

## Server/Device Management and Naming
### Server Management Requirements
Total of 20 SM SYS-7049GP-TRT servers are made available for FD.IO CSIT testbed.
For management purposes, each server must have following two ports connected to the management network:
```
- 1GE IPMI port
  - IPMI - Intelligent Platform Management Interface.
  - Required for access to embedded server management with WebUI, CLI, SNMPv3, IPMIv2.0, for firmware (BIOS) and OS updates.
- 1GE/10GE management port
  - hostOS management port for general system management.
```

### Server and Port Naming Convention
Following naming convention is used within this page to specify physical connectivity and wiring across defined CSIT testbeds:
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
        - Y=2,4,9 - slots connected to NUMA node 0.
        - Y=6,8,10 - slots connected to NUMA node 1.
    - Z - port number on the NIC card.
```

### Server Management - Addressing
Each server has a LOM (Lights-Out-Management e.g. SM IPMI) and a Management port, which are connected to two different VLANs.
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
To access these hosts, an VPN connection is required.

### LOM (IPMI) VLAN IP Addresses
..

### Management VLAN IP Addresses
..

## Testbeds Specification - Target Build
### Server/Ports Naming, NIC Placement
#### 1-Node Xeon
Each server in 1-node Xeon topology has its NIC cards placed, and NIC cards and ports indexed per following specification:
```
- Server1 [Type-6]:
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
- Server2 [Type-6]:
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

#### 2-Node Xeon
Each server in 2-node Xeon topology has its NIC cards placed, and NIC cards and ports indexed per following specification:
```
- Server3 [Type-1]:
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
- Server4 [Type-2]:
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
- Server5 [Type-1]:
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
- Server6 [Type-2]:
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
- Server7 [Type-1]:
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
- Server8 [Type-2]:
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
- Server9 [Type-1]:
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
- Server10 [Type-2]:
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

#### 3-Node Xeon
Each server in 3-node Xeon topology has its NIC cards placed, and NIC cards and ports indexed per following specification:
```
- Server11 [Type-1]:
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
- Server12 [Type-1]:
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
- Server13 [Type-2]:
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
- Server14 [Type-1]:
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
- Server15 [Type-1]:
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
- Server16 [Type-2]:
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

#### 3-Node Arm
Note: Server19 (TG) is shared between testbed33 & testbed34
```
- Server17 [Type-3]:
    - testbedname: testbed33.
    - hostname: s17-t33-sut1.
    - IPMI IP: 10.30.50.36
    - Host IP: 10.30.51.36
    - portnames:
        - s17-t33-sut1-c6/p1 - 10GE-port1 82599-2p10GE.
        - s17-t33-sut1-c6/p2 - 10GE-port2 82599-2p10GE.
        - s17-t33-sut1-c4/p1 - 25GE-port1 cx4-2p25GE.
        - s17-t33-sut1-c4/p2 - 25GE-port2 cx4-2p25GE.
- Server18 [Type-3]:
    - testbedname: testbed33.
    - hostname: s18-t33-sut2.
    - IPMI IP: 10.30.50.37
    - Host IP: 10.30.51.37
    - portnames:
        - s18-t33-sut2-c6/p1 - 10GE-port1 82599-2p10GE.
        - s18-t33-sut2-c6/p2 - 10GE-port2 82599-2p10GE.
        - s18-t33-sut2-c4/p1 - 25GE-port1 cx4-2p25GE.
        - s18-t33-sut2-c4/p2 - 25GE-port2 cx4-2p25GE.
- Server19 [Type-2]:
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
- Server20 [Type-4]:
    - testbedname: testbed34.
    - hostname: s20-t34-sut1.
    - IPMI IP: N/A
    - Host IP: 10.30.51.41
    - portnames:
        - s20-t34-sut1-ca/p1 - 10GE-port1 Marvell.
        - s20-t34-sut1-ca/p2 - 10GE-port2 Marvell.
- Server21 [Type-4]:
    - testbedname: testbed34.
    - hostname: s21-t34-sut2.
    - IPMI IP: N/A
    - Host IP: 10.30.51.42
    - portnames:
        - s21-t34-sut2-ca/p1 - 10GE-port1 Marvell.
        - s21-t34-sut2-ca/p2 - 10GE-port2 Marvell.
```

#### TCP/IP and L47
Each server (appliance) in 2-node TCP/IP topology has its NIC cards placed, and NIC cards and ports indexed per following specification:
```
- Server25 [Type-8]:
    - testbedname: testbed25.
    - hostname: s25-t25-sut1.
    - IPMI IP: 10.30.50.58
    - Host IP: 10.30.51.61
    - portnames:
        - s25-t25-sut1-c2/p1 - 10GE-port1 x710-4p10GE.
        - s25-t25-sut1-c2/p2 - 10GE-port2 x710-4p10GE.
        - s25-t25-sut1-c2/p3 - 10GE-port3 x710-4p10GE.
        - s25-t25-sut1-c2/p4 - 10GE-port4 x710-4p10GE.
- Server26 [Type-7]:
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

#### 3-Node Atom
Note: There is no IPMI. Serial console is accessible via VIRL2 and VIRL3 USB.
```
- Server22 [Type-5]:
    - testbedname: testbed35.
    - hostname: s22-t35-sut1 (vex-yul-rot-netgate-1).
    - IPMI IP: 10.30.51.29 - screen -r /dev/ttyUSB0
    - Host IP: 10.30.51.9
    - portnames:
        - s22-t35-sut1-p1 - 10GE-port1 ix0 82599.
        - s22-t35-sut1-p2 - 10GE-port2 ix1 82599.
    - 1GB ports (tbd)
- Server23 [Type-5]:
    - testbedname: testbed35.
    - hostname: s23-t35-sut2 (vex-yul-rot-netgate-2).
    - IPMI IP: 10.30.51.30 - screen -r /dev/ttyUSB1
    - Host IP: 10.30.51.10
    - portnames:
        - s23-t35-sut1-p1 - 10GE-port1 ix0 82599.
        - s23-t35-sut1-p2 - 10GE-port2 ix1 82599.
    - 1GB ports (tbd)
- Server24 [Type-5]:
    - testbedname: testbed35.
    - hostname: s24-t35-sut3 (vex-yul-rot-netgate-3).
    - IPMI IP: 10.30.51.30 - screen -r /dev/ttyUSB2
    - Host IP: 10.30.51.11
    - portnames:
        - s24-t35-sut1-p1 - 10GE-port1 ix0 82599.
        - s24-t35-sut1-p2 - 10GE-port2 ix1 82599.
    - 1GB ports (tbd)
```

### Physical Connectivity within Testbeds
#### 1-Node Xeon
Two 1-Node testbeds are constructed by connecting 2 Xeon servers using below specification:
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

#### 2-Node Xeon
Four 2-Node testbeds are constructed by connecting 8 Xeon servers using below specification:
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

#### 3-Node Xeon
Two 3-Node testbeds are constructed by connecting 6 Xeon servers using below specification:
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

#### 3-Node Arm
One 3-Node testbed is constructed by connecting 2 Arm servers with one Xeon server.
So we have testbed33 with two Arm TaiShan servers and one shared Xeon server and 
testbed34 with two Arm MACCHIATObin servers and the same one shared Xeon server.
These 4 Arm servers and 1 Xeon server are connected using below specifications:
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
- testbed34:
    - ring1 10GE-ports Marvell on SUTs:
        - t33t34-tg1-c2/p3 - t34-sut1-ca/p1.
        - t34-sut1-ca/p2 - t34-sut2-ca/p1.
        - t34-sut2-ca/p2 - t33t34-tg1-c2/p4.
```

#### TCP/IP and L47
One 2-Node TCP/IP testbed is constructed by connecting Ixia PSOne and 1 Xeon server using below specification:
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

#### 3-Node Atom
..

## Server Specification
### Hardware Configuration
The new FD.io CSIT-CPL lab (is expected to contain|contains) following hardware server configurations:
```
1. Type-1: Purpose - (Intel Xeon Processor) SUT for SW Data Plane Workload i.e. VPP, testpmd.
    - Quantity: TBD based on testbed allocation.
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
2. Type-2: Purpose - (Intel Xeon Processor) TG for T-Rex.
    - Quantity: TBD based on testbed allocation.
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
3. Type-3: Purpose - (Arm hip07-d05 Processor) SUT for SW Data Plane Workload i.e. VPP, testpmd.
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
4. Type-4: Purpose - (Arm Armada 8040 Processor) SUT for SW Data Plane Workload i.e. VPP, testpmd.
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
5. Type-5: Purpose - (Intel Atom Processor) SUT for SW Data Plane Workload i.e. VPP, testpmd.
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
6. Type-6: Purpose - (Intel Xeon Processor) SUT for VPP_Device functional tests.
    - Quantity: 1.
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
7. Type-7: Purpose - Ixia PerfectStorm One Appliance TG for TCP/IP performance tests.
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
8. Type-8: Purpose - (Intel Xeon Processor) SUT for TCP/IP host stack tests.
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
9. Type-9: Purpose - (Cavium ThunderX2 Processor) SUT for VPP_Device functional tests.
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
        - PCIe Slotx <TBD>: XL710-QDA2.
        - PCIe Sloty <TBD>: XL710-QDA2.
  - PCIe Slotz <TBD>: XL710-QDA2.
10. Type-10: Purpose - (Intel Atom C3000 Processor) SUT for SW Data Plane Workload i.e. VPP, testpmd.
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
