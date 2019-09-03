VPP Features
------------

VPP is tested in a number of data plane feature configurations across
different forwarding modes. Following sections list features tested.

ACL Security-Groups
~~~~~~~~~~~~~~~~~~~

Both stateless and stateful access control lists (ACL), also known as
security-groups, are supported by VPP.

Following ACL configurations are tested for MAC switching with L2
bridge-domains:

- *l2bdbasemaclrn-iacl{E}sl-{F}flows*: Input stateless ACL, with {E}
  entries and {F} flows.
- *l2bdbasemaclrn-oacl{E}sl-{F}flows*: Output stateless ACL, with {E}
  entries and {F} flows.
- *l2bdbasemaclrn-iacl{E}sf-{F}flows*: Input stateful ACL, with {E}
  entries and {F} flows.
- *l2bdbasemaclrn-oacl{E}sf-{F}flows*: Output stateful ACL, with {E}
  entries and {F} flows.

Following ACL configurations are tested with IPv4 routing:

- *ip4base-iacl{E}sl-{F}flows*: Input stateless ACL, with {E} entries
  and {F} flows.
- *ip4base-oacl{E}sl-{F}flows*: Output stateless ACL, with {E} entries
  and {F} flows.
- *ip4base-iacl{E}sf-{F}flows*: Input stateful ACL, with {E} entries and
  {F} flows.
- *ip4base-oacl{E}sf-{F}flows*: Output stateful ACL, with {E} entries
  and {F} flows.

ACL tests are executed with the following combinations of ACL entries
and number of flows:

- ACL entry definitions

  - flow non-matching deny entry: (src-ip4, dst-ip4, src-port, dst-port).
  - flow matching permit ACL entry: (src-ip4, dst-ip4).

- {E} - number of non-matching deny ACL entries, {E} = [1, 10, 50].
- {F} - number of UDP flows with different tuple (src-ip4, dst-ip4,
  src-port, dst-port), {F} = [100, 10k, 100k].
- All {E}x{F} combinations are tested per ACL type, for a total of 9.

ACL MAC-IP
~~~~~~~~~~

MAC-IP binding ACLs are tested for MAC switching with L2 bridge-domains:

- *l2bdbasemaclrn-macip-iacl{E}sl-{F}flows*: Input stateless ACL, with
  {E} entries and {F} flows.

MAC-IP ACL tests are executed with the following combinations of ACL
entries and number of flows:

- ACL entry definitions

  - flow non-matching deny entry: (dst-ip4, dst-mac, bit-mask)
  - flow matching permit ACL entry: (dst-ip4, dst-mac, bit-mask)

- {E} - number of non-matching deny ACL entries, {E} = [1, 10, 50]
- {F} - number of UDP flows with different tuple (dst-ip4, dst-mac),
  {F} = [100, 10k, 100k]
- All {E}x{F} combinations are tested per ACL type, for a total of 9.

NAT44
~~~~~

NAT44 is tested in baseline and scale configurations with IPv4 routing:

- *ip4base-nat44*: baseline test with single NAT entry (addr, port),
  single UDP flow.
- *ip4base-udpsrcscale{U}-nat44*: baseline test with {U} NAT entries
  (addr, {U}ports), {U}=15.
- *ip4scale{R}-udpsrcscale{U}-nat44*: scale tests with {R}*{U} NAT
  entries ({R}addr, {U}ports), {R}=[100, 1k, 2k, 4k], {U}=15.
