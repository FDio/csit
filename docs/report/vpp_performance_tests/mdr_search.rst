MDR Search
==========

Placeholder for previous sections
---------------------------------

Test effectiveness comparison
-----------------------------

Table
`````

.. table:: Search part of test duration

   ==============================  =============  ==============
   Duration +- stdev (in seconds)  IP4 per test   Vhost per test
   ==============================  =============  ==============
   MDR with 30s final duration     131.2 +- 30.2  220.4 +- 89.2
   NDR+PDR binary, projected 30s   557.6 +- 0.2   679.3 +- 0.5
   NDR+PDR binary, 10s duration    197.6 +- 0.2   239.3 +- 0.5
   ==============================  =============  ==============


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
includes a single 5-second warmup (per each drop rate), which is
critical for search result correctness, so it is included in the search duration.
The trial measurements in the pre-existing binary search are 10 second long,
and the search stops if the absolute difference of target transmit rates
decreased below a threshold parameter.

In the newly added tests which use MDR search,
there is no separate warmup (as initial measurements
are not critical to the final result),
and the final trial duration is 30 seconds.
The search stops when *relative* difference in target transmit rates
decreases below a given goal (for both intervals).
The resulting interval width is smaller than in the binary search tests.

The "projected" durations are computed from old test runs,
and correspond to binary search with 30 second trial durations,
assuming the measured drop fractions would remain the same.
Basically, 20 seconds were added for every trial measurement.

The pre-existing suites contain, 9 combinations of packet size and thread count,
but some of them show zero packet loss even at maximum rate.
The pre-existing tests exit early in this case,
so for the sake of fair comparison, (and to avoid averaging over different thread counts)
we have chosen only one test case (64B packets processed by 1 thread).
The table is based on result of 4 runs.
