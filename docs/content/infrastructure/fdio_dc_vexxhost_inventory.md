---
title: "FD.io DC Vexxhost Inventory"
weight: 1
---

# FD.io DC Vexxhost Inventory

Captured inventory data:
  - **name**: CSIT functional server name as tracked in
    [CSIT testbed specification]({{< ref "fdio_dc_testbed_specifications#FD.io CSIT Testbed Specifications" >}}),
    followed by "/" and the actual configured hostname, unless it is the same
    as CSIT name.
  - **role**: 2n/3n-xxx performance testbed, nomad-client, nomad-server.
    - role exceptions: decommission, repurpose, spare.
  - **model**: server model.
  - **s/n**: serial number.
  - **mgmt-ip4**: current management IPv4 address on management VLAN.
  - **ipmi-ip4**: current IPMI IPv4 address on LOM VLAN.
  - **rackid**: new location rack id.
  - **rackunit**: new location rack unit id.

## Equinix Inventory

### Rack 206

 **name**        | **role**      | **model**           | **s/n**         | **mgmt-ip4** | **ipmi-ip4** | **rackid** | **rackunit**
-----------------|---------------|---------------------|-----------------|--------------|--------------|------------|--------------
 ToR switch      | uplink        | ?                   | ?               | ?            | ?            | 206        | u45
 s75-t37-sut1    | 3n-icx        | SYS-740GP-TNRT      | C7470KK25P50098 | 10.30.51.75  | 10.30.50.75  | 206        | u41-u44
 s76-t37-sut2    | 3n-icx        | SYS-740GP-TNRT      | C7470KK33P50247 | 10.30.51.76  | 10.30.50.76  | 206        | u37-u40
 s77-t37-tg1     | 3n-icx        | SYS-740GP-TNRT      | C7470KK25P50076 | 10.30.51.77  | 10.30.50.77  | 206        | u33-u36
 s81-t212-sut1   | 2n-icx        | SYS-740GP-TNRT      | C7470KK25P50173 | 10.30.51.81  | 10.30.50.81  | 206        | u29-u32
 s82-t212-tg1    | 2n-icx        | SYS-740GP-TNRT      | C7470KK33P50220 | 10.30.51.82  | 10.30.50.82  | 206        | u25-u28
 s83-t213-sut1   | 2n-icx        | SYS-740GP-TNRT      | C7470KL07P50300 | 10.30.51.83  | 10.30.50.83  | 206        | u21-u24
 s84-t213-tg1    | 2n-icx        | SYS-740GP-TNRT      | C7470KL03P50187 | 10.30.51.84  | 10.30.50.84  | 206        | u17-u20
 s85-t214-sut1   | 2n-icx        | SYS-740GP-TNRT      | C7470KK33P50219 | 10.30.51.85  | 10.30.50.85  | 206        | u13-u16
 s86-t214-tg1    | 2n-icx        | SYS-740GP-TNRT      | C7470KL07P50312 | 10.30.51.86  | 10.30.50.86  | 206        | u9-u12
 s87-t215-sut1   | 2n-oct        | SYS-740GP-TNRT      | C7470KL03P50171 | 10.30.51.87  | 10.30.50.87  | 206        | u5-u8
 s95-t215-dpu1   | 2n-oct-dpu1   | -                   | -               | 10.30.51.95  | 10.30.50.95  | 206        | u5-u8
 s96-t215-dpu2   | 2n-oct-dpu2   | -                   | -               | 10.30.51.96  | 10.30.50.96  | 206        | u5-u8
 s88-t215-tg1    | 2n-oct        | SYS-740GP-TNRT      | C7470KL07P50301 | 10.30.51.88  | 10.30.50.88  | 206        | u1-u4

### Rack 207

 **name**        | **role**      | **model**           | **s/n**         | **mgmt-ip4** | **ipmi-ip4** | **rackid** | **rackunit**
-----------------|---------------|---------------------|-----------------|--------------|--------------|------------|--------------
 ToR switch      | uplink        | ?                   | ?               | ?            | ?            | 207        | u45
 s52-t21-sut1    | 2n-spr        | SYS-741GE-TNRT      | C7490FL36A40118 | 10.30.51.52  | 10.30.50.52  | 207        | u41-u44
 s53-t21-tg1     | 2n-spr        | SYS-741GE-TNRT      | C7490FL36A40115 | 10.30.51.53  | 10.30.50.53  | 207        | u37-u40
 s54-t22-sut1    | 2n-spr        | SYS-741GE-TNRT      | C7490FL36A40117 | 10.30.51.54  | 10.30.50.54  | 207        | u33-u36
 s55-t22-tg1     | 2n-spr        | SYS-741GE-TNRT      | C7490FL36A40114 | 10.30.51.55  | 10.30.50.55  | 207        | u29-u32
 s56-t23-sut1    | 2n-spr        | SYS-741GE-TNRT      | C7490FL36A40121 | 10.30.51.56  | 10.30.50.56  | 207        | u25-u28
 s57-t23-tg1     | 2n-spr        | SYS-741GE-TNRT      | C7490FL36A40116 | 10.30.51.57  | 10.30.50.57  | 207        | u21-u24
 s58-t24-sut1    | 2n-spr        | SYS-741GE-TNRT      | C7490FL36A40107 | 10.30.51.58  | 10.30.50.58  | 207        | u17-u20
 s59-t24-tg1     | 2n-spr        | SYS-741GE-TNRT      | C7490FL36A40122 | 10.30.51.59  | 10.30.50.59  | 207        | u13-u16
 s78-t38-sut1    | 3n-icx        | SYS-740GP-TNRT      | C7470KL03P50450 | 10.30.51.78  | 10.30.50.78  | 207        | u9-u12
 s79-t38-sut2    | 3n-icx        | SYS-740GP-TNRT      | C7470KL07P50297 | 10.30.51.79  | 10.30.50.79  | 207        | u5-u8
 s80-t38-tg1     | 3n-icx        | SYS-740GP-TNRT      | C7470KL03P50454 | 10.30.51.80  | 10.30.50.80  | 207        | u1-u4

### Rack 208

 **name**        | **role**      | **model**           | **s/n**         | **mgmt-ip4** | **ipmi-ip4** | **rackid** | **rackunit**
-----------------|---------------|---------------------|-----------------|--------------|--------------|------------|--------------
 ToR Switch      | uplink        | ?                   | ?               | ?            | ?            | 208        | u45
 s21-nomad       | nomad-client  | SYS-741GE-TNRT      | C7490FL47A50150 | 10.30.51.21  | 10.30.50.21  | 208        | u41-u44
 s22-nomad       | nomad-client  | SYS-741GE-TNRT      | C7490FL47A50155 | 10.30.51.22  | 10.30.50.22  | 208        | u37-u40
 s30-nomad       | nomad-client  | SYS-741GE-TNRT      | C7490FL47A50154 | 10.30.51.30  | 10.30.50.30  | 208        | u33-u36
 s31-nomad       | nomad-client  | SYS-741GE-TNRT      | C7490FL47A50149 | 10.30.51.31  | 10.30.50.31  | 208        | u29-u32
 s89-t39t310-tg1 | nomad-client  | SYS-7049GP-TRT      | C7470KH37A30506 | 10.30.51.89  | 10.30.50.89  | 208        | u25-u28
 s90-t31t32-tg1  | nomad-client  | SYS-740GP-TNRT      | C7470KL03P50184 | 10.30.51.90  | 10.30.50.90  | 208        | u21-u24
 s70-nomad       | nomad-client  | E252-P30-00         | GMG252012A0098  | 10.30.51.70  | 10.30.50.70  | 208        | u19-u20
 s71-nomad       | nomad-client  | E252-P30-00         | GMG252012A0089  | 10.30.51.71  | 10.30.50.71  | 208        | u17-u18
 s40-t28-sut1    | 2n-emr        | SYS-??-TRT          | S512539X4A04503 | 10.30.51.40  | 10.30.50.40  | 208        | u13-u16
 s41-t28-tg1     | 2n-emr        | SYS-??-TRT          | S512539X4A04502 | 10.30.51.41  | 10.30.50.41  | 208        | u9-u12
 s42-t29-sut1    | 2n-emr        | SYS-??-TRT          | S512539X4A04504 | 10.30.51.42  | 10.30.50.42  | 208        | u5-u8
 s43-t29-tg1     | 2n-emr        | SYS-??-TRT          | S512539X4A04500 | 10.30.51.43  | 10.30.50.43  | 208        | u1-u4

### Rack 209

 **name**        | **role**      | **model**           | **s/n**         | **mgmt-ip4** | **ipmi-ip4** | **rackid** | **rackunit**
-----------------|---------------|---------------------|-----------------|--------------|--------------|------------|--------------
 ToR Switch      | uplink        | ?                   | ?               | ?            | ?            | 209        | u45
 fdio-marvell-dev| dev           | ThunderX-88XX       | N/A             | 10.30.51.38  | 10.30.50.38  | 209        | u43-u43
 s61-t210-tg1    | 2n-zn2        | AS-1014S-WTRT       | S366866X0515596 | 10.30.51.61  | 10.30.55.25  | 209        | u42-u42
 s60-t210-sut1   | 2n-zn2        | AS-1114S-WTRT       | S367023X0304458 | 10.30.51.60  | 10.30.55.24  | 209        | u41-u41
 s27-nomad       | nomad-client  | SYS-7049GP-TRT      | C7470KH06A20055 | 10.30.51.27  | 10.30.50.27  | 209        | u37-u40
 s28-nomad       | nomad-client  | SYS-7049GP-TRT      | C7470KH06A20196 | 10.30.51.28  | 10.30.50.28  | 209        | u33-u36
 s50-nomad       | nomad-client  | SYS-7049GP-TRT      | C7470KH06A20154 | 10.30.51.50  | 10.30.50.50  | 209        | u29-u32
 s51-nomad       | nomad-client  | SYS-7049GP-TRT      | C7470KH06A20119 | 10.30.51.51  | 10.30.50.51  | 209        | u25-u28
 s62-t216-sut1   | 3n-srf        | SYS-222H-TN         | CH219AO34BD0172 | 10.30.51.62  | 10.30.50.62  | 209        | u23-u24
 s63-t216-sut2   | 3n-srf        | SYS-222H-TN         | CH219AO34BD0171 | 10.30.51.63  | 10.30.50.63  | 209        | u21-u22
 s49-t216-tg1    | 3n-srf        | SYS-??-TRT          | S512539X4A04501 | 10.30.51.49  | 10.30.50.49  | 209        | u17-u20
 s72-t34-sut1    | 3n-alt        | WIWYNN              | 04000059N0SC    | 10.30.51.72  | 10.30.50.72  | 209        | u15-u16
 s73-t34-sut2    | 3n-alt        | WIWYNN              | 0390003EN0SC    | 10.30.51.73  | 10.30.50.73  | 209        | u13-u14
 s74-t34-tg1     | 3n-alt        | SYS-740GP-TNRT      | C7470KK40P50249 | 10.30.51.74  | 10.30.50.74  | 209        | u9-u12
 s64-t217-sut1   | 2n-gnr        | SYS-222H-TN         | CH219AO34BD0165 | 10.30.51.64  | 10.30.50.64  | 209        | u7-u8
 s65-t217-tg1    | 2n-gnr        | SYS-222H-TN         | CH219AO34BD0164 | 10.30.51.65  | 10.30.50.65  | 209        | u5-u6
 s66-t218-sut1   | 2n-gnr        | SYS-222H-TN         | CH219AO34BD0173 | 10.30.51.66  | 10.30.50.66  | 209        | u3-u4
 s67-t218-tg1    | 2n-gnr        | SYS-222H-TN         | CH219AO34BD0174 | 10.30.51.67  | 10.30.50.67  | 209        | u1-u2

### Rack 210

 **name**        | **role**      | **model**           | **s/n**         | **mgmt-ip4** | **ipmi-ip4** | **rackid** | **rackunit**
-----------------|---------------|---------------------|-----------------|--------------|--------------|------------|--------------
 ToR Switch      | uplink        | ?                   | ?               | ?            | ?            | 210        | u45
 s91-nomad       | nomad-client  | R152-P30-00         | GLG4P9912A0016  | 10.30.51.91  | 10.30.50.91  | 210        | u44
 s92-nomad       | nomad-client  | R152-P30-00         | GLG4P9912A0004  | 10.30.51.92  | 10.30.50.92  | 210        | u43
 s23-nomad       | nomad-server  | SYS-1029P-WTRT      | C1160LI12NM0256 | 10.30.51.23  | 10.30.50.23  | 210        | u42
 s24-nomad       | nomad-server  | SYS-1029P-WTRT      | C1160LI12NM0241 | 10.30.51.24  | 10.30.50.24  | 210        | u41
 s25-nomad       | nomad-server  | SYS-1029P-WTRT      | C1160LI12NM0540 | 10.30.51.25  | 10.30.50.25  | 210        | u40
 s26-nomad       | nomad-server  | SYS-7049GP-TRT      | C7470KH37A30505 | 10.30.51.26  | 10.30.50.26  | 210        | u36-u39
 s37-t27-tg1     | 2n-grc        | SYS-740GP-TNRT      | S424016X1C31746 | 10.30.51.37  | 10.30.50.37  | 210        | u10-u13
 s36-t27-sut1    | 2n-grc        | --                  | --              | 10.30.51.36  | 10.30.50.36  | 210        | u9-u9
 s45-t25-tg1     | RESERVED      | SYS-??-TRT          | S512539X4A04499 | 10.30.51.45  | 10.30.50.45  | 210        | u1-u4
