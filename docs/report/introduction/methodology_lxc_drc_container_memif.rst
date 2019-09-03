LXC/DRC Container Memif
-----------------------

CSIT includes tests taking advantage of VPP memif virtual
interface (shared memory interface) to interconnect VPP running in
Containers. VPP vswitch instance runs in bare-metal user-mode handling
NIC interfaces and connects over memif (Slave side) to VPPs running in
:abbr:`Linux Container (LXC)` or in Docker Container (DRC) configured
with memif (Master side). LXCs and DRCs run in priviliged mode, with
VPP data plane worker threads pinned to dedicated physical CPU cores, per
usual CSIT practice. All VPP instances run the same version of software.
This test topology is equivalent to existing tests with vhost-user and
VMs as described earlier in :ref:`tested_logical_topologies`.

In addition to above vswitch tests, a single memif interface test is
executed. It runs in a simple topology of two VPP container instances
connected over memif interface in order to verify standalone memif
interface performance.

More information about CSIT LXC and DRC setup and control is available
in :ref:`container_orchestration_in_csit`.
