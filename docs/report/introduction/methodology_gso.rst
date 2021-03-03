.. _gso_methodology:

Generic Segmentation Offload Tests
----------------------------------

Overview
~~~~~~~~

Generic Segmentation Offload (GSO) reduces per-packet processing
overhead by enabling applications  to pass a multi-packet buffer to
(v)NIC and process a smaller number of large packets (e.g. frame size of
64 KB), instead of processing higher numbers of small packets (e.g.
frame size of 1500 B), thus reducing per-packet overhead.

|csit-release| introduced GSO tests for VPP vhostuser and tapv2
interfaces. All tests cases use iPerf3 client and server applications
running TCP/IP as a traffic generator. For performance comparison the
same tests are run without GSO enabled.

GSO Test Topologies
~~~~~~~~~~~~~~~~~~~

Two VPP GSO test topologies are implemented in |csit-release|:

1. iPerfC_GSOvirtio_LinuxVM --- GSOvhost_VPP_GSOvhost --- iPerfS_GSOvirtio_LinuxVM

   - Tests VPP GSO on vhostuser interfaces and interaction with Linux
     virtio with GSO enabled.

1. iPerfC_GSOtap_LinuxCtr --- GSOtapv2_VPP_GSOtapv2 --- iPerfS_GSOtap_LinuxCtr

   - Tests VPP GSO on tapv2 interfaces and interaction with Linux tap
     with GSO enabled.

Common configuration:

- iPerfC (client) and iPerfS (server) run in TCP/IP mode without upper
  bandwidth limit.
- Trial duration is set to 30 sec.
- iPerfC, iPerfS and VPP run in the single SUT node.


VPP GSOtap Topology
-------------------

VPP Configuration
~~~~~~~~~~~~~~~~~

VPP GSOtap tests in |csit-release| are executed without using
hyperthreading. VPP worker runs on a single core. Multi-core tests are
not executed. Following core pinning scheme is used:

- 1t1c (rxq=1, rx_qsz=4096, tx_qsz=4096)

  - system isolated: 0,28,56,84
  - vpp mt:  1
  - vpp wt:  2
  - vhost:   3-5
  - iperf-s: 6
  - iperf-c: 7


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


VPP GSOvhost Topology
---------------------

VPP Configuration
~~~~~~~~~~~~~~~~~

VPP GSOvhost tests in |csit-release| are executed without using
hyperthreading. VPP worker runs on a single core. Multi-core tests are
not executed. Following core pinning scheme is used:

- 1t1c (rxq=2, rx_qsz=1024, tx_qsz=1024)
  - system isolated: 0,28,56,84
  - vpp mt:  1
  - vpp wt:  2
  - vm-iperf-s: 3,4,5,6,7
  - vm-iperf-c: 51,8,9,10,11
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