Bisecting
---------

TODO: Rename "parent" "new" "current" to "old" "middle" "new" or similar.

Updated for CSIT git commit hash: 951d90b4e70db4573de06cda25376b65758b9151.

When trending (or report release comparison) detects a performance anomaly,
it is possible to narrow down its cause in VPP repository.
This document explains how.

Bisect jobs
```````````

VPP is the only project currently using such jobs.
They are not started automatically, must be triggered on demand.
They allow full tag expressions, but only some test types are supported.
Currently it is MRR type and NDRPDR (where PDR value is used).

The trigger word contains the intended testbed type,
e.g. "bisecttest-2n-clx".

The next word needs to be a commit hash of the intended "old" VPP build.
The other boundary, "new" VPP build is the change the comment is added to.

If additional arguments are added to the Gerrit trigger, they are treated
as Robot tag expressions to select tests to run. For more details
on existing tags, see `tag documentation rst file`_.

Basic operation
```````````````

The job builds VPP .deb packages for both the "old" and "new" VPP commit.
And runs the selected tests on both (using CSIT code at HEAD
of the newest CSIT oper branch).
In archived logs, the results of "old" VPP build are in "parent" directory,
and results of "new" VPP build are in "current" directory.
(Just a consequence of reusing the same code as in per-patch performnace job.)

Then the jobs follows VPP commits selected by "git bisect".
They are built and tested, results also appear in "parent" direcotry, numbered.

The "middle" build is called "new" when comparing to current boundaries,
called "parent" and "current".
When deciding whether to "git bisect old" or "git bisect new",
the three sets of results are grouped in three ways.
The middle is either added to old, or to new, or kept separate.
The same Minimal Description Length algorithm as in trending
is used to select the grouping with smallest information content.
If the grouping with middle and old is smallest, middle becomes new old.
If the grouping with middle and new is smallest, middle becomes new new.
If the grouping with middle separate is smallest, middle becomes that boundary
which keeps larger performance difference.


Temporary specifics
```````````````````

The Minimal Description Length analysis is performed by
jumpavg-0.1.3 available on PyPI.

In hopes of strengthening of signal (code performance) compared to noise
(all other factors influencing the measured values), several workarounds
are applied.

In contrast to trending, trial duration is set to 10 seconds,
and only 5 samples are measured for each build.
Both parameters are set in ci-management.

This decreases sensitivity to regressions, but also decreases
probability of false positives.

Console output
``````````````

The following information as visible towards the end of Jenkins console output,
repeated for each analyzed test.

The original 5 values are visible in order they were measured.
The 5 values after processing are also visible in output,
this time sorted by value (so people can see minimum and maximum).

The next output is difference of averages. It is the current average
minus the parent average, expressed as percentage of the parent average.

The next three outputs contain the jumpavg representation
of the two groups and a combined group.
Here, "bits" is the description length; for "current" sequence
it includes effect from "parent" average value
(jumpavg-0.1.3 penalizes sequences with too close averages).

Next, a sentence describing which grouping description is shorter,
by how much bits.
Finally, the test result classification is visible.

The algorithm does not track test case names,
so test cases are indexed (from 0).
