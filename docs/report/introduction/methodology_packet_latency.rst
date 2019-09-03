Packet Latency
--------------

TRex Traffic Generator (TG) is used for measuring latency of VPP DUTs.
Reported latency values are measured using following methodology:

- Latency tests are performed at 100% of discovered NDR and PDR rates
  for each throughput test and packet size (except IMIX).
- TG sends dedicated latency streams, one per direction, each at the
  rate of 9 kpps at the prescribed packet size; these are sent in
  addition to the main load streams.
- TG reports min/avg/max latency values per stream direction, hence two
  sets of latency values are reported per test case; a future release of
  TRex is expected to report latency percentiles.
- Reported latency values are aggregated across two SUTs if the three
  node topology is used for given performance test; for per-SUT latency,
  reported values should be divided by two.
- 1usec is the measurement accuracy advertised by TRex TG for the setup
  used in FD.io labs used by CSIT project.
- TRex setup introduces an always-on error of about 2*2usec per latency
  flow. Additonal Tx/Rx interface latency is introduced by TRex SW writing and
  reading packet timestamps on CPU cores without HW acceleration on NICs
  closer to the interface line.
