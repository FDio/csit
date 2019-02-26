## FD.io CSIT Testbeds - Xeon Haswell

This is a low-level design implemented as an original FD.io CSIT lab based on
Cisco UCS-c240m4 servers based on Intel Xeon Haswell processors.

### Server Hardware Configuration

Total of 10 Cisco UCS-c240 servers with Intel Xeon Haswell processors have been
used to built FD.io CSIT 3-Node Haswell (3n-hsw) performance testbeds and VIRL
functional testbeds. Following three HW configuration types of UCS x86 servers
are used:

```
 1. Type-1: Purpose - VPP functional and performance conformance testing.
    - Quantity: 6 computers as SUT hosts (Systems Under Test).
    - Physical connectivity:
        - CIMC and host management ports.
        - NIC ports connected in 3-node topologies.
    - Main HW configuration:
        - Chassis: UCSC-C240-M4SX with 6 PCIe3.0 slots.
        - Processors: 2* E5-2699v3 2.3 GHz.
        - RAM Memory: 16* 32GB DDR4-2133MHz.
        - Disks: 2* 2TB 12G SAS 7.2K RPM SFF HDD.
    - NICs configuration:
        - Right PCIe Riser Board (Riser 1) (x8, x8, x8 PCIe3.0 lanes)
            - PCIe Slot1: Cisco VIC 1385 2p40GE.
            - PCIe Slot2: Intel NIC x520 2p10GE.
            - PCIe Slot3: empty.
        - Left PCIe Riser Board (Riser 2) (x8, x16, x8 PCIe3.0 lanes)
            - PCIe Slot4: Intel NIC xl710 2p40GE.
            - PCIe Slot5: Intel NIC x710 2p10GE.
            - PCIe Slot6: Intel QAT 8950 50G (Walnut Hill)
        - MLOM slot: Cisco VIC 1227 2p10GE (x8 PCIe2.0 lanes).
 2. Type-2: Purpose - VPP functional and performance conformance testing.
    - Quantity: 3 computers as TG hosts (Traffic Generators).
    - Physical connectivity:
        - CIMC and host management ports.
        - NIC ports connected in 3-node topologies.
    - Main HW configuration:
        - Chassis: UCSC-C240-M4SX with 6 PCIe3.0 slots.
        - Processors: 2* E5-2699v3 2.3 GHz.
        - RAM Memory: 16* 32GB DDR4-2133MHz.
        - Disks: 2* 2TB 12G SAS 7.2K RPM SFF HDD.
    - NICs configuration:
        - Right PCIe Riser Board (Riser 1) (x8, x8, x8 lanes)
            - PCIe Slot1: Intel NIC xl710 2p40GE.
            - PCIe Slot2: Intel NIC x710 2p10GE.
            - PCIe Slot3: Intel NIC x710 2p10GE.
        - Left PCIe Riser Board (Riser 2) (x8, x16, x8 lanes)
            - PCIe Slot4: Intel NIC xl710 2p40GE.
            - PCIe Slot5: Intel NIC x710 2p10GE.
            - PCIe Slot6: Intel NIC x710 2p10GE.
        - MLOM slot: empty.
 3. Type-3: Purpose - VIRL functional conformance.
    - Quantity: 3 computers as VIRL hosts.
    - Physical connectivity:
        - CIMC and host management ports.
        - no NIC ports, standalone setup.
    - Main HW configuration:
        - Chassis: UCSC-C240-M4SX with 6 PCIe3.0 slots.
        - Processors: 2* E5-2699v3 2.3 GHz.
        - RAM Memory: 16* 32GB DDR4-2133MHz.
        - Disks: 2* 480 GB 2.5inch 6G SATA SSD.
    - NICs configuration:
        - Right PCIe Riser Board (Riser 1) (x8, x8, x8 lanes)
            - no cards.
        - Left PCIe Riser Board (Riser 2) (x8, x16, x8 lanes)
            - no cards.
        - MLOM slot: empty.
```

## Testbeds1,2,3 Connectivity

### Management Ports

Total of 10 UCSC-C240-M4SX servers is made available for FD.IO CSIT testbed. For
management purposes, each server must have following two ports connected to the
management network:

```
 1. 1GE CIMC port
    - CIMC - Cisco Integrated Management Controller.
    - Required for provides embedded server management with WebUI, CLI, SNMPv3,
      IPMIv2.0.
 2. 1GE management port
    - hostOS management port.
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
        - Y=1,2,3 - slots in Riser 1, Right PCIe Riser Board, NUMA node 0.
        - Y=4,5,6 - slots in Riser 2, Left PCIe Riser Board, NUMA node 1.
        - Y=m - the MLOM slot.
    - Z - port number on the NIC card.
```

### 3-node Topology Testbeds for Performance

Nine servers are used to build three of 3-node topologies, with each topology
using two servers of Type-1 (SUT function) and one server of Type-2
(TG function). Server NIC cards are placed and NIC ports are connected using the
scheme defined in next sections.

### LOM (CIMC) and Management networks

Each server has a LOM (Lights-Out-Management e.g. Cisco CIMC) and a Management
port, which are connected to two different VLANs.

```
 1. LOM (CIMC) VLAN:
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

#### LOM (CIMC) VLAN IP Addresses allocation

Name | Comment
---- | -------
10.30.50.0 | network
10.30.51.1 | Router
10.30.50.2 | LF Reserved
10.30.50.3 | LF Reserved
10.30.50.4 | LF Reserved
10.30.50.5 | LF Reserved
10.30.50.6 | LF Reserved
10.30.50.7 | LF Reserved
10.30.50.8 | LF Reserved
10.30.50.9 | LF Reserved
10.30.50.10 | LF Reserved
10.30.50.11 | LF Reserved
10.30.50.12 | LF Reserved
10.30.50.13 | LF Reserved
10.30.50.14 | LF Reserved
10.30.50.15 | LF Reserved
10.30.50.16 | t1-tg1
10.30.50.17 | t1-sut1
10.30.50.18 | t1-sut2
10.30.50.20 | t2-tg1
10.30.50.21 | t2-sut1
10.30.50.22 | t2-sut2
10.30.50.24 | t3-tg1
10.30.50.25 | t3-sut1
10.30.50.26 | t3-sut-2
10.30.50.28 | t4-sut1
10.30.50.29 | t4-sut2
10.30.50.30 | t4-sut3
10.30.50.255 | Broadcast

#### Management VLAN IP Addresses allocation

Name | Comment
---- | -------
10.30.51.0 | network
10.30.51.1 | Router
10.30.51.2 | LF Reserved
10.30.51.3 | LF Reserved
10.30.51.4 | LF Reserved
10.30.51.5 | LF Reserved
10.30.51.6 | LF Reserved
10.30.51.7 | LF Reserved
10.30.51.8 | LF Reserved
10.30.51.9 | netgate-1
10.30.51.10 | netgate-2
10.30.51.11 | netgate-3
10.30.51.12 | softiron-1
10.30.51.13 | softiron-2
10.30.51.14 | softiron-3
10.30.51.15 | LF Reserved
10.30.51.16 | t1-tg1
10.30.51.17 | t1-sut1
10.30.51.18 | t1-sut2
10.30.51.20 | t2-tg1
10.30.51.21 | t2-sut1
10.30.51.22 | t2-sut2
10.30.51.24 | t3-tg1
10.30.51.25 | t3-sut1
10.30.51.26 | t3-sut-2
10.30.51.28 | t4-sut1
10.30.51.29 | t4-sut2
10.30.51.30 | t4-sut3
10.30.51.31-10.30.51.105 | VIRL1
10.30.51.106-10.30.51.180 | VIRL2
10.30.51.181-10.30.51.254 | VIRL3
10.30.51.255 | Broadcast

### Testbeds1,2,3 Naming: Servers, Ports

Each server in 3-node Topology has its NIC cards placed, and NIC cards and ports
indexed using defined naming convention:

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

### Testbeds1,2,3 Network Connectivity

Listed nine servers are connected into the three of 3-node testbeds, testbed1,
testbed2 and testbed3, using defined naming convention as follows:

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

## Testbeds1,2,3 Server Specifications

### Linux lscpu

```
 $ lscpu
 Architecture:          x86_64
 CPU op-mode(s):        32-bit, 64-bit
 Byte Order:            Little Endian
 CPU(s):                36
 On-line CPU(s) list:   0-35
 Thread(s) per core:    1
 Core(s) per socket:    18
 Socket(s):             2
 NUMA node(s):          2
 Vendor ID:             GenuineIntel
 CPU family:            6
 Model:                 63
 Model name:            Intel(R) Xeon(R) CPU E5-2699 v3 @ 2.30GHz
 Stepping:              2
 CPU MHz:               2294.249
 BogoMIPS:              4589.82
 Virtualization:        VT-x
 L1d cache:             32K
 L1i cache:             32K
 L2 cache:              256K
 L3 cache:              46080K
 NUMA node0 CPU(s):     0-17
 NUMA node1 CPU(s):     18-35
 Flags:                 fpu vme de pse tsc msr pae mce cx8 apic sep mtrr pge mca cmov pat pse36 clflush dts acpi mmx fxsr sse sse2 ss ht tm pbe syscall nx pdpe1gb rdtscp lm constant_tsc arch_perfmon pebs bts rep_good nopl xtopology nonstop_tsc aperfmperf eagerfpu pni pclmulqdq
 dtes64 monitor ds_cpl vmx smx est tm2 ssse3 sdbg fma cx16 xtpr pdcm pcid dca sse4_1 sse4_2 x2apic movbe popcnt tsc_deadline_timer aes xsave avx f16c rdrand lahf_lm abm epb tpr_shadow vnmi flexpriority ept vpid fsgsbase tsc_adjust bmi1 avx2 smep bmi2 erms invpcid cqm xsaveopt
 cqm_llc cqm_occup_llc dtherm arat pln pts
```

### Linux dmidecode pci

```
 $ dmidecode --type 9 | grep 'Handle\|Slot\|Type\|Address'
 Handle 0x0046, DMI type 9, 17 bytes
 System Slot Information
     Designation: SlotID:1
     Type: x8 PCI Express 3 x8
     Bus Address: 0000:0a:02.0
 Handle 0x0047, DMI type 9, 17 bytes
 System Slot Information
     Designation: SlotID:2
     Type: x8 PCI Express 3 x8
     Bus Address: 0000:0e:03.2
 Handle 0x0048, DMI type 9, 17 bytes
 System Slot Information
     Designation: SlotID:3
     Type: x8 PCI Express 3 x8
     Bus Address: 0000:0d:03.0
 Handle 0x0049, DMI type 9, 17 bytes
 System Slot Information
     Designation: SlotID:4
     Type: x8 PCI Express 3 x8
     Bus Address: 0000:85:02.2
 Handle 0x004A, DMI type 9, 17 bytes
 System Slot Information
     Designation: SlotID:5
     Type: x8 PCI Express 3 x16
     Bus Address: 0000:87:03.0
 Handle 0x004B, DMI type 9, 17 bytes
 System Slot Information
     Designation: SlotID:6
     Type: x8 PCI Express 3 x8
     Bus Address: 0000:84:02.0
 Handle 0x004C, DMI type 9, 17 bytes
 System Slot Information
     Designation: SlotID:MLOM
     Type: x8 Other
     Bus Address: 0000:01:01.0
 Handle 0x004D, DMI type 9, 17 bytes
 System Slot Information
     Designation: SlotID:HBA
     Type: x8 Other
     Bus Address: 0000:0c:02.2
 Handle 0x004E, DMI type 9, 17 bytes
 System Slot Information
     Designation: SlotID:NVMe1
     Type: x4 PCI Express 3 x4
     Bus Address: 0000:82:01.0
 Handle 0x004F, DMI type 9, 17 bytes
 System Slot Information
     Designation: SlotID:NVMe2
     Type: x4 PCI Express 3 x4
     Bus Address: 0000:83:01.1
 Handle 0x0050, DMI type 9, 17 bytes
 System Slot Information
     Designation: SlotID:2.1
     Type: x16 PCI Express 3 x16
     Bus Address: 0000:00:1f.7
 Handle 0x0051, DMI type 9, 17 bytes
 System Slot Information
     Designation: SlotID:2.2
     Type: x16 PCI Express 3 x16
     Bus Address: 0000:00:1f.7
 Handle 0x0052, DMI type 9, 17 bytes
 System Slot Information
     Designation: SlotID:2.3
     Type: x16 PCI Express 3 x16
     Bus Address: 0000:00:1f.7
 Handle 0x0053, DMI type 9, 17 bytes
 System Slot Information
     Designation: SlotID:2.4
     Type: x16 PCI Express 3 x16
     Bus Address: 0000:00:1f.7
 Handle 0x0054, DMI type 9, 17 bytes
 System Slot Information
     Designation: SlotID:2.5
     Type: x16 PCI Express 3 x16
     Bus Address: 0000:00:1f.7
 Handle 0x0055, DMI type 9, 17 bytes
 System Slot Information
     Designation: SlotID:5.1
     Type: x8 PCI Express 3 x16
     Bus Address: 0000:00:1f.7
 Handle 0x0056, DMI type 9, 17 bytes
 System Slot Information
     Designation: SlotID:5.2
     Type: x8 PCI Express 3 x16
     Bus Address: 0000:00:1f.7
 Handle 0x0057, DMI type 9, 17 bytes
 System Slot Information
     Designation: SlotID:5.3
     Type: x8 PCI Express 3 x16
     Bus Address: 0000:00:1f.7
 Handle 0x0058, DMI type 9, 17 bytes
 System Slot Information
     Designation: SlotID:5.4
     Type: x8 PCI Express 3 x16
     Bus Address: 0000:00:1f.7
 Handle 0x0059, DMI type 9, 17 bytes
 System Slot Information
     Designation: SlotID:5.5
     Type: x8 PCI Express 3 x16
     Bus Address: 0000:00:1f.7
```

### Linux dmidecode memory

```
 $ dmidecode -t memory
 # dmidecode 2.12
 SMBIOS 2.8 present.

 Handle 0x0022, DMI type 16, 23 bytes
 Physical Memory Array
     Location: System Board Or Motherboard
     Use: System Memory
     Error Correction Type: Multi-bit ECC
     Maximum Capacity: 1536 GB
     Error Information Handle: Not Provided
     Number Of Devices: 24

 Handle 0x0024, DMI type 17, 34 bytes
 Memory Device
     Array Handle: 0x0022
     Error Information Handle: Not Provided
     Total Width: 72 bits
     Data Width: 64 bits
     Size: 32 GB
     Form Factor: DIMM
     Set: None
     Locator: DIMM_A1
     Bank Locator: NODE 0 CHANNEL 0 DIMM 0
     Type: Other
     Type Detail: None
     Speed: 2133 MHz
     Manufacturer: 0xAD00
     Serial Number: 80EC7380
     Asset Tag: DIMM_A1_AssetTag
     Part Number: HMA84GL7MMR4N-TF
     Rank: 4
     Configured Clock Speed: 2133 MHz

 Handle 0x0025, DMI type 17, 34 bytes
 Memory Device
     Array Handle: 0x0022
     Error Information Handle: Not Provided
     Total Width: 72 bits
     Data Width: 64 bits
     Size: 32 GB
     Form Factor: DIMM
     Set: None
     Locator: DIMM_A2
     Bank Locator: NODE 0 CHANNEL 0 DIMM 1
     Type: Other
     Type Detail: None
     Speed: 2133 MHz
     Manufacturer: 0xAD00
     Serial Number: 80EC73D1
     Asset Tag: DIMM_A2_AssetTag
     Part Number: HMA84GL7MMR4N-TF
     Rank: 4
     Configured Clock Speed: 2133 MHz

 Handle 0x0026, DMI type 17, 34 bytes
 Memory Device
     Array Handle: 0x0022
     Error Information Handle: Not Provided
     Total Width: Unknown
     Data Width: Unknown
     Size: No Module Installed
     Form Factor: DIMM
     Set: None
     Locator: DIMM_A3
     Bank Locator: NODE 0 CHANNEL 0 DIMM 2
     Type: Other
     Type Detail: None
     Speed: Unknown
     Manufacturer: NO DIMM
     Serial Number: NO DIMM
     Asset Tag: NO DIMM
     Part Number: NO DIMM
     Rank: Unknown
     Configured Clock Speed: Unknown

 Handle 0x0027, DMI type 17, 34 bytes
 Memory Device
     Array Handle: 0x0022
     Error Information Handle: Not Provided
     Total Width: 72 bits
     Data Width: 64 bits
     Size: 32 GB
     Form Factor: DIMM
     Set: None
     Locator: DIMM_B1
     Bank Locator: NODE 0 CHANNEL 1 DIMM 0
     Type: Other
     Type Detail: None
     Speed: 2133 MHz
     Manufacturer: 0xAD00
     Serial Number: 80EC7325
     Asset Tag: DIMM_B1_AssetTag
     Part Number: HMA84GL7MMR4N-TF
     Rank: 4
     Configured Clock Speed: 2133 MHz

 Handle 0x0028, DMI type 17, 34 bytes
 Memory Device
     Array Handle: 0x0022
     Error Information Handle: Not Provided
     Total Width: 72 bits
     Data Width: 64 bits
     Size: 32 GB
     Form Factor: DIMM
     Set: None
     Locator: DIMM_B2
     Bank Locator: NODE 0 CHANNEL 1 DIMM 1
     Type: Other
     Type Detail: None
     Speed: 2133 MHz
     Manufacturer: 0xAD00
     Serial Number: 80EC7334
     Asset Tag: DIMM_B2_AssetTag
     Part Number: HMA84GL7MMR4N-TF
     Rank: 4
     Configured Clock Speed: 2133 MHz

 Handle 0x0029, DMI type 17, 34 bytes
 Memory Device
     Array Handle: 0x0022
     Error Information Handle: Not Provided
     Total Width: Unknown
     Data Width: Unknown
     Size: No Module Installed
     Form Factor: DIMM
     Set: None
     Locator: DIMM_B3
     Bank Locator: NODE 0 CHANNEL 1 DIMM 2
     Type: Other
     Type Detail: None
     Speed: Unknown
     Manufacturer: NO DIMM
     Serial Number: NO DIMM
     Asset Tag: NO DIMM
     Part Number: NO DIMM
     Rank: Unknown
     Configured Clock Speed: Unknown

 Handle 0x002A, DMI type 17, 34 bytes
 Memory Device
     Array Handle: 0x0022
     Error Information Handle: Not Provided
     Total Width: 72 bits
     Data Width: 64 bits
     Size: 32 GB
     Form Factor: DIMM
     Set: None
     Locator: DIMM_C1
     Bank Locator: NODE 0 CHANNEL 2 DIMM 0
     Type: Other
     Type Detail: None
     Speed: 2133 MHz
     Manufacturer: 0xAD00
     Serial Number: 80EC7329
     Asset Tag: DIMM_C1_AssetTag
     Part Number: HMA84GL7MMR4N-TF
     Rank: 4
     Configured Clock Speed: 2133 MHz

 Handle 0x002B, DMI type 17, 34 bytes
 Memory Device
     Array Handle: 0x0022
     Error Information Handle: Not Provided
     Total Width: 72 bits
     Data Width: 64 bits
     Size: 32 GB
     Form Factor: DIMM
     Set: None
     Locator: DIMM_C2
     Bank Locator: NODE 0 CHANNEL 2 DIMM 1
     Type: Other
     Type Detail: None
     Speed: 2133 MHz
     Manufacturer: 0xAD00
     Serial Number: 80EC732D
     Asset Tag: DIMM_C2_AssetTag
     Part Number: HMA84GL7MMR4N-TF
     Rank: 4
     Configured Clock Speed: 2133 MHz

 Handle 0x002C, DMI type 17, 34 bytes
 Memory Device
     Array Handle: 0x0022
     Error Information Handle: Not Provided
     Total Width: Unknown
     Data Width: Unknown
     Size: No Module Installed
     Form Factor: DIMM
     Set: None
     Locator: DIMM_C3
     Bank Locator: NODE 0 CHANNEL 2 DIMM 2
     Type: Other
     Type Detail: None
     Speed: Unknown
     Manufacturer: NO DIMM
     Serial Number: NO DIMM
     Asset Tag: NO DIMM
     Part Number: NO DIMM
     Rank: Unknown
     Configured Clock Speed: Unknown

 Handle 0x002D, DMI type 17, 34 bytes
 Memory Device
     Array Handle: 0x0022
     Error Information Handle: Not Provided
     Total Width: 72 bits
     Data Width: 64 bits
     Size: 32 GB
     Form Factor: DIMM
     Set: None
     Locator: DIMM_D1
     Bank Locator: NODE 0 CHANNEL 3 DIMM 0
     Type: Other
     Type Detail: None
     Speed: 2133 MHz
     Manufacturer: 0xAD00
     Serial Number: 80EC73D3
     Asset Tag: DIMM_D1_AssetTag
     Part Number: HMA84GL7MMR4N-TF
     Rank: 4
     Configured Clock Speed: 2133 MHz

 Handle 0x002E, DMI type 17, 34 bytes
 Memory Device
     Array Handle: 0x0022
     Error Information Handle: Not Provided
     Total Width: 72 bits
     Data Width: 64 bits
     Size: 32 GB
     Form Factor: DIMM
     Set: None
     Locator: DIMM_D2
     Bank Locator: NODE 0 CHANNEL 3 DIMM 1
     Type: Other
     Type Detail: None
     Speed: 2133 MHz
     Manufacturer: 0xAD00
     Serial Number: 80EC7330
     Asset Tag: DIMM_D2_AssetTag
     Part Number: HMA84GL7MMR4N-TF
     Rank: 4
     Configured Clock Speed: 2133 MHz

 Handle 0x002F, DMI type 17, 34 bytes
 Memory Device
     Array Handle: 0x0022
     Error Information Handle: Not Provided
     Total Width: Unknown
     Data Width: Unknown
     Size: No Module Installed
     Form Factor: DIMM
     Set: None
     Locator: DIMM_D3
     Bank Locator: NODE 0 CHANNEL 3 DIMM 2
     Type: Other
     Type Detail: None
     Speed: Unknown
     Manufacturer: NO DIMM
     Serial Number: NO DIMM
     Asset Tag: NO DIMM
     Part Number: NO DIMM
     Rank: Unknown
     Configured Clock Speed: Unknown

 Handle 0x0030, DMI type 17, 34 bytes
 Memory Device
     Array Handle: 0x0022
     Error Information Handle: Not Provided
     Total Width: 72 bits
     Data Width: 64 bits
     Size: 32 GB
     Form Factor: DIMM
     Set: None
     Locator: DIMM_E1
     Bank Locator: NODE 1 CHANNEL 0 DIMM 0
     Type: Other
     Type Detail: None
     Speed: 2133 MHz
     Manufacturer: 0xAD00
     Serial Number: 80E54252
     Asset Tag: DIMM_E1_AssetTag
     Part Number: HMA84GL7MMR4N-TF
     Rank: 4
     Configured Clock Speed: 2133 MHz

 Handle 0x0031, DMI type 17, 34 bytes
 Memory Device
     Array Handle: 0x0022
     Error Information Handle: Not Provided
     Total Width: 72 bits
     Data Width: 64 bits
     Size: 32 GB
     Form Factor: DIMM
     Set: None
     Locator: DIMM_E2
     Bank Locator: NODE 1 CHANNEL 0 DIMM 1
     Type: Other
     Type Detail: None
     Speed: 2133 MHz
     Manufacturer: 0xAD00
     Serial Number: 80E54235
     Asset Tag: DIMM_E2_AssetTag
     Part Number: HMA84GL7MMR4N-TF
     Rank: 4
     Configured Clock Speed: 2133 MHz

 Handle 0x0032, DMI type 17, 34 bytes
 Memory Device
     Array Handle: 0x0022
     Error Information Handle: Not Provided
     Total Width: Unknown
     Data Width: Unknown
     Size: No Module Installed
     Form Factor: DIMM
     Set: None
     Locator: DIMM_E3
     Bank Locator: NODE 1 CHANNEL 0 DIMM 2
     Type: Other
     Type Detail: None
     Speed: Unknown
     Manufacturer: NO DIMM
     Serial Number: NO DIMM
     Asset Tag: NO DIMM
     Part Number: NO DIMM
     Rank: Unknown
     Configured Clock Speed: Unknown

 Handle 0x0033, DMI type 17, 34 bytes
 Memory Device
     Array Handle: 0x0022
     Error Information Handle: Not Provided
     Total Width: 72 bits
     Data Width: 64 bits
     Size: 32 GB
     Form Factor: DIMM
     Set: None
     Locator: DIMM_F1
     Bank Locator: NODE 1 CHANNEL 1 DIMM 0
     Type: Other
     Type Detail: None
     Speed: 2133 MHz
     Manufacturer: 0xAD00
     Serial Number: 80E54218
     Asset Tag: DIMM_F1_AssetTag
     Part Number: HMA84GL7MMR4N-TF
     Rank: 4
     Configured Clock Speed: 2133 MHz

 Handle 0x0034, DMI type 17, 34 bytes
 Memory Device
     Array Handle: 0x0022
     Error Information Handle: Not Provided
     Total Width: 72 bits
     Data Width: 64 bits
     Size: 32 GB
     Form Factor: DIMM
     Set: None
     Locator: DIMM_F2
     Bank Locator: NODE 1 CHANNEL 1 DIMM 1
     Type: Other
     Type Detail: None
     Speed: 2133 MHz
     Manufacturer: 0xAD00
     Serial Number: 80E54236
     Asset Tag: DIMM_F2_AssetTag
     Part Number: HMA84GL7MMR4N-TF
     Rank: 4
     Configured Clock Speed: 2133 MHz

 Handle 0x0035, DMI type 17, 34 bytes
 Memory Device
     Array Handle: 0x0022
     Error Information Handle: Not Provided
     Total Width: Unknown
     Data Width: Unknown
     Size: No Module Installed
     Form Factor: DIMM
     Set: None
     Locator: DIMM_F3
     Bank Locator: NODE 1 CHANNEL 1 DIMM 2
     Type: Other
     Type Detail: None
     Speed: Unknown
     Manufacturer: NO DIMM
     Serial Number: NO DIMM
     Asset Tag: NO DIMM
     Part Number: NO DIMM
     Rank: Unknown
     Configured Clock Speed: Unknown

 Handle 0x0036, DMI type 17, 34 bytes
 Memory Device
     Array Handle: 0x0022
     Error Information Handle: Not Provided
     Total Width: 72 bits
     Data Width: 64 bits
     Size: 32 GB
     Form Factor: DIMM
     Set: None
     Locator: DIMM_G1
     Bank Locator: NODE 1 CHANNEL 2 DIMM 0
     Type: Other
     Type Detail: None
     Speed: 2133 MHz
     Manufacturer: 0xAD00
     Serial Number: 80E54247
     Asset Tag: DIMM_G1_AssetTag
     Part Number: HMA84GL7MMR4N-TF
     Rank: 4
     Configured Clock Speed: 2133 MHz

 Handle 0x0037, DMI type 17, 34 bytes
 Memory Device
     Array Handle: 0x0022
     Error Information Handle: Not Provided
     Total Width: 72 bits
     Data Width: 64 bits
     Size: 32 GB
     Form Factor: DIMM
     Set: None
     Locator: DIMM_G2
     Bank Locator: NODE 1 CHANNEL 2 DIMM 1
     Type: Other
     Type Detail: None
     Speed: 2133 MHz
     Manufacturer: 0xAD00
     Serial Number: 80E5421E
     Asset Tag: DIMM_G2_AssetTag
     Part Number: HMA84GL7MMR4N-TF
     Rank: 4
     Configured Clock Speed: 2133 MHz

 Handle 0x0038, DMI type 17, 34 bytes
 Memory Device
     Array Handle: 0x0022
     Error Information Handle: Not Provided
     Total Width: Unknown
     Data Width: Unknown
     Size: No Module Installed
     Form Factor: DIMM
     Set: None
     Locator: DIMM_G3
     Bank Locator: NODE 1 CHANNEL 2 DIMM 2
     Type: Other
     Type Detail: None
     Speed: Unknown
     Manufacturer: NO DIMM
     Serial Number: NO DIMM
     Asset Tag: NO DIMM
     Part Number: NO DIMM
     Rank: Unknown
     Configured Clock Speed: Unknown

 Handle 0x0039, DMI type 17, 34 bytes
 Memory Device
     Array Handle: 0x0022
     Error Information Handle: Not Provided
     Total Width: 72 bits
     Data Width: 64 bits
     Size: 32 GB
     Form Factor: DIMM
     Set: None
     Locator: DIMM_H1
     Bank Locator: NODE 1 CHANNEL 3 DIMM 0
     Type: Other
     Type Detail: None
     Speed: 2133 MHz
     Manufacturer: 0xAD00
     Serial Number: 80E5423C
     Asset Tag: DIMM_H1_AssetTag
     Part Number: HMA84GL7MMR4N-TF
     Rank: 4
     Configured Clock Speed: 2133 MHz

 Handle 0x003A, DMI type 17, 34 bytes
 Memory Device
     Array Handle: 0x0022
     Error Information Handle: Not Provided
     Total Width: 72 bits
     Data Width: 64 bits
     Size: 32 GB
     Form Factor: DIMM
     Set: None
     Locator: DIMM_H2
     Bank Locator: NODE 1 CHANNEL 3 DIMM 1
     Type: Other
     Type Detail: None
     Speed: 2133 MHz
     Manufacturer: 0xAD00
     Serial Number: 80E5424D
     Asset Tag: DIMM_H2_AssetTag
     Part Number: HMA84GL7MMR4N-TF
     Rank: 4
     Configured Clock Speed: 2133 MHz

 Handle 0x003B, DMI type 17, 34 bytes
 Memory Device
     Array Handle: 0x0022
     Error Information Handle: Not Provided
     Total Width: Unknown
     Data Width: Unknown
     Size: No Module Installed
     Form Factor: DIMM
     Set: None
     Locator: DIMM_H3
     Bank Locator: NODE 1 CHANNEL 3 DIMM 2
     Type: Other
     Type Detail: None
     Speed: Unknown
     Manufacturer: NO DIMM
     Serial Number: NO DIMM
     Asset Tag: NO DIMM
     Part Number: NO DIMM
     Rank: Unknown
     Configured Clock Speed: Unknown
```

### Xeon Hsw Server BIOS Configuration

```
 C240 / # scope bios
 C240 /bios # show advanced detail
 Set-up parameters:
    Intel(R) VT-d ATS Support: Enabled
    Adjacent Cache Line Prefetcher: Enabled
    All Onboard LOM Ports: Enabled
    Altitude: 300 M
    Bits per second: 115200
    Power Technology: Performance
    Channel Interleaving: Auto
    Intel(R) VT-d Coherency Support: Disabled
    Console Redirection: COM 0
    Number of Enabled Cores: All
    Energy Performance: Performance
    CPU Performance: Enterprise
    DCU IP Prefetcher: Enabled
    DCU Streamer Prefetch: Enabled
    Demand Scrub: Enabled
    Direct Cache Access Support: Auto
    Enhanced Intel Speedstep(R) Tec: Disabled
    Execute Disable: Enabled
    Flow Control: None
    Hardware Prefetcher: Enabled
    Intel(R) Hyper-Threading Techno: Disabled
    Intel(R) Turbo Boost Technology: Disabled
    Intel(R) VT: Enabled
    Intel(R) VT-d: Enabled
    Intel(R) Interrupt Remapping: Enabled
    Legacy USB Support: Enabled
    Extended APIC: XAPIC
    LOM Port 1 OptionROM: Enabled
    LOM Port 2 OptionROM: Enabled
    MMIO above 4GB: Enabled
    NUMA: Enabled
    PCI ROM CLP: Disabled
    Package C State Limit: C6 Retention
    Intel(R) Pass Through DMA: Disabled
    Patrol Scrub: Enabled
    xHCI Mode: Disabled
    All PCIe Slots OptionROM: Enabled
    PCIe Slot:1 OptionROM: Disabled
    PCIe Slot:2 OptionROM: Disabled
    PCIe Slot:3 OptionROM: Disabled
    PCIe Slot:4 OptionROM: Disabled
    PCIe Slot:5 OptionROM: Disabled
    PCIe Slot:6 OptionROM: Disabled
    PCIe Slot:HBA Link Speed: GEN3
    PCIe Slot:HBA OptionROM: Enabled
    PCIe Slot:MLOM OptionROM: Enabled
    PCIe Slot:N1 OptionROM: Enabled
    PCIe Slot:N2 OptionROM: Enabled
    Processor Power state C1 Enhanc: Disabled
    Processor C3 Report: Disabled
    Processor C6 Report: Disabled
    P-STATE Coordination: HW ALL
    Putty KeyPad: ESCN
    Energy Performance Tuning: BIOS
    QPI Link Frequency Select: Auto
    QPI Snoop Mode: Home Snoop
    Rank Interleaving: Auto
    Redirection After BIOS POST: Always Enable
    PCH SATA Mode: AHCI
    Select Memory RAS: Maximum Performance
    SR-IOV Support: Enabled
    Terminal Type: VT100
    Port 60/64 Emulation: Enabled
    Workload Configuration: Balanced
    CDN Support for VIC: Disabled
    Out-of-Band Management: Disabled
 C240-FCH1950V1H5 /bios/advanced #
```

