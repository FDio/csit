# Copyright (c) 2024 Cisco and/or its affiliates.
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

"""Constants used in CSIT.

"Constant" means a value that keeps its value since initialization. The value
does not need to be hard coded here, but can be read from environment variables.
"""


import os


def get_str_from_env(env_var_names, default_value):
    """Attempt to read string from environment variable, return that or default.

    If environment variable exists, but is empty (and default is not),
    empty string is returned.

    Several environment variable names are examined, as CSIT currently supports
    a mix of naming conventions.
    Here "several" means there are hard coded prefixes to try,
    and env_var_names itself can be single name, or a list or a tuple of names.

    :param env_var_names: Base names of environment variable to attempt to read.
    :param default_value: Value to return if the env var does not exist.
    :type env_var_names: str, or list of str, or tuple of str
    :type default_value: str
    :returns: The value read, or default value.
    :rtype: str
    """
    prefixes = ("FDIO_CSIT_", "CSIT_", "")
    if not isinstance(env_var_names, (list, tuple)):
        env_var_names = [env_var_names]
    for name in env_var_names:
        for prefix in prefixes:
            value = os.environ.get(prefix + name, None)
            if value is not None:
                return value
    return default_value


def get_int_from_env(env_var_names, default_value):
    """Attempt to read int from environment variable, return that or default.

    String value is read, default is returned also if conversion fails.

    :param env_var_names: Base names of environment variable to attempt to read.
    :param default_value: Value to return if read or conversion fails.
    :type env_var_names: str, or list of str, or tuple of str
    :type default_value: int
    :returns: The value read, or default value.
    :rtype: int
    """
    env_str = get_str_from_env(env_var_names, "")
    try:
        return int(env_str)
    except ValueError:
        return default_value


def get_float_from_env(env_var_names, default_value):
    """Attempt to read float from environment variable, return that or default.

    String value is read, default is returned also if conversion fails.

    :param env_var_names: Base names of environment variable to attempt to read.
    :param default_value: Value to return if read or conversion fails.
    :type env_var_names: str, or list of str, or tuple of str
    :type default_value: float
    :returns: The value read, or default value.
    :rtype: float
    """
    env_str = get_str_from_env(env_var_names, "")
    try:
        return float(env_str)
    except ValueError:
        return default_value


def get_pessimistic_bool_from_env(env_var_names):
    """Attempt to read bool from environment variable, assume False by default.

    Conversion is lenient and pessimistic, only few strings are considered true.

    :param env_var_names: Base names of environment variable to attempt to read.
    :type env_var_names: str, or list of str, or tuple of str
    :returns: The value read, or False.
    :rtype: bool
    """
    env_str = get_str_from_env(env_var_names, "").lower()
    return bool(env_str in ("true", "yes", "y", "1"))


def get_optimistic_bool_from_env(env_var_names):
    """Attempt to read bool from environment variable, assume True by default.

    Conversion is lenient and optimistic, only few strings are considered false.

    :param env_var_names: Base names of environment variable to attempt to read.
    :type env_var_names: str, or list of str, or tuple of str
    :returns: The value read, or True.
    :rtype: bool
    """
    env_str = get_str_from_env(env_var_names, "").lower()
    return bool(env_str not in ("false", "no", "n", "0"))


class Constants:
    """Constants used in CSIT."""

    # Version for CSIT data model. See docs/model/.
    MODEL_VERSION = "1.5.1"

    # Global off-switch in case JSON export is large or slow.
    EXPORT_JSON = get_optimistic_bool_from_env("EXPORT_JSON")

    # OpenVPP testing directory location at topology nodes
    REMOTE_FW_DIR = "/tmp/openvpp-testing"

    # shell scripts location
    RESOURCES_LIB_SH = "resources/libraries/bash"

    # python scripts location
    RESOURCES_LIB_PY = "resources/libraries/python"

    # shell scripts location
    RESOURCES_TOOLS = "resources/tools"

    # Python API provider location
    RESOURCES_PAPI_PROVIDER = "resources/tools/papi/vpp_papi_provider.py"

    # Templates location
    RESOURCES_TPL = "resources/templates"

    # Kubernetes templates location
    RESOURCES_TPL_K8S = "resources/templates/kubernetes"

    # Container templates location
    RESOURCES_TPL_CONTAINER = "resources/templates/container"

    # VPP Communications Library templates location
    RESOURCES_TPL_VCL = "resources/templates/vcl"

    # VPP Communications Library templates location
    RESOURCES_TPL_TELEMETRY = "resources/templates/telemetry"

    # VPP Communications Library LD_PRELOAD library
    VCL_LDPRELOAD_LIBRARY = "/usr/lib/x86_64-linux-gnu/libvcl_ldpreload.so"

    # VPP service unit name
    VPP_UNIT = "vpp"

    # Number of system CPU cores.
    CPU_CNT_SYSTEM = 1

    # Number of vswitch main thread CPU cores.
    CPU_CNT_MAIN = 1

    # QEMU binary path
    QEMU_BIN_PATH = "/usr/bin"

    # QEMU VM kernel image path
    QEMU_VM_KERNEL = "/opt/boot/vmlinuz"

    # QEMU VM kernel initrd path
    QEMU_VM_KERNEL_INITRD = "/opt/boot/initrd.img"

    # QEMU VM nested image path
    QEMU_VM_IMAGE = "/var/lib/vm/image.iso"

    # QEMU VM DPDK path
    QEMU_VM_DPDK = "/opt/dpdk-23.11"

    # Docker container SUT image
    DOCKER_SUT_IMAGE_UBUNTU = "csit_sut-ubuntu2204:local"

    # Docker container arm SUT image
    DOCKER_SUT_IMAGE_UBUNTU_ARM = "csit_sut-ubuntu2204:local"

    # TRex install directory.
    TREX_INSTALL_DIR = "/opt/trex-core-3.03"

    # TRex pcap files directory.
    TREX_PCAP_DIR = f"{TREX_INSTALL_DIR}/scripts/avl"

    # TRex limit memory.
    TREX_LIMIT_MEMORY = get_int_from_env("TREX_LIMIT_MEMORY", 8192)

    # TRex limit memory in case multiple dual interfaces configurations.
    TREX_LIMIT_MEMORY_MULTI = get_int_from_env("TREX_LIMIT_MEMORY_MULTI", 16384)

    # TRex number of cores.
    TREX_CORE_COUNT = get_int_from_env("TREX_CORE_COUNT", 16)

    # TRex number of cores in case multiple dual interface configurations.
    TREX_CORE_COUNT_MULTI = get_int_from_env("TREX_CORE_COUNT_MULTI", 8)

    # TRex set number of RX/TX descriptors.
    # Set to 0 to use default values.
    TREX_TX_DESCRIPTORS_COUNT = get_int_from_env(
        "TREX_TX_DESCRIPTORS_COUNT", 0
    )

    TREX_RX_DESCRIPTORS_COUNT = get_int_from_env(
        "TREX_RX_DESCRIPTORS_COUNT", 0
    )

    # Trex force start regardless ports state.
    TREX_SEND_FORCE = get_pessimistic_bool_from_env("TREX_SEND_FORCE")

    # TRex extra commandline arguments.
    TREX_EXTRA_CMDLINE = get_str_from_env(
        "TREX_EXTRA_CMDLINE", "--mbuf-factor 32"
    )

    # TRex port driver default vfio-pci or set to igb_uio.
    TREX_PORT_DRIVER = get_str_from_env(
        "TREX_PORT_DRIVER", "vfio-pci"
    )

    # Graph node variant value
    GRAPH_NODE_VARIANT = get_str_from_env("GRAPH_NODE_VARIANT", "")

    # Default memory page size in case multiple configured in system
    DEFAULT_HUGEPAGE_SIZE = get_str_from_env("DEFAULT_HUGEPAGE_SIZE", "2M")

    # Sysctl kernel.core_pattern
    KERNEL_CORE_PATTERN = "/tmp/%p-%u-%g-%s-%t-%h-%e.core"

    # Core dump directory
    CORE_DUMP_DIR = "/tmp"

    # Perf stat events (comma separated).
    PERF_STAT_EVENTS = get_str_from_env(
        "PERF_STAT_EVENTS",
        "cpu-clock,context-switches,cpu-migrations,page-faults,"
        "cycles,instructions,branches,branch-misses,L1-icache-load-misses")

    # Equivalent to ~0 used in vpp code
    BITWISE_NON_ZERO = 0xffffffff

    # Default path to VPP API socket.
    SOCKSVR_PATH = "/run/vpp/api.sock"

    # Default path to VPP CLI socket.
    SOCKCLI_PATH = "/run/vpp/cli.sock"

    # Default path to VPP API Stats socket.
    SOCKSTAT_PATH = "/run/vpp/stats.sock"

    # This MTU value is used to force VPP to fragment 1518B packet into two.
    MTU_FOR_FRAGMENTATION = 1043

    # Number of trials to execute in MRR test.
    PERF_TRIAL_MULTIPLICITY = get_int_from_env("PERF_TRIAL_MULTIPLICITY", 10)

    # Duration [s] of one trial in MRR test.
    PERF_TRIAL_DURATION = get_float_from_env("PERF_TRIAL_DURATION", 1.0)

    # Whether to use latency streams in main search trials.
    PERF_USE_LATENCY = get_pessimistic_bool_from_env("PERF_USE_LATENCY")

    # Duration of one latency-specific trial in NDRPDR test.
    PERF_TRIAL_LATENCY_DURATION = get_float_from_env(
        "PERF_TRIAL_LATENCY_DURATION", 5.0)

    # For some testbeds TG takes longer than usual to start sending traffic.
    # This constant [s] allows longer wait, without affecting
    # the approximate duration. For example, use 0.098 for AWS.
    PERF_TRIAL_STL_DELAY = get_float_from_env("PERF_TRIAL_STL_DELAY", 0.0)

    # ASTF usually needs a different value for the delay.
    PERF_TRIAL_ASTF_DELAY = get_float_from_env(
        "PERF_TRIAL_ASTF_DELAY", 0.112
    )

    # Number of data frames in TPUT transaction, used both by TCP and UDP.
    # The value should be 33 to keep historic continuity for UDP TPUT tests,
    # but we are limited by TRex window of 48 KiB, so for 9000B tests
    # it means we can send only 5 full data frames in a burst.
    # https://github.com/cisco-system-traffic-generator/
    # trex-core/blob/v2.88/src/44bsd/tcp_var.h#L896-L903
    ASTF_N_DATA_FRAMES = get_int_from_env("ASTF_N_DATA_FRAMES", 5)

    # Extended debug (incl. vpp packet trace, linux perf stat, ...).
    # Full list is available as suite variable (__init__.robot) or is
    # override by test.
    EXTENDED_DEBUG = get_pessimistic_bool_from_env("EXTENDED_DEBUG")

    # UUID string of DUT1 /tmp volume created outside of the
    # DUT1 docker in case of vpp-device test. ${EMPTY} value means that
    #  /tmp directory is inside the DUT1 docker.
    DUT1_UUID = get_str_from_env("DUT1_UUID", "")

    # Global "kill switch" for CRC checking during runtime.
    FAIL_ON_CRC_MISMATCH = get_pessimistic_bool_from_env(
        "FAIL_ON_CRC_MISMATCH"
    )

    # Default IP4 prefix length (if not defined in topology file)
    DEFAULT_IP4_PREFIX_LENGTH = "24"

    # Maximum number of interfaces in a data path
    DATAPATH_INTERFACES_MAX = 100

    # Whether to gather (before config) and dump (after test) VPP API trace.
    # Helpful when debugging but slow in production (e.g. scale tests),
    # thus off by default.
    USE_VPP_API_TRACE = get_optimistic_bool_from_env(
        "USE_VPP_API_TRACE"
    )

    # Mapping from NIC name to its bps limit.
    NIC_NAME_TO_BPS_LIMIT = {
        "Intel-X520-DA2": 10000000000,
        "Intel-X710": 10000000000,
        "Intel-XL710": 24500000000,
        "Intel-XXV710": 24500000000,
        "Intel-E810XXV": 24500000000,
        "Intel-E822CQ": 24500000000,
        "Intel-E823C": 24500000000,
        "Intel-E810CQ": 100000000000,
        "Mellanox-CX556A": 100000000000,
        "Mellanox-CX6DX": 100000000000,
        "Mellanox-CX7VEAT": 200000000000,
        "Amazon-Nitro-50G": 10000000000,
        "Amazon-Nitro-100G": 10000000000,
        "Amazon-Nitro-200G": 16000000000,
        "virtual": 100000000,
    }

    # Mapping from NIC name to its pps limit.
    NIC_NAME_TO_PPS_LIMIT = {
        "Intel-X520-DA2": 14880952,
        "Intel-X710": 14880952,
        "Intel-XL710": 18750000,
        "Intel-XXV710": 18750000,
        "Intel-E810XXV": 29000000,
        "Intel-E822CQ": 29000000,
        "Intel-E823C": 29000000,
        "Intel-E810CQ": 58500000,
        "Mellanox-CX556A": 148809523,
        "Mellanox-CX6DX": 148809523,
        "Mellanox-CX7VEAT": 297619046,
        "Amazon-Nitro-50G": 1500000,
        "Amazon-Nitro-100G": 3000000,
        "Amazon-Nitro-200G": 6000000,
        "virtual": 14880952,
    }

    # Suite file names use codes for NICs.
    NIC_NAME_TO_CODE = {
        "Intel-X520-DA2": "10ge2p1x520",
        "Intel-X710": "10ge2p1x710",
        "Intel-XL710": "40ge2p1xl710",
        "Intel-XXV710": "25ge2p1xxv710",
        "Intel-E810XXV": "25ge2p1e810xxv",
        "Intel-E822CQ": "25ge2p1e822cq",
        "Intel-E823C": "25ge2p1e823c",
        "Intel-E810CQ": "100ge2p1e810cq",
        "Amazon-Nitro-50G": "50ge1p1ena",
        "Amazon-Nitro-100G": "100ge1p1ena",
        "Amazon-Nitro-200G": "200ge1p1ena",
        "Mellanox-CX556A": "100ge2p1cx556a",
        "Mellanox-CX6DX": "100ge2p1cx6dx",
        "Mellanox-CX7VEAT": "200ge2p1cx7veat",
        "Mellanox-CX7VEAT": "200ge6p3cx7veat",
        "virtual": "1ge1p82540em",
    }
    NIC_CODE_TO_NAME = {
        "10ge2p1x520": "Intel-X520-DA2",
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
        "1ge1p82540em": "virtual",
    }

    # Shortened lowercase NIC model name, useful for presentation.
    NIC_CODE_TO_SHORT_NAME = {
        "10ge2p1x520": "x520",
        "10ge2p1x710": "x710",
        "40ge2p1xl710": "xl710",
        "25ge2p1xxv710": "xxv710",
        "25ge2p1e810xxv": "e810xxv",
        "25ge2p1e822cq": "e822cq",
        "25ge2p1e823c": "e823c",
        "100ge2p1e810cq": "e810cq",
        "50ge1p1ena": "ena",
        "100ge1p1ena": "ena100",
        "200ge1p1ena": "ena200",
        "100ge2p1cx556a": "cx556a",
        "100ge2p1cx6dx": "cx6dx",
        "200ge2p1cx7veat": "cx7veat",
        "200ge6p3cx7veat": "cx7veat",
        "1ge1p82540em": "82540em",
    }

    # Not each driver is supported by each NIC.
    NIC_NAME_TO_DRIVER = {
        "Intel-X520-DA2": ["vfio-pci", "af_xdp"],
        "Intel-X710": ["vfio-pci", "avf", "af_xdp"],
        "Intel-XL710": ["vfio-pci", "avf", "af_xdp"],
        "Intel-XXV710": ["vfio-pci", "avf", "af_xdp"],
        "Intel-E810XXV": ["vfio-pci", "avf", "af_xdp"],
        "Intel-E822CQ": ["vfio-pci", "avf", "af_xdp"],
        "Intel-E823C": ["vfio-pci", "avf", "af_xdp"],
        "Intel-E810CQ": ["vfio-pci", "avf", "af_xdp"],
        "Amazon-Nitro-50G": ["vfio-pci"],
        "Amazon-Nitro-100G": ["vfio-pci"],
        "Amazon-Nitro-200G": ["vfio-pci"],
        "Mellanox-CX556A": ["rdma-core", "mlx5_core", "af_xdp"],
        "Mellanox-CX6DX": ["rdma-core", "mlx5_core", "af_xdp"],
        "Mellanox-CX7VEAT": ["rdma-core", "mlx5_core", "af_xdp"],
        "virtual": ["vfio-pci"],
    }

    # Each driver needs different plugin to work.
    NIC_DRIVER_TO_PLUGINS = {
        "vfio-pci": "dpdk_plugin.so",
        "avf": "avf_plugin.so",
        "rdma-core": "rdma_plugin.so",
        "mlx5_core": "dpdk_plugin.so",
        "af_xdp": "af_xdp_plugin.so",
    }

    # Tags to differentiate tests for different NIC driver.
    NIC_DRIVER_TO_TAG = {
        "vfio-pci": "DRV_VFIO_PCI",
        "avf": "DRV_AVF",
        "rdma-core": "DRV_RDMA_CORE",
        "mlx5_core": "DRV_MLX5_CORE",
        "af_xdp": "DRV_AF_XDP",
    }

    # Suite names have to be different, add prefix.
    NIC_DRIVER_TO_SUITE_PREFIX = {
        "vfio-pci": "",
        "avf": "avf-",
        "rdma-core": "rdma-",
        "mlx5_core": "mlx5-",
        "af_xdp": "af-xdp-",
    }

    # Number of virtual functions of physical nic.
    NIC_DRIVER_TO_VFS = {
        "vfio-pci": "nic_vfs}= | 0",
        "avf": "nic_vfs}= | 1",
        "rdma-core": "nic_vfs}= | 0",
        "mlx5_core": "nic_vfs}= | 0",
        "af_xdp": "nic_vfs}= | 0",
    }

    # Number of physical interfaces of physical nic.
    NIC_CODE_TO_PFS = {
        "10ge2p1x520": "nic_pfs}= | 2",
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
        "1ge1p82540em": "nic_pfs}= | 2",
    }

    NIC_CODE_TO_CORESCALE = {
        "10ge2p1x520": 1,
        "10ge2p1x710": 1,
        "40ge2p1xl710": 1,
        "25ge2p1xxv710": 1,
        "25ge2p1e810xxv": 1,
        "25ge2p1e822cq": 1,
        "25ge2p1e823c": 1,
        "100ge2p1e810cq": 1,
        "50ge1p1ena": 1,
        "100ge1p1ena": 1,
        "200ge1p1ena": 1,
        "100ge2p1cx556a": 1,
        "100ge2p1cx6dx": 1,
        "200ge2p1cx7veat": 1,
        "200ge6p3cx7veat": 3,
        "1ge1p82540em": 1,
    }

    # Not each driver is supported by each NIC.
    DPDK_NIC_NAME_TO_DRIVER = {
        "Intel-X520-DA2": ["vfio-pci"],
        "Intel-X710": ["vfio-pci"],
        "Intel-XL710": ["vfio-pci"],
        "Intel-XXV710": ["vfio-pci"],
        "Intel-E810XXV": ["vfio-pci"],
        "Intel-E822CQ": ["vfio-pci"],
        "Intel-E823C": ["vfio-pci"],
        "Intel-E810CQ": ["vfio-pci"],
        "Amazon-Nitro-50G": ["vfio-pci"],
        "Amazon-Nitro-100G": ["vfio-pci"],
        "Amazon-Nitro-200G": ["vfio-pci"],
        "Mellanox-CX556A": ["mlx5_core"],
        "Mellanox-CX6DX": ["mlx5_core"],
        "Mellanox-CX7VEAT": ["mlx5_core"],
        "virtual": ["vfio-pci"],
    }

    # Tags to differentiate tests for different NIC driver.
    DPDK_NIC_DRIVER_TO_TAG = {
        "vfio-pci": "DRV_VFIO_PCI",
        "mlx5_core": "DRV_MLX5_CORE",
    }

    # Suite names have to be different, add prefix.
    DPDK_NIC_DRIVER_TO_SUITE_PREFIX = {
        "vfio-pci": "",
        "mlx5_core": "mlx5-",
    }

    # Some identifiers constructed from suite names
    # have to be independent of NIC driver used.
    # In order to remove or reject the NIC driver part,
    # it is useful to have a list of such prefixes precomputed.
    FORBIDDEN_SUITE_PREFIX_LIST = [
        prefix for prefix in NIC_DRIVER_TO_SUITE_PREFIX.values() if prefix
    ]
    FORBIDDEN_SUITE_PREFIX_LIST += [
        prefix for prefix in DPDK_NIC_DRIVER_TO_SUITE_PREFIX.values() if prefix
    ]

    # TODO CSIT-1481: Crypto HW should be read from topology file instead.
    NIC_NAME_TO_CRYPTO_HW = {
        "Intel-E810CQ": "HW_4xxx",
        "Intel-E822CQ": "HW_C4xxx",
        "Intel-E823C": "HW_C4xxx",
        "Intel-X710": "HW_DH895xcc",
        "Intel-XL710": "HW_DH895xcc",
    }

    DEVICE_TYPE_TO_KEYWORD = {
        "scapy": None
    }

    PERF_TYPE_TO_KEYWORD = {
        "mrr": "Traffic should pass with maximum rate",
        "ndrpdr": "Find NDR and PDR intervals using optimized search",
        "soak": "Find critical load using PLRsearch",
    }

    PERF_TYPE_TO_SUITE_DOC_VER = {
        "mrr": u'''fication:** In MaxReceivedRate tests TG sends traffic at \\
| ... | line rate and reports total received packets over trial period. \\''',
        "ndrpdr": u'''rification:** TG finds and reports throughput NDR (Non \\
| ... | Drop Rate) with zero packet loss tolerance and throughput PDR \\
| ... | (Partial Drop Rate) with non-zero packet loss tolerance (LT) \\
| ... | expressed in percentage of packets transmitted. NDR and PDR are \\
| ... | discovered for different Ethernet L2 frame sizes using MLRsearch \\
| ... | library.''',
        "soak": u'''rification:** TG sends traffic at dynamically computed \\
| ... | rate as PLRsearch algorithm gathers data and improves its estimate \\
| ... | of a rate at which a prescribed small fraction of packets \\
| ... | would be lost. After set time, the serarch stops \\
| ... | and the algorithm reports its current estimate. \\''',
    }

    PERF_TYPE_TO_TEMPLATE_DOC_VER = {
        "mrr": u'''Measure MaxReceivedRate for ${frame_size}B frames \\
| | ... | using burst trials throughput test. \\''',
        "ndrpdr": "Measure NDR and PDR values using MLRsearch algorithm.",
        "soak": "Estimate critical rate using PLRsearch algorithm. \\",
    }
