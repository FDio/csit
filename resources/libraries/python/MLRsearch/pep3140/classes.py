# Copyright (c) 2023 Cisco and/or its affiliates.
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

"""Module defining a subclass of dict with an alternative str method."""


class Pep3140Dict(dict):
    """A dict with str support as proposed in PEP 3140.

    Python implemented str acting on dict such that the resulting string
    shows both keys and values in their repr form.
    Therefore, str() of a dict gives the same result as repr().

    This class shows both keys and values their str form instead.
    """

    def __str__(self) -> str:
        """Return comma+space separated str of items in curly brackets.

        :returns: PEP 3140 string form of the dict data.
        :rtype: str
        """
        body = ", ".join(f"{key}: {value}" for key, value in self.items())
        return f"{{{body}}}"
