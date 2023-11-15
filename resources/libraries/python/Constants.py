# Copyright (c) 2023 Cisco and/or its affiliates.
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
    prefixes = (u"FDIO_CSIT_", u"CSIT_", u"")
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
    env_str = get_str_from_env(env_var_names, u"")
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
    env_str = get_str_from_env(env_var_names, u"")
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
    env_str = get_str_from_env(env_var_names, u"").lower()
    return bool(env_str in (u"true", u"yes", u"y", u"1"))


def get_optimistic_bool_from_env(env_var_names):
    """Attempt to read bool from environment variable, assume True by default.

    Conversion is lenient and optimistic, only few strings are considered false.

    :param env_var_names: Base names of environment variable to attempt to read.
    :type env_var_names: str, or list of str, or tuple of str
    :returns: The value read, or True.
    :rtype: bool
    """
    env_str = get_str_from_env(env_var_names, u"").lower()
    return bool(env_str not in (u"false", u"no", u"n", u"0"))


class Constants:
    """Constants used in CSIT."""

    # Version for CSIT data model. See docs/model/.
    MODEL_VERSION = u"1.5.1"

    # Global off-switch in case JSON export is large or slow.
    EXPORT_JSON = get_optimistic_bool_from_env(u"EXPORT_JSON")

    # OpenVPP testing directory location at topology nodes
    REMOTE_FW_DIR = u"/tmp/openvpp-testing"

    # shell scripts location
    RESOURCES_LIB_SH = u"resources/libraries/bash"

    # python scripts location
    RESOURCES_LIB_PY = u"resources/libraries/python"

    # shell scripts location
    RESOURCES_TOOLS = u"resources/tools"

    # Python API provider location
    RESOURCES_PAPI_PROVIDER = u"resources/tools/papi/vpp_papi_provider.py"

    # Templates location
    RESOURCES_TPL = u"resources/templates"

    # Kubernetes templates location
    RESOURCES_TPL_K8S = u"resources/templates/kubernetes"

    # Container templates location
    RESOURCES_TPL_CONTAINER = u"resources/templates/container"

    # VPP Communications Library templates location
    RESOURCES_TPL_VCL = u"resources/templates/vcl"

    # VPP Communications Library templates location
    RESOURCES_TPL_TELEMETRY = u"resources/templates/telemetry"

    # VPP Communications Library LD_PRELOAD library
    VCL_LDPRELOAD_LIBRARY = u"/usr/lib/x86_64-linux-gnu/libvcl_ldpreload.so"

    # VPP service unit name
    VPP_UNIT = u"vpp"

    # Number of system CPU cores.
    CPU_CNT_SYSTEM = 1

    # Number of vswitch main thread CPU cores.
    CPU_CNT_MAIN = 1

    # QEMU binary path
    QEMU_BIN_PATH = u"/usr/bin"

    # QEMU VM kernel image path
    QEMU_VM_KERNEL = u"/opt/boot/vmlinuz"

    # QEMU VM kernel initrd path
    QEMU_VM_KERNEL_INITRD = u"/opt/boot/initrd.img"

    # QEMU VM nested image path
    QEMU_VM_IMAGE = u"/var/lib/vm/image.iso"

    # QEMU VM DPDK path
    QEMU_VM_DPDK = u"/opt/dpdk-23.07"

    # Docker container SUT image
    DOCKER_SUT_IMAGE_UBUNTU = u"csit_sut-ubuntu2204:local"

    # Docker container arm SUT image
    DOCKER_SUT_IMAGE_UBUNTU_ARM = u"csit_sut-ubuntu2204:local"

    # TRex install directory.
    TREX_INSTALL_DIR = u"/opt/trex-core-3.03"

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
    GRAPH_NODE_VARIANT = get_str_from_env(u"GRAPH_NODE_VARIANT", u"")

    # Default memory page size in case multiple configured in system
    DEFAULT_HUGEPAGE_SIZE = get_str_from_env(u"DEFAULT_HUGEPAGE_SIZE", u"2M")

    # Sysctl kernel.core_pattern
    KERNEL_CORE_PATTERN = u"/tmp/%p-%u-%g-%s-%t-%h-%e.core"

    # Core dump directory
    CORE_DUMP_DIR = u"/tmp"

    # Perf stat events (comma separated).
    PERF_STAT_EVENTS = get_str_from_env(
        u"PERF_STAT_EVENTS",
        u"cpu-clock,context-switches,cpu-migrations,page-faults,"
        u"cycles,instructions,branches,branch-misses,L1-icache-load-misses")

    # Equivalent to ~0 used in vpp code
    BITWISE_NON_ZERO = 0xffffffff

    # Default path to VPP API socket.
    SOCKSVR_PATH = u"/run/vpp/api.sock"

    # Default path to VPP CLI socket.
    SOCKCLI_PATH = u"/run/vpp/cli.sock"

    # Default path to VPP API Stats socket.
    SOCKSTAT_PATH = u"/run/vpp/stats.sock"

    # This MTU value is used to force VPP to fragment 1518B packet into two.
    MTU_FOR_FRAGMENTATION = 1043

    # Number of trials to execute in MRR test.
    PERF_TRIAL_MULTIPLICITY = get_int_from_env(u"PERF_TRIAL_MULTIPLICITY", 10)

    # Duration [s] of one trial in MRR test.
    PERF_TRIAL_DURATION = get_float_from_env(u"PERF_TRIAL_DURATION", 1.0)

    # Whether to use latency streams in main search trials.
    PERF_USE_LATENCY = get_pessimistic_bool_from_env(u"PERF_USE_LATENCY")

    # Duration of one latency-specific trial in NDRPDR test.
    PERF_TRIAL_LATENCY_DURATION = get_float_from_env(
        u"PERF_TRIAL_LATENCY_DURATION", 5.0)

    # For some testbeds TG takes longer than usual to start sending traffic.
    # This constant [s] allows longer wait, without affecting
    # the approximate duration. For example, use 0.098 for AWS.
    PERF_TRIAL_STL_DELAY = get_float_from_env(u"PERF_TRIAL_STL_DELAY", 0.0)

    # ASTF usually needs a different value for the delay.
    PERF_TRIAL_ASTF_DELAY = get_float_from_env(
        u"PERF_TRIAL_ASTF_DELAY", 0.112
    )

    # Number of data frames in TPUT transaction, used both by TCP and UDP.
    # The value should be 33 to keep historic continuity for UDP TPUT tests,
    # but we are limited by TRex window of 48 KiB, so for 9000B tests
    # it means we can send only 5 full data frames in a burst.
    # https://github.com/cisco-system-traffic-generator/
    # trex-core/blob/v2.88/src/44bsd/tcp_var.h#L896-L903
    ASTF_N_DATA_FRAMES = get_int_from_env(u"ASTF_N_DATA_FRAMES", 5)

    # Extended debug (incl. vpp packet trace, linux perf stat, ...).
    # Full list is available as suite variable (__init__.robot) or is
    # override by test.
    EXTENDED_DEBUG = get_pessimistic_bool_from_env(u"EXTENDED_DEBUG")

    # UUID string of DUT1 /tmp volume created outside of the
    # DUT1 docker in case of vpp-device test. ${EMPTY} value means that
    #  /tmp directory is inside the DUT1 docker.
    DUT1_UUID = get_str_from_env(u"DUT1_UUID", u"")

    # Global "kill switch" for CRC checking during runtime.
    FAIL_ON_CRC_MISMATCH = get_pessimistic_bool_from_env(
        u"FAIL_ON_CRC_MISMATCH"
    )

    # Default IP4 prefix length (if not defined in topology file)
    DEFAULT_IP4_PREFIX_LENGTH = u"24"

    # Maximum number of interfaces in a data path
    DATAPATH_INTERFACES_MAX = 100

    RSS_HASH_KEY = (
        "67C1206E82DA86E36B0645B99C79D8B5DF3BE4D16C33B69C4EC4EE0DF4263AB6AA54831F34B0EF5B761CD01B3C9CBE44629AA45C"
#        "3a5816cc34e6ee4126e43c6cdc1156a470d5d82bc79d712ee80f4569fd848d3c824047b5c9c7ae49292f44da5d1131d9d2b16656"
#        "61f459f66e5b0b52f696db5eb079e4f7842af4951e8f54d52b1b06c2f2873322eecf3b77951ffa616d6756123db9eb2ce89b60e1"
#        "4d9478f9b59a6fc6e06e751106d3a25a95401b3e726138440ded07f4a99dd66fe970b947581fd861c3d8158e65d7a55f7d07de77"
#        "b1c76767bc84f5f6164b3a121858519218cc529d73b5cbf190f04b93959518ec90f77350762971624368141f521adf9e9056001c"
#        "6954bde3d3cac7e37f6ea0b8410d386eedf3501543a938bdbf4c62abbea58bd6d2113ef9a110c2ac57586c07c02ed9e5bdb8ff58"

#        "6437018CE4409B91B95D597FB189A71D"
#        "A61CC60BB41B87BCDA9D7F98DC48A50B"
#        "361BD9B7CB115910084CF89E1652D579"
#        "72DCC160"
    )

    # Mapping from NIC name to its bps limit.
    NIC_NAME_TO_BPS_LIMIT = {
        u"Intel-X520-DA2": 10000000000,
        u"Intel-X710": 10000000000,
        u"Intel-XL710": 24500000000,
        u"Intel-XXV710": 24500000000,
        u"Intel-E810XXV": 24500000000,
        u"Intel-E822CQ": 24500000000,
        u"Intel-E823C": 24500000000,
        u"Intel-E810CQ": 100000000000,
        u"Mellanox-CX556A": 100000000000,
        u"Mellanox-CX6DX": 100000000000,
        u"Mellanox-CX7VEAT": 200000000000,
        u"Amazon-Nitro-50G": 10000000000,
        u"Amazon-Nitro-100G": 10000000000,
        u"Amazon-Nitro-200G": 16000000000,
        u"virtual": 100000000,
    }

    # Mapping from NIC name to its pps limit.
    NIC_NAME_TO_PPS_LIMIT = {
        u"Intel-X520-DA2": 14880952,
        u"Intel-X710": 14880952,
        u"Intel-XL710": 18750000,
        u"Intel-XXV710": 18750000,
        u"Intel-E810XXV": 29000000,
        u"Intel-E822CQ": 29000000,
        u"Intel-E823C": 29000000,
        u"Intel-E810CQ": 58500000,
        u"Mellanox-CX556A": 148809523,
        u"Mellanox-CX6DX": 148809523,
        u"Mellanox-CX7VEAT": 297619046,
        u"Amazon-Nitro-50G": 1500000,
        u"Amazon-Nitro-100G": 3000000,
        u"Amazon-Nitro-200G": 6000000,
        u"virtual": 14880952,
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
        "1ge1p82540em": "8250em",

    }

    # Not each driver is supported by each NIC.
    NIC_NAME_TO_DRIVER = {
        u"Intel-X520-DA2": [u"vfio-pci", u"af_xdp"],
        u"Intel-X710": [u"vfio-pci", u"avf", u"af_xdp"],
        u"Intel-XL710": [u"vfio-pci", u"avf", u"af_xdp"],
        u"Intel-XXV710": [u"vfio-pci", u"avf", u"af_xdp"],
        u"Intel-E810XXV": [u"vfio-pci", u"avf", u"af_xdp"],
        u"Intel-E822CQ": [u"vfio-pci", u"avf", u"af_xdp"],
        u"Intel-E823C": [u"vfio-pci", u"avf", u"af_xdp"],
        u"Intel-E810CQ": [u"vfio-pci", u"avf", u"af_xdp"],
        u"Amazon-Nitro-50G": [u"vfio-pci"],
        u"Amazon-Nitro-100G": [u"vfio-pci"],
        u"Amazon-Nitro-200G": [u"vfio-pci"],
        u"Mellanox-CX556A": [u"rdma-core", u"mlx5_core", u"af_xdp"],
        u"Mellanox-CX6DX": [u"rdma-core", u"mlx5_core", u"af_xdp"],
        u"Mellanox-CX7VEAT": [u"rdma-core", u"mlx5_core", u"af_xdp"],
        "virtual": ["vfio-pci"],
    }

    # Each driver needs different plugin to work.
    NIC_DRIVER_TO_PLUGINS = {
        u"vfio-pci": u"dpdk_plugin.so",
        u"avf": u"avf_plugin.so",
        u"rdma-core": u"rdma_plugin.so",
        u"mlx5_core": u"dpdk_plugin.so",
        u"af_xdp": u"af_xdp_plugin.so",
    }

    # Tags to differentiate tests for different NIC driver.
    NIC_DRIVER_TO_TAG = {
        u"vfio-pci": u"DRV_VFIO_PCI",
        u"avf": u"DRV_AVF",
        u"rdma-core": u"DRV_RDMA_CORE",
        u"mlx5_core": u"DRV_MLX5_CORE",
        u"af_xdp": u"DRV_AF_XDP",
    }

    # Suite names have to be different, add prefix.
    NIC_DRIVER_TO_SUITE_PREFIX = {
        u"vfio-pci": u"",
        u"avf": u"avf-",
        u"rdma-core": u"rdma-",
        u"mlx5_core": u"mlx5-",
        u"af_xdp": u"af-xdp-",
    }

    # Number of virtual functions of physical nic.
    NIC_DRIVER_TO_VFS = {
        u"vfio-pci": u"nic_vfs}= | 0",
        u"avf": u"nic_vfs}= | 1",
        u"rdma-core": u"nic_vfs}= | 0",
        u"mlx5_core": u"nic_vfs}= | 0",
        u"af_xdp": u"nic_vfs}= | 0",
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

    # Not each driver is supported by each NIC.
    DPDK_NIC_NAME_TO_DRIVER = {
        u"Intel-X520-DA2": [u"vfio-pci"],
        u"Intel-X710": [u"vfio-pci"],
        u"Intel-XL710": [u"vfio-pci"],
        u"Intel-XXV710": [u"vfio-pci"],
        u"Intel-E810XXV": [u"vfio-pci"],
        u"Intel-E822CQ": [u"vfio-pci"],
        u"Intel-E823C": [u"vfio-pci"],
        u"Intel-E810CQ": [u"vfio-pci"],
        u"Amazon-Nitro-50G": [u"vfio-pci"],
        u"Amazon-Nitro-100G": [u"vfio-pci"],
        u"Amazon-Nitro-200G": [u"vfio-pci"],
        u"Mellanox-CX556A": [u"mlx5_core"],
        u"Mellanox-CX6DX": [u"mlx5_core"],
        u"Mellanox-CX7VEAT": [u"mlx5_core"],
        "virtual": ["vfio-pci"],
    }

    # Tags to differentiate tests for different NIC driver.
    DPDK_NIC_DRIVER_TO_TAG = {
        u"vfio-pci": u"DRV_VFIO_PCI",
        u"mlx5_core": u"DRV_MLX5_CORE",
    }

    # Suite names have to be different, add prefix.
    DPDK_NIC_DRIVER_TO_SUITE_PREFIX = {
        u"vfio-pci": u"",
        u"mlx5_core": u"mlx5-",
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
        u"Intel-E810CQ": u"HW_4xxx",
        u"Intel-E822CQ": u"HW_C4xxx",
        u"Intel-E823C": u"HW_C4xxx",
        u"Intel-X710": u"HW_DH895xcc",
        u"Intel-XL710": u"HW_DH895xcc",
    }

    DEVICE_TYPE_TO_KEYWORD = {
        u"scapy": None
    }

    PERF_TYPE_TO_KEYWORD = {
        u"mrr": u"Traffic should pass with maximum rate",
        u"ndrpdr": u"Find NDR and PDR intervals using optimized search",
        u"soak": u"Find critical load using PLRsearch",
    }

    PERF_TYPE_TO_SUITE_DOC_VER = {
        u"mrr": u'''fication:** In MaxReceivedRate tests TG sends traffic at \\
| ... | line rate and reports total received packets over trial period. \\''',
        u"ndrpdr": u'''rification:** TG finds and reports throughput NDR (Non \\
| ... | Drop Rate) with zero packet loss tolerance and throughput PDR \\
| ... | (Partial Drop Rate) with non-zero packet loss tolerance (LT) \\
| ... | expressed in percentage of packets transmitted. NDR and PDR are \\
| ... | discovered for different Ethernet L2 frame sizes using MLRsearch \\
| ... | library.''',
        u"soak": u'''rification:** TG sends traffic at dynamically computed \\
| ... | rate as PLRsearch algorithm gathers data and improves its estimate \\
| ... | of a rate at which a prescribed small fraction of packets \\
| ... | would be lost. After set time, the serarch stops \\
| ... | and the algorithm reports its current estimate. \\''',
    }

    PERF_TYPE_TO_TEMPLATE_DOC_VER = {
        u"mrr": u'''Measure MaxReceivedRate for ${frame_size}B frames \\
| | ... | using burst trials throughput test. \\''',
        u"ndrpdr": u"Measure NDR and PDR values using MLRsearch algorithm.",
        u"soak": u"Estimate critical rate using PLRsearch algorithm. \\",
    }
