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


AUTOMATING VPP-API FLAG DAY IN CSIT
===================================

**ABSTRACT**

This document is intended to provide a solution to the problem of
automating the detection of VPP API changes which are not backwards
compatible with existing CSIT tests and to automate the "Flag Day"
process of deploying a new set of CSIT tests which are compatible
with the new version of the VPP API without causing a halt to the
normal VPP/CSIT operational CI process. This shall initially be
limited to changes in \*.api files contained in the vpp repo.
Eventually the detection algorithm could be extended to include
other integration points such as "directory" structure of stats
segment or PAPI python library dependencies.

**MOTIVATION**

Aside of per-release activities (release report), CSIT also provides testing
that requires somewhat tight coupling to the latest (merged but not released)
VPP code. Currently, the coupling is not as tight as possible.
Instead of testing HEAD builds of VPP directly with HEAD CSIT code,
HEAD of one project is run with somewhat older codebase of the other project.
Definition of what is the older codebase to use is maintained by CSIT project.
For older CSIT codebase, the project creates so-called "oper" branches.
For older VPP codebase, CSIT master HEAD contains identifiers
for "stable" VPP builds. Such older codebases are also used for verify jobs,
where HEAD of the other project is replaced by the commit under review.

One particular type of jobs useful for VPP development is trending jobs.
They test latests VPP build with oper branch of CSIT,
and analytics is applied to detect regressions in preformance.
For this to work properly, VPP project needs a warning against breaking
the assumptions the current oper branch makes about VPP behavior.
In the past, the most frequent type of such breakage was API change.

Earlier attempts to create a process to minimize breakage have focused
on creating a new verify job for VPP (called api-crc job) that
votes -1 on a change that affect CRC values for API messages CSIT uses.
The list of messages and CRC values (multiple values are allowed)
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

The current version of this document is still being somewhat vague
on the CSIT side of the process, but introduces a new requirement:
The api-crc job should not give false -1, under any reasonable circumstance.
That means, if a VPP change (nor any of its unmerged ancestor commits)
does not affect any CRC values for messages used by CSIT,
-1 should only mean "rebase is needed", and rebasing to HEAD should result
in +1 from the api-crc job.

**VPP API FLAG DAY ALGORITHM USE CASE**

The following steps describe the use case of the proposed
implementation for automating the VPP API "Flag Day" algorithm:

#. A VPP patch with VPP API changes is submitted to
   gerrit for review. This usually means .api files are edited,
   but a patch that affects the way CRCs are computed is also an API change.
#. The api-crc job detects the API CRC values have changed
   for some messages used by CSIT.
   Note: This requires a new CSIT test described below in the
   section "CSIT VPP API CHANGE DETECTION TEST".
#. The api-crc job runs in parallel with any other VPP verify job,
   so other jobs can hint at the impact on CSIT.
   Some API changes do not need any edit on CSIT side, except for the CRC value.
   If the api-crc job fails, an email with the appropriate reason
   is sent to the VPP patch submitter and vpp-api-dev@lists.fd.io
   including the VPP patch information and API change(s) that were detected.
#. The VPP patch developer and CSIT team create a CSIT JIRA ticket
   to identify the work required to support the new VPP API version.
#. CSIT developer creates a patch to existing CSIT tests to support
   the new VPP API version and new features in the VPP patch as required.
#. CSIT developer runs CI verification tests (without CRC checks)
   for the CSIT patch against the VPP patch (aka "Patch-On-Patch verification").
   This process verifies support for the new VPP API, associated VPP
   features and CSIT tests.  Both developers iterate until the
   verification passes.
#. CSIT developer creates a separate change, that only edits the CSIT CRC list
   to include both stable VPP CRCs, and CRCs of the VPP change under review.
#. CSIT committer requires proofs both CRCs are included correctly
   (for example the api-crc job is run with overriden CSIT_REF parameter).
#. When CSIT committer sees both CSIT changes are ready,
   the CRC-editing change is merged to CSIT master branch
   and cherry-picked to the latest oper branch.
   This does not break any jobs.
#. VPP developer issues a recheck on the VPP patch
#. On success, VPP Committer merges the patch.
#. VPP committer sends an e-mail to vpp-api-dev stating the support for
   the previous CRC values will soon be removed.
#. VPP merge jobs create and upload new VPP packages.
   This breaks trending jobs, but both VPP and CSIT verify jobs still work.
#. CSIT developer bumps stable vpp version in the test affecting change
   and rechecks it still works.
#. CSIT committer merges this change (to both master and oper).
   This fixes trending jobs. Both VPP and CSIT verify jobs continue to work.
#. CSIT committer creates a patch that removes the old CRC values.
#. CSIT committer merges that patch.
   This breaks verify jobs for old changes in VPP.
#. CSIT committer sends an e-mail to vpp-api-dev stating the support for
   the previous CRC values has been removed, and rebase is needed
   for all affected VPP changes.
#. Recheck of existing VPP patches in gerrit may cause the "VPP
   API Incompatible Change Test" to send an email to the patch
   submitter to rebase the patch to pick up the compatible VPP API
   version files.

**FEATURES REQUIRED FOR IMPLEMENTATION**

**VPP API SIGNATURE GENERATION**

The VPP PAPI generation already produces the complete set of
signatures in JSON format for all api files and includes them in the
vpp-api-python.deb package.  Upon installation all of the \*.api.json
files are installed in the /usr/share/vpp/api directory.  Each record
in the .api.json file contains the name of the api message, the fields
and their data types, and a CRC of the json object.

**VPP API CLIENT SIGNATURES**

In each CSIT branch, all of the VPP API client signatures that are supported
by the CSIT tests in that branch are contained in separate directories
under the .../csit/resources/api/vpp directory. The CSIT VPP API
client signature directory structure is the same as the one published in
/usr/share/vpp/api as generated by vppapigen.

The granularity of the CSIT VPP API client signature support
will initially be on a per VPP API JSON file.  In the future, a per VPP
api message level of granularity may be added.  If CSIT is capable of
supporting more than one version of a VPP API JSON file, then a new
CSIT VPP api client signature directory will be created containing
all of the supported VPP API JSON files.  Typically this will be identical
to the previous version with the exception of the VPP API JSON files
which have been changed in the VPP patch which triggered the VPP API FLAG
day algorithm.

See https://gerrit.fd.io/r/19027 for the baseline implementation.

**VPP API CHANGES FILE INCLUDED in VPP PACKAGE**

The VPP build system shall add a file in the /usr/share/vpp/api
directory of the vpp package which is the same directory in which
the api JSON files are published.  This file will include the list of
VPP api files which were included in the patch to be verified.

See https://gerrit.fd.io/r/19479 for the baseline implementation.

**CSIT VPP API CHANGE DETECTION TEST**

The set of VPP api signatures which are supported by the CSIT tests in
a given CSIT branch shall be stored in .../csit/resources/api/vpp which
mirrors the same directory structure as the API signature directory
generated by vppapigen (e.g. /usr/share/api/vpp/core &
/usr/share/api/vpp/plugins).

The test compares the VPP patch's API signature directory with each of
the CSIT VPP API signabture directory and determine the following state:

- No Change
- Changed
- Rebase or Merge Parent VPP Patch [0]

[0] The Rebase or Merge Parent VPP Patch result occurs when there is no valid API
signature found in .../csit/resources/api/vpp AND there are no VPP API changes
included in the patch.  This could be the result of a patch whose parent does not
include the API changes merged in another VPP patch and supported by the new CSIT
oper branch.  This case would be resolved by rebasing the patch to HEAD.  The other
possibility is that the patch is a descendent of a patch with an incompatible API
change that has not been merged yet.  This case is resolved by completing the API
Flag Day algorithm on the parent patch such that the latest CSIT oper branch supports
the API in the parent.  This importance of the detection of this state is to provide
direct feedback to the VPP patch author about how to resolve the issue in a timely
manner.

Any condition other than "No Change" shall cause an email to be sent
to the VPP patch submitter.  If the condition is "Changed" then
vpp-api-dev@lists.fd.io shall also be copied on the notification email.

**RUN CSIT VERIFY JOB AGAINST A SPECIFIC VPP PATCH IN GERRIT REVIEW BRANCH**

This is the "Patch-On-Patch" methodology documented in [TBD]?


**VPP API FLAG DAY SCENARIOS**

In the beginning, let's assume there is a single VPP API Client signature
directory in the current oper branch called vpp-api-client.sig.1 which
contains core/vpe.api.json and plugin/acl.api.json which are supported
by the CSIT tests.

**VPP PATCH CONTAINS INCOMPATIBLE API CHANGES**

Next, a VPP developer modifies vpe.api with a whole set of
new type definitions.  When the patch is submitted to gerrit.fd.io, the
"CSIT VPP API CHANGE DETECTION TEST" detects the changed api file and
votes Verified -1.  Once CSIT has been updated to support the new type
definitions and verified against the VPP patch,
vpp-api-client.sig.1/core/vpe.api.json is replaced with the vpe.api.json
file from the patch. The CSIT changes are committed into CSIT master and a
new oper branch is created. The VPP patch is then rechecked and merged
into VPP master as soon as practicable. All existing VPP patches and any
new patches not including the VPP api change patch will fail verification
with a "Rebase or Merge Parent" notification upon recheck or initial
submission to gerrit.  Rebasing is then required in order to pass
verification of the new api changes.

**VPP PATCH CONTAINS BACKWARDS COMPATIBLE CHANGES**

The next day, a VPP developer finds a need to add a new
attribute to an api message in vpe.api with a default value defined.
This is a backwards compatible change for CSIT.  Since the "CSIT VPP
API CHANGE DETECTION TEST" only works on a per api file level of granularity,
the change is flagged with Verified -1.  However, in this case, the
CSIT developer can resolve the verify failure by adding a second VPP API
client signature directory, vpp-api-client.sig.2 which is a copy of
vpp-api-client.sig.1 with the vpe.api.json file updated with the contents
of the copy from the VPP patch.  After the CSIT changes are merged and a new
CSIT oper branch is created, the VPP patch will pass verification upon recheck.
All other patches will continue to pass verification upon recheck or initial
submission to gerrit by matching the signature in  vpp-api-client.sig.1 --
life is good.

**CSIT REMOVES SUPPORT FOR A VPP API VERSION**

Since it is not desirable to maintain a bazillion CSIT VPP API client
signatures, after a reasonable period of time (let's say a week), a
CSIT developer deletes vpp-api-client.sig.1 and renames
vpp-api-client.sig.2 to vpp-api-client.sig.1, merges to CSIT master,
and creates a new oper branch.  At this point, VPP patches that do not
contain the new vpe.api file will fail verification upon recheck or initial
submission to gerrit with a "Rebase or Merge Parent" notification and
will require rebasing to pass verification.

**CSIT ADDS SUPPORT FOR A NEW FEATURE API PRIOR TO VPP**

A VPP developer has lots of ideas and decides to add a new
plugin and api which supports the "Super-Duper Feature" to VPP in
a new plugin called the "Super-Duper Plugin" and associated super_duper.api
VPP binary APi message definition file. Being a thoughtful and
helpful developer, the VPP developer notifies the CSIT team providing
them with the super_duper.api.json file. A CSIT developer
quickly produces the Super-Duper Feature CSIT test suite and updates the VPP
API Client signature with vpe-api-client.sig.1/plugin/super_duper.api.json.
In the meantime, the VPP developer pushes the Super-Duper VPP patch which
fails the CSIT VPP API CHANGE DETECTION TEST. Both developers then work
together to verify both CSIT and the VPP patch.  The CSIT developer
then merges the CSIT code into master and creates a new oper branch.  Our
VPP developer is very pleased when the VPP patch containing
the Super-Duper Plugin verifies upon recheck. All other VPP patches without
api file changes continue to pass the CSIT VPP API CHANGE DETECTION TEST
before and after the Super-Duper VPP patch is merged.

**VPP PATCH CONTAINS A NEW FEATURE API BEFORE CSIT SUPPORT**

Now let's assume that the VPP developer was having a bad day
and forgot to notify the CSIT team about the new Super-Duper Plugin.
Upon pushing the VPP patch to gerrit, the VPP developer is pleased that
there is no nastygram email from the CSIT VPP API CHANGE DETECTION TEST.
All VPP patches without api file changes continue to pass the CSIT VPP
API CHANGE DETECTION TEST. Eventually a Super-Duper Plugin test suite is
added to CSIT along with vpe-api-client.sig.1/plugin/super_duper.api.json
and release in a new CSIT oper branch. All VPP patches that are do not contain
api changes and are verified via recheck or initial submission, continue to
pass the CSIT VPP API CHANGE DETECTION TEST.
