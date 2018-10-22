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

- 64b-<?t?c>-base_and_scale

  - l2sw-<?n>-<arch>-<NIC>-64b-<?t?c>-base_and_scale-ndr
  - l2sw-<?n>-<arch>-<NIC>-64b-<?t?c>-base_and_scale-pdr

    1. <NIC>-l2patch
    2. <NIC>-l2xcbase
    3. <NIC>-l2bdbase
    4. <NIC>-l2bdscale10kmaclrn
    5. <NIC>-l2bdscale100kmaclrn
    6. <NIC>-l2bdscale1mmaclrn

- 64b-<?t?c>-base_and_features

  - l2sw-<?n>-<arch>-<NIC>-64b-<?t?c>-base_and_features-ndr
  - l2sw-<?n>-<arch>-<NIC>-64b-<?t?c>-base_and_features-pdr

    1. <NIC>-l2xcbase
    2. <NIC>-l2bdbase
    3. <NIC>-dot1q-l2xcbase
    4. <NIC>-dot1q-l2bdbase

IPv4 Routing
````````````

- 64b-<?t?c>-base_and_scale

  - ip4-<?n>-<arch>-<NIC>-64b-<?t?c>-base_and_scale-ndr
  - ip4-<?n>-<arch>-<NIC>-64b-<?t?c>-base_and_scale-pdr

    1. <NIC>-ethip4-ip4base
    2. <NIC>-ethip4-ip4scale20k
    3. <NIC>-ethip4-ip4scale200k
    4. <NIC>-ethip4-ip4scale2m

- 64b-<?t?c>-base_and_features

  - ip4-<?n>-<arch>-<NIC>-64b-<?t?c>-base_and_features-ndr
  - ip4-<?n>-<arch>-<NIC>-64b-<?t?c>-base_and_features-pdr

    1. <NIC>-ethip4-ip4base
    2. <NIC>-ethip4-ip4base-nat44
    3. <NIC>-ethip4-ip4base-ipolicemarkbase
    4. <NIC>-ethip4-ip4base-copwhtlistbase
    5. <NIC>-ethip4udp-ip4base-iacl10sl-10kflows
    6. <NIC>-ethip4udp-ip4base-oacl10sl-10kflows

- 64b-<?t?c>-features_and_scale_nat44

  - ip4-<?n>-<arch>-<NIC>-64b-<?t?c>-features_and_scale_nat44-ndr
  - ip4-<?n>-<arch>-<NIC>-64b-<?t?c>-features_and_scale_nat44-pdr

    1. <NIC>-ethip4-ip4base-nat44
    2. <NIC>-ethip4-ip4base-updsrcscale15-nat44
    3. <NIC>-ethip4-ip4scale10-updsrcscale15-nat44
    4. <NIC>-ethip4-ip4scale100-updsrcscale15-nat44
    5. <NIC>-ethip4-ip4scale1000-updsrcscale15-nat44
    6. <NIC>-ethip4-ip4scale2000-updsrcscale15-nat44

- 64b-<?t?c>-features_and_scale_iacl

  - ip4-<?n>-<arch>-<NIC>-64b-<?t?c>-features_and_scale_iacl-ndr
  - ip4-<?n>-<arch>-<NIC>-64b-<?t?c>-features_and_scale_iacl-pdr

    1. <NIC>-ethip4udp-ip4base-iacl10sl-10kflows
    2. <NIC>-ethip4udp-ip4base-iacl10sf-10kflows
    3. <NIC>-ethip4udp-ip4base-iacl50sl-10kflows
    4. <NIC>-ethip4udp-ip4base-iacl50sf-10kflows

- 64b-<?t?c>-features_and_scale_oacl

  - ip4-<?n>-<arch>-<NIC>-64b-<?t?c>-features_and_scale_oacl-ndr
  - ip4-<?n>-<arch>-<NIC>-64b-<?t?c>-features_and_scale_oacl-pdr

    1. <NIC>-ethip4udp-ip4base-oacl10sl-10kflows
    2. <NIC>-ethip4udp-ip4base-oacl10sf-10kflows
    3. <NIC>-ethip4udp-ip4base-oacl50sl-10kflows
    4. <NIC>-ethip4udp-ip4base-oacl50sf-10kflows

IPv6 Routing
````````````

- 78b-<?t?c>-base_and_scale

  - ip6-<?n>-<arch>-<NIC>-78b-<?t?c>-base_and_scale-ndr
  - ip6-<?n>-<arch>-<NIC>-78b-<?t?c>-base_and_scale-pdr

    1. <NIC>-ethip6-ip6base
    2. <NIC>-ethip6-ip6scale20k
    3. <NIC>-ethip6-ip6scale200k
    4. <NIC>-ethip6-ip6scale2m

- 78b-<?t?c>-base_and_features

  - ip6-<?n>-<arch>-<NIC>-78b-<?t?c>-base_and_features-ndr
  - ip6-<?n>-<arch>-<NIC>-78b-<?t?c>-base_and_features-pdr

    1. <NIC>-ethip6-ip6base
    2. <NIC>-ethip6-ip6base-copwhtlistbase
    3. <NIC>-ethip6-ip6base-iacldstbase

SRv6 Routing
````````````

- 78b-<?t?c>-features

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

- 64b-<?t?c>-base_and_features

  - ip4tun-<?n>-<arch>-<NIC>-64b-<?t?c>-base_and_features-ndr
  - ip4tun-<?n>-<arch>-<NIC>-64b-<?t?c>-base_and_features-pdr

    1. <NIC>-ethip4vxlan-l2bdbasemaclrn
    2. <NIC>-ethip4vxlan-l2xcbase
    3. <NIC>-ethip4lispip4-ip4base

- 64b-<?t?c>-base_and_scale

  - ip4tun-<?n>-<arch>-<NIC>-64b-<?t?c>-base_and_scale-ndr
  - ip4tun-<?n>-<arch>-<NIC>-64b-<?t?c>-base_and_scale-pdr

    1. <NIC>-ethip4vxlan-l2bdbasemaclrn
    2. <NIC>-dot1q--ethip4vxlan-l2bdscale1l2bd1vlan1vxlan
    3. <NIC>-dot1q--ethip4vxlan-l2bdscale10l2bd10vlan10vxlan
    4. <NIC>-dot1q--ethip4vxlan-l2bdscale100l2bd100vlan100vxlan
    5. <NIC>-dot1q--ethip4vxlan-l2bdscale1kl2bd1kvlan1kvxlan

IPv6 Tunnels
````````````

- 78b-<?t?c>-base

  - ip6tun-<?n>-<arch>-<NIC>-78b-<?t?c>-base-ndr
  - ip6tun-<?n>-<arch>-<NIC>-78b-<?t?c>-base-pdr

    1. <NIC>-ethip6lispip4-ip6base
    2. <NIC>-ethip6lispip6-ip6base

KVM VMs vhost-user
``````````````````

- 64b-<?t?c>-base-l2sw

  - vhost-l2sw-<?n>-<arch>-<NIC>-64b-<?t?c>-base-ndr
  - vhost-l2sw-<?n>-<arch>-<NIC>-64b-<?t?c>-base-pdr

    1. <NIC>-eth-l2xcbase-eth-2vhostvr1024-1vm
    2. <NIC>-eth-l2xcbase-eth-2vhostvr1024-1vm-cfsrr1
    3. <NIC>-eth-l2bdbasemaclrn-eth-2vhostvr1024-1vm
    4. <NIC>-eth-l2bdbasemaclrn-eth-2vhostvr1024-1vm-cfsrr1

- 64b-<?t?c>-base_and_scale-l2sw

  - vhost-l2sw-<?n>-<arch>-<NIC>-64b-<?t?c>-base_and_scale-ndr
  - vhost-l2sw-<?n>-<arch>-<NIC>-64b-<?t?c>-base_and_scale-pdr

    1. <NIC>-eth-l2bdbasemaclrn-eth-2vhostvr1024-1vm
    2. <NIC>-eth-l2bdbasemaclrn-eth-2vhostvr1024-1vm-cfsrr1
    3. <NIC>-eth-l2bdscale10kmaclrn-eth-2vhostvr1024-1vm-cfsrr1
    4. <NIC>-eth-l2bdscale100kmaclrn-eth-2vhostvr1024-1vm-cfsrr1
    5. <NIC>-eth-l2bdscale1mmaclrn-eth-2vhostvr1024-1vm-cfsrr1

- 64b-<?t?c>-base_and_scale-l2sw-vm

  - vhost-l2sw-<?n>-<arch>-<NIC>-64b-<?t?c>-base_and_scale-vm-ndr
  - vhost-l2sw-<?n>-<arch>-<NIC>-64b-<?t?c>-base_and_scale-vm-pdr

    1. <NIC>-eth-l2xcbase-eth-2vhostvr1024-1vm
    2. <NIC>-eth-l2xcbase-eth-4vhostvr1024-2vm
    3. <NIC>-eth-l2bdbasemaclrn-eth-2vhostvr1024-1vm
    4. <NIC>-eth-l2bdbasemaclrn-eth-4vhostvr1024-2vm

- 64b-<?t?c>-base_and_scale-ip4

  - vhost-ip4-<?n>-<arch>-<NIC>-64b-<?t?c>-base_and_scale-ndr
  - vhost-ip4-<?n>-<arch>-<NIC>-64b-<?t?c>-base_and_scale-pdr

    1. <NIC>-ethip4-ip4base-eth-2vhostvr1024-1vm
    2. <NIC>-ethip4-ip4base-eth-2vhostvr1024-1vm-cfsrr1
    3. <NIC>-ethip4-ip4base-eth-4vhostvr1024-2vm

LXC/DRC Container Memif
```````````````````````

- 64b-<?t?c>-base_and_scale

  - memif-<?n>-<arch>-<NIC>-64b-<?t?c>-base_and_scale-ndr
  - memif-<?n>-<arch>-<NIC>-64b-<?t?c>-base_and_scale-pdr

    1. <NIC>-eth-l2xcbase-eth-1memif-1dcr
    2. <NIC>-eth-l2xcbase-eth-2memif-1dcr
    3. <NIC>-eth-l2xcbase-eth-2memif-1lxc
    4. <NIC>-eth-l2bdbasemaclrn-eth-2memif-1lxc
    5. <NIC>-dot1q-l2bdbasemaclrn-eth-2memif-1dcr
    6. <NIC>-ethip4-ip4base-eth-2memif-1dcr

K8s Container Memif
```````````````````

- 64b-<?t?c>-base_and_scale-l2xc

  - k8s-memif-<?n>-<arch>-<NIC>-64b-<?t?c>-base_and_scale-l2xc-ndr
  - k8s-memif-<?n>-<arch>-<NIC>-64b-<?t?c>-base_and_scale-l2xc-pdr

    1. <NIC>-eth-1drcl2xcbase-eth-2memif-1drcl2xc-1paral-k8s
    2. <NIC>-eth-1drcl2xcbase-eth-2memif-2drcl2xc-1horiz-k8s
    3. <NIC>-eth-1drcl2xcbase-eth-2memif-4drcl2xc-1horiz-k8s
    4. <NIC>-eth-1drcl2xcbase-eth-4memif-2drcl2xc-1chain-k8s
    5. <NIC>-eth-1drcl2xcbase-eth-8memif-4drcl2xc-1chain-k8s

- 64b-<?t?c>-base_and_scale-l2bd

  - k8s-memif-<?n>-<arch>-<NIC>-64b-<?t?c>-base_and_scale-l2bd-ndr
  - k8s-memif-<?n>-<arch>-<NIC>-64b-<?t?c>-base_and_scale-l2bd-pdr

    1. <NIC>-eth-1drcl2bdbasemaclrn-eth-2memif-1drcl2xc-1paral-k8s
    2. <NIC>-eth-1drcl2bdbasemaclrn-eth-2memif-2drcl2xc-1horiz-k8s
    3. <NIC>-eth-1drcl2bdbasemaclrn-eth-2memif-4drcl2xc-1horiz-k8s
    4. <NIC>-eth-1drcl2bdbasemaclrn-eth-4memif-2drcl2xc-1chain-k8s
    5. <NIC>-eth-1drcl2bdbasemaclrn-eth-8memif-4drcl2xc-1chain-k8s

IPSec IPv4 Routing
``````````````````

- 64b-<?t?c>-base_and_scale-aes

  - ipsec-<?n>-<arch>-<NIC>-64b-<?t?c>-base_and_scale-aes-ndr
  - ipsec-<?n>-<arch>-<NIC>-64b-<?t?c>-base_and_scale-aes-pdr

    1. <NIC>-ethip4ipsecbasetnl-ip4base-int-aes-gcm
    2. <NIC>-ethip4ipsecbasetnl-ip4base-tnl-aes-gcm
    3. <NIC>-ethip4ipsecscale1000tnl-ip4base-int-aes-gcm
    4. <NIC>-ethip4ipsecscale1000tnl-ip4base-tnl-aes-gcm
    5. <NIC>-ethip4ipsecbasetnlsw-ip4base-int-aes-gcm
    6. <NIC>-ethip4ipsecbasetnlsw-ip4base-tnl-aes-gcm

- 64b-<?t?c>-base_and_scale-cbc

  - ipsec-<?n>-<arch>-<NIC>-64b-<?t?c>-base_and_scale-cbc-ndr
  - ipsec-<?n>-<arch>-<NIC>-64b-<?t?c>-base_and_scale-cbc-pdr

    1. <NIC>-ethip4ipsecbasetnl-ip4base-int-cbc-sha1
    2. <NIC>-ethip4ipsecbasetnl-ip4base-tnl-cbc-sha1
    3. <NIC>-ethip4ipsecscale1000tnl-ip4base-int-cbc-sha1
    4. <NIC>-ethip4ipsecscale1000tnl-ip4base-tnl-cbc-sha1
    5. <NIC>-ethip4ipsecbasetnlsw-ip4base-int-cbc-sha1
    6. <NIC>-ethip4ipsecbasetnlsw-ip4base-tnl-cbc-sha1

VTS
```

- 114b-<?t?c>-base_and_features

  - vts-<?n>-<arch>-<NIC>-114b-<?t?c>-ndr
  - vts-<?n>-<arch>-<NIC>-114b-<?t?c>-pdr

    1. <NIC>-ethip4vxlan-l2bdbasemaclrn-eth-iacldstbase-noacl-2vhostvr1024-1vm
    2. <NIC>-ethip4vxlan-l2bdbasemaclrn-eth-iacldstbase-aclpermitreflect-2vhostvr1024-1vm
    3. <NIC>-ethip4vxlan-l2bdbasemaclrn-eth-iacldstbase-aclpermit-2vhostvr1024-1vm

Testpmd
```````

- 64b-<?t?c>-base

  - testpmd-<?n>-<arch>-<NIC>-64b-<?t?c>-base-ndr
  - testpmd-<?n>-<arch>-<NIC>-64b-<?t?c>-base-pdr

    1. 10ge2p1x710-eth-l2xcbase-testpmd

L3fwd
`````

- 64b-<?t?c>-base

  - l3fwd-<?n>-<arch>-<NIC>-64b-<?t?c>-base-ndr
  - l3fwd-<?n>-<arch>-<NIC>-64b-<?t?c>-base-pdr

    1. <NIC>-ethip4-ip4base-l3fwd

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

L2 Ethernet Switching
`````````````````````

- 64b-<?t?c>-base_and_scale

  - l2sw-<?n>-<arch>-<NIC>-64b-<?t?c>-base_and_scale-ndr

    1. <NIC>-l2patch
    2. <NIC>-l2xcbase
    3. <NIC>-l2bdbase
    4. <NIC>-l2bdscale10kmaclrn
    5. <NIC>-l2bdscale100kmaclrn
    6. <NIC>-l2bdscale1mmaclrn

- 64b-<?t?c>-base_and_features

  - l2sw-<?n>-<arch>-<NIC>-64b-<?t?c>-base_and_features-ndr

    1. <NIC>-l2xcbase
    2. <NIC>-l2bdbase
    3. <NIC>-dot1q-l2xcbase
    4. <NIC>-dot1q-l2bdbase

IPv4 Routing
````````````

- 64b-<?t?c>-base_and_scale

  - ip4-<?n>-<arch>-<NIC>-64b-<?t?c>-base_and_scale-ndr

    1. <NIC>-ethip4-ip4base
    2. <NIC>-ethip4-ip4scale20k
    3. <NIC>-ethip4-ip4scale200k
    4. <NIC>-ethip4-ip4scale2m

- 64b-<?t?c>-base_and_features

  - ip4-<?n>-<arch>-<NIC>-64b-<?t?c>-base_and_features-ndr

    1. <NIC>-ethip4-ip4base
    2. <NIC>-ethip4-ip4base-nat44
    3. <NIC>-ethip4-ip4base-ipolicemarkbase
    4. <NIC>-ethip4-ip4base-copwhtlistbase
    5. <NIC>-ethip4udp-ip4base-iacl10sl-10kflows
    6. <NIC>-ethip4udp-ip4base-oacl10sl-10kflows

- 64b-<?t?c>-features_and_scale_nat44

  - ip4-<?n>-<arch>-<NIC>-64b-<?t?c>-features_and_scale_nat44-ndr

    1. <NIC>-ethip4-ip4base-nat44
    2. <NIC>-ethip4-ip4base-updsrcscale15-nat44
    3. <NIC>-ethip4-ip4scale10-updsrcscale15-nat44
    4. <NIC>-ethip4-ip4scale100-updsrcscale15-nat44
    5. <NIC>-ethip4-ip4scale1000-updsrcscale15-nat44
    6. <NIC>-ethip4-ip4scale2000-updsrcscale15-nat44

- 64b-<?t?c>-features_and_scale_iacl

  - ip4-<?n>-<arch>-<NIC>-64b-<?t?c>-features_and_scale_iacl-ndr

    1. <NIC>-ethip4udp-ip4base-iacl10sl-10kflows
    2. <NIC>-ethip4udp-ip4base-iacl10sf-10kflows
    3. <NIC>-ethip4udp-ip4base-iacl50sl-10kflows
    4. <NIC>-ethip4udp-ip4base-iacl50sf-10kflows

- 64b-<?t?c>-features_and_scale_oacl

  - ip4-<?n>-<arch>-<NIC>-64b-<?t?c>-features_and_scale_oacl-ndr

    1. <NIC>-ethip4udp-ip4base-oacl10sl-10kflows
    2. <NIC>-ethip4udp-ip4base-oacl10sf-10kflows
    3. <NIC>-ethip4udp-ip4base-oacl50sl-10kflows
    4. <NIC>-ethip4udp-ip4base-oacl50sf-10kflows

IPv6 Routing
````````````

- 78b-<?t?c>-base_and_scale

  - ip6-<?n>-<arch>-<NIC>-78b-<?t?c>-base_and_scale-ndr

    1. <NIC>-ethip6-ip6base
    2. <NIC>-ethip6-ip6scale20k
    3. <NIC>-ethip6-ip6scale200k
    4. <NIC>-ethip6-ip6scale2m

- 78b-<?t?c>-base_and_features

  - ip6-<?n>-<arch>-<NIC>-78b-<?t?c>-base_and_features-ndr

    1. <NIC>-ethip6-ip6base
    2. <NIC>-ethip6-ip6base-copwhtlistbase
    3. <NIC>-ethip6-ip6base-iacldstbase

SRv6 Routing
````````````

- 78b-<?t?c>-features

  - srv6-<?n>-<arch>-<NIC>-78b-<?t?c>-features-ndr

    1. <NIC>-ethip6ip6-ip6base-srv6enc1sid
    2. <NIC>-ethip6srhip6-ip6base-srv6enc2sids
    3. <NIC>-ethip6srhip6-ip6base-srv6enc2sids-nodecaps
    4. <NIC>-ethip6srhip6-ip6base-srv6proxy-dyn
    5. <NIC>-ethip6srhip6-ip6base-srv6proxy-masq
    6. <NIC>-ethip6srhip6-ip6base-srv6proxy-stat

IPv4 Tunnels
````````````

- 64b-<?t?c>-base_and_features

  - ip4tun-<?n>-<arch>-<NIC>-64b-<?t?c>-base_and_features-ndr

    1. <NIC>-ethip4vxlan-l2bdbasemaclrn
    2. <NIC>-ethip4vxlan-l2xcbase
    3. <NIC>-ethip4lispip4-ip4base

- 64b-<?t?c>-base_and_scale

  - ip4tun-<?n>-<arch>-<NIC>-64b-<?t?c>-base_and_scale-ndr

    1. <NIC>-ethip4vxlan-l2bdbasemaclrn
    2. <NIC>-dot1q--ethip4vxlan-l2bdscale1l2bd1vlan1vxlan
    3. <NIC>-dot1q--ethip4vxlan-l2bdscale10l2bd10vlan10vxlan
    4. <NIC>-dot1q--ethip4vxlan-l2bdscale100l2bd100vlan100vxlan
    5. <NIC>-dot1q--ethip4vxlan-l2bdscale1kl2bd1kvlan1kvxlan

IPv6 Tunnels
````````````

- 78b-<?t?c>-base

  - ip6tun-<?n>-<arch>-<NIC>-78b-<?t?c>-base-ndr

    1. <NIC>-ethip6lispip4-ip6base
    2. <NIC>-ethip6lispip6-ip6base

KVM VMs vhost-user
``````````````````

- 64b-<?t?c>-base-l2sw

  - vhost-l2sw-<?n>-<arch>-<NIC>-64b-<?t?c>-base-ndr

    1. <NIC>-eth-l2xcbase-eth-2vhostvr1024-1vm
    2. <NIC>-eth-l2xcbase-eth-2vhostvr1024-1vm-cfsrr1
    3. <NIC>-eth-l2bdbasemaclrn-eth-2vhostvr1024-1vm
    4. <NIC>-eth-l2bdbasemaclrn-eth-2vhostvr1024-1vm-cfsrr1

- 64b-<?t?c>-base_and_scale-l2sw

  - vhost-l2sw-<?n>-<arch>-<NIC>-64b-<?t?c>-base_and_scale-ndr

    1. <NIC>-eth-l2bdbasemaclrn-eth-2vhostvr1024-1vm
    2. <NIC>-eth-l2bdbasemaclrn-eth-2vhostvr1024-1vm-cfsrr1
    3. <NIC>-eth-l2bdscale10kmaclrn-eth-2vhostvr1024-1vm-cfsrr1
    4. <NIC>-eth-l2bdscale100kmaclrn-eth-2vhostvr1024-1vm-cfsrr1
    5. <NIC>-eth-l2bdscale1mmaclrn-eth-2vhostvr1024-1vm-cfsrr1

- 64b-<?t?c>-base_and_scale-l2sw-vm

  - vhost-l2sw-<?n>-<arch>-<NIC>-64b-<?t?c>-base_and_scale-vm-ndr

    1. <NIC>-eth-l2xcbase-eth-2vhostvr1024-1vm
    2. <NIC>-eth-l2xcbase-eth-4vhostvr1024-2vm
    3. <NIC>-eth-l2bdbasemaclrn-eth-2vhostvr1024-1vm
    4. <NIC>-eth-l2bdbasemaclrn-eth-4vhostvr1024-2vm

- 64b-<?t?c>-base_and_scale-ip4

  - vhost-ip4-<?n>-<arch>-<NIC>-64b-<?t?c>-base_and_scale-ndr

    1. <NIC>-ethip4-ip4base-eth-2vhostvr1024-1vm
    2. <NIC>-ethip4-ip4base-eth-2vhostvr1024-1vm-cfsrr1
    3. <NIC>-ethip4-ip4base-eth-4vhostvr1024-2vm

LXC/DRC Container Memif
```````````````````````

- 64b-<?t?c>-base_and_scale

  - memif-<?n>-<arch>-<NIC>-64b-<?t?c>-base_and_scale-ndr

    1. <NIC>-eth-l2xcbase-eth-1memif-1dcr
    2. <NIC>-eth-l2xcbase-eth-2memif-1dcr
    3. <NIC>-eth-l2xcbase-eth-2memif-1lxc
    4. <NIC>-eth-l2bdbasemaclrn-eth-2memif-1lxc
    5. <NIC>-dot1q-l2bdbasemaclrn-eth-2memif-1dcr
    6. <NIC>-ethip4-ip4base-eth-2memif-1dcr

K8s Container Memif
```````````````````

- 64b-<?t?c>-base_and_scale-l2xc

  - k8s-memif-<?n>-<arch>-<NIC>-64b-<?t?c>-base_and_scale-l2xc-ndr

    1. <NIC>-eth-1drcl2xcbase-eth-2memif-1drcl2xc-1paral-k8s
    2. <NIC>-eth-1drcl2xcbase-eth-2memif-2drcl2xc-1horiz-k8s
    3. <NIC>-eth-1drcl2xcbase-eth-2memif-4drcl2xc-1horiz-k8s
    4. <NIC>-eth-1drcl2xcbase-eth-4memif-2drcl2xc-1chain-k8s
    5. <NIC>-eth-1drcl2xcbase-eth-8memif-4drcl2xc-1chain-k8s

- 64b-<?t?c>-base_and_scale-l2bd

  - k8s-memif-<?n>-<arch>-<NIC>-64b-<?t?c>-base_and_scale-l2bd-ndr

    1. <NIC>-eth-1drcl2bdbasemaclrn-eth-2memif-1drcl2xc-1paral-k8s
    2. <NIC>-eth-1drcl2bdbasemaclrn-eth-2memif-2drcl2xc-1horiz-k8s
    3. <NIC>-eth-1drcl2bdbasemaclrn-eth-2memif-4drcl2xc-1horiz-k8s
    4. <NIC>-eth-1drcl2bdbasemaclrn-eth-4memif-2drcl2xc-1chain-k8s
    5. <NIC>-eth-1drcl2bdbasemaclrn-eth-8memif-4drcl2xc-1chain-k8s

IPSec IPv4 Routing
``````````````````

- 64b-<?t?c>-base_and_scale-aes

  - ipsec-<?n>-<arch>-<NIC>-64b-<?t?c>-base_and_scale-aes-ndr

    1. <NIC>-ethip4ipsecbasetnl-ip4base-int-aes-gcm
    2. <NIC>-ethip4ipsecbasetnl-ip4base-tnl-aes-gcm
    3. <NIC>-ethip4ipsecscale1000tnl-ip4base-int-aes-gcm
    4. <NIC>-ethip4ipsecscale1000tnl-ip4base-tnl-aes-gcm
    5. <NIC>-ethip4ipsecbasetnlsw-ip4base-int-aes-gcm
    6. <NIC>-ethip4ipsecbasetnlsw-ip4base-tnl-aes-gcm

- 64b-<?t?c>-base_and_scale-cbc

  - ipsec-<?n>-<arch>-<NIC>-64b-<?t?c>-base_and_scale-cbc-ndr

    1. <NIC>-ethip4ipsecbasetnl-ip4base-int-cbc-sha1
    2. <NIC>-ethip4ipsecbasetnl-ip4base-tnl-cbc-sha1
    3. <NIC>-ethip4ipsecscale1000tnl-ip4base-int-cbc-sha1
    4. <NIC>-ethip4ipsecscale1000tnl-ip4base-tnl-cbc-sha1
    5. <NIC>-ethip4ipsecbasetnlsw-ip4base-int-cbc-sha1
    6. <NIC>-ethip4ipsecbasetnlsw-ip4base-tnl-cbc-sha1

VTS
```

- 114b-<?t?c>-base_and_features

  - vts-<?n>-<arch>-<NIC>-114b-<?t?c>-ndr

    1. <NIC>-ethip4vxlan-l2bdbasemaclrn-eth-iacldstbase-noacl-2vhostvr1024-1vm
    2. <NIC>-ethip4vxlan-l2bdbasemaclrn-eth-iacldstbase-aclpermitreflect-2vhostvr1024-1vm
    3. <NIC>-ethip4vxlan-l2bdbasemaclrn-eth-iacldstbase-aclpermit-2vhostvr1024-1vm

Testpmd
```````

- 64b-<?t?c>-base

  - testpmd-<?n>-<arch>-<NIC>-64b-<?t?c>-base-ndr

    1. 10ge2p1x710-eth-l2xcbase-testpmd

L3fwd
`````

- 64b-<?t?c>-base

  - l3fwd-<?n>-<arch>-<NIC>-64b-<?t?c>-base-ndr

    1. <NIC>-ethip4-ip4base-l3fwd

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

L2 Ethernet Switching
`````````````````````

- 64b-base_and_scale

  - l2sw-<?n>-<arch>-<NIC>-64b-base_and_scale-ndr
  - l2sw-<?n>-<arch>-<NIC>-64b-base_and_scale-pdr

    1. <NIC>-l2patch
    2. <NIC>-l2xcbase
    3. <NIC>-l2bdbase
    4. <NIC>-l2bdscale10kmaclrn
    5. <NIC>-l2bdscale100kmaclrn
    6. <NIC>-l2bdscale1mmaclrn

- 64b-base_and_features

  - l2sw-<?n>-<arch>-<NIC>-64b-base_and_features-ndr
  - l2sw-<?n>-<arch>-<NIC>-64b-base_and_features-pdr

    1. <NIC>-l2xcbase
    2. <NIC>-l2bdbase
    3. <NIC>-dot1q-l2xcbase
    4. <NIC>-dot1q-l2bdbase

IPv4 Routing
````````````

- 64b-base_and_scale

  - ip4-<?n>-<arch>-<NIC>-64b-base_and_scale-ndr
  - ip4-<?n>-<arch>-<NIC>-64b-base_and_scale-pdr

    1. <NIC>-ethip4-ip4base
    2. <NIC>-ethip4-ip4scale20k
    3. <NIC>-ethip4-ip4scale200k
    4. <NIC>-ethip4-ip4scale2m

- 64b-base_and_features

  - ip4-<?n>-<arch>-<NIC>-64b-base_and_features-ndr
  - ip4-<?n>-<arch>-<NIC>-64b-base_and_features-pdr

    1. <NIC>-ethip4-ip4base
    2. <NIC>-ethip4-ip4base-nat44
    3. <NIC>-ethip4-ip4base-ipolicemarkbase
    4. <NIC>-ethip4-ip4base-copwhtlistbase
    5. <NIC>-ethip4udp-ip4base-iacl10sl-10kflows
    6. <NIC>-ethip4udp-ip4base-oacl10sl-10kflows

- 64b-features_and_scale_nat44

  - ip4-<?n>-<arch>-<NIC>-64b-features_and_scale_nat44-ndr
  - ip4-<?n>-<arch>-<NIC>-64b-features_and_scale_nat44-pdr

    1. <NIC>-ethip4-ip4base-nat44
    2. <NIC>-ethip4-ip4base-updsrcscale15-nat44
    3. <NIC>-ethip4-ip4scale10-updsrcscale15-nat44
    4. <NIC>-ethip4-ip4scale100-updsrcscale15-nat44
    5. <NIC>-ethip4-ip4scale1000-updsrcscale15-nat44
    6. <NIC>-ethip4-ip4scale2000-updsrcscale15-nat44

- 64b-features_and_scale_iacl

  - ip4-<?n>-<arch>-<NIC>-64b-features_and_scale_iacl-ndr
  - ip4-<?n>-<arch>-<NIC>-64b-features_and_scale_iacl-pdr

    1. <NIC>-ethip4udp-ip4base-iacl10sl-10kflows
    2. <NIC>-ethip4udp-ip4base-iacl10sf-10kflows
    3. <NIC>-ethip4udp-ip4base-iacl50sl-10kflows
    4. <NIC>-ethip4udp-ip4base-iacl50sf-10kflows

- 64b-features_and_scale_oacl

  - ip4-<?n>-<arch>-<NIC>-64b-features_and_scale_oacl-ndr
  - ip4-<?n>-<arch>-<NIC>-64b-features_and_scale_oacl-pdr

    1. <NIC>-ethip4udp-ip4base-oacl10sl-10kflows
    2. <NIC>-ethip4udp-ip4base-oacl10sf-10kflows
    3. <NIC>-ethip4udp-ip4base-oacl50sl-10kflows
    4. <NIC>-ethip4udp-ip4base-oacl50sf-10kflows

IPv6 Routing
````````````

- 78b-base_and_scale

  - ip6-<?n>-<arch>-<NIC>-78b-base_and_scale-ndr
  - ip6-<?n>-<arch>-<NIC>-78b-base_and_scale-pdr

    1. <NIC>-ethip6-ip6base
    2. <NIC>-ethip6-ip6scale20k
    3. <NIC>-ethip6-ip6scale200k
    4. <NIC>-ethip6-ip6scale2m

- 78b-base_and_features

  - ip6-<?n>-<arch>-<NIC>-78b-base_and_features-ndr
  - ip6-<?n>-<arch>-<NIC>-78b-base_and_features-pdr

    1. <NIC>-ethip6-ip6base
    2. <NIC>-ethip6-ip6base-copwhtlistbase
    3. <NIC>-ethip6-ip6base-iacldstbase

SRv6 Routing
````````````

- 78b-features

  - srv6-<?n>-<arch>-<NIC>-78b-features-ndr
  - srv6-<?n>-<arch>-<NIC>-78b-features-pdr

    1. <NIC>-ethip6ip6-ip6base-srv6enc1sid
    2. <NIC>-ethip6srhip6-ip6base-srv6enc2sids
    3. <NIC>-ethip6srhip6-ip6base-srv6enc2sids-nodecaps
    4. <NIC>-ethip6srhip6-ip6base-srv6proxy-dyn
    5. <NIC>-ethip6srhip6-ip6base-srv6proxy-masq
    6. <NIC>-ethip6srhip6-ip6base-srv6proxy-stat

IPv4 Tunnels
````````````

- 64b-base_and_features

  - ip4tun-<?n>-<arch>-<NIC>-64b-base_and_features-ndr
  - ip4tun-<?n>-<arch>-<NIC>-64b-base_and_features-pdr

    1. <NIC>-ethip4vxlan-l2bdbasemaclrn
    2. <NIC>-ethip4vxlan-l2xcbase
    3. <NIC>-ethip4lispip4-ip4base

- 64b-base_and_scale

  - ip4tun-<?n>-<arch>-<NIC>-64b-base_and_scale-ndr
  - ip4tun-<?n>-<arch>-<NIC>-64b-base_and_scale-pdr

    1. <NIC>-ethip4vxlan-l2bdbasemaclrn
    2. <NIC>-dot1q--ethip4vxlan-l2bdscale1l2bd1vlan1vxlan
    3. <NIC>-dot1q--ethip4vxlan-l2bdscale10l2bd10vlan10vxlan
    4. <NIC>-dot1q--ethip4vxlan-l2bdscale100l2bd100vlan100vxlan
    5. <NIC>-dot1q--ethip4vxlan-l2bdscale1kl2bd1kvlan1kvxlan

IPv6 Tunnels
````````````

- 78b-base

  - ip6tun-<?n>-<arch>-<NIC>-78b-base-ndr
  - ip6tun-<?n>-<arch>-<NIC>-78b-base-pdr

    1. <NIC>-ethip6lispip4-ip6base
    2. <NIC>-ethip6lispip6-ip6base

KVM VMs vhost-user
``````````````````

- 64b-base-l2sw

  - vhost-l2sw-<?n>-<arch>-<NIC>-64b-base-ndr
  - vhost-l2sw-<?n>-<arch>-<NIC>-64b-base-pdr

    1. <NIC>-eth-l2xcbase-eth-2vhostvr1024-1vm
    2. <NIC>-eth-l2xcbase-eth-2vhostvr1024-1vm-cfsrr1
    3. <NIC>-eth-l2bdbasemaclrn-eth-2vhostvr1024-1vm
    4. <NIC>-eth-l2bdbasemaclrn-eth-2vhostvr1024-1vm-cfsrr1

- 64b-base_and_scale-l2sw

  - vhost-l2sw-<?n>-<arch>-<NIC>-64b-base_and_scale-ndr
  - vhost-l2sw-<?n>-<arch>-<NIC>-64b-base_and_scale-pdr

    1. <NIC>-eth-l2bdbasemaclrn-eth-2vhostvr1024-1vm
    2. <NIC>-eth-l2bdbasemaclrn-eth-2vhostvr1024-1vm-cfsrr1
    3. <NIC>-eth-l2bdscale10kmaclrn-eth-2vhostvr1024-1vm-cfsrr1
    4. <NIC>-eth-l2bdscale100kmaclrn-eth-2vhostvr1024-1vm-cfsrr1
    5. <NIC>-eth-l2bdscale1mmaclrn-eth-2vhostvr1024-1vm-cfsrr1

- 64b-base_and_scale-l2sw-vm

  - vhost-l2sw-<?n>-<arch>-<NIC>-64b-base_and_scale-vm-ndr
  - vhost-l2sw-<?n>-<arch>-<NIC>-64b-base_and_scale-vm-pdr

    1. <NIC>-eth-l2xcbase-eth-2vhostvr1024-1vm
    2. <NIC>-eth-l2xcbase-eth-4vhostvr1024-2vm
    3. <NIC>-eth-l2bdbasemaclrn-eth-2vhostvr1024-1vm
    4. <NIC>-eth-l2bdbasemaclrn-eth-4vhostvr1024-2vm

- 64b-base_and_scale-ip4

  - vhost-ip4-<?n>-<arch>-<NIC>-64b-base_and_scale-ndr
  - vhost-ip4-<?n>-<arch>-<NIC>-64b-base_and_scale-pdr

    1. <NIC>-ethip4-ip4base-eth-2vhostvr1024-1vm
    2. <NIC>-ethip4-ip4base-eth-2vhostvr1024-1vm-cfsrr1
    3. <NIC>-ethip4-ip4base-eth-4vhostvr1024-2vm

LXC/DRC Container Memif
```````````````````````

- 64b-base_and_scale

  - memif-<?n>-<arch>-<NIC>-64b-base_and_scale-ndr
  - memif-<?n>-<arch>-<NIC>-64b-base_and_scale-pdr

    1. <NIC>-eth-l2xcbase-eth-1memif-1dcr
    2. <NIC>-eth-l2xcbase-eth-2memif-1dcr
    3. <NIC>-eth-l2xcbase-eth-2memif-1lxc
    4. <NIC>-eth-l2bdbasemaclrn-eth-2memif-1lxc
    5. <NIC>-dot1q-l2bdbasemaclrn-eth-2memif-1dcr
    6. <NIC>-ethip4-ip4base-eth-2memif-1dcr

K8s Container Memif
```````````````````

- 64b-base_and_scale-l2xc

  - k8s-memif-<?n>-<arch>-<NIC>-64b-base_and_scale-l2xc-ndr
  - k8s-memif-<?n>-<arch>-<NIC>-64b-base_and_scale-l2xc-pdr

    1. <NIC>-eth-1drcl2xcbase-eth-2memif-1drcl2xc-1paral-k8s
    2. <NIC>-eth-1drcl2xcbase-eth-2memif-2drcl2xc-1horiz-k8s
    3. <NIC>-eth-1drcl2xcbase-eth-2memif-4drcl2xc-1horiz-k8s
    4. <NIC>-eth-1drcl2xcbase-eth-4memif-2drcl2xc-1chain-k8s
    5. <NIC>-eth-1drcl2xcbase-eth-8memif-4drcl2xc-1chain-k8s

- 64b-base_and_scale-l2bd

  - k8s-memif-<?n>-<arch>-<NIC>-64b-base_and_scale-l2bd-ndr
  - k8s-memif-<?n>-<arch>-<NIC>-64b-base_and_scale-l2bd-pdr

    1. <NIC>-eth-1drcl2bdbasemaclrn-eth-2memif-1drcl2xc-1paral-k8s
    2. <NIC>-eth-1drcl2bdbasemaclrn-eth-2memif-2drcl2xc-1horiz-k8s
    3. <NIC>-eth-1drcl2bdbasemaclrn-eth-2memif-4drcl2xc-1horiz-k8s
    4. <NIC>-eth-1drcl2bdbasemaclrn-eth-4memif-2drcl2xc-1chain-k8s
    5. <NIC>-eth-1drcl2bdbasemaclrn-eth-8memif-4drcl2xc-1chain-k8s

IPSec IPv4 Routing
``````````````````

- 64b-base_and_scale-aes

  - ipsec-<?n>-<arch>-<NIC>-64b-base_and_scale-aes-ndr
  - ipsec-<?n>-<arch>-<NIC>-64b-base_and_scale-aes-pdr

    1. <NIC>-ethip4ipsecbasetnl-ip4base-int-aes-gcm
    2. <NIC>-ethip4ipsecbasetnl-ip4base-tnl-aes-gcm
    3. <NIC>-ethip4ipsecscale1000tnl-ip4base-int-aes-gcm
    4. <NIC>-ethip4ipsecscale1000tnl-ip4base-tnl-aes-gcm
    5. <NIC>-ethip4ipsecbasetnlsw-ip4base-int-aes-gcm
    6. <NIC>-ethip4ipsecbasetnlsw-ip4base-tnl-aes-gcm

- 64b-base_and_scale-cbc

  - ipsec-<?n>-<arch>-<NIC>-64b-base_and_scale-cbc-ndr
  - ipsec-<?n>-<arch>-<NIC>-64b-base_and_scale-cbc-pdr

    1. <NIC>-ethip4ipsecbasetnl-ip4base-int-cbc-sha1
    2. <NIC>-ethip4ipsecbasetnl-ip4base-tnl-cbc-sha1
    3. <NIC>-ethip4ipsecscale1000tnl-ip4base-int-cbc-sha1
    4. <NIC>-ethip4ipsecscale1000tnl-ip4base-tnl-cbc-sha1
    5. <NIC>-ethip4ipsecbasetnlsw-ip4base-int-cbc-sha1
    6. <NIC>-ethip4ipsecbasetnlsw-ip4base-tnl-cbc-sha1

VTS
```

- 114b-base_and_features

  - vts-<?n>-<arch>-<NIC>-114b-ndr
  - vts-<?n>-<arch>-<NIC>-114b-pdr

    1. <NIC>-ethip4vxlan-l2bdbasemaclrn-eth-iacldstbase-noacl-2vhostvr1024-1vm
    2. <NIC>-ethip4vxlan-l2bdbasemaclrn-eth-iacldstbase-aclpermitreflect-2vhostvr1024-1vm
    3. <NIC>-ethip4vxlan-l2bdbasemaclrn-eth-iacldstbase-aclpermit-2vhostvr1024-1vm

Testpmd
```````

- 64b-base

  - testpmd-<?n>-<arch>-<NIC>-64b-base-ndr
  - testpmd-<?n>-<arch>-<NIC>-64b-base-pdr

    1. 10ge2p1x710-eth-l2xcbase-testpmd

L3fwd
`````

- 64b-base

  - l3fwd-<?n>-<arch>-<NIC>-64b-base-ndr
  - l3fwd-<?n>-<arch>-<NIC>-64b-base-pdr

    1. <NIC>-ethip4-ip4base-l3fwd
