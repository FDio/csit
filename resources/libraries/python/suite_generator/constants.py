# Copyright (c) 2025 Cisco and/or its affiliates.
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at:
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Constants used by the Suite Generator.

TODO: Consider reading environment variables to set some of the constants.
"""


import generator_functions as gf


# Logging
LOGGING_LEVEL = ("NOTSET", "DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL")
DEFAULT_LOG_LEVEL = "INFO"

TEST_TYPES = ("mrr", "ndrpdr", "soak", "hoststack")

# Directory with job specifications:
DIR_JOB_SPEC = "../../../job_specifications"
# The directory with test templates:
DIR_TESTS_IN = "../../../.."

# Default path for generated json and md files.
DEFAULT_OUTPUT_PATH = "./out"
# Default filename for generated files.
DEFAULT_OUTPUT_FILE = "job_spec"


# Parameters of test(s) applied to the test groups. Their order in this tuple
# defines the order in the output MD file.
TEST_PARAMS = ("core", "framesize", "test-type", "infra")

# Values used in the template files (NIC, driver, test type).
TMPL_NIC = "10ge2p1x710"
TMPL_DRV = "vfio-pci"
TMPL_TTYPE = "ndrpdr"

# The line which separates test specifications from the rest of file.
TMPL_SEP_TESTS = "*** Test Cases ***\n"

TMPL_TEST = {
    "default": """
| $frame_str-$cores_str-$driver$suite_id-$test_type
| | [Tags] | $frame_tag | $cores_tag
| | frame_size=$frame_num | phy_cores=$cores_num
""",
    "trex": """
| $frame_str--$suite_id-$test_type
| | [Tags] | $frame_tag
| | frame_size=$frame_num
""",
    "iperf3": """
| 128KB-$cores_str-$suite_id-mrr
| | [Tags] | 128KB | $cores_tag
| | frame_size=$frame_num | phy_cores=$cores_num
""",
    "hoststack_cps_rps": """
| $frame_str-$cores_str-$suite_id
| | [Tags] | $frame_str | $cores_str
| | frame_size=$frame_num | phy_cores=$cores_num
""",
    "hoststack_bps": """
| $frame_str-$cores_str-$suite_id
| | [Tags] | $cores_tag
| | phy_cores=$cores_num
"""
}

# Mappings

# Functions used to generate particular kind of suite
GEN_SUITE_PARAMS = {
    "default": gf.generate_suite_params_default,
    "trex": gf.generate_suite_params_trex,
    "iperf3": gf.generate_suite_params_iperf3,
    "hoststack_cps_rps": gf.generate_suite_params_hoststack_cps_rps,
    "hoststack_bps": gf.generate_suite_params_hoststack_bps
}
GEN_TEST = {
    "default": gf.generate_test_default,
    "trex": gf.generate_test_trex,
    "iperf3": gf.generate_test_iperf3,
    "hoststack_cps_rps": gf.generate_test_hoststack_cps_rps,
    "hoststack_bps": gf.generate_test_hoststack_bps
}

NIC_CODE_TO_NAME = {
    "10ge2p1x710": "Intel-X710",
    "40ge2p1xl710": "Intel-XL710",
    "25ge2p1xxv710": "Intel-XXV710",
    "25ge2p1e810xxv": "Intel-E810XXV",
    "25ge2p1e822cq": "Intel-E822CQ",
    "25ge2p1e823c": "Intel-E823C",
    "100ge2p1e810cq": "Intel-E810CQ",
    "50ge1p1ena": "Amazon-Nitro-50G",
    "100ge1p1ena": "Amazon-Nitro-100G",
    "200ge1p1ena": "Amazon-Nitro-200G",
    "100ge2p1cx556a": "Mellanox-CX556A",
    "100ge2p1cx6dx": "Mellanox-CX6DX",
    "200ge2p1cx7veat": "Mellanox-CX7VEAT",
    "200ge6p3cx7veat": "Mellanox-CX7VEAT",
    "100ge2p1a063": "Cavium-A063-100G",
    "1ge1p82540em": "virtual",
}

# Tags to differentiate tests for different NIC driver.
NIC_DRIVER_TO_TAG = {
    "vfio-pci": "DRV_VFIO_PCI",
    "oct-vfio-pci": "DRV_VFIO_PCI",
    "avf": "DRV_AVF",
    "rdma-core": "DRV_RDMA_CORE",
    "mlx5_core": "DRV_MLX5_CORE",
    "af_xdp": "DRV_AF_XDP",
    "tap": "DRV_TAP",
    "vhost": "DRV_VHOST"
}

# Suite names have to be different, add prefix.
NIC_DRIVER_TO_SUITE_PREFIX = {
    "vfio-pci": "",
    "oct-vfio-pci": "",
    "avf": "avf",
    "rdma-core": "rdma",
    "mlx5_core": "mlx5",
    "af_xdp": "af_xdp",
    "tap": "",
    "vhost": ""
}
# Driver name from job spec to driver variable mapping.
NIC_DRIVER_TO_VARIABLE = {
    "vfio-pci": "vfio-pci",
    "oct-vfio-pci": "vfio-pci",
    "avf": "avf",
    "rdma-core": "rdma-core",
    "mlx5_core": "mlx5_core",
    "af_xdp": "af_xdp"
}
DRIVERS_NOT_IN_NAME = (
    "vfio-pci",
    "oct-vfio-pci",
    "tap",
    "vhost",
    "-"
)

# Each driver needs different plugin to work.
NIC_DRIVER_TO_PLUGINS = {
    "vfio-pci": "dpdk_plugin.so",
    "oct-vfio-pci": "dev_octeon_plugin.so",
    "avf": "dev_iavf_plugin.so",
    "rdma-core": "rdma_plugin.so",
    "mlx5_core": "dpdk_plugin.so",
    "af_xdp": "af_xdp_plugin.so"
}

# Number of virtual functions of physical nic.
NIC_DRIVER_TO_VFS = {
    "vfio-pci": "nic_vfs}= | 0",
    "oct-vfio-pci": "nic_vfs}= | 0",
    "avf": "nic_vfs}= | 1",
    "rdma-core": "nic_vfs}= | 0",
    "mlx5_core": "nic_vfs}= | 0",
    "af_xdp": "nic_vfs}= | 0",
    "tap": "nic_vfs}= | 0",
    "vhost": "nic_vfs}= | 0"
}

# Number of physical interfaces of physical nic.
NIC_CODE_TO_PFS = {
    "10ge2p1x710": "nic_pfs}= | 2",
    "40ge2p1xl710": "nic_pfs}= | 2",
    "25ge2p1xxv710": "nic_pfs}= | 2",
    "25ge2p1e810xxv": "nic_pfs}= | 2",
    "25ge2p1e822cq": "nic_pfs}= | 2",
    "25ge2p1e823c": "nic_pfs}= | 2",
    "100ge2p1e810cq": "nic_pfs}= | 2",
    "50ge1p1ena": "nic_pfs}= | 2",
    "100ge1p1ena": "nic_pfs}= | 2",
    "200ge1p1ena": "nic_pfs}= | 2",
    "100ge2p1cx556a": "nic_pfs}= | 2",
    "100ge2p1cx6dx": "nic_pfs}= | 2",
    "200ge2p1cx7veat": "nic_pfs}= | 2",
    "200ge6p3cx7veat": "nic_pfs}= | 6",
    "100ge2p1a063": "nic_pfs}= | 2",
    "1ge1p82540em": "nic_pfs}= | 2"
}

PERF_TYPE_TO_KEYWORD = {
    "mrr": "Traffic should pass with maximum rate",
    "ndrpdr": "Find NDR and PDR intervals using optimized search",
    "soak": "Find critical load using PLRsearch"
}

PERF_TYPE_TO_SUITE_DOC_VER = {
        "mrr": """fication:** In MaxReceivedRate tests TG sends traffic at \\
| ... | line rate and reports total received packets over trial period. \\""",
        "ndrpdr": """rification:** TG finds and reports throughput NDR (Non \\
| ... | Drop Rate) with zero packet loss tolerance and throughput PDR \\
| ... | (Partial Drop Rate) with non-zero packet loss tolerance (LT) \\
| ... | expressed in percentage of packets transmitted. NDR and PDR are \\
| ... | discovered for different Ethernet L2 frame sizes using MLRsearch \\
| ... | library.""",
        "soak": """rification:** TG sends traffic at dynamically computed \\
| ... | rate as PLRsearch algorithm gathers data and improves its estimate \\
| ... | of a rate at which a prescribed small fraction of packets \\
| ... | would be lost. After set time, the serarch stops \\
| ... | and the algorithm reports its current estimate. \\"""
}

PERF_TYPE_TO_TEMPLATE_DOC_VER = {
        "mrr": """Measure MaxReceivedRate for ${frame_size}B frames \\
| | ... | using burst trials throughput test. \\""",
        "ndrpdr": "Measure NDR and PDR values using MLRsearch algorithm.",
        "soak": "Estimate critical rate using PLRsearch algorithm. \\"
}
