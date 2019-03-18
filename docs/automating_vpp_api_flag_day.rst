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
#. CSIT committer updates the supported API signature(s) such that
   all signatures included in the branch are supported by the
   current version of CSIT.
#. CSIT committer merges CSIT patch and creates a new operational
   branch in the CSIT repo.
#. VPP developer issues a recheck on the VPP patch and a VPP
   Committer merges the patch.
#. Recheck of existing VPP patches in gerrit may cause the "VPP
   API Incompatible Change Test" to send an email to the patch
   submitter to rebase the patch to pick up the compatible VPP API
   version files.

**FEATURES REQUIRED FOR IMPLEMENTATION**

**VPP SIGNATURE GENERATION**

The VPP PAPI generation already produces the complete set of
signatures in JSON format for all api files and includes them in the
vpp-api-python.deb package.  Upon installation all of the *.api.json
files are installed in the /usr/share/vpp/api directory.  Each record
in the .api.json file contains the name of the api message, the fields
and their data types, and a CRC of the json object.

**VPP API CHANGES FILE INCLUDED in VPP PACKAGE**
The VPP build system shall add a file in the /usr/share/vpp/api
directory of the vpp package which is the same directory in which
the api JSON files are published.  This file will include the list of
VPP api files which were included in the patch to be verified.

See https://gerrit.fd.io/r/19479 for the baseline implementation.

**CSIT VPP API CHANGE DETECTION TEST**

The set of VPP api signatures which are supported shall be stored in
.../csit/resources/api/vpp which are of the same directory structure
as the published api JSON files in /usr/share/vpp/api contained in the
vpp package.

See https://gerrit.fd.io/r/19027 for the baseline implementation.

The test compares the two signature directories and determine the following state:

- No Change
- Changed
- Rebase VPP Patch [0]

[0] The Rebase VPP Patch result occurs when there is no valid API signature found
in .../csit/resources/api/vpp AND there are no VPP API changes included in the patch.

Any condition other than "No Change" shall cause an email to be sent
to the VPP patch submitter.  If the condition is "Changed" then
vpp-api-dev@lists.fd.io shall also be copied on the notification email.

**RUN CSIT VERIFY JOB AGAINST A SPECIFIC VPP PATCH IN GERRIT REVIEW BRANCH**

This is the "Patch-On-Patch" methodology documented in [TBD]?
