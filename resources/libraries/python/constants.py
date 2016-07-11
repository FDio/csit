# Copyright (c) 2016 Cisco and/or its affiliates.
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

"""Constants used in tests."""


class Constants(object):  # pylint: disable=too-few-public-methods
    """Constants used in tests."""
    # OpenVPP testing directory location at topology nodes
    REMOTE_FW_DIR = '/tmp/openvpp-testing'

    # shell scripts location
    RESOURCES_LIB_SH = 'resources/libraries/bash'

    # vat templates location
    RESOURCES_TPL_VAT = 'resources/templates/vat'

    # OpenVPP VAT binary name
    VAT_BIN_NAME = 'vpp_api_test'

    # Honeycomb directory location at topology nodes:
    REMOTE_HC_DIR = '/opt/honeycomb/v3po-karaf-1.0.0-SNAPSHOT'

    # Honeycomb templates location
    RESOURCES_TPL_HC = 'resources/templates/honeycomb'
