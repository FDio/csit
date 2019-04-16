Per-patch performance tests
---------------------------

Updated for CSIT git commit id: 661035ac4ce6e51649f302fe2b7a8218257c0587.

A methodology similar to trending analysis is used for comparing performance
before a DUT code change is merged. This can act as a verify job to disallow
changes which would decrease performance without a good reason.

Existing jobs
`````````````

VPP is the only project currently using such jobs.
They are not started automatically, must be triggered on demand.
They allow full tag expressions, but some tags are enforced (such as MRR).

Only the three types of tesbed based on Xeon processors have jobs created.
Their Gerrit triggers words are "perftest-3n-hsw", "perftest-3n-skx"
and "perftest-2n-skx".

If additional arguments are added to the Gerrit trigger, they are treated
as Robot tag expressions to select tests to run. For more details
on existing tags, see `tag documentation rst file`_.

Basic operation
```````````````

The job builds VPP .deb packages for both the patch under test
(called "current") and its parent patch (called "parent").

For each test (from a set defined by tag expression),
both builds are subjected to several trial measurements (BMRR).
Measured samples are grouped to "parent" sequence,
followed by "current" sequence. The same Minimal Description Length
algorithm as in trending is used to decide whether it is one big group,
or two smaller gropus. If it is one group, a "normal" result
is declared for the test. If it is two groups, and current average
is less then parent average, the test is declared a regression.
If it is two groups and current average is larger or equal,
the test is declared a progression.

The whole job fails (giving -1) if some trial measurement failed,
or if any test was declared a regression.

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
