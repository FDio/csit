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

#. 10Ge2P1X520-Ethip4-Ip4Base-Ndrpdr - yielding very consistent binary
   search results.
#. 10Ge2P1X520-Eth-L2Bdbasemaclrn-Eth-2Vhostvr1024-1Vm-Ndrpdr - yielding
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

The table is based on result of 6 runs.

Tables
``````

.. table:: Search part of test duration

   ======================  ============  =============  =============  ============  =============  =============
   Duration +- avgdev [s]  IP4, 10s      IP4, 30s       IP4, 60s       Vhost 10s     Vhost 30s      Vhost 60s
   ======================  ============  =============  =============  ============  =============  =============
   MDR (both intervals)    50.8 +- 1.2   109.0 +- 10.0  202.8 +- 11.7  80.5 +- 9.0   201.9 +- 20.6  474.9 +- 58.2
   NDR binary              98.9 +- 0.1   278.6 +- 0.1   548.8 +- 0.1   119.8 +- 0.0  339.3 +- 0.1   669.6 +- 0.2
   PDR binary              98.9 +- 0.1   278.6 +- 0.1   548.8 +- 0.1   119.7 +- 0.1  339.3 +- 0.1   669.5 +- 0.1
   NDR+PDR sum             197.8 +- 0.1  557.2 +- 0.2   1097.6 +- 0.1  239.5 +- 0.1  678.7 +- 0.1   1339.2 +- 0.1
   ======================  ============  =============  =============  ============  =============  =============

.. note:: Here "avgdev" is the estimated difference between
   the average duration computed from the limted sample
   and a true average duration as its hypothetical limit for infinite samples.
   To get the typical difference detween one sample duration
   and computed average duration, "avgdev" has to be multiplied
   by the square root of the number of samples.

.. table:: MDR duration as percentage of NDR duration

   ====================================  ===========  ===========  ===========  ===========  ===========  ===========
   Fraction +- uncertainty [%]           IP4, 10s     IP4, 30s     IP4, 60s     Vhost 10s    Vhost 30s    Vhost 60s
   ====================================  ===========  ===========  ===========  ===========  ===========  ===========
   MDR duration divided by NDR duration  51.4 +- 1.2  39.1 +- 3.6  37.0 +- 2.1  67.2 +- 7.5  59.5 +- 6.1  70.9 +- 8.7
   ====================================  ===========  ===========  ===========  ===========  ===========  ===========

Conclusions
```````````

In consistent tests, MDR is on average more than 50% faster than single NDR binary search
(even when MDR also detects PDR). One exception is 10 second final trial duration,
probably presence of 2 intermediate phases (instead of just 1) hurts.
Even in this case MDR is almost 50% faster than NDR binary search.

In inconsistent tests MDR is still somewhat faster than NDR binary search,
but it is not by 50%, and it is hard to quantify as samples have wildly
varying durations.
