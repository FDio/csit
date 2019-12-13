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

But sometimes, especially for young dynamic (a.k.a. immature) products,
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

TODO: The process should be resistant to any background VPP or CSIT committers
merging any Change that got Verified+1. Make sure it is the case,
and add to the guiding principles.

Main ideas
^^^^^^^^^^

Big changes that require different CSIT code should be visible
as changes in API CRC values.

Git server is performing a transaction on merge. It moves HEAD "at once",
so no user can see "partial merge" with some directiories updated
and some not. When working with two independent git servers,
we need to emulate this kind of transaction, distributed over two servers.

When there are different CSIT codebases supporting different VPP builds,
the VPP build should be the selector of which tests to use,
regardless of whether the build (or the test) comes from merged code or not.

As it is not convinient to store two slightly different codebases
in a single CSIT commit, some indirection is required.
This process choses to store one codebase in an (unmerged) Gerrit Change
(with patch set number specified).

Simplifications
^^^^^^^^^^^^^^^

This document talks only about VPP master branch, CSIT master branch,
and directly related constructs (see oper branches below).
Stable VPP branches and release CSIT branches are not mentioned.
as it is not expected to see API changes in those.

Naming
^^^^^^

It is easier to define the process after chosing shorter names
for notions that need long definition.

Two quality standards
---------------------

Ideally, every commit to VPP or CSIT would get enough testing before merge.
But CSIT contains so many test cases, this is not really possible.

The solution is to use a faster verify (with less coverage) for each merge,
but periodically run slower jobs to verify everything works
(with larger coverage). Then either start fixing found breakages
and regressions, or mark (somehow) the commit achieves higher quality standards.

The higher quality commits are very useful when working on the broader product.
Development of one component can use the higher quality shanphots
of the rest of the broader product. That way a new failure or regression
is most likely caused by the component being worked on
(rather than uncovered bug from another component).
Basically, the higher quality mark is a weaker form of continuous delivery,
except all the versioning and archiving part.

Ideally, the process described in this document should not depend
on technical details of the marking implementation,
but it is easier to describe the process using the naming tied
to the current way of marking.

Commits and builds
__________________

CSIT does not have any merge jobs. A merge to a branch affects any jobs
that checkouts the affected branch.

But VPP does have merge jobs. That means there is a delay between
a VPP commit is merged, and its build becoming available
(currently in packagecloud). What is worse, rapid merges to a VPP branch
may cause the merge job to skip building builds for intermediate commits,
as a merge job cannot execute two runs at the same time,
and always checkouts the current HEAD.

When this process mentions a VPP build correspnding to a particular
VPP commit, usually a build of later VPP commit is allowed to be used instead.

CSIT oper branch
________________

Currently, CSIT uses "oper" branches. The HEAD of latest oper branch
is the mark of the most recent higher quality CSIT commit.
This HEAD moves in two different ways:

Over the weekend, weekly jobs are run (using CSIT master HEAD).
When examined, not showing any unexpected failures nor regressions,
a new oper branch is created.

When a critical fix is merged to CSIT master branch,
it is cherry-picked to the latest oper branch.
Also CSIT commits related to VPP API changes are cherry-picked.

The second way can introduce cause a lower quality commit
to be marked as higher quality, but currently it is considered
to be worth the risk.

VPP stable version
__________________

Any CSIT commit contains a marker pointing to the snapshot build version
of a recent VPP build. The VPP version is called "stable VPP version".
Not to be confused with stable VPP branches.

When the CSIT commit in question is the HEAD of the latest oper branch,
the stable VPP version points to the latest VPP commit considered
to be of higher quality. When stable VPP version is bumped
in the CSIT master branch, the bump should be cherry-picked
to the latest CSIT oper branch, so it is not necessary to specify
whether the version comes from an oper branch.

There are periodic jobs running larger coverage tests on builds
of the current VPP master HEAD. After examining their results,
the tested VPP version can be marked as the new stable VPP version.
This is used when the prebious build is in the risk
of becoming not available (there is limited hstory
in snapshot build archive).

But the API changes also necessarily create new stable vpp versions.
Once again, the risk of marking poor quality build is deemed worth it.

Conclusion
__________

Both markings are tracked in CSIT repository.
The API change process makes it questionable whether the quality
is still guaranteed, but for the time being CSIT is not planning
to remove the markings.

Jobs
----

Note: Everytime a single job is mentioned,
in practice it can be a set of jobs, each covering a part of functionality.
A "run" of the set of jobs passes only if each job within the set
has been run (again) and has passed.

+ A *vpp verify* job: Any job run automatically, and voting on open VPP changes.
  Some verify jobs compile and package VPP for target operating system
  and processor architecture, the packages are (currently) NOT archived.
  They should be cached somewhere in future to speed up downstream jobs,
  but currently each such downstream job has to clone and build.

+ The *api-crc* job: A very quick verify job for VPP changes, that accesses
  CSIT repository (checkouts the latest oper branch HEAD) to figure out
  whether merging the change is safe from CSIT point of view.
  Here, -1 means CSIT is not ready. +1 means CSIT looks to be ready
  for the new CRC values, but there still may be failures on real tests.

+ A *trending* job: Any job that is started by timer and performs testing.
  It checkouts CSIT latest oper branch HEAD, downloads the most recent
  completely uploaded VPP package, looks at CRC values, conditionally
  checkouts a different CSIT commit (e.g. unmerged closing change, see below,
  patch set number specified) and unconditionally runs the tests.
  CRC checks are optional, ideally only written to console log
  without otherwise affecting the test cases.
  The set of trending jobs covers multiple architectures and testcases,
  taking hours to finish. The tests consist mostly of performance tests.

+ A *vpp-csit* job: A somewhat quick verify job for VPP changes,
  that accesses CSIT repository and runs tests from the correct CSIT commit
  (chosen as in trending) against the VPP (built from
  the VPP patch under review).
  Vote -1 means there were test failures. +1 means no test failures, meaning
  the closing change (see below) addresses all API changes (within coverage).
  The set of vpp-csit jobs is aimed on API coverage, and on testing features
  not coverable by "make test" (anything requiring root), mostly device tests.

+ A *csit-vpp* job: Verify job for unmerged CSIT changes. Downloads
  the build of stable VPP version (as specified in
  the CSIT commit under review), and runs a selection of tests
  (from the CSIT commit under review).
  Vote +1 means all tests have passed, so it is safe to merge
  the patch under review.
  The set of csit-vpp jobs usually runs the same tests as vpp-csit jobs do.

+ A *patch-on-patch* job: Manually triggered non-voting job
  for unmerged CSIT changes. Compiles and packages from VPP source
  (usually of an unmerged change). Then runs the same tests as csit-vpp job.
  This job is used to prove the CSIT patch under review is supporting
  the specified VPP code. The set of jobs should include all device tests,
  but also the performance tests assumed to be affected by the open API change.

+ A *manual verification* is done by a CSIT committer, locally executing steps
  equivalent to the patch-on-patch job. This saves time and resources,
  but is not sufficient if the CSIT committer cannot see all the logs.

CRC Collections
---------------

Any commit in/for the CSIT repository contains a file (supported_crcs.yaml),
which contains either one or two collections. A collection is a mapping
that maps API message name to its CRC value.

A collection name (or comments around it) specifies which VPP build
is this collection for. An API message name is present in a collection
if and only if it is used by a test implementation
(can be in a different CSIT commit) targeted at the VPP build
(pointed out by the collection name/comment).

+ The *stable collection*: Always present, listed first.
  Has comments and name pointing to the VPP build
  this CSIT commit marks as stable.
  The test implementation in this CSIT commit is to be used for testing
  the stable VPP version builds.

+ The *open collection*: Present when there is an open API change (see below).
  Listed second, has comments pointing to the VPP Gerrit
  (including patch set number) the currently open API process is processing.
  The patch set number part can be behind the actual Gerrit state,
  as some verify job will fail if it is no longer compatible.
  The open collection has name pointing to the closing change (see below).
  The test implementation in the CSIT commit pointed by the collection name
  is to be used for testing the VPP built from the Gerrit patch pointed
  to by the comments.

Changes
-------

+ An *API change*: The name for Gerrit Change for VPP repository
  that does not pass api-crc job right away, and needs this whole process.

+ The *open API change*: The API change currently being processed.
  While many API changes can be waiting/queued/scheduled, only one can be open.

+ A *CSIT-blocked change*: The name for Gerrit Change for VPP repository
  that does not pass some vpp-csit job right away.
  This process does not specify what to do with CSIT-blocked changes
  that are not also API changes.

+ The *opening change*: The name for Gerrit Change for CSIT repository
  that does not change the test code, but adds the open CRC collection,
  which redirects to the closing change (below).
  Merging this defines which API change has become open,
  and makes trending and (rebased recently enough) vpp-csit jobs
  work regardless whether the open api change has been merged.

TODO: WIP: Continue editing below.

+ The *closing change*: The name for Gerrit Change for CSIT repository
  that only supports tests and CRC values for VPP with the open API change.
  No redirects, trending jobs would not checkout anything else on this.
  That implies the previously stable CRC collection is deleted,
  and any edits to the test implementation are done here.

+ The *mergeable closing change*: The closing change with additional
  requirements. The stable VPP build indicator is bumped to the build
  that contains the (now merged) open API change. The open CRC collection
  (added by the opening change) is renamed to the new stable collection.
  Merging this change closes the process for the open API change.

+ The *clopening change*: A mergeable closing change for a previously open
  API change, squashed together with an opening change for a next open
  API change. This saves time in practice.

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
