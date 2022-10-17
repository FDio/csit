.. _latency_methodology:

Packet Latency
^^^^^^^^^^^^^^

TRex Traffic Generator (TG) is used for measuring one-way latency in
2-Node and 3-Node physical testbed topologies. TRex integrates `High
Dynamic Range Histogram (HDRH) <http://hdrhistogram.org/>`_
functionality and reports per packet latency distribution for latency
streams sent in parallel to the main load packet streams.

Following methodology is used:

- Only NDRPDR test type measures latency and only after NDR and PDR
  values are determined. Other test types do not involve latency
  streams.
- Latency is measured at different background load packet rates:

  - No-Load: latency streams only.
  - Low-Load: at 10% PDR.
  - Mid-Load: at 50% PDR.
  - High-Load: at 90% PDR.

- Latency is measured for all tested packet sizes except IMIX due to
  TRex TG restriction.
- TG sends dedicated latency streams, one per direction, each at the
  rate of 9 kpps at the prescribed packet size; these are sent in
  addition to the main load streams.
- TG reports Min/Avg/Max and HDRH latency values distribution per stream
  direction, hence two sets of latency values are reported per test case
  (marked as E-W and W-E).
- +/- 1 usec is the measurement accuracy of TRex TG and the data in HDRH
  latency values distribution is rounded to microseconds.
- TRex TG introduces a (background) always-on Tx + Rx latency bias of 4
  usec on average per direction resulting from TRex software writing and
  reading packet timestamps on CPU cores. Quoted values are based on TG
  back-to-back latency measurements.
- Latency graphs are not smoothed, each latency value has its own
  horizontal line across corresponding packet percentiles.
- Percentiles are shown on X-axis using a logarithmic scale, so the
  maximal latency value (ending at 100% percentile) would be in
  infinity. The graphs are cut at 99.9999% (hover information still
  lists 100%).