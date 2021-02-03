Packet Latency
--------------

TRex Traffic Generator (TG) is used for measuring one-way latency in
2-Node and 3-Node physical testbed topologies. TRex integrates `High
Dynamic Range Histogram (HDRH) <http://hdrhistogram.org/>`_
functionality providing per packet latency distribution for latency
streams sent in parallel to the main load packet streams.

Latency is measured at different background packet rate levels in
reference to discovered PDR throughput:

- No-Load: latency streams only.
- Low-Load: at 10% PDR (PDR is discovered per test case).
- Mid-Load: at 50% PDR.
- High-Load: at 90% PDR.

Additional description:

- TG sends dedicated latency streams, one per direction, each at the
  rate of 9 kpps at the prescribed packet size; these are sent in
  addition to the main load streams. (No IMIX due to TRex restriction.)
- TG reports Min/Avg/Max and HDRH latency values distribution per stream
  direction, hence two sets of latency values are reported.
- +/- 1 usec is the measurement accuracy of TRex.
- Reported latency values are aggregate across tested topology.
- TG introduces an always-on Tx + Rx latency bias of 4-5 usec per
  direction resulting from TRex software writing and reading packet
  timestamps on CPU cores. Quoted values are based on TG back-to-back
  latency measurements.
