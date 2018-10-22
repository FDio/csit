=======================================
Test Data Presentation Rules for Graphs
=======================================

**General rules to create the groups:**

- max 6 test cases grouped per graph
- test cases listed in specified order:

  - base
  - scale, in scaling order

  or

  - base
  - features

**Applicability**

- all plotly graphs used in FD.io CSIT reports up to CSIT-18.10

  - plotly.graph_objs.Box for Packet Throughput
  - plotly.graph_objs.Scatter for Packet Latency E-W W-E
  - plotly.graph_objs.Scatter for Speedup Multi-Core

Packet Throughput Graphs
------------------------

Applicable for:

- All topologies and NICs combinations:

  - 3n-hsw-x520
  - 3n-hsw-x710
  - 3n-hsw-xl710
  - 3n-hsw-vic1227
  - 3n-hsw-vic1385
  - 3n-skx-x710
  - 3n-skx-xxv710
  - 2n-skx-x710
  - 2n-skx-xxv710

- All threads and cores combinations:

  - 1t1c
  - 2t1c
  - 2t2c
  - 4t2c
  - 4t4c
  - 8t4c

If the corresponding tests are implemented.

L2 Ethernet Switching
`````````````````````

- 64b-2t1c-base_and_scale
- 64b-4t2c-base_and_scale
- 64b-8t4c-base_and_scale

  - l2sw-<?n>-<arch>-<NIC>-64b-<?t?c>-base_and_scale-ndr
  - l2sw-<?n>-<arch>-<NIC>-64b-<?t?c>-base_and_scale-pdr

    1. <NIC>-l2patch
    2. <NIC>-l2xcbase
    3. <NIC>-l2bdbase
    4. <NIC>-l2bdscale10kmaclrn
    5. <NIC>-l2bdscale100kmaclrn
    6. <NIC>-l2bdscale1mmaclrn

- 64b-2t1c-base_and_features
- 64b-4t2c-base_and_features
- 64b-8t4c-base_and_features

  - l2sw-<?n>-<arch>-<NIC>-64b-<?t?c>-base_and_features-ndr
  - l2sw-<?n>-<arch>-<NIC>-64b-<?t?c>-base_and_features-pdr

    1. <NIC>-l2xcbase
    2. <NIC>-l2bdbase
    3. <NIC>-dot1q-l2xcbase
    4. <NIC>-dot1q-l2bdbase

IPv4 Routing
````````````

- 64b-1t1c-base_and_scale
- 64b-2t2c-base_and_scale
- 64b-4t4c-base_and_scale

  - ip4-<?n>-<arch>-<NIC>-64b-<?t?c>-base_and_scale-ndr
  - ip4-<?n>-<arch>-<NIC>-64b-<?t?c>-base_and_scale-pdr

    1. <NIC>-ethip4-ip4base
    2. <NIC>-ethip4-ip4scale20k
    3. <NIC>-ethip4-ip4scale200k
    4. <NIC>-ethip4-ip4scale2m

- 64b-1t1c-base_and_features
- 64b-2t2c-base_and_features
- 64b-4t4c-base_and_features

  - ip4-<?n>-<arch>-<NIC>-64b-<?t?c>-base_and_features-ndr
  - ip4-<?n>-<arch>-<NIC>-64b-<?t?c>-base_and_features-pdr

    1. <NIC>-ethip4-ip4base
    2. <NIC>-ethip4-ip4base-nat44
    3. <NIC>-ethip4-ip4base-ipolicemarkbase
    4. <NIC>-ethip4-ip4base-copwhtlistbase
    5. <NIC>-ethip4udp-ip4base-iacl10sl-10kflows
    6. <NIC>-ethip4udp-ip4base-oacl10sl-10kflows

- 64b-1t1c-features_and_scale_nat44
- 64b-2t2c-features_and_scale_nat44
- 64b-4t4c-features_and_scale_nat44

  - ip4-<?n>-<arch>-<NIC>-64b-<?t?c>-features_and_scale_nat44-ndr
  - ip4-<?n>-<arch>-<NIC>-64b-<?t?c>-features_and_scale_nat44-pdr

    1. <NIC>-ethip4-ip4base-nat44
    2. <NIC>-ethip4-ip4base-updsrcscale15-nat44
    3. <NIC>-ethip4-ip4scale10-updsrcscale15-nat44
    4. <NIC>-ethip4-ip4scale100-updsrcscale15-nat44
    5. <NIC>-ethip4-ip4scale1000-updsrcscale15-nat44
    6. <NIC>-ethip4-ip4scale2000-updsrcscale15-nat44

- 64b-1t1c-features_and_scale_iacl
- 64b-2t2c-features_and_scale_iacl
- 64b-4t4c-features_and_scale_iacl

  - ip4-<?n>-<arch>-<NIC>-64b-<?t?c>-features_and_scale_iacl-ndr
  - ip4-<?n>-<arch>-<NIC>-64b-<?t?c>-features_and_scale_iacl-pdr

    1. <NIC>-ethip4udp-ip4base-iacl10sl-10kflows
    2. <NIC>-ethip4udp-ip4base-iacl10sf-10kflows
    3. <NIC>-ethip4udp-ip4base-iacl50sl-10kflows
    4. <NIC>-ethip4udp-ip4base-iacl50sf-10kflows

- 64b-1t1c-features_and_scale_oacl
- 64b-2t2c-features_and_scale_oacl
- 64b-4t4c-features_and_scale_oacl

  - ip4-<?n>-<arch>-<NIC>-64b-<?t?c>-features_and_scale_oacl-ndr
  - ip4-<?n>-<arch>-<NIC>-64b-<?t?c>-features_and_scale_oacl-pdr

    1. <NIC>-ethip4udp-ip4base-oacl10sl-10kflows
    2. <NIC>-ethip4udp-ip4base-oacl10sf-10kflows
    3. <NIC>-ethip4udp-ip4base-oacl50sf-10kflows
    4. <NIC>-ethip4udp-ip4base-oacl50sl-10kflows

IPv6 Routing
````````````

- 78b-1t1c-base_and_scale
- 78b-2t2c-base_and_scale
- 78b-4t4c-base_and_scale

  - ip6-<?n>-<arch>-<NIC>-78b-<?t?c>-base_and_scale-ndr
  - ip6-<?n>-<arch>-<NIC>-78b-<?t?c>-base_and_scale-pdr

    1. <NIC>-ethip6-ip6base
    2. <NIC>-ethip6-ip6scale20k
    3. <NIC>-ethip6-ip6scale200k
    4. <NIC>-ethip6-ip6scale2m

- 78b-1t1c-base_and_features
- 78b-2t2c-base_and_features
- 78b-4t4c-base_and_features

  - ip6-<?n>-<arch>-<NIC>-78b-<?t?c>-base_and_features-ndr
  - ip6-<?n>-<arch>-<NIC>-78b-<?t?c>-base_and_features-pdr

    1. <NIC>-ethip6-ip6base
    2. <NIC>-ethip6-ip6base-copwhtlistbase
    3. <NIC>-ethip6-ip6base-iacldstbase

SRv6 Routing
````````````

- 78b-1t1c-features
- 78b-2t2c-features
- 78b-4t4c-features

  - srv6-<?n>-<arch>-<NIC>-78b-<?t?c>-features-ndr
  - srv6-<?n>-<arch>-<NIC>-78b-<?t?c>-features-pdr

    1. <NIC>-ethip6ip6-ip6base-srv6enc1sid
    2. <NIC>-ethip6srhip6-ip6base-srv6enc2sids
    3. <NIC>-ethip6srhip6-ip6base-srv6enc2sids-nodecaps
    4. <NIC>-ethip6srhip6-ip6base-srv6proxy-dyn
    5. <NIC>-ethip6srhip6-ip6base-srv6proxy-masq
    6. <NIC>-ethip6srhip6-ip6base-srv6proxy-stat

IPv4 Tunnels
````````````

- 64b-1t1c-base_and_features
- 64b-2t2c-base_and_features
- 64b-4t4c-base_and_features

  - ip4tun-<?n>-<arch>-<NIC>-64b-<?t?c>-base_and_features-ndr
  - ip4tun-<?n>-<arch>-<NIC>-64b-<?t?c>-base_and_features-pdr

    1. <NIC>-ethip4lispip4-ip4base
    2. <NIC>-ethip4vxlan-l2bdbasemaclrn
    3. <NIC>-ethip4vxlan-l2xcbase

- 64b-1t1c-base_and_scale
- 64b-2t2c-base_and_scale
- 64b-4t4c-base_and_scale

  - ip4tun-<?n>-<arch>-<NIC>-64b-<?t?c>-base_and_scale-ndr
  - ip4tun-<?n>-<arch>-<NIC>-64b-<?t?c>-base_and_scale-pdr

    1. <NIC>-ethip4vxlan-l2bdbasemaclrn
    2. <NIC>-dot1q--ethip4vxlan-l2bdscale1l2bd1vlan1vxlan
    3. <NIC>-dot1q--ethip4vxlan-l2bdscale10l2bd10vlan10vxlan
    4. <NIC>-dot1q--ethip4vxlan-l2bdscale100l2bd100vlan100vxlan
    5. <NIC>-dot1q--ethip4vxlan-l2bdscale1kl2bd1kvlan1kvxlan

IPv6 Tunnels
````````````

- 78b-1t1c-base
- 78b-2t2c-base
- 78b-4t4c-base

  - ip6tun-<?n>-<arch>-<NIC>-78b-<?t?c>-base-ndr
  - ip6tun-<?n>-<arch>-<NIC>-78b-<?t?c>-base-pdr

    1. <NIC>-ethip6lispip4-ip6base
    2. <NIC>-ethip6lispip6-ip6base

KVM VMs vhost-user
``````````````````

- 64b-1t1c-base-l2sw
- 64b-2t2c-base-l2sw
- 64b-4t4c-base-l2sw

  - vhost-l2sw-<?n>-<arch>-<NIC>-64b-<?t?c>-base-ndr
  - vhost-l2sw-<?n>-<arch>-<NIC>-64b-<?t?c>-base-pdr

    1. <NIC>-eth-l2xcbase-eth-2vhostvr1024-1vm
    2. <NIC>-eth-l2xcbase-eth-2vhostvr1024-1vm-cfsrr1
    3. <NIC>-eth-l2bdbasemaclrn-eth-2vhostvr1024-1vm
    4. <NIC>-eth-l2bdbasemaclrn-eth-2vhostvr1024-1vm-cfsrr1

- 64b-1t1c-base_and_scale-l2sw
- 64b-2t2c-base_and_scale-l2sw
- 64b-4t4c-base_and_scale-l2sw

  - vhost-l2sw-<?n>-<arch>-<NIC>-64b-<?t?c>-base_and_scale-ndr
  - vhost-l2sw-<?n>-<arch>-<NIC>-64b-<?t?c>-base_and_scale-pdr

    1. <NIC>-eth-l2bdbasemaclrn-eth-2vhostvr1024-1vm
    2. <NIC>-eth-l2bdbasemaclrn-eth-2vhostvr1024-1vm-cfsrr1
    3. <NIC>-eth-l2bdscale10kmaclrn-eth-2vhostvr1024-1vm-cfsrr1
    4. <NIC>-eth-l2bdscale100kmaclrn-eth-2vhostvr1024-1vm-cfsrr1
    5. <NIC>-eth-l2bdscale1mmaclrn-eth-2vhostvr1024-1vm-cfsrr1

- 64b-1t1c-base_and_scale-l2sw-vm
- 64b-2t2c-base_and_scale-l2sw-vm
- 64b-4t4c-base_and_scale-l2sw-vm

  - vhost-l2sw-<?n>-<arch>-<NIC>-64b-<?t?c>-base_and_scale-vm-ndr
  - vhost-l2sw-<?n>-<arch>-<NIC>-64b-<?t?c>-base_and_scale-vm-pdr

    1. <NIC>-eth-l2xcbase-eth-2vhostvr1024-1vm
    2. <NIC>-eth-l2xcbase-eth-4vhostvr1024-2vm
    3. <NIC>-eth-l2bdbasemaclrn-eth-2vhostvr1024-1vm
    4. <NIC>-eth-l2bdbasemaclrn-eth-4vhostvr1024-2vm

- 64b-1t1c-base_and_scale-ip4
- 64b-2t2c-base_and_scale-ip4
- 64b-4t4c-base_and_scale-ip4

  - vhost-ip4-<?n>-<arch>-<NIC>-64b-<?t?c>-base_and_scale-ndr
  - vhost-ip4-<?n>-<arch>-<NIC>-64b-<?t?c>-base_and_scale-pdr

    1. <NIC>-ethip4-ip4base-eth-2vhostvr1024-1vm
    2. <NIC>-ethip4-ip4base-eth-4vhostvr1024-2vm
    3. <NIC>-ethip4-ip4base-eth-2vhostvr1024-1vm

LXC/DRC Container Memif
```````````````````````



K8s Container Memif
```````````````````


IPSec IPv4 Routing
``````````````````



VTS
```


Testpmd
```````





L3fwd
`````




Packet Latency Graphs
---------------------

Applicable for:

- All topologies and NICs combinations:

  - 3n-hsw-x520
  - 3n-hsw-x710
  - 3n-hsw-xl710
  - 3n-hsw-vic1227
  - 3n-hsw-vic1385
  - 3n-skx-x710
  - 3n-skx-xxv710
  - 2n-skx-x710
  - 2n-skx-xxv710

- All threads and cores combinations:

  - 1t1c
  - 2t1c
  - 2t2c
  - 4t2c
  - 4t4c
  - 8t4c

If the corresponding tests are implemented.







Speedup Multi-Core Graphs
-------------------------

Applicable for:

- All topologies and NICs combinations:

  - 3n-hsw-x520
  - 3n-hsw-x710
  - 3n-hsw-xl710
  - 3n-hsw-vic1227
  - 3n-hsw-vic1385
  - 3n-skx-x710
  - 3n-skx-xxv710
  - 2n-skx-x710
  - 2n-skx-xxv710

If the corresponding tests are implemented.
