IPv4 Routed-Forwarding
======================

This section includes summary graphs of L3FWD Phy-to-Phy performance with packet
routed forwarding measured at 50% of discovered NDR throughput rate. Latency is
reported for L3FWD running in multiple configurations of L3FWD pmd thread(s),
a.k.a. L3FWD data plane thread(s), and their physical CPU core(s) placement.

L3FWD packet latency - running in configuration of **one worker thread (1t) on one
physical core (1c)** - is presented in the figure below.

.. raw:: html

    <iframe width="700" height="1000" frameborder="0" scrolling="no" src="../../_static/dpdk/64B-1t1c-ipv4-ndrdisc-lat50.html"></iframe>

*Figure 1. L3FWD 1thread 1core - packet latency for Phy-to-Phy IPv4 Routed-Forwarding.*

CSIT test cases used to generate results presented above can be found in CSIT
git repository by filtering with specified regex as follows:

.. program-output:: cd ../../ && set -x && cd tests/dpdk/perf && grep -E '64B-1t1c-ethip4-ip4base-l3fwd-ndrdisc' *
   :shell:

Testpmd packet latency - running in configuration of **two worker threads (2t)
on two physical cores (2c)** - is presented in the figure below.

.. raw:: html

    <iframe width="700" height="1000" frameborder="0" scrolling="no" src="../../_static/dpdk/64B-2t2c-ipv4-ndrdisc-lat50.html"></iframe>

*Figure 2. L3FWD 2thread 2core - packet latency for Phy-to-Phy IPv4 Routed-Forwarding.*

CSIT test cases used to generate results presented above can be found in CSIT
git repository by filtering with specified regex as follows:

.. program-output:: cd ../../ && set -x && cd tests/dpdk/perf && grep -E '64B-2t2c-ethip4-ip4base-l3fwd-ndrdisc' *
   :shell:
