# Copyright (c) 2018 Cisco and/or its affiliates.
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

"""Module with utilities for autogeneration of non-customizable testcases."""

from .Testcase import Testcase


class DefaultTestcase(Testcase):
    """Testcase subclass with a rigid template string."""

    def __init__(self, suite_id):
        """Construct instance for identified suite.

        :param suite_id: Suite identifier, without NIC prefix and .robot suffix.
            Example: ethip6srhip6-ip6base-srv6enc2sids-nodecaps-ndrpdr
        :type suite_id: str
        """
        template_string = r'''
| ${tc_num}-${frame_str}-${cores_str}c-''' + suite_id + r'''
| | [Tags] | ${frame_str} | ${cores_str}C
| | framesize=${frame_num} | phy_cores=${cores_num}
'''
        super(DefaultTestcase, self).__init__(template_string)
