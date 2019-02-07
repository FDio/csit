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
    """Constants used in CSIT."""

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
