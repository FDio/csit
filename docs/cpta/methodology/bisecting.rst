Bisecting
---------

Updated for CSIT git commit hash: 1388907ce0f74a0e679c9992deea9566e81f9b70.

When trending (or report release comparison) detects a performance anomaly,
it is possible to narrow down its cause in VPP repository.
This document explains how.

Naming
``````

Bisect is a binary search. Git has a "git bisect" command. At the start,
two commits need to be marked. One as "old" or "good", the other as
"new" or "bad". Upon second mark, "git bisect" checks out
a commit in the middle, and waits for the user to mark it
either old/good or new/bad. This effectively replaces the previous mark
of the same type, so "new middle" is checked out, halving the search interval.

But, "good" or "bad" frequently refers to high or low performance,
and "old" and "new" frequently refers to the time order bisect chooses commits,
so in this document we use different adjectives:
Early, middle, late. Early commit and late commit are the current
boundaries of the search interval, middle commit is the next one
to test and classify.
The initial boundaries, as input parameters to the whole search process
are called the earliest commit and the latest commit.

Bisect jobs
```````````

VPP is the only project currently using such jobs.
They are not started automatically, they must be triggered on demand.
They allow full tag expressions, but only some test types are supported.
Currently it is MRR, NDRPDR (where PDR value is used), soak and functional.
The unsupported types are those related to host stack tests.

The trigger word contains the intended testbed type,
e.g. "bisecttest-2n-clx".

The next word needs to be a commit hash of the intended earliest VPP build.
The latest VPP build is the change the comment is added to.

If additional arguments are added to the Gerrit trigger, they are treated
as Robot tag expressions to select tests to run. For more details
on existing tags, see `tag documentation rst file`_.

Basic operation
```````````````

The job builds VPP .deb packages for both the earliest and latest VPP commit,
then runs the selected tests on both (using CSIT code at HEAD
of the newest CSIT oper branch, or CSIT_REF if started manually on Jenkins).
In archived logs, the results of earliest VPP build are in "earliest" directory,
and results of latest VPP build are in "latest" directory.

Then the job follows VPP middle commits selected by "git bisect".
They are built and tested, results appear in "middle" directory, numbered.

When classifying the newly measured performance of the current middle commit,
the three sets of current results (early, middle, late) are grouped
in three ways. The middle is either added to early group, or to late group,
or kept as a separate group.
The same Minimal Description Length algorithm as in `trend analysis`_
is used to select the grouping with smallest information content.
If the grouping with the middle results added to the early group
is the smallest, the middle commit becomes the new early.
If the grouping with the middle results added to the late group
is the smallest, the middle commit becomes the new late.
If the grouping with the middle results separate is the smallest,
the middle commit becomes that boundary which keeps larger difference
of average performances (relative to the larger value, pairwise).

Temporary specifics
```````````````````

The Minimal Description Length analysis is performed by
jumpavg-0.2.0 (not yet available on PyPI).

In contrast to trending, MRR trial duration is kept at 1 second,
but trial multiplicity is set to 60 samples.
Both parameters are set in ci-management.

This increases probability of false anomalies, but bisect always converges
to a commit; it is up to humans to decide if that is a real anomaly.
On upside, stdev is estimated better, making the bisection less sensitive
to randomness. Systematic errors are still possible,
but overall this choice leads to more human-like search decisions.

Console output
``````````````

FIXME.
