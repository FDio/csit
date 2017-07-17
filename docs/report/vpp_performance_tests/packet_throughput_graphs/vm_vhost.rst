VM vhost Connections
====================

Following sections include summary graphs of VPP Phy-to-VM(s)-to-Phy
performance with VM virtio and VPP vhost-user virtual interfaces,
including NDR throughput (zero packet loss) and PDR throughput (<0.5%
packet loss). Performance is reported for VPP running in multiple
configurations of VPP worker thread(s), a.k.a. VPP data plane thread(s),
and their physical CPU core(s) placement.

NDR Throughput
~~~~~~~~~~~~~~

VPP NDR 64B packet throughput in 1t1c setup (1thread, 1core) is presented
in the graph below.

.. raw:: html

    <iframe width="700" height="1000" frameborder="0" scrolling="no" src="../../_static/vpp/64B-1t1c-vhost-ndrdisc.html"></iframe>

*Figure 1. VPP 1thread 1core - NDR Throughput for Phy-to-VM-to-Phy VM vhost-user
vhost-user.*

CSIT source code for the test cases used for above plots can be found in CSIT
git repository:

.. program-output:: cd ../../ && set -x && cd tests/vpp/perf/vm_vhost && grep -E "64B-1t1c-.*vhost.*-ndrdisc" *
   :shell:

VPP NDR 64B packet throughput in 2t2c setup (2thread, 2core) is presented
in the graph below.

.. raw:: html

    <iframe width="700" height="1000" frameborder="0" scrolling="no" src="../../_static/vpp/64B-2t2c-vhost-ndrdisc.html"></iframe>

*Figure 2. VPP 2threads 2cores - NDR Throughput for Phy-to-VM-to-Phy VM vhost-user
vhost-user.*

CSIT source code for the test cases used for above plots can be found in CSIT
git repository:

.. program-output:: cd ../../ && set -x && cd tests/vpp/perf/vm_vhost && grep -E "64B-2t2c-.*vhost.*-ndrdisc" *
   :shell:

PDR Throughput
~~~~~~~~~~~~~~

VPP PDR 64B packet throughput in 1t1c setup (1thread, 1core) is presented
in the graph below. PDR measured for 0.5% packet loss ratio.

.. raw:: html

    <iframe width="700" height="1000" frameborder="0" scrolling="no" src="../../_static/vpp/64B-1t1c-vhost-pdrdisc.html"></iframe>

*Figure 3. VPP 1thread 1core - PDR Throughput for Phy-to-VM-to-Phy VM vhost-user
vhost-user.*

CSIT source code for the test cases used for above plots can be found in CSIT
git repository:

.. program-output:: cd ../../ && set -x && cd tests/vpp/perf/vm_vhost && grep -E "64B-1t1c-.*vhost.*-pdrdisc" *
   :shell:

VPP PDR 64B packet throughput in 2t2c setup (2thread, 2core) is presented
in the graph below. PDR measured for 0.5% packet loss ratio.

.. raw:: html

    <iframe width="700" height="1000" frameborder="0" scrolling="no" src="../../_static/vpp/64B-2t2c-vhost-pdrdisc.html"></iframe>

*Figure 4. VPP 2thread 2core - PDR Throughput for Phy-to-VM-to-Phy VM vhost-user
vhost-user.*

CSIT source code for the test cases used for above plots can be found in CSIT
git repository:

.. program-output:: cd ../../ && set -x && cd tests/vpp/perf/vm_vhost && grep -E "64B-2t2c-.*vhost.*-pdrdisc" *
   :shell:
