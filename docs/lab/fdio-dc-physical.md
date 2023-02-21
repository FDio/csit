<!-- MarkdownTOC autolink="true" -->

- [FD.io DC Vexxhost Inventory](#fdio-dc-vexxhost-inventory)
  - [Missing Equipment Inventory](#missing-equipment-inventory)
  - [YUL1 Inventory](#yul1-inventory)
    - [Rack YUL1-8 (3016.8)](#rack-yul1-8-3016.8)
    - [Rack YUL1-9 (3016.9)](#rack-yul1-9-3016.9)
    - [Rack YUL1-10 (3016.10)](#rack-yul1-10-3016.10)
    - [Rack YUL1-11 (3016.11)](#rack-yul1-11-3016.11)
    - [Rack YUL1-12 (3016.12)](#rack-yul1-12-3016.12)

<!-- /MarkdownTOC -->

## FD.io DC Vexxhost Inventory

- for each DC location, per rack .csv table with server inventory
- captured inventory data: name,oper-status,testbed-id,role,model,s/n,rackid,rackunit,mgmt-ip4,ipmi-ip4,new-rackid,new-rackunit,new-mgmt-ip4,new-ipmi-ip4
  - name: CSIT functional server name as tracked in [CSIT testbed specification](https://git.fd.io/csit/tree/docs/lab/testbed_specifications.md), followed by "/" and the actual configured hostname, unless it is the same as CSIT name.
  - oper-status: operational status (up|down|ipmi).
  - testbed-id: CSIT testbed identifier.
  - role: 2n/3n-xxx performance testbed, nomad-client, nomad-server.
    - role exceptions: decommission, repurpose, spare.
  - model: server model.
  - s/n: serial number.
  - mgmt-ip4: current management IPv4 address on management VLAN.
  - ipmi-ip4: current IPMI IPv4 address on LOM VLAN.
  - rackid: new location rack id.
  - rackunit: new location rack unit id.

### Missing Equipment Inventory

1. Ixia PerfectStorm One Appliance
   - [Specification: Ixia PerfectStorm One Appliance TG for FD.io TCP/IP performance tests.](https://git.fd.io/csit/tree/docs/lab/testbed_specifications.md#n554)
   - [Wiring: 2-Node-IxiaPS1L47 Servers (2n-ps1)](https://git.fd.io/csit/tree/docs/lab/testbed_specifications.md#n1017)
   - [mgmt-ip4 10.30.51.62 s26-t25-tg1](https://git.fd.io/csit/tree/docs/lab/testbed_specifications.md#n374)
   - [ipmi-ip4 10.30.50.59 s26-t25-tg1](https://git.fd.io/csit/tree/docs/lab/testbed_specifications.md#n281)

### YUL1 Inventory

#### Rack YUL1-8 (3016.8)
name,oper-status,testbed-id,role,model,s/n,mgmt-ip4,ipmi-ip4,rackid,rackunit
mtl1-8-lb4m,up,switch,uplink,?,?,?,?,3016.8,u47,?,?
s65-t37-sut1,up,t37,3n-icx,SYS-740GP-TNRT,C7470KK25P50098,10.30.51.75,10.30.50.75,3016.8,u42-u45
s66-t37-sut2,up,t37,3n-icx,SYS-740GP-TNRT,C7470KK33P50247,10.30.51.76,10.30.50.76,3016.8,u38-u41
s67-t37-tg1,up,t37,3n-icx,SYS-740GP-TNRT,C7470KK25P50076,10.30.51.77,10.30.50.77,3016.8,u34-u37
s71-t212-sut1,up,t212,2n-icx,SYS-740GP-TNRT,C7470KK25P50173,10.30.51.81,10.30.50.81,3016.8,u30-u33
s72-t212-tg1,up,t212,2n-icx,SYS-740GP-TNRT,C7470KK33P50220,10.30.51.82,10.30.50.82,3016.8,u26-u29
s83-t213-sut1,up,t213,2n-icx,SYS-740GP-TNRT,C7470KL07P50300,10.30.51.83,10.30.50.83,3016.8,u22-u25
s84-t213-tg1,up,t213,2n-icx,SYS-740GP-TNRT,C7470KL03P50187,10.30.51.84,10.30.50.84,3016.8,u18-u21
s85-t214-sut1,up,t214,2n-icx,SYS-740GP-TNRT,C7470KK33P50219,10.30.51.85,10.30.50.85,3016.8,u14-u17
s86-t214-tg1,up,t214,2n-icx,SYS-740GP-TNRT,C7470KL07P50312,10.30.51.86,10.30.50.86,3016.8,u10-u13
s87-t215-sut1,up,t215,2n-icx,SYS-740GP-TNRT,C7470KL03P50171,10.30.51.87,10.30.50.87,3016.8,u6-u9
s88-t215-tg1,up,t215,2n-icx,SYS-740GP-TNRT,C7470KL07P50301,10.30.51.88,10.30.50.88,3016.8,u2-u5

#### Rack YUL1-9 (3016.9)
name,oper-status,testbed-id,role,model,s/n,mgmt-ip4,ipmi-ip4,rackid,rackunit
mtl1-5-lb4m,up,switch,uplink,?,?,?,?,3016.9,u47,?,?
s52-t21-sut1,up,t21,2n-spr,SYS-741GE-TNRT,???,10.30.51.52,10.30.50.52,3016.9,u42-u45
s53-t21-tg1,up,t21,2n-spr,SYS-741GE-TNRT,???,10.30.51.53,10.30.50.53,3016.9,u38-u41
s54-t22-sut1,up,t22,2n-spr,SYS-741GE-TNRT,???,10.30.51.54,10.30.50.54,3016.9,u34-u37
s55-t22-tg1,up,t22,2n-spr,SYS-741GE-TNRT,???,10.30.51.55,10.30.50.55,3016.9,u30-u33
s56-t23-sut1,up,t23,2n-spr,SYS-741GE-TNRT,???,10.30.51.56,10.30.50.56,3016.9,u26-u29
s57-t23-tg1,up,t23,2n-spr,SYS-741GE-TNRT,???,10.30.51.57,10.30.50.57,3016.9,u22-u25
s25-t25-sut1,down,t25,2n-p1,SYS-7049GP-TRT,C7470KH06A20022,10.30.51.61,10.30.50.58,3016.9,u18-u21
s19-t33t211-tg1,up,t33t211,3n-tsh/2n-tx2,SYS-7049GP-TRT,C7470KH06A20056,10.30.51.49,10.30.50.46,3016.9,u14-u17
s27-t211-sut1,up,t211,2n-tx2,ThunderX2-9975,K61186073100003,10.30.51.69,10.30.50.69,3016.9,u13
s18-t33-sut2,up,t33,3n-tsh,HUAWEI-TAISHAN-2280,N/A,10.30.51.37,10.30.50.37,3016.9,u11-u12
s17-t33-sut1,up,t33,3n-tsh,HUAWEI-TAISHAN-2280,N/A,10.30.51.36,10.30.50.36,3016.9,u9-u10
s79-t39t310-tg1,in-transit,t39t310,tbd,SYS-740GP-TNRT,???,10.30.51.89,10.30.50.89,3016.9,u5-u8

#### Rack YUL1-10 (3016.10)

name,oper-status,testbed-id,role,model,s/n,mgmt-ip4,ipmi-ip4,rackid,rackunit
yul1-10-lb4m,up,switch,uplink,?,?,?,?,3016.10,u47,?,?
s2-t12-sut1,up,t12,1n-skx,SYS-7049GP-TRT,C7470KH06A20119,10.30.51.51,10.30.50.48,3016.10,u42-u45
s1-t11-sut1,up,t11,1n-skx,SYS-7049GP-TRT,C7470KH06A20154,10.30.51.50,10.30.50.47,3016.10,u38-u41
s58-t24-sut1,up,t24,2n-spr,SYS-741GE-TNRT,???,10.30.51.58,10.30.50.58,3016.10,u34-u37
s59-t24-tg1,up,t24,2n-spr,SYS-741GE-TNRT,???,10.30.51.59,10.30.50.59,3016.10,u30-u33
s93-t39-sut1,up,t39,3n-snr,?,?,10.30.51.93,10.30.50.93,3016.10,u10-u13
s94-t39-sut2,up,t39,3n-snr,?,?,10.30.51.94,10.30.50.94,3016.10,u6-u9
s89-t39t310-tg1,up,t39,3n-snr,?,?,10.30.51.89,10.30.50.89,3016.10,u2-u5

#### Rack YUL1-11 (3016.11)

name,oper-status,testbed-id,role,model,s/n,mgmt-ip4,ipmi-ip4,rackid,rackunit
yul1-11-lb6m,up,switch,arm-uplink,?,?,?,?,3016.11,u48
yul1-11-lf-tor-switch,up,switch,uplink,?,?,?,?,3016.11,u47
mtl1-6-7050QX-32,up,switch,uplink,?,?,?,?,3016.11,u46
fdio-marvell-dev,up,N/A,dev,ThunderX-88XX,N/A,10.30.51.38,10.30.50.38,3016.11,u45
s56-t14-sut1,up,t14,1n-tx2,ThunderX2-9980,N/A,10.30.51.71,10.30.50.71,3016.11,u41-u42
s78-t38-sut1,up,t38,3n-icx,SYS-740GP-TNRT,C7470KL03P50450,10.30.51.78,10.30.50.78,3016.11,u31-u34
s79-t38-sut2,up,t38,3n-icx,SYS-740GP-TNRT,C7470KL07P50297,10.30.51.79,10.30.50.79,3016.11,u27-u30
s80-t38-tg1,up,t38,3n-icx,SYS-740GP-TNRT,C7470KL03P50454,10.30.51.80,10.30.50.80,3016.11,u23-u26
s55-t13-sut1,up,t13,1n-tx2,ThunderX2-9980,N/A,10.30.51.70,10.30.50.70,3016.11,u11-u12
s62-t34-sut1,up,t34,3n-alt,WIWYNN,04000059N0SC,10.30.51.72,10.30.50.72,3016.11,u9-u10
s63-t34-sut2,up,t34,3n-alt,WIWYNN,0390003EN0SC,10.30.51.73,10.30.50.73,3016.11,u7-u8
s64-t34-tg1,up,t34,3n-alt,SYS-740GP-TNRT,C7470KK40P50249,10.30.51.74,10.30.50.74,3016.11,u3-u6

#### Rack YUL1-12 (3016.12)

name,oper-status,testbed-id,role,model,s/n,mgmt-ip4,ipmi-ip4,rackid,rackunit
yul1-12-lb4m,up,switch,uplink,?,?,?,?,3016.12,u47
s28-nomad,up,nomad-cluster1.nomad-client,SYS-7049GP-TRT,C7470KH06A20196,10.30.51.28,10.30.50.28,3016.12,u41-u44
s27-nomad,up,nomad-cluster1,nomad-client,SYS-7049GP-TRT,C7470KH06A20055,10.30.51.27,10.30.50.27,3016.12,u37-u40
s91-nomad,up,nomad-cluster1,nomad-client,R152-P30-00,GLG4P9912A0016,10.30.51.91,10.30.50.91,3016.12,u36
s92-nomad,up,nomad-cluster1,nomad-client,R152-P30-00,GLG4P9912A0004,10.30.51.92,10.30.50.92,3016.12,u35
s23-nomad,up,nomad-cluster1,nomad-server,SYS-1029P-WTRT,C1160LI12NM0256,10.30.51.23,10.30.51.23,3016.12,u34
s24-nomad,up,nomad-cluster1,nomad-server,SYS-1029P-WTRT,C1160LI12NM0241,10.30.51.24,10.30.51.24,3016.12,u33
s25-nomad,up,nomad-cluster1,nomad-server,SYS-1029P-WTRT,C1160LI12NM0540,10.30.51.25,10.30.51.25,3016.12,u32
s61-t210-tg1,up,t210,2n-zn2,AS-1014S-WTRT,C8150LI50NS2689,10.32.8.25,10.30.55.25,3016.12,u31
s60-t210-sut1,up,t210,2n-zn2,AS-1114S-WTRT,N/A,10.32.8.24,10.30.55.24,3016.12,u30
s26-nomad,up,nomad-cluster1,nomad-server,SYS-7049GP-TRT,C7470KH37A30505,10.30.51.26,10.30.51.26,3016.12,u26-u29
s33-t27-sut1,up,t27,2n-clx,SYS-7049GP-TRT,C7470KH37A30567,10.32.8.18,10.30.55.18,3016.12,u22-u25
s34-t27-tg1,up,t27,2n-clx,SYS-7049GP-TRT,C7470KH37A30565,10.32.8.19,10.30.55.19,3016.12,u18-u21
s35-t28-sut1,up,t28,2n-clx,SYS-7049GP-TRT,C7470KH37A30509,10.32.8.20,10.30.55.20,3016.12,u14-u17
s36-t28-tg1,up,t28,2n-clx,SYS-7049GP-TRT,C7470KH37A30511,10.32.8.21,10.30.55.21,3016.12,u10-u13
s37-t29-sut1,up,t29,2n-clx,SYS-7049GP-TRT,C7470KH37A30566,10.32.8.22,10.30.55.22,3016.12,u6-u9
s38-t29-tg1,up,t29,2n-clx,SYS-7049GP-TRT,C7470KH37A30506,10.32.8.23,10.30.55.23,3016.12,u2-u5
