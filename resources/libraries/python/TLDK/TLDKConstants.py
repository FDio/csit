# Copyright (c) 2017 Cisco and/or its affiliates.
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


"""This file defines the constants variables for the TLDK test."""


class TLDKConstants(object):
    """Define the directory path for the TLDK test."""

    # TLDK testing directory location at topology nodes
    REMOTE_FW_DIR = '/tmp/TLDK-testing'

    # Shell scripts location
    TLDK_SCRIPTS = 'tests/tldk/tldk_scripts'

    # Libraries location
    TLDK_DEPLIBS = 'tests/tldk/tldk_deplibs'

    # Config files location for the TLDK test
    TLDK_TESTCONFIG = 'tests/tldk/tldk_testconfig'

    # URL with TLDK git repository
    TLDK_REPOSITORY = 'https://gerrit.fd.io/r/tldk'

    # Exact filename for DPDK archive
    DPDK_ARCHIVE = 'dpdk-16.11.1.tar.xz'

    # URL with DPDK archive
    DPDK_ARCHIVE_URL = 'http://fast.dpdk.org/rel/{0}'.format(DPDK_ARCHIVE)
