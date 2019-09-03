Tunnel Encapsulations
---------------------

Tunnel encapsulations testing is grouped based on the type of outer
header: either IPv4 or IPv6.

IPv4 Tunnels
~~~~~~~~~~~~

VPP is tested in the following IPv4 tunnel baseline configurations:

- *ip4vxlan-l2bdbase*: VXLAN over IPv4 tunnels with L2 bridge-domain MAC
  switching.
- *ip4vxlan-l2xcbase*: VXLAN over IPv4 tunnels with L2 cross-connect.
- *ip4lispip4-ip4base*: LISP over IPv4 tunnels with IPv4 routing.
- *ip4lispip6-ip6base*: LISP over IPv4 tunnels with IPv6 routing.

In all cases listed above, low number of MAC, IPv4, IPv6 flows (254 or 253 per
direction) is switched or routed by VPP.

In addition, selected IPv4 tunnels are tested at scale:

- *dot1q--ip4vxlanscale-l2bd*: VXLAN over IPv4 tunnels with L2 bridge-
  domain MAC switching, with scaled-up dot1q VLANs (10, 100, 1k),
  mapped to scaled-up L2 bridge-domains (10, 100, 1k), that are in turn
  mapped to (10, 100, 1k) VXLAN tunnels. 64.5k flows are transmitted per
  direction.

IPv6 Tunnels
~~~~~~~~~~~~

VPP is tested in the following IPv6 tunnel baseline configurations:

- *ip6lispip4-ip4base*: LISP over IPv4 tunnels with IPv4 routing.
- *ip6lispip6-ip6base*: LISP over IPv4 tunnels with IPv6 routing.

In all cases listed above, low number of IPv4, IPv6 flows (253 per
direction) is routed by VPP.
