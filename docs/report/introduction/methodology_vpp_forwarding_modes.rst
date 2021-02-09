VPP Forwarding Modes
--------------------

VPP is tested in a number of L2, IPv4 and IPv6 packet lookup and
forwarding modes. Within each mode baseline and scale tests are
executed, the latter with varying number of FIB entries.

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
  Both source and destination MAC addresses are incremented for every
  packet.

- *l2bdscale*: high number of L2 flows is switched by VPP. Tested MAC
  FIB sizes include: i) 10k (5k unique flows per direction), ii) 100k
  (2x 50k flows) and iii) 1M (2x 500k). Both source and destination MAC
  addresses are changed for every packet using incremental ordering
  making VPP learn (or refresh) distinct src MAC entries and look up
  distinct dst MAC entries for every packet. For details, see
  :ref:`packet_flow_ordering`.

Ethernet wire encapsulations tested include: untagged, dot1q, dot1ad.

IPv4 Routing
~~~~~~~~~~~~

IPv4 routing tests are executed in baseline and scale configurations:

- *ip4base*: a low number of IPv4 /32 prefix FIB entries are configured
  in VPP (506 or 508) with a corresponding number of IPv4 flows (253 or
  254 per direction) being routed by VPP.  Destination IPv4 addresses
  are incremented for every packet.

- *ip4scale*: a high number of IPv4 /32 prefix FIB entries are
  configured in VPP. Tested IPv4 FIB sizes of /32 prefixes include: i)
  20k with 10k unique flows per direction, ii) 200k with 2x 100k flows
  and iii) 2M with 2x 1M flows. Destination IPv4 addresses are changed
  for every packet using either incremental or random ordering
  depending on test type, ensuring distinct FIB entries being hit for
  every packet. For details, see :ref:`packet_flow_ordering`.

IPv6 Routing
~~~~~~~~~~~~

Similarly to IPv4, IPv6 routing tests are executed in baseline and scale
configurations:

- *ip6base*: a low number of IPv6 /128 prefix FIB entries are configured
  in VPP (506 or 508) with a corresponding number of IPv6 flows (253 or
  254 per direction) being routed by VPP.  Destination IPv6 addresses
  are incremented for every packet.

- *ip4scale*: a high number of IPv6 /128 prefix FIB entries are
  configured in VPP. Tested IPv6 FIB sizes of /128 prefixes include: i)
  20k with 10k unique flows per direction, ii) 200k with 2x 100k flows
  and iii) 2M with 2x 1M flows. Destination IPv6 addresses are changed
  for every packet using either incremental or random ordering
  depending on test type, ensuring distinct FIB entries being hit for
  every packet. For details, see :ref:`packet_flow_ordering`.

SRv6 Routing
~~~~~~~~~~~~

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
