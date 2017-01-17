Introduction
============

This report aims to provide a comprehensive and self-explanatory summary of all
CSIT test cases that have been executed against FD.io VPP-16.09 code release,
driven by the automated test infrastructure developed within the FD.io CSIT
project (FD.io Continuous System and Integration Testing).

CSIT source code for the executed test suites is available in CSIT branch
rls1701 in the directory ./tests/<name_of_the_test_suite>. A local copy of CSIT
source code can be obtained by cloning CSIT git repository ("git clone
https://gerrit.fd.io/r/csit"). The CSIT testing virtual environment can be run
on a local workstation/laptop/server using Vagrant by following the instructions
in CSIT tutorials.

Followings sections provide brief description of CSIT performance and functional
test suites executed against VPP-16.09 release (vpp branch stable/1701).
Description of LF FD.io virtual and physical test environments is provided to
aid anyone interested in reproducing the complete LF FD.io CSIT testing
environment, in either virtual or physical test beds. The last two sections
cover complete list of CSIT test suites and test cases executed against
VPP-17.01 release (vpp branch stable/1701), with description and results per
test case.
