VPP_Device Functional
---------------------

|csit-release| includes VPP_Device test environment for functional VPP
device tests integrated into LFN CI/CD infrastructure. VPP_Device tests
run on 1-Node testbeds (1n-skx, 1n-arm) and rely on Linux SRIOV Virtual
Function (VF), dot1q VLAN tagging and external loopback cables to
facilitate packet passing over external physical links. Initial focus is
on few baseline tests. New device tests can be added by small edits
to existing CSIT Performance (2-node) test. RF test definition code
stays unchanged with the exception of traffic generator related L2 KWs.
