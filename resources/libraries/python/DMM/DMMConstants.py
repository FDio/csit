# Copyright (c) 2018 Huawei Technologies Co.,Ltd.
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

"""This file defines the constants variables for the DMM test."""

class DMMConstants(object):
    """Define the directory path for the DMM test."""

    # DMM testing directory location at topology nodes
    REMOTE_FW_DIR = '/tmp/DMM-testing'

    # Shell scripts location
    DMM_SCRIPTS = 'tests/dmm/dmm_scripts'

    # Libraries location
    DMM_DEPLIBS = 'tests/dmm/dmm_deplibs'

    # Config files location for the DMM test
    DMM_TESTCONFIG = 'tests/dmm/dmm_testconfig'