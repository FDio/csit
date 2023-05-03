---
title: "Tunnel Encapsulations"
weight: 3
---

# Tunnel Encapsulations

Tunnel encapsulations testing is grouped based on the type of outer
header: IPv4 or IPv6.

## IPv4 Tunnels

VPP is tested in the following IPv4 tunnel baseline configurations:

- *ip4vxlan-l2bdbase*: VXLAN over IPv4 tunnels with L2 bridge-domain MAC
  switching.
- *ip4vxlan-l2xcbase*: VXLAN over IPv4 tunnels with L2 cross-connect.
- *ip4lispip4-ip4base*: LISP over IPv4 tunnels with IPv4 routing.
- *ip4lispip6-ip6base*: LISP over IPv4 tunnels with IPv6 routing.
- *ip4gtpusw-ip4base*: GTPU over IPv4 tunnels with IPv4 routing.

In all cases listed above low number of MAC, IPv4, IPv6 flows (253 or 254 per
direction) is switched or routed by VPP.

In addition selected IPv4 tunnels are tested at scale:

- *dot1q--ip4vxlanscale-l2bd*: VXLAN over IPv4 tunnels with L2 bridge-
  domain MAC switching, with scaled up dot1q VLANs (10, 100, 1k),
  mapped to scaled up L2 bridge-domains (10, 100, 1k), that are in turn
  mapped to (10, 100, 1k) VXLAN tunnels. 64.5k flows are transmitted per
  direction.

## IPv6 Tunnels

VPP is tested in the following IPv6 tunnel baseline configurations:

- *ip6lispip4-ip4base*: LISP over IPv4 tunnels with IPv4 routing.
- *ip6lispip6-ip6base*: LISP over IPv4 tunnels with IPv6 routing.

In all cases listed above low number of IPv4, IPv6 flows (253 or 254 per
direction) is routed by VPP.

## GENEVE

### GENEVE Prefix Bindings

GENEVE prefix bindings should be representative to target applications, where
a packet flows of particular set of IPv4 addresses (L3 underlay network) is
routed via dedicated GENEVE interface by building an L2 overlay.

Private address ranges to be used in tests:

- East hosts ip address range: 10.0.1.0 - 10.127.255.255 (10.0/9 prefix)
  - Total of 2^23 - 256 (8 388 352) of usable IPv4 addresses
  - Usable in tests for up to 32 767 GENEVE tunnels (IPv4 underlay networks)
- West hosts ip address range: 10.128.1.0 - 10.255.255.255 (10.128/9 prefix)
  - Total of 2^23 - 256 (8 388 352) of usable IPv4 addresses
  - Usable in tests for up to 32 767 GENEVE tunnels (IPv4 underlay networks)

### GENEVE Tunnel Scale

If N is a number of GENEVE tunnels (and IPv4 underlay networks) then TG sends
256 packet flows in every of N different sets:

- i = 1,2,3, ... N - GENEVE tunnel index
- East-West direction: GENEVE encapsulated packets
  - Outer IP header:
    - src ip: 1.1.1.1
    - dst ip: 1.1.1.2
  - GENEVE header:
    - vni: i
  - Inner IP header:
    - src_ip_range(i) = 10.(0 + rounddown(i/255)).(modulo(i/255)).(0-to-255)
    - dst_ip_range(i) = 10.(128 + rounddown(i/255)).(modulo(i/255)).(0-to-255)
- West-East direction: non-encapsulated packets
  - IP header:
    - src_ip_range(i) = 10.(128 + rounddown(i/255)).(modulo(i/255)).(0-to-255)
    - dst_ip_range(i) = 10.(0 + rounddown(i/255)).(modulo(i/255)).(0-to-255)

 **geneve-tunnels** | **total-flows**
-------------------:|----------------:
 1                  | 256
 4                  | 1 024
 16                 | 4 096
 64                 | 16 384
 256                | 65 536
 1 024              | 262 144
