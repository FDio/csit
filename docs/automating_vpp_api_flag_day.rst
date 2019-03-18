AUTOMATING VPP-API FLAG DAY IN CSIT
===================================

**ABSTRACT**

This document is intended to provide a solution to the problem of
automating the detection of VPP API changes which are not backwards
compatible with existing CSIT tests and to automate the "Flag Day"
process of deploying a new set of CSIT tests which are compatible
with the new version of the VPP API without causing a halt to the
normal VPP/CSIT operational CI process.

**VPP API FLAG DAY ALGORITHM USE CASE**

The following steps describe the use case of the proposed
implementation for automating the VPP API "Flag Day" algorithm:

#. A VPP patch with incompatible VPP API changes is submitted to
   gerrit for review
#. CSIT verify job detects the incompatible VPP API change.
   Note: This requires a new CSIT test described below in the
   section "VPP API INCOMPATIBLE CHANGE TEST".
#. CSIT verify job fails before starting to run any tests and
   an email with the appropriate reason is sent to the VPP patch
   submitter and csit-dev@lists.fd.io including the VPP patch
   information and applicable error information (e.g. API changes
   that were flagged as incompatible).
#. The VPP patch developer and CSIT team create a CSIT JIRA ticket
   to identify the work required to support the new VPP API version.
#. CSIT developer pushes a patch with updates that support the new
   VPP API version. This invokes the CSIT CI verification tests
   which tests support for the existing VPP API. CSIT developer
   iterates until the patch verification passes.
#. CSIT developer runs CI verification tests against the VPP patch.
   This test support for the new VPP API, associated VPP
   features and CSIT tests.  Both developers iterate until the
   verification passes.
#. CSIT committer merges CSIT patch.
#. VPP developer issues a recheck on the VPP patch and a VPP
   Committer merges the patch.
#. Recheck of existing VPP patches in gerrit shall cause the "VPP
   API Incompatible Change Test" to send an email to the patch
   submitter to rebase the patch to pick up the compatible VPP API
   version files.

**NEW FEATURES REQUIRED FOR IMPLEMENTATION**

**VPP API Incompatible Change Test**

PAPP JSON build artifacts contain a CRC of each VPP-API message.
The VPP git commit id and the concatenation of all PAPI API JSON
files shall be stored in the CSIT repo in the file
.../csit/PAPI_SIGNATURE.

The test shall be added to the CSIT infrastructure after the PAPI
library has been created.  The test shall build a temporary
PAPI_SIGNATURE file in the same manner as the one stored in the
CSIT repo from the VPP patch being tested.  The test shall then
compare the two signature files and determine the following state:

- No Change
- Backwards Compatible (new messages or new fields have been added)
- Incompatible (messages deleted, modified, etc)
- Rebase VPP Patch (current patch does not include PAPI_SIGNATURE commit)

Any condition other than "No Change" shall cause an email to be sent
to the VPP patch submitter.  If the condition is "Backwards Compatible"
or "Incompatible" then csit-dev@lists.fd.io shall also be copied on the
notification email.

**Run CSIT Verify Job against a specific VPP Patch in gerrit review branch**

TBD how to implement this.