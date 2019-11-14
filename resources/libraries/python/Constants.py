# Copyright (c) 2019 Cisco and/or its affiliates.
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

Here, "constant" means a value that keeps its value since initialization.
However, the value does not need to be hardcoded here,
some values are affected by environment variables.

TODO: Review env and constant names, make them matching if possible.
"""


import os


def get_str_from_env(env_var_names, default_value):
    """Attempt to read string from environment variable, return that or default.

    If environment variable exists, but is empty (and default is not),
    empty string is returned.

    Several environment variable names are examined, as CSIT currently supports
    a mix of naming convensions.
    Here "several" means there are hardcoded prefixes to try,
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
    return True if env_str in ("true", "yes", "y", "1") else False


def get_optimistic_bool_from_env(env_var_names):
    """Attempt to read bool from environment variable, assume True by default.

    Conversion is lenient and optimistic, only few strings are considered false.

    :param env_var_names: Base names of environment variable to attempt to read.
    :type env_var_names: str, or list of str, or tuple of str
    :returns: The value read, or True.
    :rtype: bool
    """
    env_str = get_str_from_env(env_var_names, "").lower()
    return False if env_str in ("false", "no", "n", "0") else True


class Constants(object):
    """Constants used in CSIT.

    TODO: Yaml files are easier for humans to edit.
    Figure out how to set the attributes by parsing a file
    that works regardless of current working directory.
    """

    # OpenVPP testing directory location at topology nodes
    REMOTE_FW_DIR = '/tmp/openvpp-testing'

    # shell scripts location
    RESOURCES_LIB_SH = 'resources/libraries/bash'

    # Python API provider location
    RESOURCES_PAPI_PROVIDER = 'resources/tools/papi/vpp_papi_provider.py'

    # vat templates location
    RESOURCES_TPL_VAT = 'resources/templates/vat'

    # Kubernetes templates location
    RESOURCES_TPL_K8S = 'resources/templates/kubernetes'

    # KernelVM templates location
    RESOURCES_TPL_VM = 'resources/templates/vm'

    # Container templates location
    RESOURCES_TPL_CONTAINER = 'resources/templates/container'

    # HTTP Server www root directory
    RESOURCES_TP_WRK_WWW = 'resources/traffic_profiles/wrk/www'

    # OpenVPP VAT binary name
    VAT_BIN_NAME = 'vpp_api_test'

    # VPP service unit name
    VPP_UNIT = 'vpp'

    # Number of system CPU cores.
    CPU_CNT_SYSTEM = 1

    # Number of vswitch main thread CPU cores.
    CPU_CNT_MAIN = 1

    # QEMU binary path
    QEMU_BIN_PATH = '/usr/bin'

    # QEMU VM kernel image path
    QEMU_VM_KERNEL = '/opt/boot/vmlinuz'

    # QEMU VM kernel initrd path
    QEMU_VM_KERNEL_INITRD = '/opt/boot/initrd.img'

    # QEMU VM nested image path
    QEMU_VM_IMAGE = '/var/lib/vm/vhost-nested.img'

    # QEMU VM DPDK path
    QEMU_VM_DPDK = '/opt/dpdk-19.02'

    # Docker container SUT image
    DOCKER_SUT_IMAGE_UBUNTU = 'snergster/csit-sut:latest'

    # Docker container arm SUT image
    DOCKER_SUT_IMAGE_UBUNTU_ARM = 'snergster/csit-arm-sut:latest'

    # TRex install directory
    TREX_INSTALL_DIR = '/opt/trex-core-2.61'

    # Honeycomb directory location at topology nodes:
    REMOTE_HC_DIR = '/opt/honeycomb'

    # Honeycomb persistence files location
    REMOTE_HC_PERSIST = '/var/lib/honeycomb/persist'

    # Honeycomb log file location
    REMOTE_HC_LOG = '/var/log/honeycomb/honeycomb.log'

    # Honeycomb templates location
    RESOURCES_TPL_HC = 'resources/templates/honeycomb'

    # ODL Client Restconf listener port
    ODL_PORT = 8181

    # Sysctl kernel.core_pattern
    KERNEL_CORE_PATTERN = '/tmp/%p-%u-%g-%s-%t-%h-%e.core'

    # Core dump directory
    CORE_DUMP_DIR = '/tmp'

    # Equivalent to ~0 used in vpp code
    BITWISE_NON_ZERO = 0xffffffff

    # Default path to VPP API socket.
    SOCKSVR_PATH = "/run/vpp/api.sock"

    # Number of trials to execute in MRR test.
    PERF_TRIAL_MULTIPLICITY = get_int_from_env("PERF_TRIAL_MULTIPLICITY", 10)

    # Duration of one trial in MRR test.
    PERF_TRIAL_DURATION = get_float_from_env("PERF_TRIAL_DURATION", 1.0)

    # UUID string of DUT1 /tmp volume created outside of the
    # DUT1 docker in case of vpp-device test. ${EMPTY} value means that
    #  /tmp directory is inside the DUT1 docker.
    DUT1_UUID = get_str_from_env("DUT1_UUID", "")

    # Default path to VPP API Stats socket.
    SOCKSTAT_PATH = "/run/vpp/stats.sock"

    # Global "kill switch" for CRC checking during runtime.
    FAIL_ON_CRC_MISMATCH = get_pessimistic_bool_from_env("FAIL_ON_CRC_MISMATCH")

    # Mapping from NIC name to its bps limit.
    NIC_NAME_TO_BPS_LIMIT = {
        "Cisco-VIC-1227": 10000000000,
        "Cisco-VIC-1385": 24500000000,
        "Intel-X520-DA2": 10000000000,
        "Intel-X553": 10000000000,
        "Intel-X710": 10000000000,
        "Intel-XL710": 24500000000,
        "Intel-XXV710": 24500000000,
        "Mellanox-CX556A": 100000000000,
        "virtual": 100000000,
    }

    # Mapping from NIC name to its pps limit.
    NIC_NAME_TO_PPS_LIMIT = {
        "Cisco-VIC-1227": 14880952,
        "Cisco-VIC-1385": 18750000,
        "Intel-X520-DA2": 14880952,
        "Intel-X553": 14880952,
        "Intel-X710": 14880952,
        "Intel-XL710": 18750000,
        "Intel-XXV710": 18750000,
        "Mellanox-CX556A": 60000000, #148809523,
        "virtual": 14880952,
    }

    # Suite file names use codes for NICs.
    NIC_NAME_TO_CODE = {
        "Cisco-VIC-1227": "10ge2p1vic1227",
        "Cisco-VIC-1385": "40ge2p1vic1385",
        "Intel-X520-DA2": "10ge2p1x520",
        "Intel-X553": "10ge2p1x553",
        "Intel-X710": "10ge2p1x710",
        "Intel-XL710": "40ge2p1xl710",
        "Intel-XXV710": "25ge2p1xxv710",
        "Mellanox-CX556A": "100ge2p1cx556a",
    }

    # Not each driver is supported by each NIC.
    NIC_NAME_TO_DRIVER = {
        "Cisco-VIC-1227": ["vfio-pci"],
        "Cisco-VIC-1385": ["vfio-pci"],
        "Intel-X520-DA2": ["vfio-pci"],
        "Intel-X553": ["vfio-pci"],
        "Intel-X710": ["vfio-pci", "avf"],
        "Intel-XL710": ["vfio-pci", "avf"],
        "Intel-XXV710": ["vfio-pci", "avf"],
        "Mellanox-CX556A": ["rdma-core"],
    }

    # Each driver needs different prugin to work.
    NIC_DRIVER_TO_PLUGINS = {
        "vfio-pci": "dpdk_plugin.so",
        "avf": "avf_plugin.so",
        "rdma-core": "rdma_plugin.so",
    }

    # Tags to differentiate tests for different NIC driver.
    NIC_DRIVER_TO_TAG = {
        "vfio-pci": "DRV_VFIO_PCI",
        "avf": "DRV_AVF",
        "rdma-core": "DRV_RDMA_CORE",
    }

    # Suite names have to be different, add prefix.
    NIC_DRIVER_TO_SUITE_PREFIX = {
        "vfio-pci": "",
        "avf": "avf-",
        "rdma-core": "rdma-",
    }

    # Additional step for perf needs to know driver type.
    # Contains part of suite setup line, matching both single and double link.
    NIC_DRIVER_TO_SETUP_ARG = {
        "vfio-pci": "le link | performance",
        "avf": "le link | performance_avf",
        "rdma-core": "le link | performance_rdma",
    }

    # TODO CSIT-1481: Crypto HW should be read from topology file instead.
    NIC_NAME_TO_CRYPTO_HW = {
        "Intel-X553": "HW_C3xxx",
        "Intel-X710": "HW_DH895xcc",
        "Intel-XL710": "HW_DH895xcc",
    }

    PERF_TYPE_TO_KEYWORD = {
        "mrr": "Traffic should pass with maximum rate",
        "ndrpdr": "Find NDR and PDR intervals using optimized search",
        "soak": "Find critical load using PLRsearch",
    }

    PERF_TYPE_TO_SUITE_DOC_VER = {
        "mrr" : '''fication:* In MaxReceivedRate tests TG sends traffic\\
| ... | at line rate and reports total received packets over trial period.\\''',
        # TODO: Figure out how to include the full "*[Ver] TG verification:*"
        # while keeping this readable and without breaking line length limit.
        "ndrpdr": '''fication:* TG finds and reports throughput NDR (Non Drop\\
| ... | Rate) with zero packet loss tolerance and throughput PDR (Partial Drop\\
| ... | Rate) with non-zero packet loss tolerance (LT) expressed in percentage\\
| ... | of packets transmitted. NDR and PDR are discovered for different\\
| ... | Ethernet L2 frame sizes using MLRsearch library.\\''',
        "soak": '''fication:* TG sends traffic at dynamically computed\\
| ... | rate as PLRsearch algorithm gathers data and improves its estimate\\
| ... | of a rate at which a prescribed small fraction of packets\\
| ... | would be lost. After set time, the serarch stops\\
| ... | and the algorithm reports its current estimate.\\''',
    }

    PERF_TYPE_TO_TEMPLATE_DOC_VER = {
        "mrr": '''Measure MaxReceivedRate for ${frame_size}B frames\\
| | ... | using burst trials throughput test.\\''',
        "ndrpdr": '''Measure NDR and PDR values using MLRsearch algorithm.\\''',
        "soak": '''Estimate critical rate using PLRsearch algorithm.\\''',
    }

