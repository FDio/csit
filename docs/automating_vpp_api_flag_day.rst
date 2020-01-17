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


VPP API Flag Day Algorithm
^^^^^^^^^^^^^^^^^^^^^^^^^^

Abstract
~~~~~~~~

This document describes the current solution to the problem of
automating the detection of VPP API changes which are not backwards
compatible with existing CSIT tests, by defining the "Flag Day"
process of deploying a new set of CSIT tests which are compatible
with the new version of the VPP API without causing a halt to the
normal VPP/CSIT operational CI process. This is initially
limited to changes in \*.api files contained in the vpp repo.
Eventually the detection algorithm could be extended to include
other integration points such as "directory" structure of stats
segment or PAPI python library dependencies.

Motivation
~~~~~~~~~~

Aside of per-release activities (release report), CSIT also provides testing
that requires somewhat tight coupling to the latest (merged but not released)
VPP code. Currently, HEAD of one project is run against somewhat older codebase
of the other project. Definition of what is the older codebase to use
is maintained by CSIT project. For older CSIT codebase, there are so-called
"oper" branches. For older VPP codebase, CSIT master HEAD contains identifiers
for "stable" VPP builds. Such older codebases are also used for verify jobs,
where HEAD of the other project is replaced by the commit under review.

One particular type of jobs useful for VPP development is trending jobs.
They test latests VPP build with latest oper branch of CSIT,
and analytics is applied to detect regressions in preformance.
For this to work properly, VPP project needs a warning against breaking
the assumptions the current oper branch makes about VPP behavior.
In the past, the most frequent type of such breakage was API change.

Earlier attempts to create a process to minimize breakage have focused
on creating a new verify job for VPP (called api-crc job) that
votes -1 on a change that affects CRC values for API messages CSIT uses.
The list of messages and CRC values (multiple "collections" are allowed)
is maintained in CSIT repository (in oper branch).
The process was less explicit on how should CSIT project maintain such list.
As CSIT was not willing to support two incpompatible API messages
by the same codebase (commit), there were unavoidable windows
where either trenging jobs, or CSIT verify jobs were failing.

Practice showed that human (or infra) errors can create two kinds of breakages.
Either the unavoidable short window gets long, affecting a trending job run
or two, or the api-crc job starts giving -1 to innocent changes
because oper branch went out of sync with VPP HEAD codebase.
This second type of failure prevents any merges to VPP for a long time
(12 hours is the typical time, give time zone differences).

The current version of this document introduces two new requirements.
Firstly, the api-crc job should not give false -1, under any
(reasonable) circumstances. That means, if a VPP change
(nor any of its unmerged ancestor commits) does not affect any CRC values
for messages used by CSIT, -1 should only mean "rebase is needed",
and rebasing to HEAD should result in +1 from the api-crc job.
Secondly, no more than one VPP change is allowed to be processed
(at the same time).

Naming
~~~~~~

It is easier to define the process after chosing shorter names
for notions that need long definition.

Note: Everytime a single job is mentioned,
in practice it can be a set of jobs covering parts of functionality.
A "run" of the set of jobs passes only if each job within the set
has been run (again) and passed.

Jobs
----

+ A *vpp verify* job: Any job run automatically, and voting on open VPP changes.
  Some verify jobs compile and package VPP for target operating system
  and processor architecture, the packages are NOT archived (currently).
  They should be cached somewhere in future to speed up in downstream jobs,
  but currently each such downstream job can clone and build.

+ The *api-crc* job: Quick verify job for VPP changes, that accesses
  CSIT repository (checkout latest oper branch HEAD) to figure out
  whether merging the change is safe from CSIT point of view.
  Here, -1 means CSIT is not ready. +1 means CSIT looks to be ready
  for the new CRC values, but there still may be failures on real tests.

+ A *trending* job: Any job that is started by timer and performs testing.
  It checkouts CSIT latest oper branch HEAD, downloads the most recent
  completely uploaded VPP package, and unconditionally runs the tests.
  CRC checks are optional, ideally only written to console log
  without otherwise affecting the test cases.

+ A *vpp-csit* job: A slower verify job for VPP changes, that accesses CSIT
  repository and runs tests from the correct CSIT commit (chosen as in trending)
  against the VPP (built from the VPP patch under review).
  Vote -1 means there were test failures. +1 means no test failures, meaning
  there either was no API change, or it was backward compatible.

+ A *csit-vpp* job: Verify job for open CSIT changes. Downloads the
  (completely uploaded) VPP package marked as "stable", and runs a selection
  of tests (from the CSIT patch under review).
  Vote +1 means all tests have passed, so it is safe to merge
  the patch under review.

+ A *patch-on-patch* job: Manually triggered non-voting job
  for open CSIT changes. Compiles and packages from VPP source
  (usually of an unmerged change). Then runs the same tests as csit-vpp job.
  This job is used to prove the CSIT patch under review is supporting
  the specified VPP code.
  In practice, this can be a vpp-csit job started with CSIT_REF set.

+ A *manual verification* is done by a CSIT committer, locally executing steps
  equivalent to the patch-on-patch job. This can to save time and resources.

CRC Collections
---------------

Any commit in/for the CSIT repository contains a file (supported_crcs.yaml),
which contains either one or two collections. A collection is a mapping
that maps API message name to its CRC value.

A collection name specifies which VPP build is this collection for.
An API message name is present in a collection if and only if
it is used by a test implementation (can be in different CSIT commit)
targeted at the VPP build (pointed out by the collection name).

+ The *stable collection*: Usually required, listed first, has comments and name
  pointing to the VPP build this CSIT commit marks as stable.
  The stable collection is only missing in deactivating changes (see below)
  when not mergeable yet.

+ The *active collection*: Optional, listed second, has comments and name
  pointing to the VPP Gerrit (including patch set number)
  the currently active API process is processing.
  The patch set number part can be behind the actual Gerrit state.
  This is safe, because api-crc job on the active API change will fail
  if the older patch is no longer API-equivalent to the newer patch.

Changes
-------

+ An *API change*: The name for any Gerrit Change for VPP repository
  that does not pass api-crc job right away, and needs this whole process.
  This usually means .api files are edited, but a patch that affects
  the way CRC values are computed is also an API change.

  Full name could be VPP API Change, but as no CSIT change is named "API change"
  (and this document does not talk about other FD.io or external projects),
  "API change" is shorter.

  TODO: Is there a magic incantation for Gerrit WebUI to search for API changes?
  Open, -1 from api-crc job, +1 from other (non-csit) jobs.

+ A *blocked change*: The name for open Gerrit Change for VPP repository
  that got -1 from some of voting verify jobs.

+ A *VPP-blocked change": A blocked change which got -1 from some "pure VPP"
  verify job, meaning no CSIT code has been involved in the vote.
  Example: "make test" fails.

  VPP contributor is expected to fix the change, or VPP developers
  are expected to found a cause in an earlier VPP change, and fix it.
  No interaction with CSIT developers is necessary.

+ A *CSIT-blocked change*: A blocked change which is not VPP-blocked,
  but does not pass some vpp-csit job.
  To fix a CSIT-blocked change, an interaction with a CSIT committer
  is usually necessary. Even if a VPP developer is experienced enough
  to identify the cause of the failure, a merge to CSIT is usually needed
  for a full fix.

  This process does not specify what to do with CSIT-blocked changes
  that are not also API changes.

+ The *active API change*: The API change currently being processed
  by the API Flag Day Algorithm.
  While many API changes can be open (waiting/queued/scheduled),
  only one is allowed be active at a time.

+ The *activating change*: The name for a Gerrit Change for CSIT repository
  that does not change the test code, but adds the active CRC collection.
  Merge of the opening change (to latest CSIT oper branch) defines
  which API change has become active.

+ The *deactivating change*: The name for Gerrit Change for CSIT repository
  that only supports tests and CRC values for VPP with the active API change.
  That implies the previously stable CRC collection is deleted,
  and any edits to the test implementation are done here.

+ The *mergeable deactivating change*: The deactivating change with additional
  requirements. Details on the requirements are listed in the next section.
  Merging this change finishes the process for the active API change.

It is possible for a single CSIT change to act both as a mergeable
deactivating change for one API change, and as an activating change
for another API change. As English lacks a good adjective for such a thing,
this document does not name this change.
When this documents says a change is activating or deactivating,
it allows the possibility for the change to fullfill also other purposes
(e.g. acting as deactivating / activating change for another API change).

Algorithm Steps
~~~~~~~~~~~~~~~

The following steps describe the application of the API "Flag Day" algorithm:

#. A VPP patch for an API change is submitted to
   gerrit for review.
#. The api-crc job detects the API CRC values have changed
   for some messages used by CSIT.
#. The api-crc job runs in parallel with any other vpp-csit verify job,
   so those other jobs can hint at the impact on CSIT.
   Currently, any such vpp-csit job is non-voting,
   as the current process does not guarantee such jobs passes
   when the API change is merged.
#. If the api-crc job fails, an email with the appropriate reason
   is sent to the VPP patch submitter and vpp-api-dev@lists.fd.io
   including the VPP patch information and .api files that are edited.
#. The VPP patch developer and CSIT team create a CSIT JIRA ticket
   to identify the work required to support the new VPP API version.
#. CSIT developer creates a patch of the deactivating change
   (upload to Gerrit not required yet).
#. CSIT developer runs patch-on-patch job (or manual verification).
   Both developers iterate until the verification passes.
   Note that in this phase csit-vpp job is expected to vote -1,
   as the deactivating change is not mergeable yet.
#. CSIT developer creates the activating change, uploads to Gerrit,
   waits for vote (usual review cycle applies).
#. When CSIT committer is satisfied, the activating change is merged
   to CSIT master branch and cherry-picked to the latest oper branch.
   This enters a "critical section" of the process.
   Merges of other activating changes are not allowed from now on.
   The targeted API change becomes the active API change.
   This does not break any jobs.
#. VPP developer (or CSIT committer) issues a recheck on the VPP patch.
#. On failure, VPP and CSIT committers analyze what went wrong.
   Typically, the active CRC collection is matching only an older patch set,
   but a newer patch set needs different CRC values.
   Either due to improvements on the VPP change in question,
   or due to a rebase over previously merged (unrelated) API change.
   VPP perhaps needs to rebase, and CSIT definitely needs
   to merge edits to the active collection. Then issue a recheck again,
   and iterate until success.
#. On success, VPP Committer merges the active API change patch.
   (This is also a delayed verification of the current active CRC collection.)
#. VPP committer sends an e-mail to vpp-api-dev stating the support for
   the previous CRC values will soon be removed, implying other changes
   (whether API or not) should be rebased soon.
#. VPP merge jobs create and upload new VPP packages.
   This breaks trending jobs, but both VPP and CSIT verify jobs still work.
#. CSIT developer makes the deactivating change mergeable:
   The stable VPP build indicator is bumped to the build
   that contains the active API change. The active CRC collection
   (added by the activating change) is renamed to the new stable collection.
   (The previous stable collection has already been deleted.)
   At this time, the deactivating change should be uploaded to Gerrit and
   csit verify jobs should be triggered.
#. CSIT committer reviews the code, perhaps triggering any additional jobs
   needed to verify the tests using the edited APIs are still working.
#. When satisfied, CSIT committer merges the mergeable deactivating change
   (to both master and oper).
   The merge fixes trending jobs. VPP and CSIT verify jobs continue to work.
   The merge also breaks some verify jobs for old changes in VPP,
   as announced when the active API change was merged.
   The merge is the point where the process leaves the "critical section",
   thus allowing merges of activating changes for other API changes.
#. CSIT committer sends an e-mail to vpp-api-dev stating the support for
   the previous CRC values has been removed, and rebase is needed
   for all affected VPP changes.
#. Recheck of existing VPP patches in gerrit may cause the "VPP
   API Incompatible Change Test" to send an email to the patch
   submitter to rebase the patch to pick up the compatible VPP API
   version files.

Real life examples
~~~~~~~~~~~~~~~~~~

Simple API change: https://gerrit.fd.io/r/c/vpp/+/23829

Activating change: https://gerrit.fd.io/r/c/csit/+/23956

Mergeable deactivating change: https://gerrit.fd.io/r/c/csit/+/24280

Less straightforward mergeable deactivating change:
https://gerrit.fd.io/r/c/csit/+/22526
It shows:

+ Crc edits: supported_crcs.yaml
+ Version bump: VPP_STABLE_VER_UBUNTU_BIONIC
+ And even a way to work around failing tests:
  eth2p-ethicmpv4-ip4base-eth-1tap-dev.robot

Simple change that is both deactivating and activating:
https://gerrit.fd.io/r/c/csit/+/23969
