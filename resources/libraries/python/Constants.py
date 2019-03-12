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

    # OpenVPP VAT binary name
    VAT_BIN_NAME = 'vpp_api_test'

    # VPP service unit name
    VPP_UNIT = 'vpp'

    # QEMU version to install
    QEMU_INSTALL_VERSION = 'qemu-2.11.2'

    # QEMU install directory
    QEMU_INSTALL_DIR = '/opt/qemu-2.11.2'

    # TRex install version
    TREX_INSTALL_VERSION = '2.35'

    # TRex install directory
    TREX_INSTALL_DIR = '/opt/trex-core-2.35'

    # Kubernetes templates location
    RESOURCES_TPL_K8S = 'resources/templates/kubernetes'

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

    # Mapping from NIC name to its bps limit.
    # TODO: Implement logic to lower limits to TG NIC or software. Or PCI.
    NIC_NAME_TO_LIMIT = {
        # VIC-1385 and XL710 could have ~40Gbps limit, not 24.5Gbps.
        # Make sure we use 24.5Gbps just because the TG NIC is 25ge.
        "Cisco-VIC-1227": 10000000000,
        "Cisco-VIC-1385": 24500000000,
        "Intel-X520-DA2": 10000000000,
        "Intel-X553": 10000000000,
        "Intel-X710": 10000000000,
        "Intel-XL710": 24500000000,
        "Intel-XXV710": 24500000000,
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

    NIC_CODE_TO_NAME = {
        "10ge2p1vic1227": "Cisco-VIC-1227",
        "40ge2p1vic1385": "Cisco-VIC-1385",
        "10ge2p1x520": "Intel-X520-DA2",
        "10ge2p1x553": "Intel-X553",
        "10ge2p1x710": "Intel-X710",
        "40ge2p1xl710": "Intel-XL710",
        "25ge2p1xxv710": "Intel-XXV710",
    }
