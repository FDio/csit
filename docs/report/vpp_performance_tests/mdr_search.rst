MDR Search
==========

Placeholder for previous sections
---------------------------------

Test effectiveness comparison
-----------------------------

Implementation details
``````````````````````

CSIT release 1804 contains two suites which use MDR search.
They are intended to replace the previous NDR and PDR search tests.

The previous suites consist of three stages.
The first stage is the test setup, configuring Devices Under Tests (DUTs).
The second stage is the binary search itself,
which includes a single 5 second warmup, as all trial measurements are critical.
The trial measurements in the binary search are 10 second long,
and the search stops if the absolute difference of target transmit rates
decreased below a threshold parameter.
The third stage contains additional measurements
which do not affect the drop rates found, but they are gathering data
useful in debugging, such as various telemetry data
and latency results at smaller transmit rates.
All of the additional measurements are tone at 10 second duration.

The new suites also consist of three stages.
The first, setup phase, is identical to the old tests.
The second stage performs the MDR search itself.
There is no warmup (as initial measurements are not critical for the result),
and the final trial duration is 30 seconds.
The search stops when *relative* difference in target transmit rates
decreases below a given goal (for both intervals).
The resulting interval width is smaller than in the old tests.
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

TODO: Figure out exact rows and columns, fill in the data,
gathering it if it is not available yet.
