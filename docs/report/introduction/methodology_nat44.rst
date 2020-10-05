Network Address Translation IPv4 to IPv4
----------------------------------------

NAT44 Deterministic
~~~~~~~~~~~~~~~~~~~

NAT44 is tested in baseline and scale configurations with IPv4 routing:

- *ip4base-nat44*: baseline test with single NAT entry (addr, port),
  single UDP flow.
- *ip4base-udpsrcscale{U}-nat44*: baseline test with {U} NAT entries
  (addr, {U}ports), {U}=15.
- *ip4scale{R}-udpsrcscale{U}-nat44*: scale tests with {R}*{U} NAT
  entries ({R}addr, {U}ports), {R}=[100, 1k, 2k, 4k], {U}=15.

NAT44 Endpoint-Dependent
~~~~~~~~~~~~~~~~~~~~~~~~

