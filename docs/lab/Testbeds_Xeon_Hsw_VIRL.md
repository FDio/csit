## FD.io CSIT Testbeds - Xeon Haswell
This is a low-level design implemented as an original FD.io CSIT lab based on Cisco UCS-c240m4 servers based on Intel Xeon Haswell processors. Content has been copied from [FD.io CSIT testbeds wiki page: Xeon_Hsw](https://wiki.fd.io/view/CSIT/Testbeds:_Xeon_Hsw,_VIRL.).

### Server Hardware Configuration
Total of 10 Cisco UCS-c240 servers with Intel Xeon Haswell processors have been used to built FD.io CSIT 3-Node Haswell (3n-hsw) performance testbeds and VIRL functional testbeds. Following three HW configuration types of UCS x86 servers are used:
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
Total of 10 UCSC-C240-M4SX servers is made available for FD.IO CSIT testbed.
For management purposes, each server must have following two ports connected to the management network:
```
 1. 1GE CIMC port
    - CIMC - Cisco Integrated Management Controller.
    - Required for provides embedded server management with WebUI, CLI, SNMPv3, IPMIv2.0.
 2. 1GE management port
    - hostOS management port.
```

### Naming Convention
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
        - Y=1,2,3 - slots in Riser 1, Right PCIe Riser Board, NUMA node 0.
        - Y=4,5,6 - slots in Riser 2, Left PCIe Riser Board, NUMA node 1.
        - Y=m - the MLOM slot.
    - Z - port number on the NIC card.
```

### 3-node Topology Testbeds for Performance
Nine servers are used to build three of 3-node topologies, with each topology using two servers of Type-1 (SUT function) and one server of Type-2 (TG function). Server NIC cards are placed and NIC ports are connected using the scheme defined in next sections.

### LOM (CIMC) and Management networks
Each server has a LOM (Lights-Out-Management e.g. Cisco CIMC) and a Management port, which are connected to two different VLANs.
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
Each server in 3-node Topology has its NIC cards placed, and NIC cards and ports indexed using defined naming convention:
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
Listed nine servers are connected into the three of 3-node testbeds, testbed1, testbed2 and testbed3, using defined naming convention as follows:
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
### Linux Version
```
 $ lsb_release -a
 No LSB modules are available.
 Distributor ID:     Ubuntu
 Description:        Ubuntu 16.04.1 LTS
 Release:    16.04
 Codename:   xenial
```

### Linux Boot Parameters

```
 $ cat /proc/cmdline
 BOOT_IMAGE=/vmlinuz-4.4.0-72-generic root=UUID=0c1a1da6-e805-4858-8176-fff859b7dfd6 ro isolcpus=1-17,19-35 nohz_full=1-17,19-35 rcu_nocbs=1-17,19-35 intel_pstate=disable console=tty0 console=ttyS0,115200n8
```

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

### Linux dmesg
```
 $ dmesg | grep NUMA
 [    0.000000] NUMA: Initialized distance table, cnt=2
 [    0.000000] NUMA: Node 0 [mem 0x00000000-0x7fffffff] + [mem 0x100000000-0x407fffffff] -> [mem 0x00000000-0x407fffffff]
 [    0.000000] mempolicy: Enabling automatic NUMA balancing. Configure with numa_balancing= or the kernel.numa_balancing sysctl
 [    3.181820] pci_bus 0000:00: on NUMA node 0
 [    3.437378] pci_bus 0000:80: on NUMA node 1
```

### Linux lspci
```
 $ lspci | grep Ethernet
 06:00.0 Ethernet controller: Cisco Systems Inc VIC Ethernet NIC (rev a2)
 07:00.0 Ethernet controller: Cisco Systems Inc VIC Ethernet NIC (rev a2)
 0a:00.0 Ethernet controller: Intel Corporation 82599ES 10-Gigabit SFI/SFP+ Network Connection (rev 01)
 0a:00.1 Ethernet controller: Intel Corporation 82599ES 10-Gigabit SFI/SFP+ Network Connection (rev 01)
 13:00.0 Ethernet controller: Cisco Systems Inc VIC Ethernet NIC (rev a2)
 15:00.0 Ethernet controller: Cisco Systems Inc VIC Ethernet NIC (rev a2)
 19:00.0 Ethernet controller: Intel Corporation I350 Gigabit Network Connection (rev 01)
 19:00.1 Ethernet controller: Intel Corporation I350 Gigabit Network Connection (rev 01)
 85:00.0 Ethernet controller: Intel Corporation Ethernet Controller LX710 for 40GbE QSFP+ (rev 01)
 85:00.1 Ethernet controller: Intel Corporation Ethernet Controller LX710 for 40GbE QSFP+ (rev 01)
 87:00.0 Ethernet controller: Intel Corporation Ethernet 10G 2P X710 Adapter (rev 01)
 87:00.1 Ethernet controller: Intel Corporation Ethernet 10G 2P X710 Adapter (rev 01)
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

### Linux meminfo
```
 # cat /proc/meminfo
 MemTotal:       528284344 kB
 MemFree:        517162472 kB
 MemAvailable:   517479752 kB
 Buffers:           92700 kB
 Cached:          1521248 kB
 SwapCached:            0 kB
 Active:          1256440 kB
 Inactive:         392368 kB
 Active(anon):      65196 kB
 Inactive(anon):    28756 kB
 Active(file):    1191244 kB
 Inactive(file):   363612 kB
 Unevictable:           0 kB
 Mlocked:               0 kB
 SwapTotal:        999420 kB
 SwapFree:         999420 kB
 Dirty:                 0 kB
 Writeback:             0 kB
 AnonPages:         35000 kB
 Mapped:            35716 kB
 Shmem:             59096 kB
 Slab:             144416 kB
 SReclaimable:     100160 kB
 SUnreclaim:        44256 kB
 KernelStack:        6160 kB
 PageTables:         2560 kB
 NFS_Unstable:          0 kB
 Bounce:                0 kB
 WritebackTmp:          0 kB
 CommitLimit:    260947288 kB
 Committed_AS:     310872 kB
 VmallocTotal:   34359738367 kB
 VmallocUsed:           0 kB
 VmallocChunk:          0 kB
 HardwareCorrupted:     0 kB
 AnonHugePages:      2048 kB
 CmaTotal:              0 kB
 CmaFree:               0 kB
 HugePages_Total:    4096
 HugePages_Free:        0
 HugePages_Rsvd:        0
 HugePages_Surp:        0
 Hugepagesize:       2048 kB
 DirectMap4k:      114720 kB
 DirectMap2M:     5017600 kB
 DirectMap1G:    533725184 kB
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

### Installed Packages
```
 $ dpkg -l
 Desired=Unknown/Install/Remove/Purge/Hold
 | Status=Not/Inst/Conf-files/Unpacked/halF-conf/Half-inst/trig-aWait/Trig-pend
 |/ Err?=(none)/Reinst-required (Status,Err: uppercase=bad)
 ||/ Name                                                              Version                               Architecture                          Description
 +++-=================================================================-=====================================-=====================================-
 ========================================================================================================================================
 ii  accountsservice                                                   0.6.40-2ubuntu11.1                    amd64                                 query and manipulate user account information
 ii  acl                                                               2.2.52-3                              amd64                                 Access control list utilities
 ii  adduser                                                           3.113+nmu3ubuntu4                     all                                   add and remove users and groups
 ii  apparmor                                                          2.10.95-0ubuntu2.6                    amd64                                 user-space parser utility for AppArmor
 ii  apt                                                               1.2.12~ubuntu16.04.1                  amd64                                 commandline package manager
 ii  apt-utils                                                         1.2.12~ubuntu16.04.1                  amd64                                 package management related utility programs
 ii  autoconf                                                          2.69-9                                all                                   automatic configure script builder
 ii  automake                                                          1:1.15-4ubuntu1                       all                                   Tool for generating GNU Standards-compliant Makefiles
 ii  autotools-dev                                                     20150820.1                            all                                   Update infrastructure for config.{guess,sub} files
 ii  base-files                                                        9.4ubuntu4.2                          amd64                                 Debian base system miscellaneous files
 ii  base-passwd                                                       3.5.39                                amd64                                 Debian base system master password and group files
 ii  bash                                                              4.3-14ubuntu1.1                       amd64                                 GNU Bourne Again SHell
 ii  binutils                                                          2.26.1-1ubuntu1~16.04.3               amd64                                 GNU assembler, linker and binary utilities
 ii  bridge-utils                                                      1.5-9ubuntu1                          amd64                                 Utilities for configuring the Linux Ethernet bridge
 ii  bsdutils                                                          1:2.27.1-6ubuntu3.1                   amd64                                 basic utilities from 4.4BSD-Lite
 ii  build-essential                                                   12.1ubuntu2                           amd64                                 Informational list of build-essential packages
 ii  busybox-initramfs                                                 1:1.22.0-15ubuntu1                    amd64                                 Standalone shell setup for initramfs
 ii  busybox-static                                                    1:1.22.0-15ubuntu1                    amd64                                 Standalone rescue shell with tons of builtin utilities
 ii  bzip2                                                             1.0.6-8                               amd64                                 high-quality block-sorting file compressor - utilities
 ii  ca-certificates                                                   20160104ubuntu1                       all                                   Common CA certificates
 ii  ca-certificates-java                                              20160321                              all                                   Common CA certificates (JKS keystore)
 ii  cgroup-bin                                                        0.41-7ubuntu1                         all                                   control and monitor control groups (transitional package)
 ii  cgroup-lite                                                       1.11                                  all                                   Light-weight package to set up cgroups at system boot
 ii  cgroup-tools                                                      0.41-7ubuntu1                         amd64                                 control and monitor control groups (tools)
 ii  cloud-image-utils                                                 0.27-0ubuntu24                        all                                   cloud image management utilities
 ii  console-setup                                                     1.108ubuntu15.2                       all                                   console font and keymap setup program
 ii  console-setup-linux                                               1.108ubuntu15.2                       all                                   Linux specific part of console-setup
 ii  coreutils                                                         8.25-2ubuntu2                         amd64                                 GNU core utilities
 ii  cpio                                                              2.11+dfsg-5ubuntu1                    amd64                                 GNU cpio -- a program to manage archives of files
 ii  cpp                                                               4:5.3.1-1ubuntu1                      amd64                                 GNU C preprocessor (cpp)
 ii  cpp-5                                                             5.4.0-6ubuntu1~16.04.2                amd64                                 GNU C preprocessor
 ii  cpu-checker                                                       0.7-0ubuntu7                          amd64                                 tools to help evaluate certain CPU (or BIOS) features
 ii  cpufrequtils                                                      008-1                                 amd64                                 utilities to deal with the cpufreq Linux kernel feature
 ii  crda                                                              3.13-1                                amd64                                 wireless Central Regulatory Domain Agent
 ii  cron                                                              3.0pl1-128ubuntu2                     amd64                                 process scheduling daemon
 ii  crudini                                                           0.7-1                                 amd64                                 utility for manipulating ini files
 ii  dash                                                              0.5.8-2.1ubuntu2                      amd64                                 POSIX-compliant shell
 ii  dbus                                                              1.10.6-1ubuntu3                       amd64                                 simple interprocess messaging system (daemon and utilities)
 ii  debconf                                                           1.5.58ubuntu1                         all                                   Debian configuration management system
 ii  debconf-i18n                                                      1.5.58ubuntu1                         all                                   full internationalization support for debconf
 ii  debianutils                                                       4.7                                   amd64                                 Miscellaneous utilities specific to Debian
 ii  debootstrap                                                       1.0.78+nmu1ubuntu1.3                  all                                   Bootstrap a basic Debian system
 ii  dh-python                                                         2.20151103ubuntu1.1                   all                                   Debian helper tools for packaging Python libraries and applications
 ii  diffutils                                                         1:3.3-3                               amd64                                 File comparison utilities
 ii  distro-info                                                       0.14build1                            amd64                                 provides information about the distributions' releases
 ii  distro-info-data                                                  0.28ubuntu0.1                         all                                   information about the distributions' releases (data files)
 ii  dkms                                                              2.2.0.3-2ubuntu11.2                   all                                   Dynamic Kernel Module Support Framework
 ii  dmidecode                                                         3.0-2ubuntu0.1                        amd64                                 SMBIOS/DMI table decoder
 ii  dns-root-data                                                     2015052300+h+1                        all                                   DNS root data including root zone and DNSSEC key
 ii  dnsmasq-base                                                      2.75-1ubuntu0.16.04.2                 amd64                                 Small caching DNS proxy and DHCP/TFTP server
 ii  dpkg                                                              1.18.4ubuntu1.1                       amd64                                 Debian package management system
 ii  dpkg-dev                                                          1.18.4ubuntu1.1                       all                                   Debian package development tools
 ii  e2fslibs:amd64                                                    1.42.13-1ubuntu1                      amd64                                 ext2/ext3/ext4 file system libraries
 ii  e2fsprogs                                                         1.42.13-1ubuntu1                      amd64                                 ext2/ext3/ext4 file system utilities
 ii  eject                                                             2.1.5+deb1+cvs20081104-13.1           amd64                                 ejects CDs and operates CD-Changers under Linux
 ii  expect                                                            5.45-7                                amd64                                 Automates interactive applications
 ii  fakeroot                                                          1.20.2-1ubuntu1                       amd64                                 tool for simulating superuser privileges
 ii  file                                                              1:5.25-2ubuntu1                       amd64                                 Determines file type using "magic" numbers
 ii  findutils                                                         4.6.0+git+20160126-2                  amd64                                 utilities for finding files--find, xargs
 ii  fontconfig-config                                                 2.11.94-0ubuntu1.1                    all                                   generic font configuration library - configuration
 ii  fonts-dejavu-core                                                 2.35-1                                all                                   Vera font family derivate with additional characters
 ii  g++                                                               4:5.3.1-1ubuntu1                      amd64                                 GNU C++ compiler
 ii  g++-5                                                             5.4.0-6ubuntu1~16.04.2                amd64                                 GNU C++ compiler
 ii  gcc                                                               4:5.3.1-1ubuntu1                      amd64                                 GNU C compiler
 ii  gcc-5                                                             5.4.0-6ubuntu1~16.04.2                amd64                                 GNU C compiler
 ii  gcc-5-base:amd64                                                  5.4.0-6ubuntu1~16.04.2                amd64                                 GCC, the GNU Compiler Collection (base package)
 ii  gcc-6-base:amd64                                                  6.0.1-0ubuntu1                        amd64                                 GCC, the GNU Compiler Collection (base package)
 ii  genisoimage                                                       9:1.1.11-3ubuntu1                     amd64                                 Creates ISO-9660 CD-ROM filesystem images
 ii  gettext-base                                                      0.19.7-2ubuntu3                       amd64                                 GNU Internationalization utilities for the base system
 ii  gir1.2-glib-2.0:amd64                                             1.46.0-3ubuntu1                       amd64                                 Introspection data for GLib, GObject, Gio and GModule
 ii  git                                                               1:2.7.4-0ubuntu1                      amd64                                 fast, scalable, distributed revision control system
 ii  git-man                                                           1:2.7.4-0ubuntu1                      all                                   fast, scalable, distributed revision control system (manual pages)
 ii  gnupg                                                             1.4.20-1ubuntu3.1                     amd64                                 GNU privacy guard - a free PGP replacement
 ii  gpgv                                                              1.4.20-1ubuntu3.1                     amd64                                 GNU privacy guard - signature verification tool
 ii  grep                                                              2.25-1~16.04.1                        amd64                                 GNU grep, egrep and fgrep
 ii  grub-common                                                       2.02~beta2-36ubuntu3.1                amd64                                 GRand Unified Bootloader (common files)
 ii  grub-gfxpayload-lists                                             0.7                                   amd64                                 GRUB gfxpayload blacklist
 ii  grub-pc                                                           2.02~beta2-36ubuntu3.1                amd64                                 GRand Unified Bootloader, version 2 (PC/BIOS version)
 ii  grub-pc-bin                                                       2.02~beta2-36ubuntu3.1                amd64                                 GRand Unified Bootloader, version 2 (PC/BIOS binaries)
 ii  grub2-common                                                      2.02~beta2-36ubuntu3.1                amd64                                 GRand Unified Bootloader (common files for version 2)
 ii  gzip                                                              1.6-4ubuntu1                          amd64                                 GNU compression utilities
 ii  hostname                                                          3.16ubuntu2                           amd64                                 utility to set/show the host name or domain name
 ii  ifupdown                                                          0.8.10ubuntu1                         amd64                                 high level tools to configure network interfaces
 ii  init                                                              1.29ubuntu2                           amd64                                 System-V-like init utilities - metapackage
 ii  init-system-helpers                                               1.29ubuntu2                           all                                   helper tools for all init systems
 ii  initramfs-tools                                                   0.122ubuntu8.1                        all                                   generic modular initramfs generator (automation)
 ii  initramfs-tools-bin                                               0.122ubuntu8.1                        amd64                                 binaries used by initramfs-tools
 ii  initramfs-tools-core                                              0.122ubuntu8.1                        all                                   generic modular initramfs generator (core tools)
 ii  initscripts                                                       2.88dsf-59.3ubuntu2                   amd64                                 scripts for initializing and shutting down the system
 ii  insserv                                                           1.14.0-5ubuntu3                       amd64                                 boot sequence organizer using LSB init.d script dependency information
 ii  installation-report                                               2.60ubuntu1                           all                                   system installation report
 ii  iproute2                                                          4.3.0-1ubuntu3                        amd64                                 networking and traffic control tools
 ii  iptables                                                          1.6.0-2ubuntu3                        amd64                                 administration tools for packet filtering and NAT
 ii  iputils-ping                                                      3:20121221-5ubuntu2                   amd64                                 Tools to test the reachability of network hosts
 ii  ipxe-qemu                                                         1.0.0+git-20150424.a25a16d-1ubuntu1   all                                   PXE boot firmware - ROM images for qemu
 ii  isc-dhcp-client                                                   4.3.3-5ubuntu12.1                     amd64                                 DHCP client for automatically obtaining an IP address
 ii  isc-dhcp-common                                                   4.3.3-5ubuntu12.1                     amd64                                 common files used by all of the isc-dhcp packages
 ii  iso-codes                                                         3.65-1                                all                                   ISO language, territory, currency, script codes and their translations
 ii  iw                                                                3.17-1                                amd64                                 tool for configuring Linux wireless devices
 ii  java-common                                                       0.56ubuntu2                           all                                   Base package for Java runtimes
 ii  kbd                                                               1.15.5-1ubuntu4                       amd64                                 Linux console font and keytable utilities
 ii  keyboard-configuration                                            1.108ubuntu15.2                       all                                   system-wide keyboard preferences
 ii  klibc-utils                                                       2.0.4-8ubuntu1.16.04.1                amd64                                 small utilities built with klibc for early boot
 ii  kmod                                                              22-1ubuntu4                           amd64                                 tools for managing Linux kernel modules
 ii  krb5-locales                                                      1.13.2+dfsg-5                         all                                   Internationalization support for MIT Kerberos
 ii  language-selector-common                                          0.165.3                               all                                   Language selector for Ubuntu
 ii  laptop-detect                                                     0.13.7ubuntu2                         amd64                                 attempt to detect a laptop
 ii  less                                                              481-2.1                               amd64                                 pager program similar to more
 ii  libaccountsservice0:amd64                                         0.6.40-2ubuntu11.1                    amd64                                 query and manipulate user account information - shared libraries
 ii  libacl1:amd64                                                     2.2.52-3                              amd64                                 Access control list shared library
 ii  libaio1:amd64                                                     0.3.110-2                             amd64                                 Linux kernel AIO access library - shared library
 ii  libalgorithm-diff-perl                                            1.19.03-1                             all                                   module to find differences between files
 ii  libalgorithm-diff-xs-perl                                         0.04-4build1                          amd64                                 module to find differences between files (XS accelerated)
 ii  libalgorithm-merge-perl                                           0.08-3                                all                                   Perl module for three-way merge of textual data
 ii  libapparmor-perl                                                  2.10.95-0ubuntu2.6                    amd64                                 AppArmor library Perl bindings
 ii  libapparmor1:amd64                                                2.10.95-0ubuntu2                      amd64                                 changehat AppArmor library
 ii  libapr1:amd64                                                     1.5.2-3                               amd64                                 Apache Portable Runtime Library
 ii  libapt-inst2.0:amd64                                              1.2.12~ubuntu16.04.1                  amd64                                 deb package format runtime library
 ii  libapt-pkg5.0:amd64                                               1.2.12~ubuntu16.04.1                  amd64                                 package management runtime library
 ii  libasan2:amd64                                                    5.4.0-6ubuntu1~16.04.2                amd64                                 AddressSanitizer -- a fast memory error detector
 ii  libasn1-8-heimdal:amd64                                           1.7~git20150920+dfsg-4ubuntu1         amd64                                 Heimdal Kerberos - ASN.1 library
 ii  libasound2:amd64                                                  1.1.0-0ubuntu1                        amd64                                 shared library for ALSA applications
 ii  libasound2-data                                                   1.1.0-0ubuntu1                        all                                   Configuration files and profiles for ALSA drivers
 ii  libasprintf0v5:amd64                                              0.19.7-2ubuntu3                       amd64                                 GNU library to use fprintf and friends in C++
 ii  libasyncns0:amd64                                                 0.8-5build1                           amd64                                 Asynchronous name service query library
 ii  libatm1:amd64                                                     1:2.5.1-1.5                           amd64                                 shared library for ATM (Asynchronous Transfer Mode)
 ii  libatomic1:amd64                                                  5.4.0-6ubuntu1~16.04.2                amd64                                 support library providing __atomic built-in functions
 ii  libattr1:amd64                                                    1:2.4.47-2                            amd64                                 Extended attribute shared library
 ii  libaudit-common                                                   1:2.4.5-1ubuntu2                      all                                   Dynamic library for security auditing - common files
 ii  libaudit1:amd64                                                   1:2.4.5-1ubuntu2                      amd64                                 Dynamic library for security auditing
 ii  libavahi-client3:amd64                                            0.6.32~rc+dfsg-1ubuntu2               amd64                                 Avahi client library
 ii  libavahi-common-data:amd64                                        0.6.32~rc+dfsg-1ubuntu2               amd64                                 Avahi common data files
 ii  libavahi-common3:amd64                                            0.6.32~rc+dfsg-1ubuntu2               amd64                                 Avahi common library
 ii  libblkid1:amd64                                                   2.27.1-6ubuntu3.1                     amd64                                 block device ID library
 ii  libbluetooth3:amd64                                               5.37-0ubuntu5                         amd64                                 Library to use the BlueZ Linux Bluetooth stack
 ii  libboost-iostreams1.58.0:amd64                                    1.58.0+dfsg-5ubuntu3.1                amd64                                 Boost.Iostreams Library
 ii  libboost-random1.58.0:amd64                                       1.58.0+dfsg-5ubuntu3.1                amd64                                 Boost Random Number Library
 ii  libboost-system1.58.0:amd64                                       1.58.0+dfsg-5ubuntu3.1                amd64                                 Operating system (e.g. diagnostics support) library
 ii  libboost-thread1.58.0:amd64                                       1.58.0+dfsg-5ubuntu3.1                amd64                                 portable C++ multi-threading
 ii  libbrlapi0.6:amd64                                                5.3.1-2ubuntu2.1                      amd64                                 braille display access via BRLTTY - shared library
 ii  libbsd0:amd64                                                     0.8.2-1                               amd64                                 utility functions from BSD systems - shared library
 ii  libbz2-1.0:amd64                                                  1.0.6-8                               amd64                                 high-quality block-sorting file compressor library - runtime
 ii  libc-bin                                                          2.23-0ubuntu3                         amd64                                 GNU C Library: Binaries
 ii  libc-dev-bin                                                      2.23-0ubuntu3                         amd64                                 GNU C Library: Development binaries
 ii  libc6:amd64                                                       2.23-0ubuntu3                         amd64                                 GNU C Library: Shared libraries
 ii  libc6-dev:amd64                                                   2.23-0ubuntu3                         amd64                                 GNU C Library: Development Libraries and Header Files
 ii  libcaca0:amd64                                                    0.99.beta19-2build2~gcc5.2            amd64                                 colour ASCII art library
 ii  libcacard0:amd64                                                  1:2.5.0-2                             amd64                                 Virtual Common Access Card (CAC) Emulator (runtime library)
 ii  libcap-ng0:amd64                                                  0.7.7-1                               amd64                                 An alternate POSIX capabilities library
 ii  libcap2:amd64                                                     1:2.24-12                             amd64                                 POSIX 1003.1e capabilities (library)
 ii  libcap2-bin                                                       1:2.24-12                             amd64                                 POSIX 1003.1e capabilities (utilities)
 ii  libcc1-0:amd64                                                    5.4.0-6ubuntu1~16.04.2                amd64                                 GCC cc1 plugin for GDB
 ii  libcgroup1:amd64                                                  0.41-7ubuntu1                         amd64                                 control and monitor control groups (library)
 ii  libcilkrts5:amd64                                                 5.4.0-6ubuntu1~16.04.2                amd64                                 Intel Cilk Plus language extensions (runtime)
 ii  libcomerr2:amd64                                                  1.42.13-1ubuntu1                      amd64                                 common error description library
 ii  libcpufreq0                                                       008-1                                 amd64                                 shared library to deal with the cpufreq Linux kernel feature
 ii  libcryptsetup4:amd64                                              2:1.6.6-5ubuntu2                      amd64                                 disk encryption support - shared library
 ii  libcups2:amd64                                                    2.1.3-4                               amd64                                 Common UNIX Printing System(tm) - Core library
 ii  libcurl3-gnutls:amd64                                             7.47.0-1ubuntu2.1                     amd64                                 easy-to-use client-side URL transfer library (GnuTLS flavour)
 ii  libdb5.3:amd64                                                    5.3.28-11                             amd64                                 Berkeley v5.3 Database Libraries [runtime]
 ii  libdbus-1-3:amd64                                                 1.10.6-1ubuntu3                       amd64                                 simple interprocess messaging system (library)
 ii  libdbus-glib-1-2:amd64                                            0.106-1                               amd64                                 simple interprocess messaging system (GLib-based shared library)
 ii  libdebconfclient0:amd64                                           0.198ubuntu1                          amd64                                 Debian Configuration Management System (C-implementation library)
 ii  libdevmapper1.02.1:amd64                                          2:1.02.110-1ubuntu10                  amd64                                 Linux Kernel Device Mapper userspace library
 ii  libdns-export162                                                  1:9.10.3.dfsg.P4-8ubuntu1.1           amd64                                 Exported DNS Shared Library
 ii  libdpkg-perl                                                      1.18.4ubuntu1.1                       all                                   Dpkg perl modules
 ii  libdrm-amdgpu1:amd64                                              2.4.67-1ubuntu0.16.04.2               amd64                                 Userspace interface to amdgpu-specific kernel DRM services -- runtime
 ii  libdrm-intel1:amd64                                               2.4.67-1ubuntu0.16.04.2               amd64                                 Userspace interface to intel-specific kernel DRM services -- runtime
 ii  libdrm-nouveau2:amd64                                             2.4.67-1ubuntu0.16.04.2               amd64                                 Userspace interface to nouveau-specific kernel DRM services -- runtime
 ii  libdrm-radeon1:amd64                                              2.4.67-1ubuntu0.16.04.2               amd64                                 Userspace interface to radeon-specific kernel DRM services -- runtime
 ii  libdrm2:amd64                                                     2.4.67-1ubuntu0.16.04.2               amd64                                 Userspace interface to kernel DRM services -- runtime
 ii  libedit2:amd64                                                    3.1-20150325-1ubuntu2                 amd64                                 BSD editline and history libraries
 ii  libelf1:amd64                                                     0.165-3ubuntu1                        amd64                                 library to read and write ELF files
 ii  liberror-perl                                                     0.17-1.2                              all                                   Perl module for error/exception handling in an OO-ish way
 ii  libestr0                                                          0.1.10-1                              amd64                                 Helper functions for handling strings (lib)
 ii  libexpat1:amd64                                                   2.1.0-7ubuntu0.16.04.2                amd64                                 XML parsing C library - runtime library
 ii  libexpat1-dev:amd64                                               2.1.0-7ubuntu0.16.04.2                amd64                                 XML parsing C library - development kit
 ii  libfakeroot:amd64                                                 1.20.2-1ubuntu1                       amd64                                 tool for simulating superuser privileges - shared libraries
 ii  libfdisk1:amd64                                                   2.27.1-6ubuntu3.1                     amd64                                 fdisk partitioning library
 ii  libfdt1:amd64                                                     1.4.0+dfsg-2                          amd64                                 Flat Device Trees manipulation library
 ii  libffi6:amd64                                                     3.2.1-4                               amd64                                 Foreign Function Interface library runtime
 ii  libfile-fcntllock-perl                                            0.22-3                                amd64                                 Perl module for file locking with fcntl(2)
 ii  libflac8:amd64                                                    1.3.1-4                               amd64                                 Free Lossless Audio Codec - runtime C library
 ii  libfontconfig1:amd64                                              2.11.94-0ubuntu1.1                    amd64                                 generic font configuration library - runtime
 ii  libfontenc1:amd64                                                 1:1.1.3-1                             amd64                                 X11 font encoding library
 ii  libfreetype6:amd64                                                2.6.1-0.1ubuntu2                      amd64                                 FreeType 2 font engine, shared library files
 ii  libfribidi0:amd64                                                 0.19.7-1                              amd64                                 Free Implementation of the Unicode BiDi algorithm
 ii  libfuse2:amd64                                                    2.9.4-1ubuntu3                        amd64                                 Filesystem in Userspace (library)
 ii  libgcc-5-dev:amd64                                                5.4.0-6ubuntu1~16.04.2                amd64                                 GCC support library (development files)
 ii  libgcc1:amd64                                                     1:6.0.1-0ubuntu1                      amd64                                 GCC support library
 ii  libgcrypt20:amd64                                                 1.6.5-2ubuntu0.2                      amd64                                 LGPL Crypto library - runtime library
 ii  libgdbm3:amd64                                                    1.8.3-13.1                            amd64                                 GNU dbm database routines (runtime version)
 ii  libgirepository-1.0-1:amd64                                       1.46.0-3ubuntu1                       amd64                                 Library for handling GObject introspection data (runtime library)
 ii  libgl1-mesa-dri:amd64                                             11.2.0-1ubuntu2.2                     amd64                                 free implementation of the OpenGL API -- DRI modules
 ii  libgl1-mesa-glx:amd64                                             11.2.0-1ubuntu2.2                     amd64                                 free implementation of the OpenGL API -- GLX runtime
 ii  libglapi-mesa:amd64                                               11.2.0-1ubuntu2.2                     amd64                                 free implementation of the GL API -- shared library
 ii  libglib2.0-0:amd64                                                2.48.1-1~ubuntu16.04.1                amd64                                 GLib library of C routines
 ii  libglib2.0-bin                                                    2.48.1-1~ubuntu16.04.1                amd64                                 Programs for the GLib library
 ii  libglib2.0-data                                                   2.48.1-1~ubuntu16.04.1                all                                   Common files for GLib library
 ii  libglib2.0-dev                                                    2.48.1-1~ubuntu16.04.1                amd64                                 Development files for the GLib library
 ii  libgmp10:amd64                                                    2:6.1.0+dfsg-2                        amd64                                 Multiprecision arithmetic library
 ii  libgnutls-openssl27:amd64                                         3.4.10-4ubuntu1.1                     amd64                                 GNU TLS library - OpenSSL wrapper
 ii  libgnutls30:amd64                                                 3.4.10-4ubuntu1.1                     amd64                                 GNU TLS library - main runtime library
 ii  libgomp1:amd64                                                    5.4.0-6ubuntu1~16.04.2                amd64                                 GCC OpenMP (GOMP) support library
 ii  libgpg-error0:amd64                                               1.21-2ubuntu1                         amd64                                 library for common error values and messages in GnuPG components
 ii  libgssapi-krb5-2:amd64                                            1.13.2+dfsg-5                         amd64                                 MIT Kerberos runtime libraries - krb5 GSS-API Mechanism
 ii  libgssapi3-heimdal:amd64                                          1.7~git20150920+dfsg-4ubuntu1         amd64                                 Heimdal Kerberos - GSSAPI support library
 ii  libhcrypto4-heimdal:amd64                                         1.7~git20150920+dfsg-4ubuntu1         amd64                                 Heimdal Kerberos - crypto library
 ii  libheimbase1-heimdal:amd64                                        1.7~git20150920+dfsg-4ubuntu1         amd64                                 Heimdal Kerberos - Base library
 ii  libheimntlm0-heimdal:amd64                                        1.7~git20150920+dfsg-4ubuntu1         amd64                                 Heimdal Kerberos - NTLM support library
 ii  libhogweed4:amd64                                                 3.2-1                                 amd64                                 low level cryptographic library (public-key cryptos)
 ii  libhx509-5-heimdal:amd64                                          1.7~git20150920+dfsg-4ubuntu1         amd64                                 Heimdal Kerberos - X509 support library
 ii  libice6:amd64                                                     2:1.0.9-1                             amd64                                 X11 Inter-Client Exchange library
 ii  libicu55:amd64                                                    55.1-7                                amd64                                 International Components for Unicode
 ii  libidn11:amd64                                                    1.32-3ubuntu1.1                       amd64                                 GNU Libidn library, implementation of IETF IDN specifications
 ii  libisc-export160                                                  1:9.10.3.dfsg.P4-8ubuntu1.1           amd64                                 Exported ISC Shared Library
 ii  libiscsi2:amd64                                                   1.12.0-2                              amd64                                 iSCSI client shared library
 ii  libisl15:amd64                                                    0.16.1-1                              amd64                                 manipulating sets and relations of integer points bounded by linear constraints
 ii  libitm1:amd64                                                     5.4.0-6ubuntu1~16.04.2                amd64                                 GNU Transactional Memory Library
 ii  libjpeg-turbo8:amd64                                              1.4.2-0ubuntu3                        amd64                                 IJG JPEG compliant runtime library.
 ii  libjpeg8:amd64                                                    8c-2ubuntu8                           amd64                                 Independent JPEG Group's JPEG runtime library (dependency package)
 ii  libjson-c2:amd64                                                  0.11-4ubuntu2                         amd64                                 JSON manipulation library - shared library
 ii  libk5crypto3:amd64                                                1.13.2+dfsg-5                         amd64                                 MIT Kerberos runtime libraries - Crypto Library
 ii  libkeyutils1:amd64                                                1.5.9-8ubuntu1                        amd64                                 Linux Key Management Utilities (library)
 ii  libklibc                                                          2.0.4-8ubuntu1.16.04.1                amd64                                 minimal libc subset for use with initramfs
 ii  libkmod2:amd64                                                    22-1ubuntu4                           amd64                                 libkmod shared library
 ii  libkrb5-26-heimdal:amd64                                          1.7~git20150920+dfsg-4ubuntu1         amd64                                 Heimdal Kerberos - libraries
 ii  libkrb5-3:amd64                                                   1.13.2+dfsg-5                         amd64                                 MIT Kerberos runtime libraries
 ii  libkrb5support0:amd64                                             1.13.2+dfsg-5                         amd64                                 MIT Kerberos runtime libraries - Support library
 ii  liblcms2-2:amd64                                                  2.6-3ubuntu2                          amd64                                 Little CMS 2 color management library
 ii  libldap-2.4-2:amd64                                               2.4.42+dfsg-2ubuntu3.1                amd64                                 OpenLDAP libraries
 ii  libllvm3.8:amd64                                                  1:3.8-2ubuntu4                        amd64                                 Modular compiler and toolchain technologies, runtime library
 ii  liblocale-gettext-perl                                            1.07-1build1                          amd64                                 module using libc functions for internationalization in Perl
 ii  liblsan0:amd64                                                    5.4.0-6ubuntu1~16.04.2                amd64                                 LeakSanitizer -- a memory leak detector (runtime)
 ii  libltdl-dev:amd64                                                 2.4.6-0.1                             amd64                                 System independent dlopen wrapper for GNU libtool
 ii  libltdl7:amd64                                                    2.4.6-0.1                             amd64                                 System independent dlopen wrapper for GNU libtool
 ii  liblxc1                                                           2.0.7-0ubuntu1~16.04.2                amd64                                 Linux Containers userspace tools (library)
 ii  liblz4-1:amd64                                                    0.0~r131-2ubuntu2                     amd64                                 Fast LZ compression algorithm library - runtime
 ii  liblzma5:amd64                                                    5.1.1alpha+20120614-2ubuntu2          amd64                                 XZ-format compression library
 ii  libmagic1:amd64                                                   1:5.25-2ubuntu1                       amd64                                 File type determination library using "magic" numbers
 ii  libmnl0:amd64                                                     1.0.3-5                               amd64                                 minimalistic Netlink communication library
 ii  libmount1:amd64                                                   2.27.1-6ubuntu3.1                     amd64                                 device mounting library
 ii  libmpc3:amd64                                                     1.0.3-1                               amd64                                 multiple precision complex floating-point library
 ii  libmpdec2:amd64                                                   2.4.2-1                               amd64                                 library for decimal floating point arithmetic (runtime library)
 ii  libmpfr4:amd64                                                    3.1.4-1                               amd64                                 multiple precision floating-point computation
 ii  libmpx0:amd64                                                     5.4.0-6ubuntu1~16.04.2                amd64                                 Intel memory protection extensions (runtime)
 ii  libncurses5:amd64                                                 6.0+20160213-1ubuntu1                 amd64                                 shared libraries for terminal handling
 ii  libncursesw5:amd64                                                6.0+20160213-1ubuntu1                 amd64                                 shared libraries for terminal handling (wide character support)
 ii  libnetfilter-conntrack3:amd64                                     1.0.5-1                               amd64                                 Netfilter netlink-conntrack library
 ii  libnettle6:amd64                                                  3.2-1                                 amd64                                 low level cryptographic library (symmetric and one-way cryptos)
 ii  libnewt0.52:amd64                                                 0.52.18-1ubuntu2                      amd64                                 Not Erik's Windowing Toolkit - text mode windowing with slang
 ii  libnfnetlink0:amd64                                               1.0.1-3                               amd64                                 Netfilter netlink library
 ii  libnih-dbus1:amd64                                                1.0.3-4.3ubuntu1                      amd64                                 NIH D-Bus Bindings Library
 ii  libnih1:amd64                                                     1.0.3-4.3ubuntu1                      amd64                                 NIH Utility Library
 ii  libnl-3-200:amd64                                                 3.2.27-1                              amd64                                 library for dealing with netlink sockets
 ii  libnl-genl-3-200:amd64                                            3.2.27-1                              amd64                                 library for dealing with netlink sockets - generic netlink
 ii  libnspr4:amd64                                                    2:4.12-0ubuntu0.16.04.1               amd64                                 NetScape Portable Runtime Library
 ii  libnss3:amd64                                                     2:3.23-0ubuntu0.16.04.1               amd64                                 Network Security Service libraries
 ii  libnss3-nssdb                                                     2:3.23-0ubuntu0.16.04.1               all                                   Network Security Security libraries - shared databases
 ii  libnuma1:amd64                                                    2.0.11-1ubuntu1                       amd64                                 Libraries for controlling NUMA policy
 ii  libogg0:amd64                                                     1.3.2-1                               amd64                                 Ogg bitstream library
 ii  libopus0:amd64                                                    1.1.2-1ubuntu1                        amd64                                 Opus codec runtime library
 ii  libp11-kit0:amd64                                                 0.23.2-3                              amd64                                 Library for loading and coordinating access to PKCS#11 modules - runtime
 ii  libpam-cgfs                                                       2.0.6-0ubuntu1~16.04.1                amd64                                 PAM module for managing cgroups for LXC
 ii  libpam-modules:amd64                                              1.1.8-3.2ubuntu2                      amd64                                 Pluggable Authentication Modules for PAM
 ii  libpam-modules-bin                                                1.1.8-3.2ubuntu2                      amd64                                 Pluggable Authentication Modules for PAM - helper binaries
 ii  libpam-runtime                                                    1.1.8-3.2ubuntu2                      all                                   Runtime support for the PAM library
 ii  libpam0g:amd64                                                    1.1.8-3.2ubuntu2                      amd64                                 Pluggable Authentication Modules library
 ii  libpcap-dev                                                       1.7.4-2                               all                                   development library for libpcap (transitional package)
 ii  libpcap0.8:amd64                                                  1.7.4-2                               amd64                                 system interface for user-level packet capture
 ii  libpcap0.8-dev                                                    1.7.4-2                               amd64                                 development library and header files for libpcap0.8
 ii  libpci3:amd64                                                     1:3.3.1-1.1ubuntu1                    amd64                                 Linux PCI Utilities (shared library)
 ii  libpciaccess0:amd64                                               0.13.4-1                              amd64                                 Generic PCI access library for X
 ii  libpcre16-3:amd64                                                 2:8.38-3.1                            amd64                                 Perl 5 Compatible Regular Expression Library - 16 bit runtime files
 ii  libpcre3:amd64                                                    2:8.38-3.1                            amd64                                 Perl 5 Compatible Regular Expression Library - runtime files
 ii  libpcre3-dev:amd64                                                2:8.38-3.1                            amd64                                 Perl 5 Compatible Regular Expression Library - development files
 ii  libpcre32-3:amd64                                                 2:8.38-3.1                            amd64                                 Perl 5 Compatible Regular Expression Library - 32 bit runtime files
 ii  libpcrecpp0v5:amd64                                               2:8.38-3.1                            amd64                                 Perl 5 Compatible Regular Expression Library - C++ runtime files
 ii  libpcsclite1:amd64                                                1.8.14-1ubuntu1.16.04.1               amd64                                 Middleware to access a smart card using PC/SC (library)
 ii  libperl5.22:amd64                                                 5.22.1-9                              amd64                                 shared Perl library
 ii  libpixman-1-0:amd64                                               0.33.6-1                              amd64                                 pixel-manipulation library for X and cairo
 ii  libplymouth4:amd64                                                0.9.2-3ubuntu13.1                     amd64                                 graphical boot animation and logger - shared libraries
 ii  libpng12-0:amd64                                                  1.2.54-1ubuntu1                       amd64                                 PNG library - runtime
 ii  libpolkit-gobject-1-0:amd64                                       0.105-14.1                            amd64                                 PolicyKit Authorization API
 ii  libpopt0:amd64                                                    1.16-10                               amd64                                 lib for parsing cmdline parameters
 ii  libprocps4:amd64                                                  2:3.3.10-4ubuntu2                     amd64                                 library for accessing process information from /proc
 ii  libpulse0:amd64                                                   1:8.0-0ubuntu3                        amd64                                 PulseAudio client libraries
 ii  libpython-all-dev:amd64                                           2.7.11-1                              amd64                                 package depending on all supported Python development packages
 ii  libpython-dev:amd64                                               2.7.11-1                              amd64                                 header files and a static library for Python (default)
 ii  libpython-stdlib:amd64                                            2.7.11-1                              amd64                                 interactive high-level object-oriented language (default python version)
 ii  libpython2.7:amd64                                                2.7.12-1~16.04                        amd64                                 Shared Python runtime library (version 2.7)
 ii  libpython2.7-dev:amd64                                            2.7.12-1~16.04                        amd64                                 Header files and a static library for Python (v2.7)
 ii  libpython2.7-minimal:amd64                                        2.7.12-1~16.04                        amd64                                 Minimal subset of the Python language (version 2.7)
 ii  libpython2.7-stdlib:amd64                                         2.7.12-1~16.04                        amd64                                 Interactive high-level object-oriented language (standard library, version 2.7)
 ii  libpython3-stdlib:amd64                                           3.5.1-3                               amd64                                 interactive high-level object-oriented language (default python3 version)
 ii  libpython3.5-minimal:amd64                                        3.5.2-2~16.01                         amd64                                 Minimal subset of the Python language (version 3.5)
 ii  libpython3.5-stdlib:amd64                                         3.5.2-2~16.01                         amd64                                 Interactive high-level object-oriented language (standard library, version 3.5)
 ii  libquadmath0:amd64                                                5.4.0-6ubuntu1~16.04.2                amd64                                 GCC Quad-Precision Math Library
 ii  librados2                                                         10.2.2-0ubuntu0.16.04.2               amd64                                 RADOS distributed object store client library
 ii  librbd1                                                           10.2.2-0ubuntu0.16.04.2               amd64                                 RADOS block device client library
 ii  libreadline6:amd64                                                6.3-8ubuntu2                          amd64                                 GNU readline and history libraries, run-time libraries
 ii  libroken18-heimdal:amd64                                          1.7~git20150920+dfsg-4ubuntu1         amd64                                 Heimdal Kerberos - roken support library
 ii  librtmp1:amd64                                                    2.4+20151223.gitfa8646d-1build1       amd64                                 toolkit for RTMP streams (shared library)
 ii  libsasl2-2:amd64                                                  2.1.26.dfsg1-14build1                 amd64                                 Cyrus SASL - authentication abstraction library
 ii  libsasl2-modules:amd64                                            2.1.26.dfsg1-14build1                 amd64                                 Cyrus SASL - pluggable authentication modules
 ii  libsasl2-modules-db:amd64                                         2.1.26.dfsg1-14build1                 amd64                                 Cyrus SASL - pluggable authentication modules (DB)
 ii  libsdl1.2debian:amd64                                             1.2.15+dfsg1-3                        amd64                                 Simple DirectMedia Layer
 ii  libseccomp2:amd64                                                 2.2.3-3ubuntu3                        amd64                                 high level interface to Linux seccomp filter
 ii  libselinux1:amd64                                                 2.4-3build2                           amd64                                 SELinux runtime shared libraries
 ii  libsemanage-common                                                2.3-1build3                           all                                   Common files for SELinux policy management libraries
 ii  libsemanage1:amd64                                                2.3-1build3                           amd64                                 SELinux policy management library
 ii  libsepol1:amd64                                                   2.4-2                                 amd64                                 SELinux library for manipulating binary security policies
 ii  libsigsegv2:amd64                                                 2.10-4                                amd64                                 Library for handling page faults in a portable way
 ii  libslang2:amd64                                                   2.3.0-2ubuntu1                        amd64                                 S-Lang programming library - runtime version
 ii  libsm6:amd64                                                      2:1.2.2-1                             amd64                                 X11 Session Management library
 ii  libsmartcols1:amd64                                               2.27.1-6ubuntu3.1                     amd64                                 smart column output alignment library
 ii  libsndfile1:amd64                                                 1.0.25-10                             amd64                                 Library for reading/writing audio files
 ii  libspice-server1:amd64                                            0.12.6-4ubuntu0.1                     amd64                                 Implements the server side of the SPICE protocol
 ii  libsqlite3-0:amd64                                                3.11.0-1ubuntu1                       amd64                                 SQLite 3 shared library
 ii  libss2:amd64                                                      1.42.13-1ubuntu1                      amd64                                 command-line interface parsing library
 ii  libssl1.0.0:amd64                                                 1.0.2g-1ubuntu4.5                     amd64                                 Secure Sockets Layer toolkit - shared libraries
 ii  libstdc++-5-dev:amd64                                             5.4.0-6ubuntu1~16.04.2                amd64                                 GNU Standard C++ Library v3 (development files)
 ii  libstdc++6:amd64                                                  5.4.0-6ubuntu1~16.04.2                amd64                                 GNU Standard C++ Library v3
 ii  libsystemd0:amd64                                                 229-4ubuntu10                         amd64                                 systemd utility library
 ii  libtasn1-6:amd64                                                  4.7-3ubuntu0.16.04.1                  amd64                                 Manage ASN.1 structures (runtime)
 ii  libtcl8.6:amd64                                                   8.6.5+dfsg-2                          amd64                                 Tcl (the Tool Command Language) v8.6 - run-time library files
 ii  libtext-charwidth-perl                                            0.04-7build5                          amd64                                 get display widths of characters on the terminal
 ii  libtext-iconv-perl                                                1.7-5build4                           amd64                                 converts between character sets in Perl
 ii  libtext-wrapi18n-perl                                             0.06-7.1                              all                                   internationalized substitute of Text::Wrap
 ii  libtinfo5:amd64                                                   6.0+20160213-1ubuntu1                 amd64                                 shared low-level terminfo library for terminal handling
 ii  libtk8.6:amd64                                                    8.6.5-1                               amd64                                 Tk toolkit for Tcl and X11 v8.6 - run-time files
 ii  libtool                                                           2.4.6-0.1                             all                                   Generic library support script
 ii  libtsan0:amd64                                                    5.4.0-6ubuntu1~16.04.2                amd64                                 ThreadSanitizer -- a Valgrind-based detector of data races (runtime)
 ii  libtxc-dxtn-s2tc0:amd64                                           0~git20131104-1.1                     amd64                                 Texture compression library for Mesa
 ii  libubsan0:amd64                                                   5.4.0-6ubuntu1~16.04.2                amd64                                 UBSan -- undefined behaviour sanitizer (runtime)
 ii  libudev1:amd64                                                    229-4ubuntu10                         amd64                                 libudev shared library
 ii  libusb-0.1-4:amd64                                                2:0.1.12-28                           amd64                                 userspace USB programming library
 ii  libusb-1.0-0:amd64                                                2:1.0.20-1                            amd64                                 userspace USB programming library
 ii  libusbredirparser1:amd64                                          0.7.1-1                               amd64                                 Parser for the usbredir protocol (runtime)
 ii  libustr-1.0-1:amd64                                               1.0.4-5                               amd64                                 Micro string library: shared library
 ii  libutempter0:amd64                                                1.1.6-3                               amd64                                 privileged helper for utmp/wtmp updates (runtime)
 ii  libuuid1:amd64                                                    2.27.1-6ubuntu3.1                     amd64                                 Universally Unique ID library
 ii  libvorbis0a:amd64                                                 1.3.5-3                               amd64                                 decoder library for Vorbis General Audio Compression Codec
 ii  libvorbisenc2:amd64                                               1.3.5-3                               amd64                                 encoder library for Vorbis General Audio Compression Codec
 ii  libwind0-heimdal:amd64                                            1.7~git20150920+dfsg-4ubuntu1         amd64                                 Heimdal Kerberos - stringprep implementation
 ii  libwrap0:amd64                                                    7.6.q-25                              amd64                                 Wietse Venema's TCP wrappers library
 ii  libx11-6:amd64                                                    2:1.6.3-1ubuntu2                      amd64                                 X11 client-side library
 ii  libx11-data                                                       2:1.6.3-1ubuntu2                      all                                   X11 client-side library
 ii  libx11-xcb1:amd64                                                 2:1.6.3-1ubuntu2                      amd64                                 Xlib/XCB interface library
 ii  libxau6:amd64                                                     1:1.0.8-1                             amd64                                 X11 authorisation library
 ii  libxaw7:amd64                                                     2:1.0.13-1                            amd64                                 X11 Athena Widget library
 ii  libxcb-dri2-0:amd64                                               1.11.1-1ubuntu1                       amd64                                 X C Binding, dri2 extension
 ii  libxcb-dri3-0:amd64                                               1.11.1-1ubuntu1                       amd64                                 X C Binding, dri3 extension
 ii  libxcb-glx0:amd64                                                 1.11.1-1ubuntu1                       amd64                                 X C Binding, glx extension
 ii  libxcb-present0:amd64                                             1.11.1-1ubuntu1                       amd64                                 X C Binding, present extension
 ii  libxcb-shape0:amd64                                               1.11.1-1ubuntu1                       amd64                                 X C Binding, shape extension
 ii  libxcb-sync1:amd64                                                1.11.1-1ubuntu1                       amd64                                 X C Binding, sync extension
 ii  libxcb1:amd64                                                     1.11.1-1ubuntu1                       amd64                                 X C Binding
 ii  libxcomposite1:amd64                                              1:0.4.4-1                             amd64                                 X11 Composite extension library
 ii  libxdamage1:amd64                                                 1:1.1.4-2                             amd64                                 X11 damaged region extension library
 ii  libxdmcp6:amd64                                                   1:1.1.2-1.1                           amd64                                 X11 Display Manager Control Protocol library
 ii  libxen-4.6:amd64                                                  4.6.0-1ubuntu4.2                      amd64                                 Public libs for Xen
 ii  libxenstore3.0:amd64                                              4.6.0-1ubuntu4.2                      amd64                                 Xenstore communications library for Xen
 ii  libxext6:amd64                                                    2:1.3.3-1                             amd64                                 X11 miscellaneous extension library
 ii  libxfixes3:amd64                                                  1:5.0.1-2                             amd64                                 X11 miscellaneous 'fixes' extension library
 ii  libxft2:amd64                                                     2.3.2-1                               amd64                                 FreeType-based font drawing library for X
 ii  libxi6:amd64                                                      2:1.7.6-1                             amd64                                 X11 Input extension library
 ii  libxinerama1:amd64                                                2:1.1.3-1                             amd64                                 X11 Xinerama extension library
 ii  libxml2:amd64                                                     2.9.3+dfsg1-1ubuntu0.1                amd64                                 GNOME XML library
 ii  libxmu6:amd64                                                     2:1.1.2-2                             amd64                                 X11 miscellaneous utility library
 ii  libxmuu1:amd64                                                    2:1.1.2-2                             amd64                                 X11 miscellaneous micro-utility library
 ii  libxpm4:amd64                                                     1:3.5.11-1                            amd64                                 X11 pixmap library
 ii  libxrandr2:amd64                                                  2:1.5.0-1                             amd64                                 X11 RandR extension library
 ii  libxrender1:amd64                                                 1:0.9.9-0ubuntu1                      amd64                                 X Rendering Extension client library
 ii  libxshmfence1:amd64                                               1.2-1                                 amd64                                 X shared memory fences - shared library
 ii  libxss1:amd64                                                     1:1.2.2-1                             amd64                                 X11 Screen Saver extension library
 ii  libxt6:amd64                                                      1:1.1.5-0ubuntu1                      amd64                                 X11 toolkit intrinsics library
 ii  libxtables11:amd64                                                1.6.0-2ubuntu3                        amd64                                 netfilter xtables library
 ii  libxtst6:amd64                                                    2:1.2.2-1                             amd64                                 X11 Testing -- Record extension library
 ii  libxv1:amd64                                                      2:1.0.10-1                            amd64                                 X11 Video extension library
 ii  libxxf86dga1:amd64                                                2:1.1.4-1                             amd64                                 X11 Direct Graphics Access extension library
 ii  libxxf86vm1:amd64                                                 1:1.1.4-1                             amd64                                 X11 XFree86 video mode extension library
 ii  libyajl2:amd64                                                    2.1.0-2                               amd64                                 Yet Another JSON Library
 ii  linux-base                                                        4.0ubuntu1                            all                                   Linux image base package
 ii  linux-firmware                                                    1.157.2                               all                                   Firmware for Linux kernel drivers
 ii  linux-generic                                                     4.4.0.72.78                           amd64                                 Complete Generic Linux kernel and headers
 ii  linux-headers-4.4.0-72                                            4.4.0-72.93                           all                                   Header files related to Linux kernel version 4.4.0
 ii  linux-headers-4.4.0-72-generic                                    4.4.0-72.93                           amd64                                 Linux kernel headers for version 4.4.0 on 64 bit x86 SMP
 ii  linux-headers-generic                                             4.4.0.72.78                           amd64                                 Generic Linux kernel headers
 ii  linux-image-4.4.0-72-generic                                      4.4.0-72.93                           amd64                                 Linux kernel image for version 4.4.0 on 64 bit x86 SMP
 ii  linux-image-extra-4.4.0-72-generic                                4.4.0-72.93                           amd64                                 Linux kernel extra modules for version 4.4.0 on 64 bit x86 SMP
 ii  linux-image-generic                                               4.4.0.72.78                           amd64                                 Generic Linux kernel image
 ii  linux-libc-dev:amd64                                              4.4.0-72.93                           amd64                                 Linux Kernel Headers for development
 ii  locales                                                           2.23-0ubuntu3                         all                                   GNU C Library: National Language (locale) data [support]
 ii  login                                                             1:4.2-3.1ubuntu5                      amd64                                 system login tools
 ii  logrotate                                                         3.8.7-2ubuntu2                        amd64                                 Log rotation utility
 ii  lsb-base                                                          9.20160110ubuntu0.2                   all                                   Linux Standard Base init script functionality
 ii  lsb-release                                                       9.20160110ubuntu0.2                   all                                   Linux Standard Base version reporting utility
 ii  lxc                                                               2.0.7-0ubuntu1~16.04.2                all                                   Transitional package for lxc1
 ii  lxc-common                                                        2.0.7-0ubuntu1~16.04.2                amd64                                 Linux Containers userspace tools (common tools)
 ii  lxc-templates                                                     2.0.7-0ubuntu1~16.04.2                amd64                                 Linux Containers userspace tools (templates)
 ii  lxc1                                                              2.0.7-0ubuntu1~16.04.2                amd64                                 Linux Containers userspace tools
 ii  lxcfs                                                             2.0.6-0ubuntu1~16.04.1                amd64                                 FUSE based filesystem for LXC
 ii  m4                                                                1.4.17-5                              amd64                                 macro processing language
 ii  make                                                              4.1-6                                 amd64                                 utility for directing compilation
 ii  makedev                                                           2.3.1-93ubuntu1                       all                                   creates device files in /dev
 ii  manpages                                                          4.04-2                                all                                   Manual pages about using a GNU/Linux system
 ii  manpages-dev                                                      4.04-2                                all                                   Manual pages about using GNU/Linux for development
 ii  mawk                                                              1.3.3-17ubuntu2                       amd64                                 a pattern scanning and text processing language
 ii  mime-support                                                      3.59ubuntu1                           all                                   MIME files 'mime.types' & 'mailcap', and support programs
 ii  mount                                                             2.27.1-6ubuntu3.1                     amd64                                 tools for mounting and manipulating filesystems
 ii  mountall                                                          2.54ubuntu1                           amd64                                 filesystem mounting tool
 ii  msr-tools                                                         1.3-2                                 amd64                                 Utilities for modifying MSRs from userspace
 ii  multiarch-support                                                 2.23-0ubuntu3                         amd64                                 Transitional package to ensure multiarch compatibility
 ii  ncurses-base                                                      6.0+20160213-1ubuntu1                 all                                   basic terminal type definitions
 ii  ncurses-bin                                                       6.0+20160213-1ubuntu1                 amd64                                 terminal-related programs and man pages
 ii  ncurses-term                                                      6.0+20160213-1ubuntu1                 all                                   additional terminal type definitions
 ii  net-tools                                                         1.60-26ubuntu1                        amd64                                 NET-3 networking toolkit
 ii  netbase                                                           5.3                                   all                                   Basic TCP/IP networking system
 ii  netcat-openbsd                                                    1.105-7ubuntu1                        amd64                                 TCP/IP swiss army knife
 ii  openjdk-8-jre-headless:amd64                                      8u131-b11-0ubuntu1.16.04.2            amd64                                 OpenJDK Java runtime, using Hotspot JIT (headless)
 ii  openssh-client                                                    1:7.2p2-4ubuntu2.1                    amd64                                 secure shell (SSH) client, for secure access to remote machines
 ii  openssh-server                                                    1:7.2p2-4ubuntu2.1                    amd64                                 secure shell (SSH) server, for secure access from remote machines
 ii  openssh-sftp-server                                               1:7.2p2-4ubuntu2.1                    amd64                                 secure shell (SSH) sftp server module, for SFTP access from remote machines
 ii  openssl                                                           1.0.2g-1ubuntu4.5                     amd64                                 Secure Sockets Layer toolkit - cryptographic utility
 ii  os-prober                                                         1.70ubuntu3                           amd64                                 utility to detect other OSes on a set of drives
 ii  passwd                                                            1:4.2-3.1ubuntu5                      amd64                                 change and administer password and group data
 ii  patch                                                             2.7.5-1                               amd64                                 Apply a diff file to an original
 ii  pciutils                                                          1:3.3.1-1.1ubuntu1                    amd64                                 Linux PCI Utilities
 ii  perl                                                              5.22.1-9                              amd64                                 Larry Wall's Practical Extraction and Report Language
 ii  perl-base                                                         5.22.1-9                              amd64                                 minimal Perl system
 ii  perl-modules-5.22                                                 5.22.1-9                              all                                   Core Perl modules
 ii  pkg-config                                                        0.29.1-0ubuntu1                       amd64                                 manage compile and link flags for libraries
 ii  plymouth                                                          0.9.2-3ubuntu13.1                     amd64                                 boot animation, logger and I/O multiplexer
 ii  plymouth-theme-ubuntu-text                                        0.9.2-3ubuntu13.1                     amd64                                 boot animation, logger and I/O multiplexer - ubuntu text theme
 ii  procps                                                            2:3.3.10-4ubuntu2                     amd64                                 /proc file system utilities
 ii  python                                                            2.7.11-1                              amd64                                 interactive high-level object-oriented language (default version)
 ii  python-all                                                        2.7.11-1                              amd64                                 package depending on all supported Python runtime versions
 ii  python-all-dev                                                    2.7.11-1                              amd64                                 package depending on all supported Python development packages
 ii  python-apt                                                        1.1.0~beta1build1                     amd64                                 Python interface to libapt-pkg
 ii  python-apt-common                                                 1.1.0~beta1build1                     all                                   Python interface to libapt-pkg (locales)
 ii  python-dev                                                        2.7.11-1                              amd64                                 header files and a static library for Python (default)
 ii  python-iniparse                                                   0.4-2.2                               all                                   access and modify configuration data in INI files (Python 2)
 ii  python-minimal                                                    2.7.11-1                              amd64                                 minimal subset of the Python language (default version)
 ii  python-pip                                                        8.1.1-2ubuntu0.2                      all                                   alternative Python package installer
 ii  python-pip-whl                                                    8.1.1-2ubuntu0.2                      all                                   alternative Python package installer
 ii  python-pkg-resources                                              20.7.0-1                              all                                   Package Discovery and Resource Access using pkg_resources
 ii  python-setuptools                                                 20.7.0-1                              all                                   Python Distutils Enhancements
 ii  python-six                                                        1.10.0-3                              all                                   Python 2 and 3 compatibility library (Python 2 interface)
 ii  python-virtualenv                                                 15.0.1+ds-3                           all                                   Python virtual environment creator
 ii  python-wheel                                                      0.29.0-1                              all                                   built-package format for Python
 ii  python2.7                                                         2.7.12-1~16.04                        amd64                                 Interactive high-level object-oriented language (version 2.7)
 ii  python2.7-dev                                                     2.7.12-1~16.04                        amd64                                 Header files and a static library for Python (v2.7)
 ii  python2.7-minimal                                                 2.7.12-1~16.04                        amd64                                 Minimal subset of the Python language (version 2.7)
 ii  python3                                                           3.5.1-3                               amd64                                 interactive high-level object-oriented language (default python3 version)
 ii  python3-apt                                                       1.1.0~beta1build1                     amd64                                 Python 3 interface to libapt-pkg
 ii  python3-chardet                                                   2.3.0-2                               all                                   universal character encoding detector for Python3
 ii  python3-dbus                                                      1.2.0-3                               amd64                                 simple interprocess messaging system (Python 3 interface)
 ii  python3-gi                                                        3.20.0-0ubuntu1                       amd64                                 Python 3 bindings for gobject-introspection libraries
 ii  python3-lxc                                                       2.0.7-0ubuntu1~16.04.2                amd64                                 Linux Containers userspace tools (Python 3.x bindings)
 ii  python3-minimal                                                   3.5.1-3                               amd64                                 minimal subset of the Python language (default python3 version)
 ii  python3-pkg-resources                                             20.7.0-1                              all                                   Package Discovery and Resource Access using pkg_resources
 ii  python3-requests                                                  2.9.1-3                               all                                   elegant and simple HTTP library for Python3, built for human beings
 ii  python3-six                                                       1.10.0-3                              all                                   Python 2 and 3 compatibility library (Python 3 interface)
 ii  python3-urllib3                                                   1.13.1-2ubuntu0.16.04.1               all                                   HTTP library with thread-safe connection pooling for Python3
 ii  python3-virtualenv                                                15.0.1+ds-3                           all                                   Python virtual environment creator
 ii  python3.5                                                         3.5.2-2~16.01                         amd64                                 Interactive high-level object-oriented language (version 3.5)
 ii  python3.5-minimal                                                 3.5.2-2~16.01                         amd64                                 Minimal subset of the Python language (version 3.5)
 ii  qemu-block-extra:amd64                                            1:2.5+dfsg-5ubuntu10.5                amd64                                 extra block backend modules for qemu-system and qemu-utils
 ii  qemu-system-common                                                1:2.5+dfsg-5ubuntu10.5                amd64                                 QEMU full system emulation binaries (common files)
 ii  qemu-system-x86                                                   1:2.5+dfsg-5ubuntu10.5                amd64                                 QEMU full system emulation binaries (x86)
 ii  qemu-utils                                                        1:2.5+dfsg-5ubuntu10.5                amd64                                 QEMU utilities
 ii  readline-common                                                   6.3-8ubuntu2                          all                                   GNU readline and history libraries, common files
 ii  rename                                                            0.20-4                                all                                   Perl extension for renaming multiple files
 ii  resolvconf                                                        1.78ubuntu2                           all                                   name server information handler
 ii  rsync                                                             3.1.1-3ubuntu1                        amd64                                 fast, versatile, remote (and local) file-copying tool
 ii  rsyslog                                                           8.16.0-1ubuntu3                       amd64                                 reliable system and kernel logging daemon
 ii  screen                                                            4.3.1-2build1                         amd64                                 terminal multiplexer with VT100/ANSI terminal emulation
 ii  seabios                                                           1.8.2-1ubuntu1                        all                                   Legacy BIOS implementation
 ii  sed                                                               4.2.2-7                               amd64                                 The GNU sed stream editor
 ii  sensible-utils                                                    0.0.9                                 all                                   Utilities for sensible alternative selection
 ii  sgml-base                                                         1.26+nmu4ubuntu1                      all                                   SGML infrastructure and SGML catalog file support
 ii  shared-mime-info                                                  1.5-2ubuntu0.1                        amd64                                 FreeDesktop.org shared MIME database and spec
 ii  sharutils                                                         1:4.15.2-1                            amd64                                 shar, unshar, uuencode, uudecode
 ii  socat                                                             1.7.3.1-1                             amd64                                 multipurpose relay for bidirectional data transfer
 ii  ssh-import-id                                                     5.5-0ubuntu1                          all                                   securely retrieve an SSH public key and install it locally
 ii  sudo                                                              1.8.16-0ubuntu1.1                     amd64                                 Provide limited super user privileges to specific users
 ii  systemd                                                           229-4ubuntu10                         amd64                                 system and service manager
 ii  systemd-sysv                                                      229-4ubuntu10                         amd64                                 system and service manager - SysV links
 ii  sysv-rc                                                           2.88dsf-59.3ubuntu2                   all                                   System-V-like runlevel change mechanism
 ii  sysvinit-utils                                                    2.88dsf-59.3ubuntu2                   amd64                                 System-V-like utilities
 ii  tar                                                               1.28-2.1                              amd64                                 GNU version of the tar archiving utility
 ii  tasksel                                                           3.34ubuntu3                           all                                   tool for selecting tasks for installation on Debian systems
 ii  tasksel-data                                                      3.34ubuntu3                           all                                   official tasks used for installation of Debian systems
 ii  tcl-expect:amd64                                                  5.45-7                                amd64                                 Automates interactive applications (Tcl package)
 ii  tcl8.6                                                            8.6.5+dfsg-2                          amd64                                 Tcl (the Tool Command Language) v8.6 - shell
 ii  tcpd                                                              7.6.q-25                              amd64                                 Wietse Venema's TCP wrapper utilities
 ii  tk8.6                                                             8.6.5-1                               amd64                                 Tk toolkit for Tcl and X11 v8.6 - windowing shell
 ii  tzdata                                                            2016g-0ubuntu0.16.04                  all                                   time zone and daylight-saving time data
 ii  ubuntu-keyring                                                    2012.05.19                            all                                   GnuPG keys of the Ubuntu archive
 ii  ubuntu-minimal                                                    1.361                                 amd64                                 Minimal core of Ubuntu
 ii  ucf                                                               3.0036                                all                                   Update Configuration File(s): preserve user changes to config files
 ii  udev                                                              229-4ubuntu10                         amd64                                 /dev/ and hotplug management daemon
 ii  uidmap                                                            1:4.2-3.1ubuntu5.3                    amd64                                 programs to help use subuids
 ii  ureadahead                                                        0.100.0-19                            amd64                                 Read required files in advance
 ii  usbutils                                                          1:007-4                               amd64                                 Linux USB utilities
 ii  util-linux                                                        2.27.1-6ubuntu3.1                     amd64                                 miscellaneous system utilities
 ii  uuid-runtime                                                      2.27.1-6ubuntu3.2                     amd64                                 runtime components for the Universally Unique ID library
 ii  vim-common                                                        2:7.4.1689-3ubuntu1.1                 amd64                                 Vi IMproved - Common files
 ii  vim-tiny                                                          2:7.4.1689-3ubuntu1.1                 amd64                                 Vi IMproved - enhanced vi editor - compact version
 ii  virtualenv                                                        15.0.1+ds-3                           all                                   Python virtual environment creator
 ii  wamerican                                                         7.1-1                                 all                                   American English dictionary words for /usr/share/dict
 ii  wget                                                              1.17.1-1ubuntu1.1                     amd64                                 retrieves files from the web
 ii  whiptail                                                          0.52.18-1ubuntu2                      amd64                                 Displays user-friendly dialog boxes from shell scripts
 ii  wireless-regdb                                                    2015.07.20-1ubuntu1                   all                                   wireless regulatory database
 ii  x11-common                                                        1:7.7+13ubuntu3                       all                                   X Window System (X.Org) infrastructure
 ii  x11-utils                                                         7.7+3                                 amd64                                 X11 utilities
 ii  xauth                                                             1:1.0.9-1ubuntu2                      amd64                                 X authentication utility
 ii  xbitmaps                                                          1.1.1-2                               all                                   Base X bitmaps
 ii  xdg-user-dirs                                                     0.15-2ubuntu6                         amd64                                 tool to manage well known user directories
 ii  xkb-data                                                          2.16-1ubuntu1                         all                                   X Keyboard Extension (XKB) configuration data
 ii  xml-core                                                          0.13+nmu2                             all                                   XML infrastructure and XML catalog file support
 ii  xterm                                                             322-1ubuntu1                          amd64                                 X terminal emulator
 ii  xz-utils                                                          5.1.1alpha+20120614-2ubuntu2          amd64                                 XZ-format compression utilities
 ii  zlib1g:amd64                                                      1:1.2.8.dfsg-2ubuntu4                 amd64                                 compression library - runtime
 ii  zlib1g-dev:amd64                                                  1:1.2.8.dfsg-2ubuntu4                 amd64                                 compression library - development
```
