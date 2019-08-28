Terminology
-----------

- **Frame size**: size of an Ethernet Layer-2 frame on the wire, including
  any VLAN tags (dot1q, dot1ad) and Ethernet FCS, but excluding Ethernet
  preamble and inter-frame gap. Measured in Bytes.
- **Packet size**: same as frame size, both terms used interchangeably.
- **Inner L2 size**: for tunneled L2 frames only, size of an encapsulated
  Ethernet Layer-2 frame, preceded with tunnel header, and followed by
  tunnel trailer. Measured in Bytes.
- **Inner IP size**: for tunneled IP packets only, size of an encapsulated
  IPv4 or IPv6 packet, preceded with tunnel header, and followed by
  tunnel trailer. Measured in Bytes.
- **Device Under Test (DUT)**: In software networking, "device" denotes a
  specific piece of software tasked with packet processing. Such device
  is surrounded with other software components (such as operating system
  kernel). It is not possible to run devices without also running the
  other components, and hardware resources are shared between both. For
  purposes of testing, the whole set of hardware and software components
  is called "System Under Test" (SUT). As SUT is the part of the whole
  test setup performance of which can be measured with :rfc:`2544`, using 
  SUT instead of :rfc:`2544` DUT. Device under test
  (DUT) can be re-introduced when analyzing test results using whitebox
  techniques, but this document sticks to blackbox testing.
- **System Under Test (SUT)**: System under test (SUT) is a part of the
  whole test setup whose performance is to be benchmarked. The complete
  methodology contains other parts, whose performance is either already
  established, or not affecting the benchmarking result.
- **Bi-directional throughput tests**: involve packets/frames flowing in
  both transmit and receive directions over every tested interface of
  SUT/DUT. Packet flow metrics are measured per direction, and can be
  reported as aggregate for both directions (i.e. throughput) and/or
  separately for each measured direction (i.e. latency). In most cases
  bi-directional tests use the same (symmetric) load in both directions.
- **Uni-directional throughput tests**: involve packets/frames flowing in
  only one direction, i.e. either transmit or receive direction, over
  every tested interface of SUT/DUT. Packet flow metrics are measured
  and are reported for measured direction.
- **Packet Loss Ratio (PLR)**: ratio of packets received relative to packets
  transmitted over the test trial duration, calculated using formula:
  PLR = ( pkts_transmitted - pkts_received ) / pkts_transmitted.
  For bi-directional throughput tests aggregate PLR is calculated based
  on the aggregate number of packets transmitted and received.
- **Packet Throughput Rate**: maximum packet offered load DUT/SUT forwards
  within the specified Packet Loss Ratio (PLR). In many cases the rate
  depends on the frame size processed by DUT/SUT. Hence packet
  throughput rate MUST be quoted with specific frame size as received by
  DUT/SUT during the measurement. For bi-directional tests, packet
  throughput rate should be reported as aggregate for both directions.
  Measured in packets-per-second (pps) or frames-per-second (fps),
  equivalent metrics.
- **Bandwidth Throughput Rate**: a secondary metric calculated from packet
  throughput rate using formula: bw_rate = pkt_rate - (frame_size +
  L1_overhead) - 8, where L1_overhead for Ethernet includes preamble (8
  Bytes) and inter-frame gap (12 Bytes). For bi-directional tests,
  bandwidth throughput rate should be reported as aggregate for both
  directions. Expressed in bits-per-second (bps).
- **Non Drop Rate (NDR)**: maximum packet/bandwith throughput rate sustained
  by DUT/SUT at PLR equal zero (zero packet loss) specific to tested
  frame size(s). MUST be quoted with specific packet size as received by
  DUT/SUT during the measurement. Packet NDR measured in
  packets-per-second (or fps), bandwidth NDR expressed in
  bits-per-second (bps).
- **Partial Drop Rate (PDR)**: maximum packet/bandwith throughput rate
  sustained by DUT/SUT at PLR greater than zero (non-zero packet loss)
  specific to tested frame size(s). MUST be quoted with specific packet
  size as received by DUT/SUT during the measurement. Packet PDR
  measured in packets-per-second (or fps), bandwidth PDR expressed in
  bits-per-second (bps).
- **Maximum Receive Rate (MRR)**: packet/bandwidth rate regardless of PLR
  sustained by DUT/SUT under specified Maximum Transmit Rate (MTR)
  packet load offered by traffic generator. MUST be quoted with both
  specific packet size and MTR as received by DUT/SUT during the
  measurement. Packet MRR measured in packets-per-second (or fps),
  bandwidth MRR expressed in bits-per-second (bps).
- **Trial**: a single measurement step.
- **Trial duration**: amount of time over which packets are transmitted and
  received in a single throughput measurement step.
