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

For more information about operational branches see
[CSIT/Branching Strategy](https://wiki.fd.io/view/CSIT/Branching_Strategy) and
[CSIT/Jobs](https://wiki.fd.io/view/CSIT/Jobs) on
[fd.io](https://fd.io) [wiki](https://wiki.fd.io/view/CSIT) pages.

> Note: The branch `rls2009_lts` is used here only as an example.

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
1. Open [Gerrit](https://gerrit.fd.io).
1. Go to
   [Browse --> Repositories --> csit --> Branches](https://gerrit.fd.io/r/admin/repos/csit,branches).
1. Click `CREATE NEW`.
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

> Note: VPP release 21.01 is used here only as an example.

### Pre-requisites

1. VPP release manager sends the information email to announce that the RC1
   milestone for VPP {release}, e.g. 21.01, is complete, and the artifacts are
   available.
1. The artifacts (*.deb and *.rpm) should be available at
   `https://packagecloud.io/fdio/{release}`. For example see artifacts for the
   [VPP release 20.01](https://packagecloud.io/fdio/2101). The last available
   build is to be used.
1. All CSIT patches for the release are merged in CSIT master branch.

### Procedure

**A. Release branch**

1. Open [Gerrit](https://gerrit.fd.io).
1. Go to
   [Browse --> Repositories --> csit --> Branches](https://gerrit.fd.io/r/admin/repos/csit,branches).
1. Save the revision string of master for further use.
1. Click `CREATE NEW`.
1. Fill in the revision number and the name of the new release branch. Its
   format is: `rlsYYMM`, e.g. rls2101.
1. Click "CREATE".

**B. Jenkins jobs**

See ["Add CSIT rls2101 branch"](https://gerrit.fd.io/r/c/ci-management/+/30439)
and ["Add report jobs to csit rls2101 branch"](https://gerrit.fd.io/r/c/ci-management/+/30462)
patches as an example.

1. [csit.yaml](https://github.com/FDio/ci-management/blob/master/jjb/csit/csit.yaml):
   Documentation of the source code and the Report
   - Add release branch (rls2101) for `csit-docs-merge-{stream}` and
     `csit-report-merge-{stream}` (project --> stream).
1. [csit-perf.yaml](https://github.com/FDio/ci-management/blob/master/jjb/csit/csit-perf.yaml):
   Verify jobs
   - Add release branch (rls2101) to `project --> jobs -->
     csit-vpp-perf-verify-{stream}-{node-arch} --> stream`.
   - Add release branch (rls2101) to `project --> project: 'csit' --> stream`.
   - Add release branch (rls2101) to `project --> project: 'csit' --> stream_report`.
1. [csit-tox.yaml](https://github.com/FDio/ci-management/blob/master/jjb/csit/csit-tox.yaml):
   tox
   - Add release branch (rls2101) to `project --> stream`.
1. [csit-vpp-device.yaml](https://github.com/FDio/ci-management/blob/master/jjb/csit/csit-vpp-device.yaml):
   csit-vpp-device
   - Add release branch (rls2101) to `project --> jobs (weekly / semiweekly) --> stream`.
   - Add release branch (rls2101) to `project --> project: 'csit' --> stream`.

**C. VPP Stable version**

See the patch
[Update of VPP_REPO_URL and VPP_STABLE_VER files](https://gerrit.fd.io/r/c/csit/+/30461)
as an example.

1. Find the last successful build on the
   [Package Cloud](https://packagecloud.io) for the release, e.g.
   [VPP release 20.01](https://packagecloud.io/fdio/2101).
1. Clone the release branch to your PC:
   `git clone --depth 1 ssh://<user>@gerrit.fd.io:29418/csit --branch rls{RELEASE}`
1. Modify [VPP_STABLE_VER_UBUNTU_BIONIC](../../VPP_STABLE_VER_UBUNTU_BIONIC)
   and [VPP_STABLE_VER_CENTOS](../../VPP_STABLE_VER_CENTOS) files with the last
   successful build.
1. Modify [VPP_REPO_URL](../../VPP_REPO_URL) to point to the new release, e.g.
   `https://packagecloud.io/install/repositories/fdio/2101`.
1. You can also modify the [.gitreview](../../.gitreview) file and set the new
   default branch.
1. Wait until the verify jobs
   - [csit-vpp-device-2101-ubuntu1804-1n-skx](https://jenkins.fd.io/job/csit-vpp-device-2101-ubuntu1804-1n-skx)
   - [csit-vpp-device-2101-ubuntu1804-1n-tx2](https://jenkins.fd.io/job/csit-vpp-device-2101-ubuntu1804-1n-tx2)

   successfully finish and merge the patch.

**D. CSIT Operational Branch**

1. Manually start (Build with Parameters) the weekly job
   [csit-vpp-device-2101-ubuntu1804-1n-skx-weekly](https://jenkins.fd.io/view/csit/job/csit-vpp-device-2101-ubuntu1804-1n-skx-weekly)
1. When it successfully finishes, take the revision string e.g. **Revision**:
   876b6c1ae05bfb1ad54ff253ea021f3b46780fd4 to create a new operational branch
   for the new release.
1. Open [Gerrit](https://gerrit.fd.io).
1. Go to
   [Browse --> Repositories --> csit --> Branches](https://gerrit.fd.io/r/admin/repos/csit,branches).
1. Click `CREATE NEW`.
1. Fill in the revision number and the name of the new operational branch. Its
   format is: `oper-rls{RELEASE}-YYMMDD` e.g. `oper-rls2101-201217`.
1. Click "CREATE".
1. Manually start (Build with Parameters) the semiweekly job
   [csit-vpp-device-2101-ubuntu1804-1n-skx-semiweekly](https://jenkins.fd.io/view/csit/job/csit-vpp-device-2101-ubuntu1804-1n-skx-semiweekly)
1. When it successfully finishes check in console log if it used the right VPP
   version (search for `VPP_VERSION=`) from the right repository (search for
   `REPO_URL=`).

**E. Announcement**

If everything is as it should be, send the announcement email to
`csit-dev@lists.fd.io` mailing list.

*Example:*

Subject:
```text
CSIT rls2101 branch pulled out
```

Body:
```text
CSIT rls2101 branch [0] is created and fully functional.

Corresponding operational branch (oper-rls2101-201217) has been created too.

We are starting dry runs for performance ndrpdr iterative tests to get initial
ndrpdr values with available rc1 packages as well as to test all the infra
before starting report data collection runs.

Regards,
<signature>

[0] https://git.fd.io/csit/log/?h=rls2101
```
