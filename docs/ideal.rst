..
   Copyright (c) 2019 Cisco and/or its affiliates.
   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at:
..
       http://www.apache.org/licenses/LICENSE-2.0
..
   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.


Motivation
^^^^^^^^^^

Continuous Integration relies on testing the whole product,
if possible upon every change.

Some products are integrated from several parts,
and some of those part may be considered a standalone product of smaller scope.
But even for the smaller scope products, it is still useful
to run tests of the larger product, in order to find bugs and regressions
in situations not as easily testable within the smaller scope.

Usually, the smaller scope product is either explicitly a library,
or a provider of a specific service. In general, such "upstream dependencies"
should be integrated with the rest of the larger product loosely.
That means the development cycle of the "upstream" proceeds on its own,
each release has clearly defined APIs and other contracts,
and the larger product chooses an upstream version to integrate with.

But sometimes, especially for young dynamic (aka immature) products,
the upstream dependency changes APIs rapidly, while still wishing to
enjoy the benefits of testing within the larger product.
In these cases, the narrower product is said to be tightly integrated
with the broader product, as the broader product consumes
"snapshot builds" of the narrower product, without waiting for releases.

VPP is the narrower product in this scenario.
VPP+CSIT is the broader product useful for testing.

Ideally, the broader product would sit in a single git repository,
so a change in VPP API and appropriate changes to CSIT tests
are done in a single commit, preventing any API misalignment.

It is still possible to have a single git repository divided administrativaly
into several "components" (defined as a set of directories)
maintained by a specific group of committers,
and before giving +2, the committer would verify
whether each affected maintainer group has given +1.

But as VPP and CSIT are separate fd.io projects, git repositories
have to be separated, so merges cannot be coordinated in an easy way.

This document describes a process to restore as much single-repo behavior
as reasonably possible.

TODO: Name the exact process described here, so we do not need to use
time pointers (current process, previous process, future process).
Distributed Transactions sounds good, but is the goal of several processes.
Ideal Process is too ambitious.

Guiding principles
~~~~~~~~~~~~~~~~~~

Upstream should not depend on downstream.

That means VPP should not depend on CSIT, and neither of those two
should depend in ci-management (which can depend on both).

There will be human errors, so key decisions should be easy to do.
That means merge happens only on Verified+1. Thinking on what to do
with Verified-1 can be complicated, as long as Verified+1
can be reasonably only achieved when it is safe to merge (again).

Simplifications
^^^^^^^^^^^^^^^

Currently, CSIT uses "oper" branches. Each CSIT branch also marks a specific
VPP build as "stable". VPP has a long term support stable branch,
and a master branch.

The following description assumes we care only about (current HEAD of)
VPP master branch and CSIT master branch, plus minimal set
of open Gerrit changes needed.

Contrary to the current state, vpp-csit "devicetest" verify job
is assumed to be voting on VPP changes.

Main ideas
^^^^^^^^^^

Git server is performing a transaction on merge. It moves HEAD,
but no user can see "partial merge" with some directiories updated
and some not. When working with two independent git servers,
we need to emulate a distributed transaction.

When there are different CSIT codebases supporting different VPP builds,
the VPP build should be the selector of which tests to use,
regardless of whether the build (or the test) comes from merged code or not.

Big changes that require different CSIT code should be visible
as changes in API CRC values.

Naming
^^^^^^

It is easier to define the process after chosing shorter names
for notions that need long definition.

Note: Everytime a single job is mentioned,
in practice it can be a set of jobs covering parts of functionality.
A "run" of the set of jobs passes only if each job within the set
has been run (again) and passed.

Jobs:

+ A *vpp verify* job: Any job run automatically, and voting on open VPP changes.
  Some verify jobs compile and package VPP for target operating system
  and processor architecture, the packages are archived.
  (Currently on Jenkins. Can we move to packagecloud?)

+ The *api-crc* job: Quick verify job for VPP changes, that accesses
  CSIT repository to figure out whether merging the change is safe
  from CSIT point of view. -1 means CSIT is not ready.
  +1 means CSIT looks to be ready for the new  CRC values,
  but there still may be failures on real tests.

+ A *trending* job: Any job that is started by timer and performs testing.
  It checkouts CSIT master HEAD, downloads the most recent
  completely uploaded VPP package, looks at CRC values, conditionally
  checkouts a different commit (e.g. unmerged CSIT change,
  including patch set number) and unconditionally runs the tests.

+ A *vpp-csit* job: Slower verify job for VPP changes, that accesses CSIT
  repository and runs tests from the correct CSIT commit (chosen as in trending)
  against the VPP (built from the VPP patch under review).
  -1 means there were test failures. +1 means no test failures, meaning
  there was no API change, or it was backward compatible.

+ A *csit-vpp* job: Verify job for open CSIT changes. Downloads the most recent
  completely uploaded VPP package to run selection of tests
  (from the CSIT patch under review).
  +1 means all tests have passed, so it is safe to merge the patch under review.

+ A *patch-on-patch* job: Manually triggered non-voting job for open CSIT changes.
  Uses a link to artifacts created by a vpp verify job,
  or compiles and packages from VPP source. Then runs the same tests
  as csit-vpp job. This job is used to prove the CSIT patch under review
  is supporting the linked VPP code.

Changes:

+ The *api change*: The name for Gerrit Change for VPP repository
  that does not pass vpp-csit verify right away, and needs this whole process.

+ The *support change*: The name for Gerrit Change on CSIT repository
  that only supports tests and CRC values for VPP with the api change
  (no redirects, trending jobs would not checkout anything else on this).

  Final patch of the support change should be a child of the final patch
  of the preparation change (see bellow).
  TODO: Do we really need the last sentence?
  It makes the process more complicated.

+ The *preparation change*: The name for Gerrit Change on CSIT repository
  that does not change the test code, but adds another CRC collection,
  which redirects to the support change. Merging this makes vpp-csit and trending
  jobs work regardless whether the api change has been merged.

Proposed process
^^^^^^^^^^^^^^^^

01. Human action: A VPP contributor creates (next patch for) the api change.

02. Automatic action: VPP verify jobs are triggered, they run and show results.

03. Human action: If a verify job (or a VPP reviewer) points
    at internal error of the patch (for example not rebased recently enough),
    jump to 01.

04. Human action: If all verify jobs pass, this process is not needed,
    VPP committer can merge. End.

05. Human action: If only api-crc or vpp-csit jobs have failed, notify CSIT.
    (Slack? csit-dev? Jira?)

06. Human action: A CSIT contributor creates (next patch for) the support change.

07. Automatic action: Csit-vpp job starts, ends with probable -1.

08. Human action: A CSIT committer reviews the patch, pausing this process
    if another API change process is in progress.

09. Human action: If the review is negative (for example if it is not clear
    which patch of the api change is this supporting), jump to 06.

10. Human action: A CSIT committer triggers patch-on-patch on the support change
    with the corresponding VPP build linked.

11. Automatic action: Patch-on-patch passes or fails.

12. Human action: CSIT revewers look at the failure details
    and suggest improvements. Can jump to either 01 or 06.

13. Human action: If the patch-on-patch passed, a CSIT contributor creates
    (next patch for) the preparation change.

14. Automatic action: Csit-vpp verify job starts, ends with probable +1.

15. Human action: If csit-vpp verify gave -1, review what is wrong.
    Jump to 13 or 06 (for example of the support change needs a rebase).

16. Human action: A CSIT committer merges the preparation change.

17. Human action: A CSIT contributor rebases the support change
    so it becomes a direct child of the preparation change.
    This involves manually resolving the merge conflict in the list
    of supported CRC collections.

18. Another round of 07, 09, 17 cycle to make sure
    the rebase did not break anything. May jump to 13 in rare cases.

19. Human action: The CSIT committer types "recheck" on the api change
    (or rebases it?).

20. Automatic action: Verify jobs start, end with probable +1.

21. Human action: If a verify job ended in -1, VPP and CSIT reviewers
    examine what went wrong. Can jump to 01, 06 or even 13 (the last one should
    never happen, but you never know).

22. Human action: VPP committer merges the api change.

23. Human action: Everybody waits patiently until the VPP code
    that includes the api change is completely uploaded.

24. Human action: Trigger recheck on the support change.

25. Automatic action: Csit-vpp verify job starts, ends with probable +1.

26. Human action: If csit-vpp verify gave -1, review what is wrong.
    Not clear where to jump to, as this should never happen.

27. Human action: CSIT committer merges the support change.

28. Human action: Other CSIT contributors see (after rebase) there is
    once again just a single CRC collection supported,
    so they are free to start working on 06 for another api change.

Caveats
^^^^^^^

Checkout-by-CRC logic
~~~~~~~~~~~~~~~~~~~~~

We do not have that available, yet.

Several approaches are possible, currently I prefer this one:

Extract .api.json files and parse them.
Basically do the same logic as api-crc does, but look at the name
of the collection that matches the CRC values.
If none matches, attempt to run with the currently checked-out CSIT code.
If the one that matches points to refs/changes/{something}, checkout that.
Depending on which part of bash script is running things at the checkout,
either continue without CRC parsing, or restart with a flag
to skip CRC parsing.

Naginator
~~~~~~~~~

It retries failed jobs (only), thus confusing Gerrit on what jobs
participate in the voting. It is assumen human committers
look at Gerrit comments, and recheck if they see a false Verified+1.

Compatible API changes
~~~~~~~~~~~~~~~~~~~~~~

If vpp-csit verify job passes on an api change, it can mean no changes
to CSIT tests are needed, but it may mean vpp-csit does not have
good enough coverage. In either way, the process continues as stated,
only the step 06 does not need more than new CRC values
and troper commit message.

Behavior changes without CRC effect
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This can be bad. The process relies on trending jobs to see a difference
on a CRC value.

A possible workaround is to include a bogus message definition,
to be altered when this happens.

Head of line blocking
~~~~~~~~~~~~~~~~~~~~~

The process explicitly prohibits two (or more) different API changes
to be processed concurrently. The process has to finish for one api change
before it can start (from step 06 on) for another api change.

This can slow down API development, but it is needed,
as there is no safe enough process for handling multiple api changes at once.

Note that even single git repo projects with Gerrit can cause a breakage,
when two merges (of sibling changes) create conditions
not covered by any verify job. In single repo projects one committer
can fix the consequences. When committers from two projects need to wait
on each other, the breakage (e.g. verify jobs giving -1 on correct changes)
can be too long.

Incomplete merges
~~~~~~~~~~~~~~~~~

We do not have a good solution for this.
Uploads to packagecloud happen per-package, there is no API for transactions
consistin of multiple packages (yet?).
Package cloud is a cloud of independent packages, not of package sets.

The current workaround is to use stable_vpp marker in CSIT repository.
Csit verify jobs use this build (instead of
the latest completely uploaded build), but trending jobs do not.

A job which download while uploads are not complete usually fail,
so the process is usable if humans are willing to (examine and) recheck.

TODO
^^^^

There is a lot of theory for distributed transactions.
Is this process following a known algorithm?
Should we search for an algorithm fitting our objectives?
