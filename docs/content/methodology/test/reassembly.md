---
title: "Reassembly"
weight: 9
---

# Packet reassembly performance

IP protocols (mainly IPv4) specify conditions for packet fragmentation
and packet reassembly. For VPP, the reassembly operation is more CPU intensive.
By default, VPP avoids unnecessary work, so there are only few scenarios
where VPP fragments IP packets, and even less scenarios where it reassemblies
the fragmented packets.

The typical situation when fragmentation is performed occurs with
tunnel encapsulation protocols, when the packet after encapsulation
would not fit into interface MTU (maximum transmission unit).
Some, but not all, encapsulation protocols also require
packet reassembly for decapsulation.

As the search algorithms used in CSIT work best when the number of packets
coming from TG (traffic generator) is the same
as the number of packets expected to come back to TG,
the easiest way to test reassembly performance of VPP is using
a 3-node testbed and a tunneling test suite adapted to cause fragmentation.

## MTU

By default, testbeds in CSIT are configured with MTU high enough
for encapsulated packets to fit in.
Not all devices and drivers used by VPP do support lowering MTU value.
For reassembly tests, only the physical interfaces on the DUT1-DUT2 link
have lowered MTU, and that currently works only with dpdk plugin.

## Impacts

Reassembly suites with small number of flows and tunnels
usually place encapsulation+fragmentation and reassembly+decapsulation
on different workers, so the bottleneck seen in performance results
is not affected by fragmentation performance.

Reassembly suites with high number of flows and tunnels
achieve balanced load on all workers, so their overall performance
is affected by both fragmentation and reassembly performance.

Some protocols (e.g. IPsec) are CPU intensive not only
on fragmentation and reassembly, but also on encapsulation and decapsulation.
Reassembly (and depending on scale also fragmentation) impact
on those tests can still be visible, at least for big regressions.
