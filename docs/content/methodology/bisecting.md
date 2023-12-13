---
title: "Bisecting"
weight: 5
---

# Bisecting

Updated for CSIT git commit hash: d615aa43f36bf4335d7883420ebd8b2f7b8a3b9a.

When trending (or report release comparison) detects a performance anomaly,
it is possible to narrow down its cause in VPP repository.
This document explains how.

## Naming

Bisect is a binary search, it relies on "git bisect" command.
At the start, two commits need to be marked. One as "old", the other as "new".
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

## Bisect jobs

VPP is the only project currently using such jobs.
They are not started automatically, they must be triggered on demand.
They allow full tag expressions, but only some result types are supported.
Currently it is all perf types in UTI model:
"mrr", "ndrpdr", "soak", "reconf" and "hoststack".
Device tests (pass/fail) are not supported yet.
If a test fails, a low fake value is used instead of results,
so the bisect procedure can also find breakages (and fixes).

The trigger word contains the intended testbed type,
e.g. "bisecttest-2n-spr".

The next word needs to be a commit hash of the intended earliest VPP build.
The latest VPP build is the change the comment is added to.

If additional arguments are added to the Gerrit trigger, they are treated
as Robot tag expressions to select tests to run.

## Basic operation

The job builds VPP .deb packages for both the earliest and latest VPP commit,
then runs the selected tests on both (using CSIT code at HEAD
of the newest CSIT oper branch, or CSIT_REF if started manually on Jenkins).
In archived logs, the results of earliest VPP build are in "earliest" directory,
and results of latest VPP build are in "latest" directory.

Then the job follows VPP mid commits selected by "git bisect".
They are built and tested, results appear in "middle" directory,
numbered in order "git bisect" has chosen them.

When classifying the newly measured performance of the current mid commit,
the three sets of current results (early, mid, late) are grouped
in three ways. The mid is either added to early group, or to late group,
or kept as a separate group.
The same Minimal Description Length algorithm as in trend analysis
is used to select the grouping with smallest information content.
If the grouping with the mid results added to the early group
is the smallest, the mid commit becomes the new early.
If the grouping with the mid results added to the late group
is the smallest, the mid commit becomes the new late.
If the grouping with the mid results separate is the smallest,
the mid commit becomes that boundary which keeps larger difference
of average performances (relative to the larger value, pairwise).

## Temporary specifics

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

As test failures are tolerated, the bisect job usually succeeds
(unless there is a fatal infrastructure issue).
Human investigation is needed to confirm the identified commit is the real cause.
For example, if the cause is in CSIT and all builds lead to failed tests,
the bisect will converge to the earliest commit, which is probably innocent.

## Console output

After each mid build is tested, the tree sets of relevant results
are visible in the console output, the prefixes are (without quotes)
"Read csit_early: "
"Read csit_late: "
"Read csit_mid: ".
Each prefix is followed by a list of float values extracted from the tests,
the meaning and units depend on tests chosen
(but do not matter as the same set of tests is executed for each build).
There are also lines starting with "Stats: AvgStdevStats"
which give and overview for average and standard deviation.
Then, the information content in bits for the three possible groupings is listed,
followed by the decision, bits saving and new performance difference.
After the last iteration, the commit message of the offending commit is listed.
