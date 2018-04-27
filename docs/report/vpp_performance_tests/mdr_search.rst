MDR Search
==========

Placeholder for previous sections
---------------------------------

Test effectiveness comparison
-----------------------------

Table
`````

.. table:: Search part of test duration

   ==============================  ============  ==============
   Duration +- stdev (in seconds)  IP4 per test  Vhost per test
   ==============================  ============  ==============
   MDR with 30s final duration     92.6 +- 3.3   216.0 +- 5.7
   NDR+PDR binary, projected 30s   232.6 +- 1.1  476.4 +- 0.2
   NDR+PDR binary, 10s duration    86.5 +- 0.1   169.7 +- 0.2
   ==============================  ============  ==============


Implementation details
``````````````````````

CSIT release 1804 contains two suites which use MDR search.
The suite 10Ge2P1X520-Ethip4-Ip4Base-Ndrpdr has been chosen,
as it represents a device setup with very consistent NDR/PDR results.
The suite 10Ge2P1X520-Eth-L2Bdbasemaclrn-Eth-2Vhostvr1024-1Vm-Ndrpdr
has been chosen to represent a setup with quite inconsistent NDR/PDR results.
Here "inconsistent" means the values found differ between runs,
even though the setup and the test are exactly the same.
The effectiveness of the two newly added test suites is compared
to the pre-existing suites based on NDP and PDR being found by
independent binary searches.

The search part of the binary search tests,
includes a single 5 second warmup (per each drop rate), which is
critical for search result correctness, so it is included in the search duration.
The trial measurements in the pre-existing binary search are 10 second long,
and the search stops if the absolute difference of target transmit rates
decreased below a threshold parameter.
Alternatively, the binary search can also stop after a single measurement
at the line rate, if the measured drop fraction is low.
This early stop has been encountered fairly frequently
in the runs used for the table.

In the newly added tests which use MDR search,
there is no separate warmup (as initial measurements
are not critical to the final result),
and the final trial duration is 30 seconds.
The search stops when *relative* difference in target transmit rates
decreases below a given goal (for both intervals).
There is no early stop for low drop fractions at line rate,
but there is an early stop (at each phase) for large drop fraction at minimum rate
(although this was never activated in the runs used for the table).
Also, the search is aborted if it takes too long, 10 minutes currently
(this has been encountered once).
The general resulting interval width is smaller than in the binary search tests.

The "projected" durations are computed from old test runs,
and correspond to binary search with 30 second trial durations,
assuming the measured drop fractions would remain the same.
Basically, 20 seconds were added for every trial measurement.

For comparison, 9 combinations of frame size and thread count
were taken into account, their search durations added and divided by 9
to get the "per test" durations.
Note that this "per test" duration contains two separate binary searches
when MDR is not used. As NDR and PDR search durations are basically the same,
it is safe to just divide the listed durations by two
to get single binary search durations.

The table is based on result of 4 runs.
