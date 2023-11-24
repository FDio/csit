Bisecting
---------

Updated for CSIT git commit hash: f89347f6f3809e79e3802bda1433bf2ddc0ee73b.

When trending (or report release comparison) detects a performance anomaly,
it is possible to narrow down its cause in VPP repository.
This document explains how.

Naming
``````

Bisect is a binary search, it relies on "git bisect" command. At the start,
two commits need to be marked. One as "old", the other as "new".
Upon second mark, "git bisect" checks out a commit in the middle,
and waits for the user to mark it either old or new.
This effectively replaces the previous mark of the same type,
so "new middle" is checked out, halving the search interval.

But, "old" and "new" frequently refers to the time order bisect chooses commits,
so in this document we use different adjectives:
Early, mid, late. Early commit and late commit are the current
boundaries of the search interval, mid commit is the next one
to test and classify.
The initial boundaries, as input parameters to the whole search process
are called the earliest commit and the latest commit.

Bisect jobs
```````````

VPP is the only project currently using such jobs.
They are not started automatically, they must be triggered on demand.
They allow full tag expressions, but only some result types are supported.
Currently it is all perf types in UTI model:
"mrr", "ndrpdr", "soak", "reconf" and "hoststack".
Device tests (pass/fail) are not supported yet.

The trigger word contains the intended testbed type,
e.g. "bisecttest-2n-spr".

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

Then the job follows VPP mid commits selected by "git bisect".
They are built and tested, results appear in "middle" directory,
numbered in order "git bisect" chosen them.

When classifying the newly measured performance of the current mid commit,
the three sets of current results (early, mid, late) are grouped
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
jumpavg-0.4.1 (available on PyPI).

In contrast to trending, MRR trial duration is kept at 1 second,
but trial multiplicity is set to 60 samples.
Both parameters are set in ci-management,
overridable when triggerring manually on Jenkins.

The 60x1s setting increases probability of false anomalies,
but bisect always converges to a commit;
it is up to humans to decide if that is a real anomaly.
On upside, stdev is estimated better, making the bisection less sensitive
to randomness. Systematic errors are still possible,
but overall this choice leads to more human-like search decisions.

Console output
``````````````

FIXME.
