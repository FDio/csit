VPP_Device Functional
---------------------

|csit-release| includes a VPP_Device test environment for functional VPP
device tests integrated into LFN CI/CD infrastructure. VPP_Device tests
run on 1-Node testbeds (1n-skx, 1n-arm) and rely on Linux SRIOV Virtual
Function (VF), dot1q VLAN tagging and external loopback cables to
facilitate packet passing over exernal physical links. Initial focus is
on few baseline tests. Existing CSIT Performance tests can be moved to
the VPP_Device framework. RF test definition code stays unchanged, with the
exception of traffic-generator-related L2 Keywords.
