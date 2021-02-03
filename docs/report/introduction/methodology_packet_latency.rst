.. _latency_methodology:

Packet Latency
--------------

TRex Traffic Generator (TG) is used for measuring latency across 2-Node
and 3-Node SUT server topologies. TRex integrates `A High Dynamic Range
Histogram (HDRH) <http://hdrhistogram.org/>`_ code providing per packet
latency distribution for latency streams sent in parallel to the main
load packet streams. Packet latency is measured using following
methodology:

- Most test types and trial types do not involve latency streams.
- Only NDRPDR test type measures latency, and only after
  NDR and PDR values are determined.
- Latency trials are performed at following packet load levels:

  - No-Load: latency streams only.
  - Low-Load: at 10% PDR.
  - Mid-Load: at 50% PDR.
  - High-Load: at 90% PDR.

- Latency is measured for all tested packet sizes except IMIX due to
  TG restriction.
- TG sends dedicated latency streams, one per direction, each at the
  rate of 9 kpps at the prescribed packet size; these are sent in
  addition to the main load streams.
- TG reports Min/Avg/Max and HDRH latency values distribution per stream
  direction, hence two sets of latency values are reported per test
  case (marked as E-W and W-E).
- +/- 1 usec is the measurement accuracy advertised by TRex TG for the
  setup used. In any case, the data in HDRH latency values distribution
  is rounded to microseconds.
- TG setup introduces an always-on Tx/Rx interface latency of about 2
  * 2 usec induced by TRex SW writing and reading packet timestamps
  on CPU cores.
- Latency graphs are not smoothed, each latency value has its own
  horizontal line across corresonding percentiles.
- Percentiles are shown on x-axis using a logarithmic scale,
  so the maximal latecy value (ending at 100% percentile) would be in infinity.
  We cut the graphs at 99.9999% (hover information still lists 100%).
