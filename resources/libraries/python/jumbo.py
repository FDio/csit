# Copyright (c) 2026 Cisco and/or its affiliates.
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

"""Utility functions for handling jumbo support based on Robot variables."""

from typing import Optional

from robot.libraries.BuiltIn import BuiltIn

from resurces.libraries.python.Constants import get_str_from_env


class Jumbo:
    """Encapsulation of jumbo constants and keywords for robot."""

    # MTU values to use. Must allow tested packets including encap overhead.
    # Max overhead is 96, xxv710 refuses above 9194, 9145 is in the middle.
    MTU_JUMBO = get_str_from_env("MTU_JUMBO", 9145)
    # VPP can handle just below 2048 without chaining, 1800 should be enough.
    MTU_NORMAL = get_str_from_env("MTU_NORMAL", 1800)

    @staticmethod
    def jumbo_enabled() -> bool:
        """Detect jumbo from test variable.

        This implementation also works when jumbo is set as string and not bool.

        :returns: True only when jumbo is enabled via robot variable.
        :rtype: bool
        """
        return (
            str(BuiltIn().get_variable_value("\\${jumbo}", False)).lower()
            == "true"
        )

    @staticmethod
    def get_mtu(is_jumbo: Optional[bool] = None) -> int:
        """Return MTU value depending on whether jumbo frames are enabled.

        If the parameter is not specified (is None), detect from Robot variable.

        :param is_jumbo: Whether the current tests uses jumbo frames.
        :type is_jumbo: Optional[bool]
        :returns: One of the two constant values defined above.
        :rtype: int
        """
        if is_jumbo is None:
            is_jumbo = Jumbo.jumbo_enabled()
        if is_jumbo:
            return Jumbo.MTU_JUMBO
        return Jumbo.MTU_NORMAL
