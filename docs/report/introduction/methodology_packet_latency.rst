Packet Latency
--------------

TRex Traffic Generator (TG) is used for measuring latency across  2-Node
and 3-Node SUT server topologies. TRex integrates `A High Dynamic Range
Histogram (HDRH) <http://hdrhistogram.org/>`_ code providing per packet
latency distribution for latency streams sent in parallel to the main
load packet streams. Packet latency is measured using following
methodology:

- Latency tests are performed at following packet load levels:

  - No-Load: latency streams only.
  - Low-Load: at 10% PDR.
  - Mid-Load: at 50% PDR.
  - High-Load: at 90% PDR.
  - NDR-Load: at 100% NDR.
  - PDR-Load: at 100% PDR.

- Latency is measured for all tested packet sizes except IMIX due to
  TG restriction.
- TG sends dedicated latency streams, one per direction, each at the
  rate of 9 kpps at the prescribed packet size; these are sent in
  addition to the main load streams.
- TG reports Min/Avg/Max and HDRH latency values distribution per stream
  direction, hence two sets of latency values are reported per test
  case.
- Reported latency values are aggregate across tested topology.
- +/- 1 usec is the measurement accuracy advertised by TRex TG for the
  setup used.
- TG setup introduces an always-on Tx/Rx interface latency of about 2
  * 2 usec per direction induced by TRex SW writing and reading packet
  timestamps on CPU cores.