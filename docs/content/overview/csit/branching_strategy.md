---
title: "Branching Strategy"
weight: 6
---

# Branching Strategy

## Definitions

**CSIT development branch:** A CSIT branch used for test development which has a
1:1 association with a VPP branch of the same name. CSIT development branches
are never used for operational testing of VPP patches or images.

**CSIT operational branch:** A CSIT branch pulled from a CSIT development or
release branch which is used for operational testing of the VPP branch
associated from its' parent branch. CSIT operational branches are named
`oper-<YYMMDD>` for master and `oper-<release>-<YYMMDD>` for release branches.
CSIT operational branches are the only branches which should be used to run
verify jobs against VPP patches or images.

**CSIT release branch:** A CSIT branch which is pulled from a development branch
and is associated with a VPP release branch. CSIT release branches are never
merged back into their parent branch and are never used for operational testing
of VPP patches or images.

## VPP Selection of CSIT Operational Branches

Each VPP and release branch will have a script which specifies which CSIT
operational branch is used when executing the per patch verify jobs. This is
maintained in the VPP branch in the file
`.../vpp/build-root/scripts/csit-test-branch`.

## Branches

### Main development branch: 'master'

The CSIT development branch 'master' will be the main development for new VPP
feature tests that have not been included in a release. Weekly CSIT operational
branches will be pulled from 'master'. After validation of all CSIT verify jobs,
the VPP script 'csit-test-branch' will be updated with the latest CSIT
operational branch name. Older CSIT operational branches will be available for
manual triggered vpp-csit-verify-* jobs.

### Release branch: 'rls1606', 'rls1609', ...

CSIT release branches shall be pulled from 'master' with the the convention
`rls<release>` (e.g. rls1606, rls1609). New tests that are developed for
existing VPP features will be committed into the 'master' branch, then
cherry-picked|double committed into the latest CSIT release branch.
Periodically CSIT operational branches will be pulled from the CSIT release
branch when necessary and the VPP release branch updated to use the new CSIT
operational branch.

**VPP branch diagram:**

    -- master --------------------------------------------------------------->
              \                           \
               \--- stable/1606 ---[end]   \--- stable/1609---[end]


**CSIT branch diagram:**

                        /--- oper-rls1606-160623
                       / /--- oper-rls1606-$(DATE)
                      / /          . . .
                     / /                        /--- oper-rls1609-$(DATE)
                    / /                        /          . . .
                 /--- rls1606 ---[end]      /--- rls1609 ---[end]
                /        /                 /        /
               / (cherry-picking)         / (cherry-picking)
              /        /                 /        /
    -- master --------------------------------------------------------------->
               \ \          . . .
                \ \--- oper-$(DATE)
                 \--- oper-160710

## Creating a CSIT Operational Branch

### Check verify weekly jobs

`csit-vpp-device-weekly-<master_or_release>-<OS>-<arch>-<testbed>`
are run on the CSIT development or release branch
(e.g. 'master' or 'rls1606') using the latest
VPP package set on nexus.fd.io for the associated VPP branch. Any anomalies will
have the root cause identified and be resolved in the CSIT development branch
prior to pulling the CSIT operational branch.

### Pull CSIT operational branch from parent

The CSIT operational branch is pulled from the parent CSIT development or
release branch.

### Check verify semiweekly jobs

`csit-vpp-device-semiweekly-<master_or_release>-<OS>-<arch>-<testbed>`
is run on the CSIT operational branch
with the latest image of the associated VPP development or release branch.
This job is run to validate the next reference VPP build for
validating the results of all of the csit-vpp-verify* jobs.

### Update VPP branch to use the new CSIT operational branch

Push a patch updating the VPP branch to use the new CSIT operational branch. The
VPP verify jobs will then be run and any anomalies will have the root cause
identified and fixed in the CSIT operational branch prior to 'csit-test-branch'
being merged.

### Periodically lock/deprecate old CSIT Operational Branches

Periodically old CSIT operational branches will be locked and/or deprecated to
prevent changes being made to the operational branch.
