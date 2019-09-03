VPP Forwarding Modes
--------------------

VPP is tested in a number of L2 and IP packet lookup and forwarding
modes. Within each mode, baseline and scale tests are executed; the
latter with a varying number of lookup entries.

L2 Ethernet Switching
~~~~~~~~~~~~~~~~~~~~~

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

- *l2bdbase*: low number of L2 flows (254 per direction) is switched by
  VPP. They drive the content of MAC FIB size (508 total MAC entries).
  Both source and destination MAC addresses are incremented on a
  packet-by-packet basis.

- *l2bdscale*: high number of L2 flows is switched by VPP. Tested MAC
  FIB sizes include: i) 10k (5k unique flows per direction), ii) 100k
  (2x 50k flows) and iii) 1M (2x 500k). Both source and destination MAC
  addresses are incremented on a packet-by-packet basis. This ensures
  that new entries are learned, refreshed and looked up at every packet,
  demonstrating the worst-case scenario.

Ethernet wire encapsulations tested include: untagged, dot1q, dot1ad.

IPv4 Routing
~~~~~~~~~~~~

IPv4 routing tests are executed in baseline and scale configurations:

- *ip4base*: low number of IPv4 flows (253 or 254 per direction) is routed by
  VPP. They drive the content of IPv4 FIB size (506 or 508 total /32 prefixes).
  Destination IPv4 addresses are incremented on a packet-by-packet
  basis.

- *ip4scale*: high number of IPv4 flows is routed by VPP. Tested IPv4
  FIB sizes of /32 prefixes include: i) 20k (10k unique flows per
  direction), ii) 200k (2x 100k flows) and iii) 2M (2x 1M). Destination
  IPv4 addresses are incremented on a packet-by-packet basis. This ensures
  that new FIB entries are looked up at every packet, demonstrating
  the worst-case scenario.

IPv6 Routing
~~~~~~~~~~~~

IPv6 routing tests are executed in baseline and scale configurations:

- *ip6base*: low number of IPv6 flows (253 or 254 per direction) is routed by
  VPP. They drive the content of IPv6 FIB size (506 or 508 total /128 prefixes).
  Destination IPv6 addresses are incremented on a packet-by-packet
  basis.

- *ip6scale*: high number of IPv6 flows is routed by VPP. Tested IPv6
  FIB sizes of /128 prefixes include: i) 20k (10k unique flows per
  direction), ii) 200k (2x 100k flows) and iii) 2M (2x 1M). Destination
  IPv6 addresses are incremented on a packet-by-packet basis. This ensures
  that new FIB entries are looked up at every packet, demonstrating
  the worst-case scenario.

SRv6 Routing
~~~~~~~~~~~~

SRv6 routing tests are executed in a number of baseline configurations,
in each case SR policy and steering policy are configured in one
direction and one or two SR behaviours (functions) in the other
direction:

- *srv6enc1sid*: One SID (no SRH present), one SR function - End.
- *srv6enc2sids*: Two SIDs (SRH present), two SR functions - End and
  End.DX6.
- *srv6enc2sids-nodecaps*: Two SIDs (SRH present) without decapsulation,
  one SR function - End.
- *srv6proxy-dyn*: Dynamic SRv6 proxy, one SR function - End.AD.
- *srv6proxy-masq*: Masquerading SRv6 proxy, one SR function - End.AM.
- *srv6proxy-stat*: Static SRv6 proxy, one SR function - End.AS.

In all listed cases, low number of IPv6 flows (253 per direction) is
routed by VPP.
