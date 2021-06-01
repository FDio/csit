<!-- MarkdownTOC autolink="true" -->

- [FD.io DC Vexxhost Inventory](#fdio-dc-vexxhost-inventory)
  - [Missing Equipment Inventory](#missing-equipment-inventory)
  - [YUL1 Inventory](#yul1-inventory)
    - [Rack YUL1-9 (3016.9)](#rack-yul1-10-3016.9)
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

#### Rack YUL1-9 (3016.9)
name,oper-status,testbed-id,role,model,s/n,mgmt-ip4,ipmi-ip4,rackid,rackunit
mtl1-5-lb4m,up,switch,uplink,?,?,?,?,3016.9,u47,?,?
s11-t31-sut1,up,t31,3n-skx,SYS-7049GP-TRT,C7470KH06A20037,10.30.51.46,10.30.50.43,3016.9,u42-u45
s12-t31-sut2,up,t31,3n-skx,SYS-7049GP-TRT,C7470KH06A20018,10.30.51.47,10.30.50.44,3016.9,u38-u41
s13-t31-tg1,up,t31,3n-skx,SYS-7049GP-TRT,C7470KH06A20043,10.30.51.48,10.30.50.45,3016.9,u34-u37
s14-t32-sut1,up,t31,3n-skx,SYS-7049GP-TRT,C7470KH06A20075,10.30.51.58,10.30.50.55,3016.9,u30-u33
s15-t32-sut2,up,t31,3n-skx,SYS-7049GP-TRT,C7470KH06A20010,10.30.51.59,10.30.50.56,3016.9,u26-u29
s16-t32-tg1,up,t31,3n-skx,SYS-7049GP-TRT,C7470KH06A20047,10.30.51.60,10.30.50.57,3016.9,u22-u25
s25-t25-sut1,down,t25,2n-p1,SYS-7049GP-TRT,C7470KH06A20022,10.30.51.61,10.30.50.58,3016.9,u18-u21
s19-t33t34-tg1,up,t33t34,3n-tsh/2n-tx2,SYS-7049GP-TRT,C7470KH06A20056,10.30.51.49,10.30.50.46,3016.9,u14-u17
s27-t211-sut1,up,t25,2n-tx2,ThunderX2-9975,K61186073100003,10.30.51.69,10.30.50.69,3016.9,u13
s18-t33-sut2,up,t33,3n-tsh,HUAWEI-TAISHAN-2280,N/A,10.30.51.37,10.30.50.37,3016.9,u11-u12
s17-t33-sut1,up,t33,3n-tsh,HUAWEI-TAISHAN-2280,N/A,10.30.51.36,10.30.50.36,3016.9,u9-u10

#### Rack YUL1-10 (3016.10)

name,oper-status,testbed-id,role,model,s/n,mgmt-ip4,ipmi-ip4,rackid,rackunit
yul1-10-lb4m,up,switch,uplink,?,?,?,?,3016.10,u47,?,?
s2-t12-sut1,up,t12,1n-skx,SYS-7049GP-TRT,C7470KH06A20119,10.30.51.51,10.30.50.48,3016.10,u42-u45
s1-t11-sut1,up,t11,1n-skx,SYS-7049GP-TRT,C7470KH06A20154,10.30.51.50,10.30.50.47,3016.10,u38-u41
s3-t21-sut1,up,t21,2n-skx,SYS-7049GP-TRT,C7470KH06A20167,10.30.51.44,10.30.50.41,3016.10,u34-u37
s4-t21-tg1,up,t21,2n-skx,SYS-7049GP-TRT,C7470KH06A20158,10.30.51.45,10.30.50.42,3016.10,u30-u33
s5-t22-sut1,up,t22,2n-skx,SYS-7049GP-TRT,N/A,10.30.51.52,10.30.50.49,3016.10,u26-u29
s6-t22-tg1,up,t22,2n-skx,SYS-7049GP-TRT,N/A,10.30.51.53,10.30.50.50,3016.10,u22-u25
s7-t23-sut1,up,t23,2n-skx,SYS-7049GP-TRT,N/A,10.30.51.54,10.30.50.51,3016.10,u18-u21
s8-t23-tg1,up,t23,2n-skx,SYS-7049GP-TRT,C7470KH06A20035,10.30.51.55,10.30.50.52,3016.10,u14-u17
s9-t24-sut1,up,t24,2n-skx,SYS-7049GP-TRT,C7470KH06A20055,10.30.51.56,10.30.50.53,3016.10,u10-u13
s10-t24-tg1,up,t24,2n-skx,SYS-7049GP-TRT,C7470KH06A20196,10.30.51.57,10.30.50.54,3016.10,u6-u9

#### Rack YUL1-11 (3016.11)

name,oper-status,testbed-id,role,model,s/n,mgmt-ip4,ipmi-ip4,rackid,rackunit
yul1-11-lb6m,up,switch,arm-uplink,?,?,?,?,3016.11,u48
yul1-11-lf-tor-switch,up,switch,uplink,?,?,?,?,3016.11,u47
mtl1-6-7050QX-32,up,switch,uplink,?,?,?,?,3016.11,u46
fdio-marvell-dev,up,N/A,dev,ThunderX-88XX,N/A,10.30.51.38,10.30.50.38,3016.11,u45
s53-nomad,up,nomad-cluster1,nomad-client,ThunderX-88XX,N/A,10.30.51.39,10.30.50.39,3016.11,u44
s54-nomad,up,nomad-cluster1,nomad-client,ThunderX-88XX,N/A,10.30.51.40,10.30.50.40,3016.11,u43
s56-t37-sut1,up,t37,2n-tx2,ThunderX2-9980,N/A,10.30.51.71,10.30.50.71,3016.11,u41-u42
s41-nomad,up,nomad-cluster1,nomad-client,UCSC-C240-M4SX,FCH1950V1FQ,10.30.51.28,10.30.50.28,3016.11,u39-u40
s40-nomad,up,nomad-cluster1,nomad-server,UCSC-C240-M4SX,FCH2013V0HZ,10.30.51.30,10.30.50.30,3016.11,u37-u38
s39-nomad,up,nomad-cluster1,nomad-client,UCSC-C240-M4SX,FCH2013V0J2,10.30.51.29,10.30.50.29,3016.11,u35-u36
s42-nomad,up,nomad-cluster1,nomad-server,UCSC-C240-M4SX,FCH1950V1FN,10.30.51.22,10.30.50.22,3016.11,u19-u20
s43-nomad,up,nomad-cluster1,nomad-server,UCSC-C240-M4SX,FCH1950V1H5,10.30.51.24,10.30.50.24,3016.11,u17-u18
s44-nomad,up,nomad-cluster1,nomad-client,UCSC-C240-M4SX,FCH1950V1FS,10.30.51.25,10.30.50.25,3016.11,u15-u16
s45-nomad,up,nomad-cluster1,nomad-client,UCSC-C240-M4SX,FCH1950V1FL,10.30.51.26,10.30.50.26,3016.11,u13-u14
s55-t36-sut1,up,t36,1n-tx2,ThunderX2-9980,N/A,10.30.51.70,10.30.50.70,3016.11,u11-u12
s52-nomad,up,nomad-cluster1,nomad-client,ThunderX-88XX,N/A,10.30.51.65,10.30.50.65,3016.11,u9-u10
s51-nomad,up,nomad-cluster1,nomad-client,ThunderX-88XX,N/A,10.30.51.66,10.30.50.66,3016.11,u9-u10
s49-nomad,up,nomad-cluster1,nomad-client,ThunderX-88XX,N/A,10.30.51.67,10.30.50.67,3016.11,u9-u10
s50-nomad,up,nomad-cluster1,nomad-client,ThunderX-88XX,N/A,10.30.51.68,10.30.50.68,3016.11,u9-u10

#### Rack YUL1-12 (3016.12)

name,oper-status,testbed-id,role,model,s/n,mgmt-ip4,ipmi-ip4,rackid,rackunit
s31-t35-sut2/dnv3,up,t35,3n-dnv,SYS-E300-9A,CE300AG39040898,10.32.8.13,10.30.55.13,3016.12,u40
s30-t35-sut1/dnv2,up,t35,3n-dnv,SYS-E300-9A,CE300AG39040866,10.32.8.12,10.30.55.12,3016.12,u39
s29-t26-sut1/dnv1,up,t26,2n-dnv,SYS-E300-9A,CE300AG39040897,10.32.8.11,10.30.55.11,3016.12,u38
s28-t26t35-tg1,up,t26t35,2n/3n-dnv,SYS-7049GP-TRT,C7470KH06A20137,10.32.8.10,10.30.55.10,3016.12,u34-u37
s61-t210-tg1,up,t210,2n-zn2,AS-1014S-WTRT,C8150LI50NS2689,10.32.8.25,10.30.55.25,3016.12,u33
s60-t210-sut1,up,t210,2n-zn2,AS-1114S-WTRT,N/A,10.32.8.24,10.30.55.24,3016.12,u32
s48-nomad,up,nomad-cluster1,nomad-client,SYS-1029P-WTRT,C1160LI12NM0540,10.32.8.16,10.30.55.16,3016.12,u31
s47-nomad,up,nomad-cluster1,nomad-client,SYS-1029P-WTRT,C1160LI12NM0241,10.32.8.15,10.30.55.15,3016.12,u30
s46-nomad,up,nomad-cluster1,nomad-client,SYS-1029P-WTRT,C1160LI12NM0256,10.32.8.14,10.30.55.14,3016.12,u29
s57-nomad,up,nomad-cluster1,nomad-client,SYS-7049GP-TRT,C7470KH37A30505,10.32.8.17,10.30.55.17,3016.12,u25-u28
s33-t27-sut1,up,t27,2n-clx,SYS-7049GP-TRT,C7470KH37A30567,10.32.8.18,10.30.55.18,3016.12,u21-u24
s34-t27-tg1,up,t27,2n-clx,SYS-7049GP-TRT,C7470KH37A30565,10.32.8.19,10.30.55.19,3016.12,u17-u20
s35-t28-sut1,up,t28,2n-clx,SYS-7049GP-TRT,C7470KH37A30509,10.32.8.20,10.30.55.20,3016.12,u13-u16
s36-t28-tg1,up,t28,2n-clx,SYS-7049GP-TRT,C7470KH37A30511,10.32.8.21,10.30.55.21,3016.12,u9-u12
s37-t29-sut1,up,t29,2n-clx,SYS-7049GP-TRT,C7470KH37A30566,10.32.8.22,10.30.55.22,3016.12,u5-u8
s38-t29-tg1,up,t29,2n-clx,SYS-7049GP-TRT,C7470KH37A30506,10.32.8.23,10.30.55.23,3016.12,u1-u4

Notes:

- softiron-1, softiron-2, softiron-3, decommission request and instructions issued
  on 16-Sep-2020, per Vexxhost ticket
  [#FDU-009676 - New arm hardware - 2xThunderX2](https://secure.vexxhost.com/billing/viewticket.php?tid=FDU-009676&c=ncHht136),
  search for "softiron".
- UCSC-C240-M4 EoL:
  [End-of-Life Announcement for the Cisco Unified Computing System C-Series](https://www.cisco.com/c/en/us/products/collateral/servers-unified-computing/ucs-c-series-rack-servers/eos-eol-notice-c51-741235.html)