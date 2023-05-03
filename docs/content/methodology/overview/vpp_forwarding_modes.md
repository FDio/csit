---
title: "VPP Forwarding Modes"
weight: 4
---

# VPP Forwarding Modes

VPP is tested in a number of L2, IPv4 and IPv6 packet lookup and forwarding
modes. Within each mode baseline and scale tests are executed, the latter with
varying number of FIB entries.

## L2 Ethernet Switching

VPP is tested in three L2 forwarding modes:

- *l2patch*: L2 patch, the fastest point-to-point L2 path that loops
  packets between two interfaces without any Ethernet frame checks or
  lookups.
- *l2xc*: L2 cross-connect, point-to-point L2 path with all Ethernet
  frame checks, but no MAC learning and no MAC lookup.
- *l2bd*: L2 bridge-domain, multipoint-to-multipoint L2 path with all
  Ethernet frame checks, with MAC learning (unless static MACs are used)
  and MAC lookup.

l2bd tests are executed in baseline and scale configurations:

- *l2bdbase*: Two MAC FIB entries are learned by VPP to enable packet
  switching between two interfaces in two directions. VPP L2 switching
  is tested with 254 IPv4 unique flows per direction, varying IPv4
  source address per flow in order to invoke RSS based packet
  distribution across VPP workers. The same source and destination MAC
  address is used for all flows per direction. IPv4 source address is
  incremented for every packet.

- *l2bdscale*: A high number of MAC FIB entries are learned by VPP to
  enable packet switching between two interfaces in two directions.
  Tested MAC FIB sizes include: i) 10k with 5k unique flows per
  direction, ii) 100k with 2 x 50k flows and iii) 1M with 2 x 500k
  flows. Unique flows are created by using distinct source and
  destination MAC addresses that are changed for every packet using
  incremental ordering, making VPP learn (or refresh) distinct src MAC
  entries and look up distinct dst MAC entries for every packet. For
  details, see
  [Packet Flow Ordering]({{< ref "packet_flow_ordering#Packet Flow Ordering" >}}).

Ethernet wire encapsulations tested include: untagged, dot1q, dot1ad.

## IPv4 Routing

IPv4 routing tests are executed in baseline and scale configurations:

- *ip4base*: Two /32 IPv4 FIB entries are configured in VPP to enable
  packet routing between two interfaces in two directions. VPP routing
  is tested with 253 IPv4 unique flows per direction, varying IPv4
  source address per flow in order to invoke RSS based packet
  distribution across VPP workers. IPv4 source address is incremented
  for every packet.

- *ip4scale*: A high number of /32 IPv4 FIB entries are configured in
  VPP. Tested IPv4 FIB sizes include: i) 20k with 10k unique flows per
  direction, ii) 200k with 2 * 100k flows and iii) 2M with 2 * 1M
  flows. Unique flows are created by using distinct IPv4 destination
  addresses that are changed for every packet, using incremental or
  random ordering. For details, see
  [Packet Flow Ordering]({{< ref "packet_flow_ordering#Packet Flow Ordering" >}}).

## IPv6 Routing

Similarly to IPv4, IPv6 routing tests are executed in baseline and scale
configurations:

- *ip6base*: Two /128 IPv4 FIB entries are configured in VPP to enable
  packet routing between two interfaces in two directions. VPP routing
  is tested with 253 IPv6 unique flows per direction, varying IPv6
  source address per flow in order to invoke RSS based packet
  distribution across VPP workers. IPv6 source address is incremented
  for every packet.

- *ip4scale*: A high number of /128 IPv6 FIB entries are configured in
  VPP. Tested IPv6 FIB sizes include: i) 20k with 10k unique flows per
  direction, ii) 200k with 2 * 100k flows and iii) 2M with 2 * 1M
  flows. Unique flows are created by using distinct IPv6 destination
  addresses that are changed for every packet, using incremental or
  random ordering. For details, see
  [Packet Flow Ordering]({{< ref "packet_flow_ordering#Packet Flow Ordering" >}}).

## SRv6 Routing

SRv6 routing tests are executed in a number of baseline configurations,
in each case SR policy and steering policy are configured for one
direction and one (or two) SR behaviours (functions) in the other
directions:

- *srv6enc1sid*: One SID (no SRH present), one SR function - End.
- *srv6enc2sids*: Two SIDs (SRH present), two SR functions - End and
  End.DX6.
- *srv6enc2sids-nodecaps*: Two SIDs (SRH present) without decapsulation,
  one SR function - End.
- *srv6proxy-dyn*: Dynamic SRv6 proxy, one SR function - End.AD.
- *srv6proxy-masq*: Masquerading SRv6 proxy, one SR function - End.AM.
- *srv6proxy-stat*: Static SRv6 proxy, one SR function - End.AS.

In all listed cases low number of IPv6 flows (253 per direction) is
routed by VPP.
