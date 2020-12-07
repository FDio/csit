# Git Branches in CSIT

#### Content

- [Overview](#overview)
- [Operational Branches](#operational-branches)
- [Release Branches](#release-branches)

## Overview

This document describes how to create and remove git branches in CSIT project.

To be able to perform everything described in this file, you must be **logged
in as a committer**.

> Note: The branch `rls2009_lts` is used here only as an example.

## Operational Branches

For more information about operational branches see
[CSIT/Branching Strategy](https://wiki.fd.io/view/CSIT/Branching_Strategy) and
[CSIT/Jobs](https://wiki.fd.io/view/CSIT/Jobs) on
[fd.io](https://fd.io) [wiki](https://wiki.fd.io/view/CSIT) pages.

### Pre-requisites

1. The last builds of weekly and semiweekly jobs must finish with status
   *"Success"*.
1. If any of watched jobs failed, try to find the root cause, fix it and run it
   again.

The watched jobs are:

- master:
  - [csit-vpp-device-master-ubuntu1804-1n-skx-weekly](https://jenkins.fd.io/view/csit/job/csit-vpp-device-master-ubuntu1804-1n-skx-weekly)
  - [csit-vpp-device-master-ubuntu1804-1n-skx-semiweekly](https://jenkins.fd.io/view/csit/job/csit-vpp-device-master-ubuntu1804-1n-skx-semiweekly)
- 2009_lts:
  - [csit-vpp-device-2009_lts-ubuntu1804-1n-skx-weekly](https://jenkins.fd.io/view/csit/job/csit-vpp-device-2009_lts-ubuntu1804-1n-skx-weekly)
  - [csit-vpp-device-2009_lts-ubuntu1804-1n-skx-semiweekly](https://jenkins.fd.io/view/csit/job/csit-vpp-device-2009_lts-ubuntu1804-1n-skx-semiweekly)

### Procedure

**A. CSIT Operational Branch**
1. Take the revision string from the last successful build of the **weekly**
   job, e.g. **Revision**: 0f9b20775b4a656b67c7039e2dda4cf676af2b21.
1. Open [gerrit](https://gerrit.fd.io).
1. Go to
   [Browse --> Repositories --> csit --> Branches](https://gerrit.fd.io/r/admin/repos/csit,branches).
1. Click "CREATE NEW".
1. Fill in the revision number and the name of the new operational branch. Its
   format is: `oper-YYMMDD` for master and `oper-rls{RELEASE}-{YYMMDD}` or
   `oper-rls{RELEASE}_lts-{YYMMDD}` for release branches.
1. Click "CREATE".
1. If needed, delete old operational branches by clicking "DELETE".

**B. VPP Stable version**
1. Open the console log of the last successful **semiweekly** build and search
   for VPP version (e.g. vpp_21 ...).
1. You should find the string with this structure:
   `vpp_21.01-rc0~469-g7acab3790~b368_amd64.deb`
1. Modify [VPP_STABLE_VER_UBUNTU_BIONIC](../../VPP_STABLE_VER_UBUNTU_BIONIC)
   and [VPP_STABLE_VER_CENTOS](../../VPP_STABLE_VER_CENTOS) files.
1. Use a string with the build number, e.g. `21.01-rc0~469_g7acab3790~b129`
   for [VPP_STABLE_VER_CENTOS](../../VPP_STABLE_VER_CENTOS) and a string
   without the build number, e.g. `21.01-rc0~469_g7acab3790` for
   [VPP_STABLE_VER_UBUNTU_BIONIC](../../VPP_STABLE_VER_UBUNTU_BIONIC).
1. Update the stable versions in master and in all LTS branches.

## Release Branches

### Pre-requisites

1. 

### Release branch

1. 



### Jenkins jobs

See ["Add CSIT rls2101 branch"](https://gerrit.fd.io/r/c/ci-management/+/30439)
patch as an example. The branch "rls2101" is used here as an example.

1. [csit.yaml](https://github.com/FDio/ci-management/blob/master/jjb/csit/csit.yaml):
   Source code documentation and the Report
   - Add release branch (rls2101) for `csit-docs-merge-{stream}` and
     `csit-report-merge-{stream}` (project --> stream).
1. [csit-perf.yaml](https://github.com/FDio/ci-management/blob/master/jjb/csit/csit-perf.yaml):
   Verify jobs:
   - Add release branch (rls2101) to `project --> jobs -->
     csit-vpp-perf-verify-{stream}-{node-arch} --> stream`.
   - Add release branch (rls2101) to `project --> project: 'csit' --> stream`.
1. [csit-tox.yaml](https://github.com/FDio/ci-management/blob/master/jjb/csit/csit-tox.yaml):
   tox
   - Add release branch (rls2101) to `project --> stream`.
1. [csit-vpp-device.yaml](https://github.com/FDio/ci-management/blob/master/jjb/csit/csit-vpp-device.yaml):
   csit-vpp-device
   - Add release branch (rls2101) to `project --> jobs (weekly / semiweekly) --> stream`.
   - Add release branch (rls2101) to `project --> project: 'csit' --> stream`.
