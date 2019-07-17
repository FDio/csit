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

"""Constants used in CSIT."""


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
    DOCKER_SUT_IMAGE_UBUNTU_ARM = 'snergster/csit-sut-arm-ubuntu18:latest'

    # TRex install version
    TREX_INSTALL_VERSION = '2.54'

    # TRex install directory
    TREX_INSTALL_DIR = '/opt/trex-core-2.54'

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

    # Maximum number of API calls per PapiExecutor execution
    PAPI_MAX_API_BULK = 250

    # Mapping from NIC name to its bps limit.
    # TODO: Implement logic to lower limits to TG NIC or software. Or PCI.
    NIC_NAME_TO_LIMIT = {
        # TODO: Explain why ~40Gbps NICs are using ~25Gbps limit.
        "Cisco-VIC-1227": 10000000000,
        "Cisco-VIC-1385": 24500000000,
        "Intel-X520-DA2": 10000000000,
        "Intel-X553": 10000000000,
        "Intel-X710": 10000000000,
        "Intel-XL710": 24500000000,
        "Intel-XXV710": 24500000000,
        "virtual": 100000000,
    }

    # Suite file names use somewhat more rich (less readable) codes for NICs.
    NIC_NAME_TO_CODE = {
        "Cisco-VIC-1227": "10ge2p1vic1227",
        "Cisco-VIC-1385": "40ge2p1vic1385",
        "Intel-X520-DA2": "10ge2p1x520",
        "Intel-X553": "10ge2p1x553",
        "Intel-X710": "10ge2p1x710",
        "Intel-XL710": "40ge2p1xl710",
        "Intel-XXV710": "25ge2p1xxv710",
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
