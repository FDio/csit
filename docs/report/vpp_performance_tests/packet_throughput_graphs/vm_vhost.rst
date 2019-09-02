
.. raw:: latex

    \clearpage

.. _KVM_VMs_vhost:

KVM VMs vhost-user
==================

Following sections include summary graphs of VPP Phy-to-VM(s)-to-Phy
performance with VM virtio and VPP vhost-user virtual interfaces,
including NDR throughput (zero packet loss) and PDR throughput (<0.5%
packet loss). Performance is reported for VPP running in multiple
configurations of VPP worker thread(s), a.k.a. VPP data plane thread(s),
and their physical CPU core(s) placement.

CSIT source code for the test cases used for plots can be found in
`CSIT git repository <https://git.fd.io/csit/tree/tests/vpp/perf/vm_vhost?h=rls1908>`_.

.. toctree::

    vm_vhost-2n-skx-xxv710
    vm_vhost-3n-skx-xxv710
    vm_vhost-3n-skx-x710
    vm_vhost-3n-hsw-xl710
    vm_vhost-3n-tsh-x520
