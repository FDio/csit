MDR Search
==========

Placeholder for previous sections
---------------------------------

Test effectiveness comparison
-----------------------------

Implementation details
``````````````````````

CSIT release 1804 contains two suites which use MDR search.
The suite 10Ge2P1X520-Ethip4-Ip4Base-Ndrpdr has been chosen
as it represents a device setup with very consistent NDR/PDR results.
The suite 10Ge2P1X520-Eth-L2Bdbasemaclrn-Eth-2Vhostvr1024-1Vm-Ndrpdr
has been chosen to represent a setup with very inconsistent NDR/PDR results.
Each new suite contains 12 test cases (4 traffic types * 3 thread counts).
The corresponding old suites only contain 9 test cases for NDR and 9 for PDR
(1 traffic type is missing, either 900B or IMIX).

The previous suites consist of three stages.
The first stage is the test setup, configuring Devices Under Tests (DUTs).
The second stage is the binary search itself,
which includes a single 5 second warmup, as all trial measurements are critical.
The trial measurements in the binary search are 10 second long,
and the search stops if the absolute difference of target transmit rates
decreased below a threshold parameter.
Alternatively, the binary search can also stop after a single measurement
at line rate, if the measured drop fraction is small enough.
The third stage contains additional measurements
which do not affect the drop rates found, but they are gathering data
useful in debugging, such as various telemetry data
and latency results at smaller transmit rates.
All of the additional measurements are done at 10 second duration.

The new suites also consist of three stages.
The first, setup phase, is identical to the old tests.
The second stage performs the MDR search itself.
There is no warmup (as initial measurements are not critical for the result),
and the final trial duration is 30 seconds.
The search stops when *relative* difference in target transmit rates
decreases below a given goal (for both intervals).
There is no early stop for low drop fractions at line rate,
but there is an early stop (at each phase) for large drop fraction at minimum rate.
Also, the search is aborted if it takes too long (10 minutes currently).
The general resulting interval width is smaller than in the old tests.
The third stage contains additional measurements similar to the old tests.
One difference is that there are no measurements specifically for latency data,
as the MDR currently reports latency in its results.
The other difference is that the telemetry measurements
are performed at 5 second duration.

You see that there are multiple differences,
resulting from the desire to balance time savings
with improved result quality.
This makes it harder to compare the two tests
in an "apples to apples" way.

An obvious fairness improvement is to compare times per "test case",
which is per single new test case or per pair of old test cases (one for NDR, one for PDR).
One way of improving fairness of is to compare only the overal duration
of the second stage (binary/MDR search), as the duration of the other two phases
is not affected by the search algorithm used.
This still includes 5 second warmup in the binary search,
as that is critical to the search result validity.
Another way of improving fairness is to compute "projected" durations,
utilising the fact that difference between 10 second and 30 second trial duration
is just fixed 20 second per trial, as no overhead is affected.

Several runs were executed. It is enough data to compare average durations,
but not enough data to compare consistency of results in badly behaved est cases.

The following table sums the various average times,
ranging from unfair (but reflecting the testbed time usage) to fair
(but not related to testbed usage much).

Table
`````

.. table:: Test duration comparison

   =====================  ===============  =================  ============  ==============
   Duration (in seconds)  IP4 whole suite  Vhost whole suite  IP4 per test  Vhost per test
   =====================  ===============  =================  ============  ==============
   MDR total duration     1472             3870               123           322
   MDR search part        1069             2977               89            248
   old total duration     1744             3475               194           386
   old search part        779              1527               87            170
   projected total        3054             6235               339           693
   projected search part  2089             4287               232           476
   =====================  ===============  =================  ============  ==============
