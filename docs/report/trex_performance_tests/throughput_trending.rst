Throughput Trending
-------------------

CSIT provides continuous performance trending for master branch:

#. `TRex Trending Graphs <https://s3-docs.fd.io/csit/master/trending/ndrpdr_trending/trex.html>`_:
   per TRex test case throughput trend, trend compliance and summary of
   detected anomalies. We expect TRex to hit the curently used bps or pps limit,
   so no anomalies here (unless we change those limits in CSIT).

#. `TRex Latency Graphs <https://s3-docs.fd.io/csit/master/trending/ndrpdr_latency_trending/trex.html>`_:
   per TRex build NDRPDR latency measurements against the trendline.
   We have seen in past that the latency numbers can depend on TRex version,
   NIC firmware, or driver used.
