Throughput over QUIC/UDP/IP with vpp_echo
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

`vpp_echo performance testing tool <https://wiki.fd.io/view/VPP/HostStack#External_Echo_Server.2FClient_.28vpp_echo.29>`_
is a bespoke performance test application which utilizes the 'native
HostStack APIs' to verify performance and correct handling of
connection/stream events with uni-directional and bi-directional
streams of data.

Because iperf3 does not support the QUIC transport protocol, vpp_echo
is used for measuring the maximum attainable bandwidth of the VPP Host
Stack connection utilzing the QUIC transport protocol across two
instances of VPP running on separate DUT nodes.  The QUIC transport
protocol supports multiple streams per connection and test cases
utilize different combinations of QUIC connections and number of
streams per connection.

The test configuration is as follows:

::

            DUT1               Network                DUT2
    [ vpp_echo-client -> VPP1 ]=======[ VPP2 -> vpp_echo-server]
                          N-streams/connection

where,

 1. vpp_echo server attaches to VPP2 and LISTENs on VPP2:TCP port 1234.
 2. vpp_echo client creates one or more connections to VPP1 and opens
    one or more stream per connection to VPP2:TCP port 1234.
 3. vpp_echo client transmits a uni-directional stream as fast as the
    VPP Host Stack allows to the vpp_echo server for the test duration.
 4. At the end of the test the vpp_echo client emits the goodput
    measurements for all streams and the sum of all streams.

 Test cases include

 1. 1 QUIC Connection with 1 Stream
 2. 1 QUIC connection with 10 Streams
 3. 10 QUIC connetions with 1 Stream
 4. 10 QUIC connections with 10 Streams

 with stream sizes to provide reasonable test durations. The VPP Host
 Stack QUIC transport is configured to utilize the picotls encryption
 library. In the future, tests utilizing addtional encryption
 algorithms will be added.
