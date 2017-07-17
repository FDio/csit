IPv4 Routed-Forwarding
======================

Following sections include summary graphs ofL3FWD Phy-to-Phy performance with
packet routed forwarding, including NDR throughput (zero packet loss)
and PDR throughput (<0.5% packet loss). Performance is reported for L3FWD
running in multiple configurations of L3FWD pmd thread(s), a.k.a. L3FWD
data plane thread(s), and their physical CPU core(s) placement.

NDR Throughput
~~~~~~~~~~~~~~

Testpmd NDR 64B packet throughput in 1t1c setup (1thread, 1core) is presented
in the graph below.

.. raw:: html

    <iframe width="700" height="1000" frameborder="0" scrolling="no" src="../../_static/dpdk/64B-1t1c-ipv4-ndrdisc.html"></iframe>

*Figure 1. L3FWD 1thread 1core - NDR Throughput for Phy-to-Phy IPv4 Routed-Forwarding
Looping.*

CSIT source code for the test cases used for above plots can be found in CSIT
git repository:

.. program-output:: cd ../../ && set -x && cd tests/dpdk/perf && grep -P '64B-1t1c-ethip4-ip4base-l3fwd-ndrdisc' *
   :shell:

Testpmd NDR 64B packet throughput in 2t2c setup (2thread, 2core) is presented
in the graph below.

.. raw:: html

    <iframe width="700" height="1000" frameborder="0" scrolling="no" src="../../_static/dpdk/64B-2t2c-ipv4-ndrdisc.html"></iframe>

*Figure 2. L3FWD 2threads 2cores - NDR Throughput for Phy-to-Phy IPv4 Routed-Forwarding
Looping.*

CSIT source code for the test cases used for above plots can be found in CSIT
git repository:

.. program-output:: cd ../../ && set -x && cd tests/dpdk/perf && grep -P '64B-2t2c-ethip4-ip4base-l3fwd-ndrdisc' *
   :shell:

PDR Throughput
~~~~~~~~~~~~~~

L3FWD PDR 64B packet throughput in 1t1c setup (1thread, 1core) is presented
in the graph below. PDR measured for 0.5% packet loss ratio.

.. raw:: html

    <iframe width="700" height="1000" frameborder="0" scrolling="no" src="../../_static/dpdk/64B-1t1c-ipv4-pdrdisc.html"></iframe>

*Figure 3. L3FWD 1thread 1core - PDR Throughput for Phy-to-Phy IPv4 Routed-Forwarding
Looping.*

CSIT source code for the test cases used for above plots can be found in CSIT
git repository:

.. program-output:: cd ../../ && set -x && cd tests/dpdk/perf && grep -P '64B-1t1c-ethip4-ip4base-l3fwd-pdrdisc' *
   :shell:

L3FWD PDR 64B packet throughput in 2t2c setup (2thread, 2core) is presented
in the graph below. PDR measured for 0.5% packet loss ratio.

.. raw:: html

    <iframe width="700" height="1000" frameborder="0" scrolling="no" src="../../_static/dpdk/64B-2t2c-ipv4-pdrdisc.html"></iframe>

*Figure 4. L3FWD 2thread 2core - PDR Throughput for Phy-to-Phy IPv4 Routed-Forwarding
Looping.*

CSIT source code for the test cases used for above plots can be found in CSIT
git repository:

.. program-output:: cd ../../ && set -x && cd tests/dpdk/perf && grep -P '64B-2t2c-ethip4-ip4base-l3fwd-pdrdisc' *
   :shell:
