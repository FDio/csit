.. _geneve_methodology:

Generic Network Virtualization Encapsulation
--------------------------------------------

GENEVE Prefix Bindings
^^^^^^^^^^^^^^^^^^^^^^

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

GENEVE Tunnel Scale
~~~~~~~~~~~~~~~~~~~

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

+----------------+-------------+
| geneve-tunnels | total-flows |
+================+=============+
|              1 |         256 |
+----------------+-------------+
|              4 |       1 024 |
+----------------+-------------+
|             16 |       4 096 |
+----------------+-------------+
|             64 |      16 384 |
+----------------+-------------+
|            256 |      65 536 |
+----------------+-------------+
|          1 024 |     262 144 |
+----------------+-------------+
