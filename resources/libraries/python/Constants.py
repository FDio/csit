# Copyright (c) 2020 Cisco and/or its affiliates.
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
    """Constants used in CSIT.

    TODO: Yaml files are easier for humans to edit.
    Figure out how to set the attributes by parsing a file
    that works regardless of current working directory.
    """

    # OpenVPP testing directory location at topology nodes
    REMOTE_FW_DIR = u"/tmp/openvpp-testing"

    # shell scripts location
    RESOURCES_LIB_SH = u"resources/libraries/bash"

    # Python API provider location
    RESOURCES_PAPI_PROVIDER = u"resources/tools/papi/vpp_papi_provider.py"

    # vat templates location
    RESOURCES_TPL_VAT = u"resources/templates/vat"

    # Kubernetes templates location
    RESOURCES_TPL_K8S = u"resources/templates/kubernetes"

    # KernelVM templates location
    RESOURCES_TPL_VM = u"resources/templates/vm"

    # Container templates location
    RESOURCES_TPL_CONTAINER = u"resources/templates/container"

    # VPP Communications Library templates location
    RESOURCES_TPL_VCL = u"resources/templates/vcl"

    # HTTP Server www root directory
    RESOURCES_TP_WRK_WWW = u"resources/traffic_profiles/wrk/www"

    # VPP Communications Library LD_PRELOAD library
    VCL_LDPRELOAD_LIBRARY = u"/usr/lib/x86_64-linux-gnu/libvcl_ldpreload.so"

    # OpenVPP VAT binary name
    VAT_BIN_NAME = u"vpp_api_test"

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
    QEMU_VM_IMAGE = u"/var/lib/vm/vhost-nested.img"

    # QEMU VM DPDK path
    QEMU_VM_DPDK = u"/opt/dpdk-stable-19.08.2"

    # Docker container SUT image
    DOCKER_SUT_IMAGE_UBUNTU = u"snergster/csit-sut:latest"

    # Docker container arm SUT image
    DOCKER_SUT_IMAGE_UBUNTU_ARM = u"snergster/csit-arm-sut:latest"

    # TRex install directory
    TREX_INSTALL_DIR = u"/opt/trex-core-2.73"

    # TRex limit memory.
    TREX_LIMIT_MEMORY = get_int_from_env(u"TREX_LIMIT_MEMORY", 4096)

    # TRex number of cores
    TREX_CORE_COUNT = get_int_from_env(u"TREX_CORE_COUNT", 7)

    # Trex force start regardles ports state
    TREX_SEND_FORCE = get_pessimistic_bool_from_env(u"TREX_SEND_FORCE")

    # TRex extra commandline arguments
    TREX_EXTRA_CMDLINE = get_str_from_env(u"TREX_EXTRA_CMDLINE", u"")

    # Sysctl kernel.core_pattern
    KERNEL_CORE_PATTERN = u"/tmp/%p-%u-%g-%s-%t-%h-%e.core"

    # Core dump directory
    CORE_DUMP_DIR = u"/tmp"

    # Equivalent to ~0 used in vpp code
    BITWISE_NON_ZERO = 0xffffffff

    # Default path to VPP API socket.
    SOCKSVR_PATH = u"/run/vpp/api.sock"

    # Number of trials to execute in MRR test.
    PERF_TRIAL_MULTIPLICITY = get_int_from_env(u"PERF_TRIAL_MULTIPLICITY", 10)

    # Duration of one trial in MRR test.
    PERF_TRIAL_DURATION = get_float_from_env(u"PERF_TRIAL_DURATION", 1.0)

    # Duration of one latency-specific trial in NDRPDR test.
    PERF_TRIAL_LATENCY_DURATION = get_float_from_env(
        u"PERF_TRIAL_LATENCY_DURATION", 5.0)

    # UUID string of DUT1 /tmp volume created outside of the
    # DUT1 docker in case of vpp-device test. ${EMPTY} value means that
    #  /tmp directory is inside the DUT1 docker.
    DUT1_UUID = get_str_from_env(u"DUT1_UUID", u"")

    # Default path to VPP API Stats socket.
    SOCKSTAT_PATH = u"/run/vpp/stats.sock"

    # Global "kill switch" for CRC checking during runtime.
    FAIL_ON_CRC_MISMATCH = get_pessimistic_bool_from_env(
        u"FAIL_ON_CRC_MISMATCH"
    )

    # Default IP4 prefix length (if not defined in topology file)
    DEFAULT_IP4_PREFIX_LENGTH = u"24"

    # Maximum number of interfaces in a data path
    DATAPATH_INTERFACES_MAX = 100

    # Mapping from NIC name to its bps limit.
    NIC_NAME_TO_BPS_LIMIT = {
        u"Cisco-VIC-1227": 10000000000,
        u"Cisco-VIC-1385": 24500000000,
        u"Intel-X520-DA2": 10000000000,
        u"Intel-X553": 10000000000,
        u"Intel-X710": 10000000000,
        u"Intel-XL710": 24500000000,
        u"Intel-XXV710": 24500000000,
        u"Mellanox-CX556A": 100000000000,
        u"Amazon-Nitro-50G": 10000000000,
        u"virtual": 100000000,
    }

    # Mapping from NIC name to its pps limit.
    NIC_NAME_TO_PPS_LIMIT = {
        u"Cisco-VIC-1227": 14880952,
        u"Cisco-VIC-1385": 18750000,
        u"Intel-X520-DA2": 14880952,
        u"Intel-X553": 14880952,
        u"Intel-X710": 14880952,
        u"Intel-XL710": 18750000,
        u"Intel-XXV710": 18750000,
        u"Mellanox-CX556A": 60000000, # 148809523,
        u"Amazon-Nitro-50G": 1500000,
        u"virtual": 14880952,
    }

    # Suite file names use codes for NICs.
    NIC_NAME_TO_CODE = {
        u"Cisco-VIC-1227": u"10ge2p1vic1227",
        u"Cisco-VIC-1385": u"40ge2p1vic1385",
        u"Intel-X520-DA2": u"10ge2p1x520",
        u"Intel-X553": u"10ge2p1x553",
        u"Intel-X710": u"10ge2p1x710",
        u"Intel-XL710": u"40ge2p1xl710",
        u"Intel-XXV710": u"25ge2p1xxv710",
        u"Mellanox-CX556A": u"100ge2p1cx556a",
    }

    # Not each driver is supported by each NIC.
    NIC_NAME_TO_DRIVER = {
        u"Cisco-VIC-1227": [u"vfio-pci"],
        u"Cisco-VIC-1385": [u"vfio-pci"],
        u"Intel-X520-DA2": [u"vfio-pci"],
        u"Intel-X553": [u"vfio-pci"],
        u"Intel-X710": [u"vfio-pci", u"avf"],
        u"Intel-XL710": [u"vfio-pci", u"avf"],
        u"Intel-XXV710": [u"vfio-pci", u"avf"],
        u"Mellanox-CX556A": [u"rdma-core"],
    }

    # Each driver needs different prugin to work.
    NIC_DRIVER_TO_PLUGINS = {
        u"vfio-pci": u"dpdk_plugin.so",
        u"avf": u"avf_plugin.so",
        u"rdma-core": u"rdma_plugin.so",
    }

    # Tags to differentiate tests for different NIC driver.
    NIC_DRIVER_TO_TAG = {
        u"vfio-pci": u"DRV_VFIO_PCI",
        u"avf": u"DRV_AVF",
        u"rdma-core": u"DRV_RDMA_CORE",
    }

    # Suite names have to be different, add prefix.
    NIC_DRIVER_TO_SUITE_PREFIX = {
        u"vfio-pci": u"",
        u"avf": u"avf-",
        u"rdma-core": u"rdma-",
    }

    # Some identifiers constructed from suite names
    # have to be independent of NIC driver used.
    # In order to remove or reject the NIC driver part,
    # it is useful to have a list of such prefixes precomputed.
    FORBIDDEN_SUITE_PREFIX_LIST = [
        prefix for prefix in NIC_DRIVER_TO_SUITE_PREFIX.values() if prefix
    ]

    # Additional step for perf needs to know driver type.
    # Contains part of suite setup line, matching both single and double link.
    NIC_DRIVER_TO_SETUP_ARG = {
        u"vfio-pci": u"le link | performance",
        u"avf": u"le link | performance_avf",
        u"rdma-core": u"le link | performance_rdma",
    }

    # TODO CSIT-1481: Crypto HW should be read from topology file instead.
    NIC_NAME_TO_CRYPTO_HW = {
        u"Intel-X553": u"HW_C3xxx",
        u"Intel-X710": u"HW_DH895xcc",
        u"Intel-XL710": u"HW_DH895xcc",
    }

    PERF_TYPE_TO_KEYWORD = {
        u"mrr": u"Traffic should pass with maximum rate",
        u"ndrpdr": u"Find NDR and PDR intervals using optimized search",
        u"soak": u"Find critical load using PLRsearch",
    }

    PERF_TYPE_TO_SUITE_DOC_VER = {
        u"mrr": u'''fication:* In MaxReceivedRate tests TG sends traffic\\
| ... | at line rate and reports total received packets over trial period.\\''',
        # TODO: Figure out how to include the full "*[Ver] TG verification:*"
        # while keeping this readable and without breaking line length limit.
        u"ndrpdr": u'''ication:* TG finds and reports throughput NDR (Non Drop\\
| ... | Rate) with zero packet loss tolerance and throughput PDR (Partial Drop\\
| ... | Rate) with non-zero packet loss tolerance (LT) expressed in percentage\\
| ... | of packets transmitted. NDR and PDR are discovered for different\\
| ... | Ethernet L2 frame sizes using MLRsearch library.\\''',
        u"soak": u'''fication:* TG sends traffic at dynamically computed\\
| ... | rate as PLRsearch algorithm gathers data and improves its estimate\\
| ... | of a rate at which a prescribed small fraction of packets\\
| ... | would be lost. After set time, the serarch stops\\
| ... | and the algorithm reports its current estimate.\\''',
    }

    PERF_TYPE_TO_TEMPLATE_DOC_VER = {
        u"mrr": u'''Measure MaxReceivedRate for ${frame_size}B frames\\
| | ... | using burst trials throughput test.\\''',
        u"ndrpdr": u"Measure NDR and PDR values using MLRsearch algorithm.\\",
        u"soak": u"Estimate critical rate using PLRsearch algorithm.\\",
    }
