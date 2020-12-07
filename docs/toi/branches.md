# Git Branches in CSIT

#### Content

- [Overview](#overview)
- [Operational Branches](#operational-branches)
- [Release Branches](#release-branches)

## Overview

This document describes how to create and remove git branches in CSIT project.

To be able to perform everything described in this file, you must be **logged
in as a committer**.

## Operational Branches

**Pre-requisites:**

1. The last builds of weekly and semiweekly jobs must finish with status
   *"Success"*.

The watched jobs are:

- master:
  - [csit-vpp-device-master-ubuntu1804-1n-skx-weekly](https://jenkins.fd.io/view/csit/job/csit-vpp-device-master-ubuntu1804-1n-skx-weekly)
  - [csit-vpp-device-master-ubuntu1804-1n-skx-semiweekly](https://jenkins.fd.io/view/csit/job/csit-vpp-device-master-ubuntu1804-1n-skx-semiweekly)
- 2009_lts:
  - [csit-vpp-device-2009_lts-ubuntu1804-1n-skx-weekly](https://jenkins.fd.io/view/csit/job/csit-vpp-device-2009_lts-ubuntu1804-1n-skx-weekly)
  - [csit-vpp-device-2009_lts-ubuntu1804-1n-skx-semiweekly](https://jenkins.fd.io/view/csit/job/csit-vpp-device-2009_lts-ubuntu1804-1n-skx-semiweekly)

**Procedure:**

1. Take the revision string from the last successful build of the weekly job,
   e.g. **Revision**: 0f9b20775b4a656b67c7039e2dda4cf676af2b21.
1. Open [gerrit](https://gerrit.fd.io/).
1. Go to [Browse --> Repositories --> csit --> Branches](https://gerrit.fd.io/r/admin/repos/csit,branches).
1. Click "CREATE NEW".
1. Fill in the revision number and the name of the new operational branch. Its
   format is: oper-YYMMDD for master and oper-rls{RELEASE}-{YYMMDD} or
   oper-rls{RELEASE}_lts-{YYMMDD} for release branches.
1. Click "CREATE".
1. If needed, delete old operational branches by clicking "DELETE".

## Release Branches

**Pre-requisites:**

1. 

**Procedure:**

1. 
