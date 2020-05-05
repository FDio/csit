TCP/IP with iperf3
^^^^^^^^^^^^^^^^^^

`iperf3 goodput measurement tool <https://github.com/esnet/iperf>`_
is used for measuring the maximum attainable goodput of the VPP Host
Stack connection across two instances of VPP running on separate DUT
nodes. iperf3 is a popular open source tool for active measurements
of the maximum achievable goodput on IP networks.

Because iperf3 utilizes the POSIX socket interface APIs, the current
test configuration utilizes the LD_PRELOAD mechanism in the linux
kernel to connect iperf3 to the VPP Host Stack using the VPP
Communications Library (VCL) LD_PRELOAD library (libvcl_ldpreload.so).

In the future, a forked version of iperf3 which has been modified to
directly use the VCL application APIs may be added to determine the
difference in performance of 'VCL Native' applications versus utilizing
LD_PRELOAD which inherently has more overhead and other limitations.

The test configuration is as follows:

::

           DUT1              Network               DUT2
    [ iperf3-client -> VPP1 ]=======[ VPP2 -> iperf3-server]

where,

1. iperf3 server attaches to VPP2 and LISTENs on VPP2:TCP port 5201.
2. iperf3 client attaches to VPP1 and opens one or more stream
   connections to VPP2:TCP port 5201.
3. iperf3 client transmits a uni-directional stream as fast as the
   VPP Host Stack allows to the iperf3 server for the test duration.
4. At the end of the test the iperf3 client emits the goodput
   measurements for all streams and the sum of all streams.

Test cases include 1 and 10 Streams with a 20 second test duration
with the VPP Host Stack configured to utilize the Cubic TCP
congestion algorithm.

Note: iperf3 is single threaded, so it is expected that the 10 stream
test does not show any performance improvement due to
multi-thread/multi-core execution.

There are also variations of these test cases which use the VPP Network
Simulator (NSIM) plugin to test the VPP Hoststack goodput with 1 percent
of the traffic being dropped at the output interface of VPP1 thereby
simulating a lossy network. The NSIM tests are experimental and the
test results are not currently representative of typical results in a
lossy network.
