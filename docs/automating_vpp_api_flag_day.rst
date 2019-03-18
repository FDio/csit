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

**VPP API FLAG DAY ALGORITHM USE CASE**

The following steps describe the use case of the proposed
implementation for automating the VPP API "Flag Day" algorithm:

#. A VPP patch with VPP API changes is submitted to
   gerrit for review
#. CSIT verify job detects the VPP API change(s).
   Note: This requires a new CSIT test described below in the
   section "CSIT VPP API CHANGE DETECTION TEST".
#. CSIT verify job fails before starting to run any tests and
   an email with the appropriate reason is sent to the VPP patch
   submitter and vpp-api-dev@lists.fd.io including the VPP patch
   information and API change(s) that were detected.
#. The VPP patch developer and CSIT team create a CSIT JIRA ticket
   to identify the work required to support the new VPP API version.
#. CSIT developer converts existing CSIT tests to support the new
   VPP API version and new features in the VPP patch as required.
#. CSIT developer runs CI verification tests against the VPP patch
   (aka "Patch-On-Patch verification).
   This process verifies support for the new VPP API, associated VPP
   features and CSIT tests.  Both developers iterate until the
   verification passes.
#. CSIT committer merges CSIT patch and creates a new operational
   branch in the CSIT repo.
#. VPP developer issues a recheck on the VPP patch and a VPP
   Committer merges the patch.
#. Recheck of existing VPP patches in gerrit shall cause the "VPP
   API Incompatible Change Test" to send an email to the patch
   submitter to rebase the patch to pick up the compatible VPP API
   version files.

**FEATURES REQUIRED FOR IMPLEMENTATION**

**PAPI SIGNATURE AWARE CSIT Operational Branch Selection**

The VPP CI verification scripts needs to be able to select the
latest operational CSIT branch containing the corresponding
csit/VPP_PAPI_SIGNATURE in each VPP patch.  This may require
a VPP_PAPI_SINATURE file to be checked into the vpp repo in
order to reduce the overhead of generating the VPP PAPI Signature
every time a vpp-csit-verify job is executed.

**VPP "make papi-signature**

VPP top level makefile shall have a new target "papi-signature' which
generates all of the PAPI API JSON files and concatenates them
into a single output file (e.g. vpp_papi_signature.txt).

**CSIT VPP API CHANGE DETECTION TEST**

PAPI JSON build artifacts contain a CRC of each VPP-API message.
The VPP git commit id and the shall be stored in the CSIT repo in the file
.../csit/VPP_PAPI_SIGNATURE.

The test shall be added to the CSIT infrastructure after the PAPI
library has been created.  The test shall build a temporary
PAPI_SIGNATURE file in the same manner as the one stored in the
CSIT repo from the VPP patch being tested.  The test shall then
compare the two signature files and determine the following state:

- No Change
- Changed
- Rebase VPP Patch (current patch does not include PAPI_SIGNATURE commit)

Any condition other than "No Change" shall cause an email to be sent
to the VPP patch submitter.  If the condition is "Changed" then
vpp-api-dev@lists.fd.io shall also be copied on the notification email.

**Run CSIT Verify Job against a specific VPP Patch in gerrit review branch**

This is the "Patch-On-Patch" methodology -- where is this process documented?
