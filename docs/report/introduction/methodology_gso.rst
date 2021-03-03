.. _gso_methodology:

Generic Segmentation Offload Tests
----------------------------------

Overview
~~~~~~~~

Generic Segmentation Offload (GSO) is a widely used software implementation
of TCP Segmentation Offload (TSO), which reduces per-packet processing overhead.
Much like TSO, GSO gains performance by enabling upper layer applications to
process a smaller number of large packets (e.g. MTU size of 64KB), instead of
processing higher numbers of small packets (e.g. MTU size of 1500B), thus
reducing per-packet overhead.


Topologies
~~~~~~~~~~

Following VPP GSO test topologies are implemented in rls2101:

1. iPerfC_GSOvirtioLinux_in_VM --- GSOvhost_VPP1_GSOvhost --- iPerfS_GSOvirtioLinux_in_VM

   - tests VPP GSOvhost and interaction with Linux virtio with GSO enabled
   - uses one SUT node, no TG node needed

1. iPerfC_GSOtap_in_Ctr --- GSOtapv2_VPP1_GSOvhost --- GSOvirtio_VPP2_in_VM_GSOvirtio --- GSOvhost_VPP1_GSOtapv2 ---iPerfS_GSOtap_in_Ctr

   - tests VPP GSOvhost, VPP GSOtapv2, VPP GSOvirtio and interaction with Linux
     tap with GSO enabled
   - uses one SUT node, no TG node needed


GSOtap Topology
---------------

VPP configuration
~~~~~~~~~~~~~~~~~

In current test setup, hyperthreading is no used. The actual pinning scheme is
described below:

- hyperthreading disabled:
  - 1t1c (rxq=1, rx_qsz=4096, tx_qsz=4096)
    - system isolated: 0,28,56,84
    - vpp mt:  1
    - vpp wt:  2
    - vhost:   3-5
    - iperf-s: 6
    - iperf-c: 7
  - 2t2c (rxq=2, rx_qsz=4096, tx_qsz=4096)
    - system isolated: 0,28,56,84
    - vpp mt:  1
    - vpp wt:  2,3
    - vhost:   4-8
    - iperf-s: 9
    - iperf-c: 10
  - 4t4c (rxq=4, rx_qsz=4096, tx_qsz=4096)
    - system isolated: 0,28,56,84
    - vpp mt:  1
    - vpp wt:  2,3,4,5
    - vhost:   6-14
    - iperf-s: 15
    - iperf-c: 16


iPerf3 Server Configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~~

iPerf3 version used 3.7

```
  $ sudo -E -S ip netns exec tap1_namespace iperf3 \
      --server --daemon --pidfile /tmp/iperf3_server.pid --logfile /tmp/iperf3.log --port 5201 --affinity <X>
```


iPerf3 Client Configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~~

iPerf3 version used 3.7

```
  $ sudo -E -S ip netns exec tap1_namespace iperf3 \
      --client 2.2.2.2 --bind 1.1.1.1 --port 5201 --parallel <Y> --time 30.0 --affinity <X> --zerocopy
```


VM vhost Topology
-----------------

VPP configuration
~~~~~~~~~~~~~~~~~

In current test setup, hyperthreading is no used. The actual pinning scheme is
described below:

- hyperthreading disabled:
  - 1t1c (rxq=2, rx_qsz=1024, tx_qsz=1024)
    - system isolated: 0,28,56,84
    - vpp mt:  1
    - vpp wt:  2
    - vm-iperf-s: 3,4,5,6,7
    - vm-iperf-c: 51,8,9,10,11
    - iperf-s: 1
    - iperf-c: 1
  - 2t2c (rxq=4, rx_qsz=1024, tx_qsz=1024)
    - system isolated: 0,28,56,84
    - vpp mt:  1
    - vpp wt:  2,3,58,59
    - vm-iperf-s: 4,5,6,7,8
    - vm-iperf-c: 9,10,11,12,13
    - iperf-s: 1
    - iperf-c: 1
  - 4t4c (rxq=8, rx_qsz=1024, tx_qsz=1024)
    - system isolated: 0,28,56,84
    - vpp mt:  1
    - vpp wt:  2,3,4,5
    - vm-iperf-s: 6,7,8,9,10
    - vm-iperf-c: 11,12,13,14,15
    - iperf-s: 1
    - iperf-c: 1


iPerf3 Server Configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~~

iPerf3 version used 3.7

```
  $ sudo iperf3 \
      --server --daemon --pidfile /tmp/iperf3_server.pid --logfile /tmp/iperf3.log --port 5201 --affinity X
```


iPerf3 Client Configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~~

iPerf3 version used 3.7

```
  $ sudo iperf3 \
      --client 2.2.2.2 --bind 1.1.1.1 --port 5201 --parallel <Y> --time 30.0 --affinity X --zerocopy
```