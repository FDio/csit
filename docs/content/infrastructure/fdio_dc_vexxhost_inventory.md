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

## YUL1 Inventory

### Rack YUL1-8 (3016.8)

 **name**        | **role**      | **model**           | **s/n**         | **mgmt-ip4** | **ipmi-ip4** | **rackid** | **rackunit**
-----------------|---------------|---------------------|-----------------|--------------|--------------|------------|--------------
 mtl1-8-lb4m     | uplink        | ?                   | ?               | ?            | ?            | 3016.8     | u47
 s75-t37-sut1    | 3n-icx        | SYS-740GP-TNRT      | C7470KK25P50098 | 10.30.51.75  | 10.30.50.75  | 3016.8     | u42-u45
 s76-t37-sut2    | 3n-icx        | SYS-740GP-TNRT      | C7470KK33P50247 | 10.30.51.76  | 10.30.50.76  | 3016.8     | u38-u41
 s77-t37-tg1     | 3n-icx        | SYS-740GP-TNRT      | C7470KK25P50076 | 10.30.51.77  | 10.30.50.77  | 3016.8     | u34-u37
 s81-t212-sut1   | 2n-icx        | SYS-740GP-TNRT      | C7470KK25P50173 | 10.30.51.81  | 10.30.50.81  | 3016.8     | u30-u33
 s82-t212-tg1    | 2n-icx        | SYS-740GP-TNRT      | C7470KK33P50220 | 10.30.51.82  | 10.30.50.82  | 3016.8     | u26-u29
 s83-t213-sut1   | 2n-icx        | SYS-740GP-TNRT      | C7470KL07P50300 | 10.30.51.83  | 10.30.50.83  | 3016.8     | u22-u25
 s84-t213-tg1    | 2n-icx        | SYS-740GP-TNRT      | C7470KL03P50187 | 10.30.51.84  | 10.30.50.84  | 3016.8     | u18-u21
 s85-t214-sut1   | 2n-icx        | SYS-740GP-TNRT      | C7470KK33P50219 | 10.30.51.85  | 10.30.50.85  | 3016.8     | u14-u17
 s86-t214-tg1    | 2n-icx        | SYS-740GP-TNRT      | C7470KL07P50312 | 10.30.51.86  | 10.30.50.86  | 3016.8     | u10-u13
 s87-t215-sut1   | 2n-oct        | SYS-740GP-TNRT      | C7470KL03P50171 | 10.30.51.87  | 10.30.50.87  | 3016.8     | u6-u9
 s95-t215-dpu1   | 2n-oct-dpu1   | -                   | -               | 10.30.51.95  | 10.30.50.95  | 3016.8     | u6-u9
 s96-t215-dpu2   | 2n-oct-dpu2   | -                   | -               | 10.30.51.96  | 10.30.50.96  | 3016.8     | u6-u9
 s88-t215-tg1    | 2n-oct        | SYS-740GP-TNRT      | C7470KL07P50301 | 10.30.51.88  | 10.30.50.88  | 3016.8     | u2-u5

### Rack YUL1-9 (3016.9)

 **name**        | **role**      | **model**           | **s/n**         | **mgmt-ip4** | **ipmi-ip4** | **rackid** | **rackunit**
-----------------|---------------|---------------------|-----------------|--------------|--------------|------------|--------------
 mtl1-5-lb4m     | uplink        | ?                   | ?               | ?            | ?            | 3016.9     | u47
 s52-t21-sut1    | 2n-spr        | SYS-741GE-TNRT      | C7490FL36A40118 | 10.30.51.52  | 10.30.50.52  | 3016.9     | u42-u45
 s53-t21-tg1     | 2n-spr        | SYS-741GE-TNRT      | C7490FL36A40115 | 10.30.51.53  | 10.30.50.53  | 3016.9     | u38-u41
 s54-t22-sut1    | 2n-spr        | SYS-741GE-TNRT      | C7490FL36A40117 | 10.30.51.54  | 10.30.50.54  | 3016.9     | u34-u37
 s55-t22-tg1     | 2n-spr        | SYS-741GE-TNRT      | C7490FL36A40114 | 10.30.51.55  | 10.30.50.55  | 3016.9     | u30-u33
 s56-t23-sut1    | 2n-spr        | SYS-741GE-TNRT      | C7490FL36A40121 | 10.30.51.56  | 10.30.50.56  | 3016.9     | u26-u29
 s57-t23-tg1     | 2n-spr        | SYS-741GE-TNRT      | C7490FL36A40116 | 10.30.51.57  | 10.30.50.57  | 3016.9     | u22-u25
 s58-t24-sut1    | 2n-spr        | SYS-741GE-TNRT      | C7490FL36A40107 | 10.30.51.58  | 10.30.50.58  | 3016.9     | u18-u21
 s59-t24-tg1     | 2n-spr        | SYS-741GE-TNRT      | C7490FL36A40122 | 10.30.51.59  | 10.30.50.59  | 3016.9     | u14-u17
 s78-t38-sut1    | 3n-icx        | SYS-740GP-TNRT      | C7470KL03P50450 | 10.30.51.78  | 10.30.50.78  | 3016.9     | u10-u13
 s79-t38-sut2    | 3n-icx        | SYS-740GP-TNRT      | C7470KL07P50297 | 10.30.51.79  | 10.30.50.79  | 3016.9     | u6-u9
 s80-t38-tg1     | 3n-icx        | SYS-740GP-TNRT      | C7470KL03P50454 | 10.30.51.80  | 10.30.50.80  | 3016.9     | u2-u5

### Rack YUL1-10 (3016.10)

 **name**        | **role**      | **model**           | **s/n**         | **mgmt-ip4** | **ipmi-ip4** | **rackid** | **rackunit**
-----------------|---------------|---------------------|-----------------|--------------|--------------|------------|--------------
 yul1-10-lb4m    | uplink        | ?                   | ?               | ?            | ?            | 3016.10    | u47
 s51-nomad       | nomad-client  | SYS-7049GP-TRT      | C7470KH06A20119 | 10.30.51.51  | 10.30.50.51  | 3016.10    | u42-u45
 s50-nomad       | nomad-client  | SYS-7049GP-TRT      | C7470KH06A20154 | 10.30.51.50  | 10.30.50.50  | 3016.10    | u38-u41
 s40-t28-sut1    | 2n-emr        | SYS-??-TRT          | S512539X4A04503 | 10.30.51.40  | 10.30.50.40  | 3016.10    | u34-u37
 s41-t28-tg1     | 2n-emr        | SYS-??-TRT          | S512539X4A04502 | 10.30.51.41  | 10.30.50.41  | 3016.10    | u30-u33
 s42-t29-sut1    | 2n-emr        | SYS-??-TRT          | S512539X4A04504 | 10.30.51.42  | 10.30.50.42  | 3016.10    | u26-u29
 s43-t29-tg1     | 2n-emr        | SYS-??-TRT          | S512539X4A04500 | 10.30.51.43  | 10.30.50.43  | 3016.10    | u22-u25
 s32-t31-sut1    | 3n-icxd       | SYS-110D-20C-FRDN8TP| C515MKK41A30950 | 10.30.51.32  | 10.30.50.32  | 3016.10    | u21
 s33-t31-sut2    | 3n-icxd       | SYS-110D-20C-FRDN8TP| C515MKK41A30967 | 10.30.51.33  | 10.30.50.33  | 3016.10    | u20
 s34-t32-sut1    | 3n-icxd       | SYS-110D-20C-FRDN8TP| C515MKK41A30959 | 10.30.51.34  | 10.30.50.34  | 3016.10    | u19
 s35-t32-sut2    | 3n-icxd       | SYS-110D-20C-FRDN8TP| C515MKK41A30886 | 10.30.51.35  | 10.30.50.35  | 3016.10    | u18
 s90-t31t32-tg1  | 3n-icxd       | SYS-740GP-TNRT      | C7470KL03P50184 | 10.30.51.90  | 10.30.50.90  | 3016.10    | u14-u17
 s93-t39-sut1    | 3n-snr        | ?                   | ?               | 10.30.51.93  | 10.30.50.93  | 3016.10    | u10-u13
 s94-t39-sut2    | 3n-snr        | ?                   | ?               | 10.30.51.94  | 10.30.50.94  | 3016.10    | u6-u9
 s89-t39t310-tg1 | 3n-snr        | SYS-7049GP-TRT      | C7470KH37A30506 | 10.30.51.89  | 10.30.50.89  | 3016.10    | u2-u5

### Rack YUL1-11 (3016.11)

 **name**              | **role**     | **model**      | **s/n**         | **mgmt-ip4** | **ipmi-ip4** | **rackid** | **rackunit**
-----------------------|--------------|----------------|-----------------|--------------|--------------|------------|--------------
 yul1-11-lb6m          | arm-uplink   | ?              | ?               | ?            | ?            | 3016.11    | u48
 yul1-11-lf-tor-switch | uplink       | ?              | ?               | ?            | ?            | 3016.11    | u47
 mtl1-6-7050QX-32      | uplink       | ?              | ?               | ?            | ?            | 3016.11    | u46
 fdio-marvell-dev      | dev          | ThunderX-88XX  | N/A             | 10.30.51.38  | 10.30.50.38  | 3016.11    | u45
 s21-nomad             | nomad-client | SYS-741GE-TNRT | C7490FL47A50150 | 10.30.51.21  | 10.30.50.21  | 3016.11    | u39-u42
 s22-nomad             | nomad-client | SYS-741GE-TNRT | C7490FL47A50155 | 10.30.51.22  | 10.30.50.22  | 3016.11    | u35-u38
 s30-nomad             | nomad-client | SYS-741GE-TNRT | C7490FL47A50154 | 10.30.51.30  | 10.30.50.30  | 3016.11    | u19-u22
 s31-nomad             | nomad-client | SYS-741GE-TNRT | C7490FL47A50149 | 10.30.51.31  | 10.30.50.31  | 3016.11    | u15-u18
 s70-t13-sut1          | 1n-alt       | E252-P30-00    | GMG252012A0098  | 10.30.51.70  | 10.30.50.70  | 3016.11    | u13-u14
 s71-t14-sut1          | 1n-alt       | E252-P30-00    | GMG252012A0089  | 10.30.51.71  | 10.30.50.71  | 3016.11    | u11-u12
 s73-t34-sut2          | 3n-alt       | WIWYNN         | 04000059N0SC    | 10.30.51.72  | 10.30.50.72  | 3016.11    | u9-u10
 s72-t34-sut1          | 3n-alt       | WIWYNN         | 0390003EN0SC    | 10.30.51.73  | 10.30.50.73  | 3016.11    | u7-u8
 s74-t34-tg1           | 3n-alt       | SYS-740GP-TNRT | C7470KK40P50249 | 10.30.51.74  | 10.30.50.74  | 3016.11    | u3-u6

### Rack YUL1-12 (3016.12)

 **name**        | **role**      | **model**           | **s/n**         | **mgmt-ip4** | **ipmi-ip4** | **rackid** | **rackunit**
-----------------|---------------|---------------------|-----------------|--------------|--------------|------------|--------------
 yul1-12-lb4m    | uplink        | ?                   | ?               | ?            | ?            | 3016.12    | u47
 s28-nomad       | nomad-client  | SYS-7049GP-TRT      | C7470KH06A20196 | 10.30.51.28  | 10.30.50.28  | 3016.12    | u41-u44
 s27-nomad       | nomad-client  | SYS-7049GP-TRT      | C7470KH06A20055 | 10.30.51.27  | 10.30.50.27  | 3016.12    | u37-u40
 s91-nomad       | nomad-client  | R152-P30-00         | GLG4P9912A0016  | 10.30.51.91  | 10.30.50.91  | 3016.12    | u36
 s92-nomad       | nomad-client  | R152-P30-00         | GLG4P9912A0004  | 10.30.51.92  | 10.30.50.92  | 3016.12    | u35
 s23-nomad       | nomad-server  | SYS-1029P-WTRT      | C1160LI12NM0256 | 10.30.51.23  | 10.30.50.23  | 3016.12    | u34
 s24-nomad       | nomad-server  | SYS-1029P-WTRT      | C1160LI12NM0241 | 10.30.51.24  | 10.30.50.24  | 3016.12    | u33
 s25-nomad       | nomad-server  | SYS-1029P-WTRT      | C1160LI12NM0540 | 10.30.51.25  | 10.30.50.25  | 3016.12    | u32
 s61-t210-tg1    | 2n-zn2        | AS-1014S-WTRT       | S366866X0515596 | 10.30.51.61  | 10.30.55.25  | 3016.12    | u31
 s60-t210-sut1   | 2n-zn2        | AS-1114S-WTRT       | S367023X0304458 | 10.30.51.60  | 10.30.55.24  | 3016.12    | u30
 s26-nomad       | nomad-server  | SYS-7049GP-TRT      | C7470KH37A30505 | 10.30.51.26  | 10.30.50.26  | 3016.12    | u26-u29
 s44-t25-sut1    | 2n-zn5        | SYS-??-TRT          | -               | 10.30.51.44  | 10.30.50.44  | 3016.12    | u22-u25
 s45-t25-tg1     | 2n-zn5        | SYS-??-TRT          | S512539X4A04499 | 10.30.51.45  | 10.30.50.45  | 3016.12    | u18-u21
 s46-t26-sut1    | 2n-zn5        | SYS-??-TRT          | -               | 10.30.51.46  | 10.30.50.46  | 3016.12    | u14-u17
 s47-t26-tg1     | 2n-zn5        | SYS-??-TRT          | S512539X4A04501 | 10.30.51.47  | 10.30.50.49  | 3016.12    | u10-u13           !!!IPMI
 s37-t27-tg1     | 2n-grc        | SYS-740GP-TNRT      | S424016X1C31746 | 10.30.51.37  | 10.30.50.37  | 3016.12    | u2-u5
 s36-t27-sut1    | 2n-grc        | --                  | --              | 10.30.51.36  | 10.30.50.36  | 3016.12    | u1