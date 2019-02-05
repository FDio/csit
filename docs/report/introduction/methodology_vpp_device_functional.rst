VPP_Device Functional
---------------------

|csit-release| added new VPP_Device test environment for functional VPP
device tests integrated into LFN CI/CD infrastructure. VPP_Device tests
run on 1-Node testbeds (1n-skx, 1n-arm) and rely on Linux SRIOV Virtual
Function (VF), dot1q VLAN tagging and external loopback cables to
facilitate packet passing over exernal physical links. Initial focus is
on few baseline tests. Existing CSIT VIRL tests can be moved to
VPP_Device framework by changing L1 and L2 KW(s). RF test definition
code stays unchanged with the exception of requiring adjustments from
3-Node to 2-Node logical topologies. CSIT VIRL to VPP_Device migration
is expected in the next CSIT release.
