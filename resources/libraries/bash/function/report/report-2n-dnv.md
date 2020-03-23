# Notes:
#
# - This file defines the groups of tests for graphs.
# - Also, it defines the tests to run. Note that the same test can be more
#   than once listed in this file as it can be included in more than one graph.
# - This file exists for each topo-arch combination used for the report.
# - The files are stored in a dedicated directory and there are no other files
#   in this directory.
#
# - Graphs generated using information in this file:
#   - Packet throughput
#     - Information about threads/cores is in PAL's specification file together
#       with the template(s) for graphs.
#   - Speedup multicore
#
# - The order of tests is important, the tests are placed to graphs in this
#   order.
#
# - The information about testbed starts with "# Testbed: " followed by
#   topo-arch. It should be the first information in this file.
# - Its structure is:
#   - topology (2n, 3n),
#   - architecture (skx, clx, dnv, ...).
# - The parts of it are connected by dash "-".
#
# - The graph starts with "# Graph: " followed by the graph name.
# - The structure of name is:
#   - NIC (x710, xxv710, cx556a, ...),
#   - frame size (64b, 78b, imix, ...),
#   - area (ip6routing, l2switching, ...),
#   - test type(s) of included tests (base, scale, features, base-scale, ...),
#   - driver (ixgbe, avf, dpdk, ...),
#   - additional information.
# - The parts of the name are connected by dash "-".
# - The information about threads/cores will be added by PAL.
#
# - Add other tests which are not included in any graph but must be run for any
#   other purpose at the end of the file. Introduce them with "# Other tests:"
#   and a new line.

# Testbed: 2n-dnv
# Graph: x553-78b-ip6routing-base-scale-ixgbe
## ethip4-ip4base
1c AND 64b AND ndrpdr AND x553 AND drv_vfio_pci AND ethip4-ip4base
2c AND 64b AND ndrpdr AND x553 AND drv_vfio_pci AND ethip4-ip4base
4c AND 64b AND ndrpdr AND x553 AND drv_vfio_pci AND ethip4-ip4base
## ethip4-ip4scale20k
1c AND 64b AND ndrpdr AND x553 AND drv_vfio_pci AND ethip4-ip4scale20k
2c AND 64b AND ndrpdr AND x553 AND drv_vfio_pci AND ethip4-ip4scale20k
4c AND 64b AND ndrpdr AND x553 AND drv_vfio_pci AND ethip4-ip4scale20k

# Graph: x553-64b-l2switching-base-scale-ixgbe
## eth-l2patch
1c AND 64b AND ndrpdr AND x553 AND drv_vfio_pci AND eth-l2patch
2c AND 64b AND ndrpdr AND x553 AND drv_vfio_pci AND eth-l2patch
4c AND 64b AND ndrpdr AND x553 AND drv_vfio_pci AND eth-l2patch
## eth-l2xcbase
1c AND 64b AND ndrpdr AND x553 AND drv_vfio_pci AND eth-l2xcbase
2c AND 64b AND ndrpdr AND x553 AND drv_vfio_pci AND eth-l2xcbase
4c AND 64b AND ndrpdr AND x553 AND drv_vfio_pci AND eth-l2xcbase
## eth-l2bdbasemaclrn
1c AND 64b AND ndrpdr AND x553 AND drv_vfio_pci AND eth-l2bdbasemaclrn
2c AND 64b AND ndrpdr AND x553 AND drv_vfio_pci AND eth-l2bdbasemaclrn
4c AND 64b AND ndrpdr AND x553 AND drv_vfio_pci AND eth-l2bdbasemaclrn
## eth-l2bdscale10kmaclrn
1c AND 64b AND ndrpdr AND x553 AND drv_vfio_pci AND eth-l2bdscale10kmaclrn
2c AND 64b AND ndrpdr AND x553 AND drv_vfio_pci AND eth-l2bdscale10kmaclrn
4c AND 64b AND ndrpdr AND x553 AND drv_vfio_pci AND eth-l2bdscale10kmaclrn

# Graph: x553-78b-ip6routing-base-scale-ixgbe
## ethip6-ip6base
1c AND 78b AND ndrpdr AND x553 AND drv_vfio_pci AND ethip6-ip6base
2c AND 78b AND ndrpdr AND x553 AND drv_vfio_pci AND ethip6-ip6base
4c AND 78b AND ndrpdr AND x553 AND drv_vfio_pci AND ethip6-ip6base
## ethip6-ip6scale20k
1c AND 78b AND ndrpdr AND x553 AND drv_vfio_pci AND ethip6-ip6scale20k
2c AND 78b AND ndrpdr AND x553 AND drv_vfio_pci AND ethip6-ip6scale20k
4c AND 78b AND ndrpdr AND x553 AND drv_vfio_pci AND ethip6-ip6scale20k

# Other tests:
# List other tests which are not included in graphs
