MDR Search
==========

Placeholder for previous sections
---------------------------------

Test effectiveness comparison
-----------------------------

Introduction
````````````

CSIT release 1804 contains two test suites that use the new MDR search
to enable comparison against existing CSIT NDR and PDR binary searches.
The suites got chosen based on the level of consistency of their
historical NDR/PDR results:

#) 10Ge2P1X520-Ethip4-Ip4Base-Ndrpdr - yielding very consistent binary
   search results.
#) 10Ge2P1X520-Eth-L2Bdbasemaclrn-Eth-2Vhostvr1024-1Vm-Ndrpdr - yielding
   somewhat inconsistent results.

Here "inconsistent" means the values found differ between runs,
even though the setup and the test are exactly the same.

The search part of CSIT binary search tests requires a single 5-second warmup
and each trial measurement is set to 10 seconds.

New tests with MDR search do not have any warmup, as initial measurements
are not critical to the final result. The final trial duration is set 30 seconds.
The final MDR search resolution a.k.a. interval width is better/narrower
than in CSIT binary search tests.

The "projected" durations are computed from CSIT NDR/PDR test runs,
and correspond to binary search with 30 second trial durations.
Basically, 20 seconds were added for every trial measurement.

The table below compares overall test duration between the search tests.
For simplicity only data for single thread 64B packet tests is listed,
as it takes the longest in all cases.

The table is based on result of 4 runs.

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
