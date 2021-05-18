Result Instability
^^^^^^^^^^^^^^^^^^

Anomaly detection relies on the assumption that VPP builds of equal performance
will produce very similar MRR values. This is not always true in practice,
as can be easily verified by triggering two runs for the same VPP build.

Here is a list of known contributions to results not being as stabe as we would like.

CSIT "environment"
------------------

This includes various changes in CSIT code that end up affecting the MRR values,
ranging from obvious ones (editing the test wihtout changing its name)
to less obvious ones (changing TRex version, which ideally would not change the result,
but sometimes it does, mainly due to duration stretching mentioned below).

This creates false anomalies in the affected tests, which are not reproducible
with per-patch or bisect (as those use the same CSIT code).
Most of the time, multiple (otherwise unrelated) tests are affected,
making it easier to identify this cause.

Testbed differences
-------------------

Usually a hardware degradation causes test failures, not performance differences,
but occasionally there is a performance difference strictly correlated
to which testbed (from the set of presumably identical testbeds) runs the test.
We have seen this issue most frequently related to various firmware and OS kernel versions.
As trending tends to use the same testbed (depending on trigger timing),
this instability leads to false anomalies, but human can identify the cause
just by hovering and seeing the correlation with testbed ID.
Once the faulty testbed is identified, it should be removed from the pool
until repaired / re-installed to conform with others.

Duration stretching
-------------------

When traffic generator takes longer to send the required amount of traffic,
we call it a duration stretching (as in, the trial finishes, but in duration
stretched from the duration target given).
If a duration stretching is constant (e.g. each 1.0 second trial takes
1.02 seconds fo finish), the resulting MRR value is an over-estimate of the true value
(as VPP had more CPU cycles to process the traffic), but anomaly detection
still picks up performance changes caused by VPP code.

Unfortunalely, duration stretching is usually not constant (at least not constant enough),
leading to increased stdev of the results. Usually, this just means
the anomaly detection algorithm gets less significant signal,
so it takes more runs to identify an anomaly.
In worst case, there happen multiple runs with high/low amount of stretching,
leading to false anomaly, not repeatable, not related to CSIT not testbeds,
and overall hard to distinguish from other sources of result instability.

Depending on CSIT code used, the amount of duration stretching can be visible
in trial output (as approximated_duration). Currently, we use start+sleep+stop method,
which prevents TG to take too long for one trial, so large duration stretching
manifests as "unsent packets" instead of large duration.
But (for various reasons) the number of packets to send is not known exactly,
and (for other various reasons) the sleep and stop parts are not timed precisely enough,
so small duration stretching is still visible only as increased approximated_duration.

It is possible that the duration stretching depends on MRR value,
but we do not have enough data to decide.
The start+sleep+stop method was implemented mainly because of TRex behavior in AWS
(and on new processors/NICs we have not calibrated TRex for yet).

Time precision
--------------

To compute the MRR value, we need to divide the number of packets received by TG
by the true duration of the traffic. TRex does a good job counting packets,
but the time measurement is currently much less precise.

Before 2106 release, we did a series of experiments to investigate different options.
Using the target duration for MRR computation give worst results (highest stdev
between runs of the same build, which is bad for anomaly detection).
The current hypothesis is that there is small, non-constant amount of duration stretching,
and using approximated_duration partially compensates for it.
Another idea we tested is to use busy wait instead of sleep.
Impact of this change was not visible (other sources of result instability were too high
to see the true difference), so we decided to keep the current logic of sleep
(and stop time being part of approximate_duration).

VPP performance fluctuations
----------------------------

Using trex.log, we confirmed some test cases (e.g. ethip4-ip4base) do not have constant performance.
That means even in one long trial, the TRex Rx rate was fluctuating way more than Tx rate.
Some of the fluctuations may be due to TRex time precision and possibly small non-constant
duration stretching, but the fact Rx flustuations way ~10 times larger proves
most of the fluctuations are caused by VPP.

Even with fluctuating performance, we hoped if we use single long trial, it would reduce
the effect of time precision (and maybe also duration stretching). But once again,
series of experiments we did before 2106 release proved that using 10 1-second trials
(and using the average as the final value for anomaly detection) gives more stable results
that using 1 trial of 10 seconds. There is some possibility of that being just bad luck.
But the more probable explanation is that the "pauses" between trials cause VPP
to change its performance, thus making the averaged value more stable.
Once again, we decided to keep the previous logic of 10 trials, 1 second each.

Implications for per-patch job
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

For many important test cases, VPP performance fluctuations are
the dominant cause of result instability.
What is worse, the performance distribution is not Gaussian, it has "heavier tails",
meaning outliers are bigger and more probable, so even inreasing the number of trials
does not ensure the higher average is seen for the actually better build.

It seems tests where VPP is throttled by CPU arithmetic work (e.g. ipsec)
have more stable performance than tests throttled by caching, IO and other
less predictabe factors.

Also, testbeds with low overall performance (Denverton) show more stable results
than testbeds with high performance (Cascade Lake). That also goes for drivers,
the higher overall performance the larger stdev (even relative to the averge).
Unfortunately, we are more insterested in the faster architectures and drivers.

For per-patch job, the solution is to run with high number of trials
(in effect forcing the detection to declare progression or regression,
"no anomaly" is improbable result) and use human intuition to decide whether
the reported anomaly is real (and use more runs if the intuition does not give clear answer).

For MRR jobs, where we are restricted by the testbed time available,
no easy (nor only somewhat hard) improvement is available.
